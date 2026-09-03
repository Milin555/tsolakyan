"""
send_batch.py - send a verified outreach batch, with a pre-flight that refuses
to send if the demo it links to is broken or still carries foreign content.

    python3 send_batch.py send_batch1.json --dry-run
    python3 send_batch.py send_batch1.json --go
"""
import json, re, ssl, sys, smtplib, time, urllib.request, csv, os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone

BASE = os.path.dirname(os.path.abspath(__file__))
ACCOUNTS = os.path.join(BASE, "email_accounts.txt")
SENT_LOG = os.path.join(BASE, "sent_log.csv")
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36'}

FORBIDDEN = ["Jim Arnold", "Gary Solnit", "Englehardt-Nash", "Kathryn Alderman",
             "Buy/Sell Advisory", "Transitions Program", "Mastermind",
             "Foundation Dental Alliance", "Superheroes Behind"]


def preflight(url):
    """The demo must be live and free of the source template's own content."""
    try:
        h = urllib.request.urlopen(urllib.request.Request(url, headers=UA),
                                   timeout=25, context=ctx).read().decode("utf-8", "ignore")
    except Exception as e:
        return False, f"demo unreachable: {str(e)[:44]}"
    if len(h) < 5000:
        return False, f"demo suspiciously small ({len(h)}b)"
    vis = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", h, flags=re.S | re.I)
    vis = " ".join(re.sub(r"<[^>]+>", " ", vis).split())
    for bad in FORBIDDEN:
        if bad.lower() in vis.lower():
            return False, f"demo still shows '{bad}'"
    return True, "ok"


def accounts():
    out = []
    for line in open(ACCOUNTS):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        p = line.split(",")
        if len(p) >= 4:
            out.append({"email": p[0].strip(), "pw": p[1].strip(),
                        "host": p[2].strip(), "port": int(p[3].strip())})
    return out


def log(row):
    new = not os.path.exists(SENT_LOG) or os.path.getsize(SENT_LOG) == 0
    with open(SENT_LOG, "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["timestamp", "email", "username", "step", "sender", "subject", "demo_url"])
        w.writerow(row)


def main():
    path = sys.argv[1]
    go = "--go" in sys.argv
    batch = json.load(open(path))
    accts = accounts()
    if not accts:
        print("no sender accounts"); sys.exit(1)
    print(f"{'SENDING' if go else 'DRY RUN'} - {len(batch)} message(s), {len(accts)} inbox(es)\n")

    sent = held = 0
    for i, o in enumerate(batch):
        to = o["emails"][0]
        m = re.search(r"(https://milin555\.github\.io/\S+?)/", o["body"])
        url = (m.group(1) + "/") if m else ""
        ok, why = preflight(url) if url else (False, "no demo link in body")
        if not ok:
            print(f"  HELD  {o['name'][:34]:36s} {why}")
            held += 1
            continue
        acct = accts[i % len(accts)]
        print(f"  {'SEND' if go else 'would send'}  {o['name'][:32]:34s} {to:34s} via {acct['email']}")
        if not go:
            continue
        msg = MIMEMultipart()
        msg["From"] = f"Milin Dholiya <{acct['email']}>"
        msg["To"] = to
        msg["Subject"] = o["subject"]
        msg["Reply-To"] = "dholiyamilin@gmail.com"
        msg.attach(MIMEText(o["body"], "plain"))
        try:
            s = smtplib.SMTP(acct["host"], acct["port"], timeout=30)
            s.starttls(); s.login(acct["email"], acct["pw"])
            s.sendmail(acct["email"], to, msg.as_string()); s.quit()
            log([datetime.now(timezone.utc).isoformat(timespec="seconds"), to,
                 o.get("slug", ""), 1, acct["email"], o["subject"], url])
            sent += 1
            print("        delivered to SMTP")
        except Exception as e:
            print(f"        SMTP FAILED: {str(e)[:70]}")
        time.sleep(20)   # spacing; these are cold sends from consumer inboxes

    print(f"\n  sent {sent}   held {held}")
    if go and sent:
        print(f"  logged to {SENT_LOG}")


if __name__ == "__main__":
    main()
