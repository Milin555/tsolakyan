"""
check_bounces.py - Count hard bounces from the July campaign.

check_replies.py deliberately filtered mailer-daemon out as noise, which means
we never measured the bounce rate. That number decides one real question:

  High bounces  -> the LIST is bad -> re-verify before sending again
  Low bounces   -> mail was delivered -> the OFFER failed, not the plumbing

Usage:
    python check_bounces.py
"""

import email
import imaplib
import os
import re
from collections import Counter
from datetime import datetime, timedelta
from email.header import decode_header

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ACCOUNTS_FILE = os.path.join(BASE_DIR, "email_accounts.txt")

BOUNCE_SENDERS = ["mailer-daemon", "postmaster", "mail delivery"]
BOUNCE_SUBJECTS = [
    "undeliverable", "delivery status", "delivery failure", "returned mail",
    "failure notice", "mail delivery failed", "delivery incomplete",
    "message blocked", "delivery has failed", "couldn't be delivered",
    "address not found", "message not delivered",
]

# Phrases inside the bounce body that tell us WHY it failed.
REASONS = {
    "spam / blocked": ["spam", "blocked", "blacklist", "reputation", "policy",
                       "rejected due to", "550 5.7", "bulk", "unsolicited"],
    "no such user": ["does not exist", "no such user", "unknown user",
                     "user unknown", "address not found", "550 5.1.1",
                     "recipient not found", "invalid recipient"],
    "mailbox full": ["mailbox full", "quota", "over quota"],
    "domain problem": ["domain not found", "no mx", "host not found",
                       "unrouteable", "dns"],
    "rate limited": ["rate limit", "too many", "try again later", "throttl",
                     "421 4.7"],
}


def decode_field(raw):
    if not raw:
        return ""
    out = []
    for chunk, enc in decode_header(raw):
        if isinstance(chunk, bytes):
            try:
                out.append(chunk.decode(enc or "utf-8", errors="ignore"))
            except (LookupError, UnicodeDecodeError):
                out.append(chunk.decode("utf-8", errors="ignore"))
        else:
            out.append(chunk)
    return " ".join(out).strip()


def get_body(msg, limit=3000):
    text = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() in ("text/plain", "message/delivery-status"):
                payload = part.get_payload(decode=True)
                if payload:
                    text += payload.decode("utf-8", errors="ignore") + "\n"
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            text = payload.decode("utf-8", errors="ignore")
    return text[:limit]


def classify_reason(body):
    low = body.lower()
    for reason, needles in REASONS.items():
        if any(n in low for n in needles):
            return reason
    return "other / unknown"


def load_accounts():
    accounts = []
    if not os.path.exists(ACCOUNTS_FILE):
        return accounts
    with open(ACCOUNTS_FILE, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 4 and "gmail" in parts[2]:
                accounts.append({"email": parts[0], "password": parts[1],
                                 "imap": "imap.gmail.com"})
    return accounts


def main():
    since = (datetime.now() - timedelta(days=75)).strftime("%d-%b-%Y")
    accounts = load_accounts()

    print("=" * 60)
    print("  BOUNCE ANALYSIS - did the mail actually get delivered?")
    print("=" * 60)
    print(f"Accounts: {len(accounts)} | since {since}\n")

    total_bounces = 0
    reasons = Counter()
    bounced_addresses = set()

    for acct in accounts:
        try:
            conn = imaplib.IMAP4_SSL(acct["imap"], timeout=30)
            conn.login(acct["email"], acct["password"])
            conn.select("INBOX")

            status, data = conn.search(None, f'(SINCE "{since}")')
            if status != "OK":
                conn.logout()
                continue

            ids = data[0].split()
            acct_bounces = 0

            for msg_id in ids:
                status, raw = conn.fetch(msg_id, "(RFC822)")
                if status != "OK" or not raw or not raw[0]:
                    continue

                msg = email.message_from_bytes(raw[0][1])
                sender = decode_field(msg.get("From")).lower()
                subject = decode_field(msg.get("Subject")).lower()

                is_bounce = (any(s in sender for s in BOUNCE_SENDERS)
                             or any(s in subject for s in BOUNCE_SUBJECTS))
                if not is_bounce:
                    continue

                acct_bounces += 1
                body = get_body(msg)
                reasons[classify_reason(body)] += 1

                for addr in re.findall(r"[\w\.\-\+]+@[\w\.\-]+\.\w+", body):
                    low = addr.lower()
                    if "gmail.com" not in low and "daemon" not in low:
                        bounced_addresses.add(low)

            total_bounces += acct_bounces
            print(f"  {acct['email']}: {acct_bounces} bounces / {len(ids)} messages")

            conn.close()
            conn.logout()

        except Exception as exc:
            print(f"  ! {acct['email']}: {exc}")

    sent = 1751
    print("\n" + "=" * 60)
    print(f"  EMAILS SENT (from CRM):  {sent}")
    print(f"  BOUNCES FOUND:           {total_bounces}")
    print(f"  BOUNCE RATE:             {total_bounces / sent * 100:.2f}%")
    print(f"  UNIQUE BAD ADDRESSES:    {len(bounced_addresses)}")
    print("=" * 60)

    if reasons:
        print("\n  WHY THEY BOUNCED:")
        for reason, count in reasons.most_common():
            print(f"    {reason:<22} {count:>4}  ({count / max(total_bounces,1) * 100:.0f}%)")

    if bounced_addresses:
        out = os.path.join(BASE_DIR, "bounced_addresses.txt")
        with open(out, "w", encoding="utf-8") as fh:
            fh.write("\n".join(sorted(bounced_addresses)))
        print(f"\n  Saved: {out}")

    print("\n  VERDICT:")
    rate = total_bounces / sent * 100
    if rate > 15:
        print("    Bounce rate is HIGH. The list is the problem.")
        print("    Re-verify every address before the next send.")
    elif rate > 5:
        print("    Bounce rate is moderate. Clean the list, then send.")
    else:
        print("    Bounce rate is LOW - the mail was accepted by their servers.")
        print("    So delivery was NOT the main failure. The OFFER was.")
        print("    (No link in the email + no follow-ups.)")


if __name__ == "__main__":
    main()
