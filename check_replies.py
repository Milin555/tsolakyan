"""
check_replies.py - Scan every sender inbox for replies to the July campaign.

You sent 1,751 emails and never tracked a single reply. This finds them.

Reads credentials from email_accounts.txt (same format campaign_manager.py uses),
connects over IMAP, and pulls every message that isn't from you. Anything whose
sender matches a lead in the CRM is flagged as a reply and the CRM is updated so
the sequence stops emailing someone who already answered.

Usage:
    python check_replies.py
    python check_replies.py --days 90     # look further back
"""

import argparse
import csv
import email
import imaplib
import os
import re
from datetime import datetime, timedelta
from email.header import decode_header

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ACCOUNTS_FILE = os.path.join(BASE_DIR, "email_accounts.txt")
CRM_FILE = os.path.join(BASE_DIR, "data", "campaign_crm.csv")
REPORT_FILE = os.path.join(BASE_DIR, "REPLIES_FOUND.csv")

IMAP_SERVERS = {
    "smtp.gmail.com": "imap.gmail.com",
    "smtp.office365.com": "outlook.office365.com",
    "smtp-mail.outlook.com": "outlook.office365.com",
    "smtp.zoho.com": "imap.zoho.com",
}

# Auto-replies and delivery failures are not real replies.
NOISE = [
    "mailer-daemon", "postmaster", "no-reply", "noreply", "donotreply",
    "notification", "notifications", "support@", "billing@", "newsletter",
]
NOISE_SUBJECTS = [
    "undeliverable", "delivery status", "delivery failure", "returned mail",
    "out of office", "automatic reply", "auto-reply", "autoreply",
    "mail delivery", "failure notice", "message blocked",
]

# Words that signal a lead is actually interested. Used only for ranking.
HOT = [
    "yes", "interested", "sure", "send", "link", "sounds good", "how much",
    "price", "cost", "call", "let's", "lets talk", "tell me more", "curious",
    "looks good", "great", "love", "when can", "available",
]
COLD = [
    "unsubscribe", "remove me", "stop", "not interested", "no thanks",
    "spam", "do not contact", "take me off",
]


def decode_field(raw):
    """MIME-decode a header into a plain string."""
    if not raw:
        return ""
    parts = []
    for chunk, enc in decode_header(raw):
        if isinstance(chunk, bytes):
            try:
                parts.append(chunk.decode(enc or "utf-8", errors="ignore"))
            except (LookupError, UnicodeDecodeError):
                parts.append(chunk.decode("utf-8", errors="ignore"))
        else:
            parts.append(chunk)
    return " ".join(parts).strip()


def extract_address(raw):
    """Pull the bare email address out of a From header."""
    match = re.search(r"[\w\.\-\+]+@[\w\.\-]+\.\w+", raw or "")
    return match.group(0).lower() if match else ""


def body_preview(msg, limit=400):
    """Best-effort plain-text preview of a message body."""
    text = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                payload = part.get_payload(decode=True)
                if payload:
                    text = payload.decode("utf-8", errors="ignore")
                    break
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            text = payload.decode("utf-8", errors="ignore")

    # Drop quoted history so we score what THEY wrote, not your original email.
    for marker in ("On ", "-----Original", "________", "From:", "> "):
        idx = text.find("\n" + marker)
        if idx > 0:
            text = text[:idx]
            break

    return re.sub(r"\s+", " ", text).strip()[:limit]


def load_accounts():
    accounts = []
    if not os.path.exists(ACCOUNTS_FILE):
        print(f"ERROR: {ACCOUNTS_FILE} not found.")
        return accounts

    with open(ACCOUNTS_FILE, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 4:
                continue
            smtp_host = parts[2]
            imap_host = IMAP_SERVERS.get(smtp_host)
            if not imap_host:
                print(f"  ! No IMAP mapping for {smtp_host} ({parts[0]}) - skipped")
                continue
            accounts.append({"email": parts[0], "password": parts[1], "imap": imap_host})
    return accounts


def load_crm_emails():
    """Map lead email -> lead name, so we can tell replies from strangers."""
    leads = {}
    if not os.path.exists(CRM_FILE):
        return leads
    with open(CRM_FILE, "r", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            addr = (row.get("Email") or "").strip().lower()
            if addr:
                leads[addr] = row.get("Name", "")
    return leads


def classify(subject, preview):
    """Rank a reply so the hot ones surface first."""
    blob = f"{subject} {preview}".lower()
    if any(w in blob for w in COLD):
        return "UNSUBSCRIBE", 0
    hits = sum(1 for w in HOT if w in blob)
    if hits >= 2:
        return "HOT", 100 + hits
    if hits == 1:
        return "WARM", 50
    return "REPLY", 10


def is_noise(sender, subject):
    blob = sender.lower()
    if any(n in blob for n in NOISE):
        return True
    return any(n in subject.lower() for n in NOISE_SUBJECTS)


def scan_account(account, lead_emails, since_date):
    """Return every non-noise inbound message for one mailbox."""
    found = []
    try:
        conn = imaplib.IMAP4_SSL(account["imap"], timeout=30)
        conn.login(account["email"], account["password"])
        conn.select("INBOX")

        status, data = conn.search(None, f'(SINCE "{since_date}")')
        if status != "OK":
            conn.logout()
            return found

        ids = data[0].split()
        print(f"  {account['email']}: {len(ids)} messages since {since_date}")

        for msg_id in ids:
            status, raw = conn.fetch(msg_id, "(RFC822)")
            if status != "OK" or not raw or not raw[0]:
                continue

            msg = email.message_from_bytes(raw[0][1])
            sender_raw = decode_field(msg.get("From"))
            sender = extract_address(sender_raw)
            subject = decode_field(msg.get("Subject"))

            if not sender or sender == account["email"].lower():
                continue
            if is_noise(sender_raw, subject):
                continue

            preview = body_preview(msg)
            category, score = classify(subject, preview)

            # A known lead outranks a stranger with the same wording.
            in_crm = sender in lead_emails
            if in_crm:
                score += 25

            found.append({
                "Score": score,
                "Type": category,
                "In_CRM": "YES" if in_crm else "no",
                "From": sender,
                "Name": lead_emails.get(sender, sender_raw),
                "Subject": subject,
                "Date": decode_field(msg.get("Date")),
                "Preview": preview,
                "Inbox": account["email"],
            })

        conn.close()
        conn.logout()

    except imaplib.IMAP4.error as exc:
        print(f"  ! {account['email']}: login/IMAP failed - {exc}")
        print("    (Gmail needs IMAP enabled + an App Password)")
    except Exception as exc:
        print(f"  ! {account['email']}: {exc}")

    return found


def update_crm(replies):
    """Mark responders so the sequence stops emailing them."""
    if not os.path.exists(CRM_FILE):
        return 0

    responders = {r["From"] for r in replies if r["In_CRM"] == "YES"}
    if not responders:
        return 0

    with open(CRM_FILE, "r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        fieldnames = reader.fieldnames
        rows = list(reader)

    updated = 0
    for row in rows:
        addr = (row.get("Email") or "").strip().lower()
        if addr in responders and row.get("Status") != "Replied":
            row["Status"] = "Replied"
            updated += 1

    if updated:
        with open(CRM_FILE, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    return updated


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=60,
                        help="How far back to scan (default 60)")
    args = parser.parse_args()

    since = (datetime.now() - timedelta(days=args.days)).strftime("%d-%b-%Y")

    print("=" * 60)
    print("  REPLY SCANNER - finding what you never checked")
    print("=" * 60)

    accounts = load_accounts()
    if not accounts:
        print("No usable accounts found.")
        return

    lead_emails = load_crm_emails()
    print(f"Accounts: {len(accounts)} | CRM leads: {len(lead_emails)}")
    print(f"Scanning since {since}\n")

    replies = []
    for acct in accounts:
        replies.extend(scan_account(acct, lead_emails, since))

    if not replies:
        print("\nNo replies found.")
        print("If every account failed to log in, the passwords in")
        print("email_accounts.txt are SMTP-only or IMAP is disabled.")
        return

    replies.sort(key=lambda r: r["Score"], reverse=True)

    with open(REPORT_FILE, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(replies[0].keys()))
        writer.writeheader()
        writer.writerows(replies)

    hot = [r for r in replies if r["Type"] == "HOT"]
    warm = [r for r in replies if r["Type"] == "WARM"]
    unsub = [r for r in replies if r["Type"] == "UNSUBSCRIBE"]

    print("\n" + "=" * 60)
    print(f"  TOTAL INBOUND: {len(replies)}")
    print(f"  HOT: {len(hot)}   WARM: {len(warm)}   UNSUBSCRIBE: {len(unsub)}")
    print("=" * 60)

    for r in (hot + warm)[:15]:
        print(f"\n[{r['Type']}] {r['Name']} <{r['From']}>")
        print(f"  Subject: {r['Subject']}")
        print(f"  {r['Preview'][:180]}")

    marked = update_crm(replies)
    print(f"\nCRM: {marked} leads marked 'Replied'")
    print(f"Full report: {REPORT_FILE}")

    if hot or warm:
        print("\n>>> Reply to these TODAY. Send your live demo link. <<<")


if __name__ == "__main__":
    main()
