import argparse
import csv
import json
import os
import random
import re
import smtplib
import sys
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

# CONFIGURATION
# ==========================================

# 1. Active Hour Range (Script sleeps if outside business hours)
START_HOUR = 0
END_HOUR = 24

# 2. Delay Range (in seconds) between each email sent
MIN_DELAY_SECONDS = 6
MAX_DELAY_SECONDS = 10

# 3. Safe Sending Parameters
DAILY_LIMIT_PER_ACCOUNT = 12  # WARM-UP. Per-account per-day cap. See WARMUP_SCHEDULE.

# Cold consumer-Gmail mailboxes get flagged fast at volume. Ramp deliberately.
# Bump DAILY_LIMIT_PER_ACCOUNT (and the field-5 value in email_accounts.txt)
# one step at a time, and only if bounce rate stays under 2% and no account
# has been challenged. Going back down is much harder than going up slowly.
WARMUP_SCHEDULE = {
    "week_1": 10,
    "week_2": 15,
    "week_3": 20,
    "week_4": 25,
}
FOLLOWUP_WAIT_DAYS = 3       # Default days to wait before sending a follow-up

# 4. Sequence: 5 touches total (1 initial + 4 follow-ups)
MAX_STEP = 5

# Days to wait after step N before sending step N+1
STEP_WAIT_DAYS = {
    1: 3,   # touch 1 -> touch 2 (day 3)
    2: 4,   # touch 2 -> touch 3 (day 7)
    3: 5,   # touch 3 -> touch 4 (day 12)
    4: 6,   # touch 4 -> touch 5 (day 18, breakup)
}

ROOT = os.path.dirname(os.path.abspath(__file__))

CRM_FILE = os.path.join(ROOT, "data", "campaign_crm.csv")
ACCOUNTS_FILE = os.path.join(ROOT, "email_accounts.txt")

# 5. SAFETY RAILS (added 2026-08 - this script can reach 29,931 real people)
DEMOS_FILE = os.path.join(ROOT, "demos.json")              # {username: live demo url}
SENT_LOG_FILE = os.path.join(ROOT, "sent_log.csv")         # every address ever sent to
SUPPRESSION_FILE = os.path.join(ROOT, "SUPPRESSION_LIST.txt")
BOUNCED_FILE = os.path.join(ROOT, "bounced_addresses.txt")

MAX_SENDS_PER_RUN = 50          # hard cap for a single invocation
CONSUMER_GMAIL_SAFE_LIMIT = 20  # above this on consumer Gmail -> needs --i-know-the-risk
CONSUMER_DOMAINS = {
    "gmail.com", "googlemail.com", "yahoo.com", "yahoo.co.uk",
    "outlook.com", "hotmail.com", "live.com", "aol.com", "icloud.com",
}

# Statuses that must never be contacted again.
DEAD_STATUSES = {"unsubscribed", "replied", "bounced", "do_not_contact", "complained"}

# CASL (Canada) + GDPR (EU/EEA) - excluded unless --include-restricted.
RESTRICTED_COUNTRIES = {
    "canada",
    "austria", "belgium", "bulgaria", "croatia", "cyprus", "czechia",
    "czech republic", "denmark", "estonia", "finland", "france", "germany",
    "greece", "hungary", "ireland", "republic of ireland", "italy", "latvia",
    "lithuania", "luxembourg", "malta", "netherlands", "the netherlands",
    "poland", "portugal", "romania", "slovakia", "slovenia", "spain",
    "sweden", "iceland", "liechtenstein", "norway",
}

# CASL (Canada) heads-up: in data/dental_leads_targeted.csv the Country column
# has only 5 distinct values and 26,820 of 29,931 rows are the MERGED value
# "United States / Canada". Canada therefore cannot be excluded by country
# alone; canada_signals() below infers it from row-level signals instead.
CANADA_AREA_CODES = {
    "204", "226", "236", "249", "250", "289", "306", "343", "365", "367",
    "368", "403", "416", "418", "428", "431", "437", "438", "450", "468",
    "474", "506", "514", "519", "548", "579", "581", "584", "587", "604",
    "613", "639", "647", "672", "683", "705", "709", "742", "753", "778",
    "780", "782", "807", "819", "825", "867", "873", "879", "902", "905",
}
CANADA_PLACE_TOKENS = [
    "Toronto", "Vancouver", "Calgary", "Montreal", "Ottawa", "Edmonton",
    "Winnipeg", "Mississauga", "Hamilton", "Halifax", "Victoria", "Saskatoon",
    "Quebec", "Ontario", "Alberta", "Manitoba", "Saskatchewan", "Nova Scotia",
    "New Brunswick", "Newfoundland", "British Columbia", "Canada", "Canadian",
]

# ==========================================
# OUTREACH TEMPLATES & SPINTAX
# ==========================================

# Initial Email Templates (Step 1)
INITIAL_TEMPLATES = [
    {
        "Subject": "your site",
        "Body": "Hey {Name} -\n\nWas looking at dental clinics in the area today and noticed your website layout makes it really easy for patients to just scroll past the important info without reading.\n\nI actually spent the last 10 hours building a custom, modernized version of your entire site from scratch just to see what it could look like. It actually turned out crazy good.\n\nSince I already did all the work, can I send over the live link and a quick video just to get your thoughts?\n\nMilin"
    },
    {
        "Subject": "your website",
        "Body": "Hi {Name} -\n\nI was looking at local dental clinics this morning and noticed your website layout makes it really easy for people to just scroll past the most important info without reading.\n\nI got inspired and spent the last 10 hours building a completely custom, modern version of your entire site from scratch to see what it could look like. It turned out crazy good.\n\nSince I already put the time in, are you open to me sending over the live link and a quick video so you can take a look?\n\nMilin"
    },
    {
        "Subject": "quick question",
        "Body": "Hey {Name} -\n\nWas browsing dental clinics in the area and noticed your site layout makes it pretty easy for patients to just scroll past the important info without actually reading it.\n\nI actually spent about 10 hours this weekend building a custom, modernized version of your entire website from scratch just to see what it could look like. It honestly turned out crazy good.\n\nSince I already did the heavy lifting, can I send over the live link and a quick video walkthrough to get your thoughts?\n\nMilin"
    }
]

# Follow-up Templates (Step 2)
FOLLOWUP_TEMPLATES = [
    {
        "Subject": "Re: Website Complete: {Name}",
        "Body": "Hi {Name},\n\nJust floating this back to the top of your inbox. I know you're busy running the practice.\n\nDid you get a chance to see the website concept I sent over? I'd love to get your thoughts.\n\nThanks,\n\nMilin\n\nP.S: I would love if you have a look at what I've built, might help me sleep peacefully ;)"
    },
    # Touch 3 (~day 7) - stop teasing, hand over the live link
    {
        "Subject": "{Name} - here's the link anyway",
        "Body": "Hi {Name},\n\nI'll stop asking permission and just send it: {DemoLink}\n\nThe main thing I changed is the booking flow. On your current site a patient has to scroll past several screens before they find how to book - on this one it's one tap, right at the top. That single change is usually where practices lose people on mobile.\n\nHave a look on your phone. If you think it's worse than what you have, tell me and I'll take it down.\n\nMilin"
    },
    # Touch 4 (~day 12) - pure value, no ask
    {
        "Subject": "one thing I noticed",
        "Body": "Hi {Name},\n\nNot chasing you about the demo - just one thing worth fixing on your current site whether you ever work with me or not.\n\nYour phone number isn't a tap-to-call link on mobile. Someone on a phone has to memorise it, leave your site, and dial manually. Most won't. Whoever manages your site can fix it in about two minutes.\n\nFree tip, no strings.\n\nMilin"
    },
    # Touch 5 (~day 18) - breakup. Highest-reply message in almost any sequence.
    {
        "Subject": "closing your file",
        "Body": "Hi {Name},\n\nI'm going to assume the timing isn't right and close your file so I stop cluttering your inbox.\n\nThe site I built is here if you ever want it: {DemoLink}\n\nIt'll stay live for another two weeks.\n\nAll the best with the practice.\n\nMilin"
    }
]

# NOTE (bug fix, 2026-08): there used to be a module level
#   DEMO_LINK = "https://your-portfolio.vercel.app"
# placeholder here. Every email built from it linked to nothing.
# The demo link is now PER LEAD and comes from demos.json ({username: url}).
# A lead with no demo URL is SKIPPED - never sent with a generic/broken link.

# ==========================================
# CORE UTILITY FUNCTIONS
# ==========================================

def parse_spintax(text):
    pattern = re.compile(r'\{([^}]+?\|[^}]+?)\}')
    while True:
        match = pattern.search(text)
        if not match:
            break
        options = match.group(1).split('|')
        text = text.replace(match.group(0), random.choice(options), 1)
    return text

def clean_emojis(text):
    if not text:
        return ""
    cleaned = "".join(c for c in text if ord(c) < 0x2600)
    return re.sub(r'\s+', ' ', cleaned).strip()

def get_email_content(lead, step, template_index, demo_link):
    """Build (subject, body) for one lead.

    demo_link is MANDATORY and must be that lead's own live demo URL.
    Passing an empty value is a programming error: callers must skip the lead
    instead (see resolve_demo_link / plan_campaign).
    """
    if not demo_link or not str(demo_link).strip():
        raise ValueError(
            "get_email_content() called without a per-lead demo link for %r. "
            "Leads without a demo URL must be skipped, not emailed."
            % lead.get("Username", lead.get("Email", "?"))
        )
    demo_link = str(demo_link).strip()

    name = clean_emojis(lead.get("Name", ""))
    if not name or name.startswith("+") or name.startswith("🦷"):
        category = clean_emojis(lead.get("Category", ""))
        if category and len(category) < 35:
            name = category
        else:
            username = clean_emojis(lead.get("Username", ""))
            if username:
                name = username
            else:
                name = "there"
    
    # Select template
    if step == 1:
        template = INITIAL_TEMPLATES[template_index % len(INITIAL_TEMPLATES)]
    else:
        # Step 2 -> FOLLOWUP[0], step 3 -> FOLLOWUP[1], and so on.
        template = FOLLOWUP_TEMPLATES[min(step - 2, len(FOLLOWUP_TEMPLATES) - 1)]

    subject = template["Subject"].replace("{Name}", name).replace("{DemoLink}", demo_link)
    body = template["Body"].replace("{Name}", name).replace("{DemoLink}", demo_link)

    subject = parse_spintax(subject)
    body = parse_spintax(body)
    
    return subject, body

def read_crm():
    if not os.path.exists(CRM_FILE):
        return []
    leads = []
    # utf-8-sig: the CRM on disk carries a BOM. Reading it as plain utf-8 made
    # the first column key "﻿\"Email\"" instead of "Email", so
    # lead.get("Email") returned "" for EVERY row and the whole campaign
    # silently no-opped. Do not change this back to "utf-8".
    with open(CRM_FILE, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            leads.append({(k.strip() if k else k): v for k, v in row.items()})
    return leads

CRM_BASE_FIELDS = ["Email", "Name", "Category", "Phone", "Website", "Country",
                   "Username", "Step", "Last_Sent_Date", "Assigned_Sender", "Status"]


def write_crm(leads, path=None):
    """Write the CRM atomically, preserving any extra columns rows carry."""
    if not leads:
        return
    path = path or CRM_FILE
    extras = []
    for row in leads:
        for key in row:
            if key and key not in CRM_BASE_FIELDS and key not in extras:
                extras.append(key)
    fieldnames = CRM_BASE_FIELDS + extras
    tmp = path + ".tmp"
    with open(tmp, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in leads:
            writer.writerow({k: row.get(k, "") for k in fieldnames})
    os.replace(tmp, path)

def load_smtp_accounts():
    accounts = []
    if not os.path.exists(ACCOUNTS_FILE):
        print(f"Error: Credentials file '{ACCOUNTS_FILE}' not found.")
        return []
    with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(",")
            if len(parts) >= 4:
                daily_limit = int(parts[4].strip()) if len(parts) >= 5 else DAILY_LIMIT_PER_ACCOUNT
                accounts.append({
                    "email": parts[0].strip(),
                    "password": parts[1].strip(),
                    "smtp_server": parts[2].strip(),
                    "smtp_port": int(parts[3].strip()),
                    "daily_limit": daily_limit
                })
    return accounts

def send_smtp_email(account, to_email, subject, body):
    msg = MIMEMultipart()
    msg['From'] = account['email']
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    server = None
    try:
        server = smtplib.SMTP(account['smtp_server'], account['smtp_port'])
        server.starttls()
        server.login(account['email'], account['password'])
        server.sendmail(account['email'], to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"            SMTP Error: {e}")
        return False
    finally:
        if server:
            try:
                server.quit()
            except:
                pass

def is_within_sending_hours():
    current_hour = datetime.now().hour
    if START_HOUR <= END_HOUR:
        return START_HOUR <= current_hour < END_HOUR
    else:
        return current_hour >= START_HOUR or current_hour < END_HOUR

# ==========================================
# SAFETY RAILS
# ==========================================

def canonical_country(raw):
    """'London, England, United Kingdom' -> 'united kingdom'.

    Country values are free text and sometimes carry city/region prefixes
    (the CRM has 'Toronto, Ontario, Canada'), so only the LAST comma separated
    segment is the country. Matching the whole string would wrongly flag
    'Northern Ireland, United Kingdom' as EU (Ireland) or 'Georgia, United
    States' as European.
    """
    if not raw:
        return ""
    return raw.split(",")[-1].strip().lower()


def is_ambiguous_us_ca(raw):
    """True for the merged 'United States / Canada' value.

    26,820 of the 29,931 leads carry this single merged value, so Canada
    CANNOT be separated from the US by the Country field alone.
    """
    c = canonical_country(raw).replace("&", "/").replace(" and ", "/")
    c = re.sub(r"\s*/\s*", "/", c)
    return c in ("united states/canada", "canada/united states",
                 "usa/canada", "canada/usa", "us/canada", "canada/us")


def field(lead, name):
    """Case-insensitive field read - lead rows come from the CSV ('Email') and
    from scan_results.json ('email')."""
    for variant in (name, name.lower(), name.upper(), name.capitalize()):
        value = lead.get(variant)
        if value:
            return value
    return ""


def canada_signals(lead):
    """Row-level signals that a US/Canada-merged lead is probably Canadian.

    This is a HEURISTIC. It reduces CASL exposure, it does not remove it:
    it over-excludes some US leads (e.g. Ontario, California) and it will
    still miss Canadian leads that leave no signal in the row.
    """
    signals = []

    email = str(field(lead, "Email")).strip().lower()
    if email.endswith(".ca"):
        signals.append("email .ca")

    website = str(field(lead, "Website")).strip().lower()
    if website:
        host = re.sub(r"^[a-z]+://", "", website).split("/")[0].split("?")[0].strip(". ")
        if host.endswith(".ca"):
            signals.append("website .ca")

    digits = re.sub(r"\D", "", str(field(lead, "Phone")))
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if len(digits) == 10 and digits[:3] in CANADA_AREA_CODES:
        signals.append("area code %s" % digits[:3])

    haystack = " ".join(str(field(lead, k)) for k in
                        ("Bio", "Name", "Category", "Address", "City"))
    for token in CANADA_PLACE_TOKENS:
        if re.search(r"\b%s\b" % re.escape(token), haystack, re.IGNORECASE):
            signals.append("mentions %s" % token)
            break
    if re.search(r"\bBC\b", haystack):  # case sensitive: BC only as a province code
        signals.append("mentions BC")

    return signals


def restriction_reason(lead, include_restricted=False):
    """Return (reason, detail) if this lead must be excluded, else (None, '').

    reason is 'restricted_country' (hard, by country value) or 'likely_canada'
    (heuristic, for the merged US/Canada blob).
    """
    if include_restricted:
        return None, ""
    country = str(field(lead, "Country"))
    canon = canonical_country(country)
    if canon in RESTRICTED_COUNTRIES:
        return "restricted_country", canon
    if is_ambiguous_us_ca(country):
        signals = canada_signals(lead)
        if signals:
            return "likely_canada", ", ".join(signals[:3])
    return None, ""


def normalise_username(value):
    return (value or "").strip().lstrip("@").lower()


def load_demos(path=None):
    """Load demos.json -> {normalised_username: url}. Missing file = {}."""
    path = path or DEMOS_FILE
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except Exception as e:
        print("WARNING: could not read %s (%s). Treating as empty." % (path, e))
        return {}
    if isinstance(raw, dict) and isinstance(raw.get("demos"), dict):
        raw = raw["demos"]
    items = []
    if isinstance(raw, dict):
        items = list(raw.items())
    elif isinstance(raw, list):
        for entry in raw:
            if isinstance(entry, dict):
                items.append((entry.get("username", ""),
                              entry.get("url") or entry.get("demo_url") or ""))
    demos = {}
    for key, value in items:
        url = value.get("url") if isinstance(value, dict) else value
        key = normalise_username(key)
        if key and url and str(url).strip().lower().startswith("http"):
            demos[key] = str(url).strip()
    return demos


def resolve_demo_link(lead, demos):
    """That lead's own demo URL, or None. Never falls back to a generic link."""
    if not demos:
        return None
    for candidate in (lead.get("Username"), lead.get("username")):
        key = normalise_username(candidate)
        if key and key in demos:
            return demos[key]
    email = (lead.get("Email") or "").strip().lower()
    if email and email in demos:
        return demos[email]
    return None


def load_line_list(path, label):
    """Read one address per line. Creates the file empty if it is missing."""
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write("")
        print("Created empty %s at %s" % (label, path))
        return set()
    out = set()
    with open(path, "r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip().lower()
            if line and not line.startswith("#"):
                out.add(line)
    return out


SENT_LOG_FIELDS = ["timestamp", "email", "username", "step", "sender", "subject", "demo_url"]


def load_sent_log(path=None):
    """Every address ever sent to -> guarantees nobody is emailed twice."""
    path = path or SENT_LOG_FILE
    if not os.path.exists(path):
        with open(path, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(SENT_LOG_FIELDS)
        print("Created empty sent log at %s" % path)
        return {}
    log = {}
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            email = (row.get("email") or "").strip().lower()
            if email:
                log.setdefault(email, []).append(row)
    return log


def append_sent_log(email, username, step, sender, subject, demo_url, path=None):
    path = path or SENT_LOG_FILE
    exists = os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(SENT_LOG_FIELDS)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            email, username, step, sender, subject, demo_url,
        ])


def is_consumer_account(account_email):
    return account_email.split("@")[-1].strip().lower() in CONSUMER_DOMAINS


# ==========================================
# PLANNING (no side effects, no network, no sending)
# ==========================================

def plan_campaign(leads, accounts, demos, suppression, bounced, sent_log,
                  max_sends=MAX_SENDS_PER_RUN, include_restricted=False,
                  allow_repeat_addresses=False, verbose=True):
    """Decide exactly who WOULD be emailed. Sends nothing, writes nothing.

    Returns (plan, stats). plan items carry the lead, the sending account, the
    target step, that lead's own demo URL and the rendered email.
    """
    stats = {
        "crm_rows": len(leads),
        "no_email": 0,
        "dead_status": 0,
        "restricted_country": 0,
        "likely_canada": 0,
        "suppressed": 0,
        "bounced_list": 0,
        "already_in_sent_log": 0,
        "no_demo_link": 0,
        "not_due": 0,
        "no_sender_capacity": 0,
        "over_run_cap": 0,
        "eligible": 0,
    }

    today = datetime.now().strftime("%Y-%m-%d")
    sender_counts = {acc["email"]: 0 for acc in accounts}
    for lead in leads:
        if lead.get("Last_Sent_Date", "") == today:
            sender = lead.get("Assigned_Sender", "")
            if sender in sender_counts:
                sender_counts[sender] += 1

    def capacity(acc):
        return acc.get("daily_limit", DAILY_LIMIT_PER_ACCOUNT) - sender_counts[acc["email"]]

    plan = []
    template_counter = 0
    rr = 0
    loud = 0

    def shout(msg):
        # Loud, but do not scroll 29,931 lines past the operator.
        nonlocal loud
        if verbose and loud < 40:
            print(msg)
            loud += 1
        elif verbose and loud == 40:
            print("  ... further per-lead skip lines suppressed (see summary).")
            loud += 1

    for lead in leads:
        if len(plan) >= max_sends:
            stats["over_run_cap"] += 1
            continue

        email = (lead.get("Email") or "").strip()
        status = (lead.get("Status") or "").strip().lower()
        username = (lead.get("Username") or "").strip()
        label = username or email or "?"

        if not email or "@" not in email:
            stats["no_email"] += 1
            continue
        if status in DEAD_STATUSES:
            stats["dead_status"] += 1
            continue

        reason, detail = restriction_reason(lead, include_restricted)
        if reason == "restricted_country":
            stats["restricted_country"] += 1
            continue
        if reason == "likely_canada":
            stats["likely_canada"] += 1
            continue

        if email.lower() in suppression:
            stats["suppressed"] += 1
            shout("  SKIP [suppressed]      %s - on SUPPRESSION_LIST.txt" % email)
            continue
        if email.lower() in bounced:
            stats["bounced_list"] += 1
            shout("  SKIP [bounced]         %s - on bounced_addresses.txt" % email)
            continue

        try:
            step = int(str(lead.get("Step", "0") or "0").strip())
        except ValueError:
            step = 0

        if step == 0 and email.lower() in sent_log and not allow_repeat_addresses:
            stats["already_in_sent_log"] += 1
            shout("  SKIP [already emailed] %s - present in sent_log.csv" % email)
            continue

        # THE DEMO LINK RAIL: no personal demo URL -> no email at all. Loudly.
        demo_link = resolve_demo_link(lead, demos)
        if not demo_link:
            stats["no_demo_link"] += 1
            shout("  SKIP [no demo]         %s <%s> - no entry in demos.json; "
                  "refusing to send a generic/broken link." % (label, email))
            continue

        should_send = False
        target_step = 0
        last_sent_str = (lead.get("Last_Sent_Date") or "").strip()

        if step == 0:
            should_send = True
            target_step = 1
        elif step < MAX_STEP and last_sent_str:
            try:
                last_sent_date = datetime.strptime(last_sent_str, "%Y-%m-%d")
                wait_days = STEP_WAIT_DAYS.get(step, FOLLOWUP_WAIT_DAYS)
                if (datetime.now() - last_sent_date).days >= wait_days:
                    should_send = True
                    target_step = step + 1
            except ValueError:
                shout("  SKIP [bad date]        %s - unparseable Last_Sent_Date %r"
                      % (email, last_sent_str))

        if not should_send:
            stats["not_due"] += 1
            continue

        assigned_sender = (lead.get("Assigned_Sender") or "").strip()
        sender_to_use = None
        if target_step == 1:
            usable = [a for a in accounts if capacity(a) > 0]
            if usable:
                sender_to_use = usable[rr % len(usable)]
                rr += 1
        else:
            sender_to_use = next(
                (a for a in accounts
                 if a["email"].lower() == assigned_sender.lower() and capacity(a) > 0),
                None)

        if not sender_to_use:
            stats["no_sender_capacity"] += 1
            continue

        subject, body = get_email_content(lead, target_step, template_counter, demo_link)
        if target_step == 1:
            template_counter += 1

        sender_counts[sender_to_use["email"]] += 1
        stats["eligible"] += 1
        plan.append({
            "lead": lead,
            "account": sender_to_use,
            "step": target_step,
            "demo_link": demo_link,
            "subject": subject,
            "body": body,
        })

    return plan, stats


# ==========================================
# MAIN EXECUTION ENGINE
# ==========================================

def run_campaign(send=False, max_sends=MAX_SENDS_PER_RUN, include_restricted=False,
                 i_know_the_risk=False, allow_repeat_addresses=False, demos_file=None):
    mode = "LIVE SEND" if send else "DRY RUN"
    print("=========================================================")
    print("        OUTREACH CAMPAIGN MANAGER  [%s]" % mode)
    print("=========================================================")
    if not send:
        print("DRY RUN: nothing will be emailed. Emails are printed to console only.")
        print("         Pass --send to actually send.")
    print("Run cap: %d email(s) | Canada/EU: %s"
          % (max_sends, "INCLUDED (--include-restricted)" if include_restricted else "excluded"))
    print("")

    accounts = load_smtp_accounts()
    if not accounts:
        print("Error: No active email accounts configured. Check email_accounts.txt.")
        return 1

    leads = read_crm()
    if not leads:
        print("No leads in CRM database (%s)." % CRM_FILE)
        return 1

    demos = load_demos(demos_file)
    print("Loaded %d account(s), %d CRM row(s), %d demo link(s)."
          % (len(accounts), len(leads), len(demos)))
    if not demos:
        print("")
        print("!! demos.json has no usable entries, so EVERY lead will be skipped:")
        print("!! no email may go out with a placeholder or missing demo link.")
        print("!! Build demos first:")
        print("!!   python pipeline.py --country \"United Kingdom\" --limit 20 --deploy-demos")

    suppression = load_line_list(SUPPRESSION_FILE, "suppression list")
    bounced = load_line_list(BOUNCED_FILE, "bounce list")
    sent_log = load_sent_log()
    print("Suppression list: %d | Bounce list: %d | Already emailed (sent_log): %d"
          % (len(suppression), len(bounced), len(sent_log)))
    print("---------------------------------------------------------")

    plan, stats = plan_campaign(
        leads, accounts, demos, suppression, bounced, sent_log,
        max_sends=max_sends, include_restricted=include_restricted,
        allow_repeat_addresses=allow_repeat_addresses)

    print("---------------------------------------------------------")
    print("Compliance exclusions:")
    print("  by Country value (Canada/EU) ... %d" % stats["restricted_country"])
    print("  by Canada heuristic ............ %d" % stats["likely_canada"])
    if stats["likely_canada"] or stats["restricted_country"]:
        print("  (override with --include-restricted)")
    print("Planned sends: %d" % len(plan))
    print("---------------------------------------------------------")

    # Deliverability gate: consumer mailboxes cannot absorb cold volume.
    consumer = sorted({a["email"].split("@")[-1].lower()
                       for a in accounts if is_consumer_account(a["email"])})
    blocked = False
    if consumer and len(plan) > CONSUMER_GMAIL_SAFE_LIMIT and not i_know_the_risk:
        print("")
        print("*** DELIVERABILITY WARNING ***")
        print("Sending accounts are consumer mailboxes (%s)." % ", ".join(consumer))
        print("This run would send %d emails, over the safe limit of %d."
              % (len(plan), CONSUMER_GMAIL_SAFE_LIMIT))
        print("Consumer Gmail has no dedicated domain or IP reputation. Cold volume")
        print("at this level lands in spam and can get the account locked.")
        print("Re-run with --i-know-the-risk to proceed, or lower --max-sends to %d."
              % CONSUMER_GMAIL_SAFE_LIMIT)
        print("")
        blocked = True

    sent = 0
    failed = 0

    if blocked and send:
        print("REFUSING TO SEND. 0 emails sent.")
    elif blocked and not send:
        print("DRY RUN: previewing anyway. In LIVE mode this run would be REFUSED.")

    if send and not blocked and not is_within_sending_hours():
        print("Outside configured sending hours (%02d:00-%02d:00). Nothing sent."
              % (START_HOUR, END_HOUR))
        blocked = True

    if not (blocked and send):
        for i, item in enumerate(plan, 1):
            lead = item["lead"]
            account = item["account"]
            stamp = datetime.now().strftime("%I:%M:%S %p")
            print("")
            print("[%d/%d] [%s] step %d via %s"
                  % (i, len(plan), stamp, item["step"], account["email"]))
            print("       To:      %s" % lead.get("Email", ""))
            print("       Subject: %s" % item["subject"])
            print("       Demo:    %s" % item["demo_link"])

            if not send:
                print("       ---- body (NOT SENT) ----")
                for line in item["body"].splitlines():
                    print("       | " + line)
                print("       -------------------------")
                continue

            ok = send_smtp_email(account, lead["Email"], item["subject"], item["body"])
            if ok:
                sent += 1
                lead["Step"] = str(item["step"])
                lead["Last_Sent_Date"] = datetime.now().strftime("%Y-%m-%d")
                lead["Assigned_Sender"] = account["email"]
                if (lead.get("Status") or "").strip().lower() in ("", "draft", "staged"):
                    lead["Status"] = "Active"
                append_sent_log(lead["Email"], lead.get("Username", ""), item["step"],
                                account["email"], item["subject"], item["demo_link"])
                write_crm(leads)
                print("       Status:  SENT")
                delay = random.randint(MIN_DELAY_SECONDS, MAX_DELAY_SECONDS)
                print("       Waiting %ds..." % delay)
                time.sleep(delay)
            else:
                failed += 1
                print("       Status:  FAILED")
                time.sleep(15)

    print("")
    print("=========================================================")
    print("  SUMMARY  [%s]" % mode)
    print("=========================================================")
    print("  CRM rows read .................. %d" % stats["crm_rows"])
    print("  Skipped - no/invalid email ..... %d" % stats["no_email"])
    print("  Skipped - dead status .......... %d" % stats["dead_status"])
    print("  Skipped - Canada/EU by country . %d" % stats["restricted_country"])
    print("  Skipped - likely Canada (heur.). %d" % stats["likely_canada"])
    print("  Skipped - suppression list ..... %d" % stats["suppressed"])
    print("  Skipped - bounce list .......... %d" % stats["bounced_list"])
    print("  Skipped - already in sent_log .. %d" % stats["already_in_sent_log"])
    print("  Skipped - NO DEMO LINK ......... %d" % stats["no_demo_link"])
    print("  Skipped - not due yet .......... %d" % stats["not_due"])
    print("  Skipped - no sender capacity ... %d" % stats["no_sender_capacity"])
    print("  Skipped - over run cap (%d) ..... %d" % (max_sends, stats["over_run_cap"]))
    print("  ----------------------------------------")
    print("  Planned ........................ %d" % len(plan))
    print("  ACTUALLY SENT .................. %d" % sent)
    print("  Failed ......................... %d" % failed)
    print("=========================================================")
    if stats["likely_canada"] or not include_restricted:
        print("WARNING: US/Canada cannot be separated by the Country field")
        print("         ('United States / Canada' is one merged value on 26,820 leads).")
        print("         %d lead(s) were excluded by heuristic (email/website .ca,"
              % stats["likely_canada"])
        print("         Canadian area code, Canadian place name). The heuristic is")
        print("         imperfect - it misses unsignalled Canadian leads and")
        print("         over-excludes some US ones. CASL liability remains.")
        print("")
    if not send:
        print("DRY RUN COMPLETE - 0 emails sent, CRM unchanged.")
        print("To send for real:")
        print("  python campaign_manager.py --send --max-sends %d"
              % min(max_sends, CONSUMER_GMAIL_SAFE_LIMIT))
    return 0


def build_arg_parser():
    p = argparse.ArgumentParser(
        description="Outreach campaign sequencer. DRY RUN by default - it sends "
                    "nothing unless you pass --send.")
    p.add_argument("--send", action="store_true",
                   help="Actually send email. Without this flag it is a dry run.")
    p.add_argument("--dry-run", action="store_true",
                   help="Explicit dry run (already the default).")
    p.add_argument("--max-sends", type=int, default=MAX_SENDS_PER_RUN,
                   help="Hard cap on emails for this run (default %d)." % MAX_SENDS_PER_RUN)
    p.add_argument("--include-restricted", action="store_true",
                   help="Include Canada/EU leads (CASL & GDPR risk). Off by default.")
    p.add_argument("--i-know-the-risk", action="store_true",
                   help="Acknowledge consumer-Gmail deliverability risk above %d sends."
                        % CONSUMER_GMAIL_SAFE_LIMIT)
    p.add_argument("--allow-repeat-addresses", action="store_true",
                   help="Allow a first touch to addresses already in sent_log.csv. Dangerous.")
    p.add_argument("--demos", default=None, help="Path to demos.json.")
    return p


def main(argv=None):
    args = build_arg_parser().parse_args(argv)
    if args.dry_run and args.send:
        print("Error: --dry-run and --send are mutually exclusive.")
        return 2
    if args.max_sends < 0:
        print("Error: --max-sends must be >= 0.")
        return 2
    return run_campaign(
        send=args.send,
        max_sends=args.max_sends,
        include_restricted=args.include_restricted,
        i_know_the_risk=args.i_know_the_risk,
        allow_repeat_addresses=args.allow_repeat_addresses,
        demos_file=args.demos,
    )


if __name__ == "__main__":
    sys.exit(main())
