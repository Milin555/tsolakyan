"""
check_account_health.py - Are the 18 Gmail accounts actually safe to keep using?

Google warns before it suspends. This searches each inbox specifically for
security / policy / sending-limit notices from Google, and reports how close
each account is to trouble.

Uses targeted IMAP search (not a full fetch) so it runs in ~1 minute.

Usage:
    python check_account_health.py
"""

import email
import imaplib
import os
from email.header import decode_header

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ACCOUNTS_FILE = os.path.join(BASE_DIR, "email_accounts.txt")

# Subjects Google uses when something is wrong with an account.
DANGER = [
    "suspended", "disabled", "unusual activity", "sending limit",
    "policy violation", "compromised", "critical security",
    "temporarily locked", "review your account", "sending quota",
    "bulk sender", "spam policy", "account access",
]

WARN = [
    "security alert", "new sign-in", "new device", "less secure",
    "verify it's you", "suspicious sign in",
]


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
                accounts.append({"email": parts[0], "password": parts[1]})
    return accounts


def check(acct):
    """Return (status, [notices]) for one mailbox."""
    notices = []
    try:
        conn = imaplib.IMAP4_SSL("imap.gmail.com", timeout=30)
        conn.login(acct["email"], acct["password"])
        conn.select("INBOX")

        # Only pull mail from Google itself - fast.
        status, data = conn.search(None, '(FROM "google.com")')
        ids = data[0].split() if status == "OK" else []

        for msg_id in ids[-40:]:                      # last 40 is plenty
            status, raw = conn.fetch(msg_id, "(BODY.PEEK[HEADER.FIELDS (SUBJECT DATE)])")
            if status != "OK" or not raw or not raw[0]:
                continue
            msg = email.message_from_bytes(raw[0][1])
            subject = decode_field(msg.get("Subject"))
            date = decode_field(msg.get("Date"))
            low = subject.lower()

            if any(d in low for d in DANGER):
                notices.append(("DANGER", subject, date))
            elif any(w in low for w in WARN):
                notices.append(("warn", subject, date))

        # Gmail exposes the Spam folder - a large one is its own signal.
        spam_count = 0
        try:
            conn.select('"[Gmail]/Spam"')
            status, data = conn.search(None, "ALL")
            if status == "OK":
                spam_count = len(data[0].split())
        except Exception:
            pass

        conn.logout()

        danger = [n for n in notices if n[0] == "DANGER"]
        state = "AT RISK" if danger else ("watch" if notices else "healthy")
        return state, notices, spam_count, None

    except imaplib.IMAP4.error as exc:
        return "LOGIN FAILED", [], 0, str(exc)
    except Exception as exc:
        return "ERROR", [], 0, str(exc)


def main():
    accounts = load_accounts()
    print("=" * 66)
    print("  GMAIL ACCOUNT HEALTH - are these safe to keep sending from?")
    print("=" * 66)
    print(f"Checking {len(accounts)} accounts...\n")

    tally = {"healthy": 0, "watch": 0, "AT RISK": 0, "LOGIN FAILED": 0, "ERROR": 0}
    flagged = []

    for acct in accounts:
        state, notices, spam_count, err = check(acct)
        tally[state] = tally.get(state, 0) + 1

        mark = {"healthy": "OK  ", "watch": "WARN", "AT RISK": "RISK",
                "LOGIN FAILED": "FAIL", "ERROR": "ERR "}.get(state, "?   ")

        print(f"{mark} {acct['email']:<32} spam folder: {spam_count}")
        if err:
            print(f"       -> {err}")
        for level, subject, date in notices[:3]:
            print(f"       [{level}] {subject[:60]}")
            flagged.append((acct["email"], level, subject))

    print("\n" + "=" * 66)
    print("  SUMMARY")
    print("=" * 66)
    for state, count in tally.items():
        if count:
            print(f"  {state:<14} {count}")

    print("\n  VERDICT:")
    if tally.get("AT RISK") or tally.get("LOGIN FAILED"):
        print("    Some accounts are flagged or locked. Do NOT scale sending.")
        print("    Move to real domains before any volume campaign.")
    elif tally.get("watch"):
        print("    No suspensions, but Google has sent security notices.")
        print("    Safe for a SMALL test (10-15/account/day). Not for scale.")
    else:
        print("    No warnings found. Accounts are currently healthy.")
        print("    Still free Gmail - safe for testing, not for 200+/day.")

    print("\n  Regardless of result: use these to TEST the new offer on ~100")
    print("  emails. Only buy domains if the test shows email actually works.")


if __name__ == "__main__":
    main()
