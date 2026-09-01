# -*- coding: utf-8 -*-
"""ranker.py - turn scan_results.json into queue.csv, best targets first.

Stage 2 of the outreach pipeline:

    leads.csv -> [scanner.py] -> scan_results.json -> [ranker.py] -> queue.csv

Ranking (exactly the order the spec asks for):
    1. score DESC                      (severity weighted fault total)
    2. has an email address
    3. country in UK / Australia / US
    4. Followers > 500                 (they care about their image)
    5. has critical severity faults
    ... then critical count, then followers, as stable tie breakers.

Every row carries a `pitch_hook`: the one sentence observation that opens the
cold email.

CLI:
    python ranker.py --min-score 30 --country "United Kingdom" --limit 50 --output queue.csv
"""

import argparse
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import campaign_manager as cm  # restriction rails + demos.json loader live there

csv.field_size_limit(10 ** 7)

ROOT = os.path.dirname(os.path.abspath(__file__))
DEFAULT_INPUT = os.path.join(ROOT, "scan_results.json")
DEFAULT_OUTPUT = os.path.join(ROOT, "queue.csv")
DEFAULT_LEADS = os.path.join(ROOT, "data", "dental_leads_targeted.csv")

PREFERRED_COUNTRIES = {"united kingdom", "australia", "united states"}
SEVERITY_WEIGHT = {"critical": 30, "high": 15, "medium": 8, "low": 3}

QUEUE_FIELDS = [
    "rank", "username", "name", "email", "phone", "country", "followers",
    "website", "final_url", "platform", "score", "critical_faults",
    "high_faults", "total_faults", "fault_codes", "worst_fault",
    "pitch_hook", "demo_url", "segment", "provisional", "scanned_at",
]

# Human readable openers, keyed by fault code, used when the scanner did not
# supply a pitch_hook of its own.
HOOK_BY_CODE = {
    "NO_WEBSITE": "You have no website at all - every patient who searches for you lands on someone else's page.",
    "LINK_IN_BIO_ONLY": "Your only web presence is a link-in-bio page, so anyone searching for your practice finds nothing they can book from.",
    "DNS_FAIL": "Your domain does not resolve at all right now - the site is simply unreachable.",
    "WWW_DNS_FAIL": "The www version of your domain does not resolve, so a chunk of visitors hit a dead page.",
    "SSL_EXPIRED": "Your SSL certificate has expired, so Chrome now shows patients a full page security warning before your site.",
    "SSL_EXPIRING": "Your SSL certificate expires within the month - after that Chrome shows a security warning instead of your site.",
    "NO_SSL": "Your site still loads over plain http, so browsers mark it 'Not secure' in front of patients.",
    "HTTP_ERROR": "Your homepage is returning a server error rather than loading.",
    "NO_BOOKING": "There is no way to book an appointment from your site - patients have to phone during opening hours or give up.",
    "DEAD_IMAGES": "Several images on your site are broken and showing as empty boxes.",
    "DEAD_LINKS": "Several links on your site lead to dead pages.",
    "PHONE_CONFLICT": "There are two different phone numbers on your site, so patients cannot tell which one is really yours.",
    "NO_PHONE": "There is no phone number anywhere on your site.",
    "NO_EMAIL_ON_SITE": "There is no email address on your site, so anyone who does not want to phone has no way to reach you.",
    "STALE_COPYRIGHT": "The footer still shows an old copyright year, which makes the practice look closed.",
    "NO_SSR_CONTENT": "Your pages render almost nothing without JavaScript, so Google indexes an effectively empty site.",
    "SLOW_LOAD": "Your site takes long enough to load that most mobile visitors leave before they see it.",
    "NO_MOBILE_VIEWPORT": "Your site is not mobile responsive, and most patients search on a phone.",
    "NO_TESTIMONIALS": "There are no patient reviews anywhere on the site, which is usually the first thing people look for.",
}
SEVERITY_ORDER = ["critical", "high", "medium", "low"]


def load_scan_results(path):
    """Accept a JSON array, {'results': [...]}, or one JSON object per line."""
    if not os.path.exists(path):
        raise SystemExit(
            "ranker: input not found: %s\n"
            "Run the scanner first, e.g.\n"
            "  python scanner.py --limit 50 --country \"United Kingdom\" --output %s"
            % (path, path))
    with open(path, "r", encoding="utf-8") as f:
        text = f.read().strip()
    if not text:
        return []
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        records = []
        for line in text.splitlines():
            line = line.strip().rstrip(",")
            if line and line[0] == "{":
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
        if not records:
            raise SystemExit("ranker: %s is not valid JSON or JSONL." % path)
        return records
    if isinstance(data, dict):
        for key in ("results", "scans", "leads", "data"):
            if isinstance(data.get(key), list):
                return data[key]
        return [data]
    if isinstance(data, list):
        return [r for r in data if isinstance(r, dict)]
    raise SystemExit("ranker: unexpected JSON shape in %s" % path)


def load_lead_index(path):
    """username -> lead row, for the fields the scan contract does not carry
    (Followers, Phone, Bio - needed for ranking and for the Canada heuristic)."""
    index = {}
    if not path or not os.path.exists(path):
        return index
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            key = cm.normalise_username(row.get("Username"))
            if key:
                index.setdefault(key, row)
    return index


def to_int(value, default=0):
    try:
        return int(str(value).strip().replace(",", ""))
    except (TypeError, ValueError):
        return default


def faults_of(record):
    faults = record.get("faults") or []
    clean = []
    for fault in faults:
        if isinstance(fault, dict):
            clean.append({
                "code": str(fault.get("code", "") or "").upper(),
                "severity": str(fault.get("severity", "") or "").lower(),
                "evidence": str(fault.get("evidence", "") or ""),
            })
        elif isinstance(fault, str):
            clean.append({"code": fault.upper(), "severity": "medium", "evidence": ""})
    return clean


def score_of(record, faults):
    """Use the scanner's score; recompute from severities if it is missing."""
    if record.get("score") not in (None, ""):
        return max(0, min(100, to_int(record.get("score"))))
    total = sum(SEVERITY_WEIGHT.get(f["severity"], 0) for f in faults)
    return min(100, total)


def worst_fault(faults):
    for severity in SEVERITY_ORDER:
        for fault in faults:
            if fault["severity"] == severity:
                return fault
    return None


def build_pitch_hook(record, faults):
    """One sentence to open the cold email with."""
    hook = str(record.get("pitch_hook") or "").strip()
    if hook:
        return " ".join(hook.split())
    fault = worst_fault(faults)
    if not fault:
        return ""
    hook = HOOK_BY_CODE.get(fault["code"])
    if hook:
        return hook
    evidence = fault["evidence"] or fault["code"].replace("_", " ").lower()
    return "I noticed something on your site worth fixing: %s." % evidence


def country_matches(record_country, wanted):
    """Free text country match. '--country "United Kingdom"' has to match
    'London, England, United Kingdom' too."""
    if not wanted:
        return True
    have = str(record_country or "").strip().lower()
    want = wanted.strip().lower()
    return want in have or have in want or cm.canonical_country(have) == want


THIRD_PARTY_CODES = {"NO_REAL_WEBSITE", "DEAD_BIO_LINK", "NOT_THEIR_SITE"}
THIRD_PARTY_PLATFORM_HINTS = ("link-in-bio", "fundraising", "provider profile",
                              "whatsapp", "calendly", "directory listing")


def segment_of(record, lead_row, faults=()):
    """Which route this lead takes - and a warning when the 'website' on the
    record is not actually theirs (a charity page, a JustGiving link, a
    directory profile). Pitching a site they do not own reads as spam."""
    codes = {f["code"] for f in faults}
    platform = str(record.get("platform") or "").lower()
    if codes & THIRD_PARTY_CODES or any(h in platform for h in THIRD_PARTY_PLATFORM_HINTS):
        return "third_party_link"

    website = str(cm.field(record, "website") or cm.field(lead_row or {}, "Website")).strip()
    if not website:
        return "no_website"
    low = website.lower()
    for token in ("linktr.ee", "bit.ly", "wa.me", "beacons", "msha.ke",
                  "campsite", "linkin.bio", "lnk.bio", "taplink", "solo.to",
                  "tinyurl", "facebook.com", "instagram.com", "youtu"):
        if token in low:
            return "link_in_bio"
    return "real_site"


def rank_records(records, lead_index, demos, min_score=1, country=None, limit=None,
                 require_email=False, include_restricted=False):
    rows = []
    stats = {
        "input": len(records),
        "country_filtered": 0,
        "below_min_score": 0,
        "no_email": 0,
        "restricted_country": 0,
        "likely_canada": 0,
        "kept": 0,
    }

    for record in records:
        username = cm.normalise_username(cm.field(record, "username"))
        lead_row = lead_index.get(username, {})
        merged = dict(lead_row)
        merged.update({k: v for k, v in record.items() if v not in (None, "")})

        record_country = cm.field(record, "country") or cm.field(lead_row, "Country")
        if not country_matches(record_country, country):
            stats["country_filtered"] += 1
            continue

        faults = faults_of(record)
        score = score_of(record, faults)
        if score < min_score:
            stats["below_min_score"] += 1
            continue

        email = str(cm.field(record, "email") or cm.field(lead_row, "Email")).strip()
        if require_email and (not email or "@" not in email):
            stats["no_email"] += 1
            continue

        reason, _detail = cm.restriction_reason(merged, include_restricted)
        if reason:
            stats[reason] += 1
            continue

        followers = to_int(cm.field(lead_row, "Followers"), to_int(record.get("followers"), 0))
        criticals = [f for f in faults if f["severity"] == "critical"]
        highs = [f for f in faults if f["severity"] == "high"]
        worst = worst_fault(faults)

        rows.append({
            "username": cm.field(record, "username") or username,
            "name": cm.field(record, "name") or cm.field(lead_row, "Name"),
            "email": email,
            "phone": cm.field(lead_row, "Phone"),
            "country": record_country,
            "followers": followers,
            "website": cm.field(record, "website") or cm.field(lead_row, "Website"),
            "final_url": record.get("final_url", ""),
            "platform": record.get("platform", ""),
            "score": score,
            "critical_faults": len(criticals),
            "high_faults": len(highs),
            "total_faults": len(faults),
            "fault_codes": "|".join(f["code"] for f in faults),
            "worst_fault": worst["code"] if worst else "",
            "pitch_hook": build_pitch_hook(record, faults),
            "demo_url": demos.get(username, ""),
            "segment": segment_of(record, lead_row, faults),
            "provisional": "yes" if record.get("provisional") else "",
            "scanned_at": record.get("scanned_at", ""),
        })

    rows.sort(key=lambda r: (
        -r["score"],                                                # 1 score DESC
        0 if r["email"] else 1,                                     # 2 has email
        0 if cm.canonical_country(r["country"]) in PREFERRED_COUNTRIES else 1,  # 3 country
        0 if r["followers"] > 500 else 1,                           # 4 followers > 500
        0 if r["critical_faults"] else 1,                           # 5 critical faults
        -r["critical_faults"],
        -r["followers"],
        str(r["username"]).lower(),
    ))

    if limit:
        rows = rows[:limit]
    for i, row in enumerate(rows, 1):
        row["rank"] = i
    stats["kept"] = len(rows)
    return rows, stats


def write_queue(rows, path):
    tmp = path + ".tmp"
    with open(tmp, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=QUEUE_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in QUEUE_FIELDS})
    os.replace(tmp, path)


def read_queue(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def build_arg_parser():
    p = argparse.ArgumentParser(description="Rank scanned leads into queue.csv (best first).")
    p.add_argument("--input", default=DEFAULT_INPUT, help="scan_results.json path.")
    p.add_argument("--output", default=DEFAULT_OUTPUT, help="Output queue CSV path.")
    p.add_argument("--leads", default=DEFAULT_LEADS,
                   help="Lead CSV used to enrich Followers/Phone/Bio.")
    p.add_argument("--min-score", type=int, default=1,
                   help="Drop anything below this score (default 1: a clean site scores 0 "
                        "and must not be contacted).")
    p.add_argument("--country", default=None, help='e.g. "United Kingdom".')
    p.add_argument("--limit", type=int, default=None, help="Keep only the top N.")
    p.add_argument("--require-email", action="store_true",
                   help="Drop leads with no email address.")
    p.add_argument("--include-restricted", action="store_true",
                   help="Keep Canada/EU leads (CASL & GDPR risk). Off by default.")
    p.add_argument("--quiet", action="store_true")
    return p


def main(argv=None):
    args = build_arg_parser().parse_args(argv)

    records = load_scan_results(args.input)
    lead_index = load_lead_index(args.leads)
    demos = cm.load_demos()

    rows, stats = rank_records(
        records, lead_index, demos,
        min_score=args.min_score, country=args.country, limit=args.limit,
        require_email=args.require_email, include_restricted=args.include_restricted)

    write_queue(rows, args.output)

    if not args.quiet:
        print("RANKER")
        print("  input records .............. %d (%s)" % (stats["input"], args.input))
        print("  dropped - country filter ... %d" % stats["country_filtered"])
        print("  dropped - score < %-3d ...... %d" % (args.min_score, stats["below_min_score"]))
        print("  dropped - no email ......... %d" % stats["no_email"])
        print("  dropped - Canada/EU country. %d" % stats["restricted_country"])
        print("  dropped - likely Canada .... %d" % stats["likely_canada"])
        print("  QUEUED ..................... %d -> %s" % (stats["kept"], args.output))
        if rows:
            print("")
            print("  Top of queue:")
            for row in rows[:5]:
                print("    %2d. %-22s score %-3d %-14s %s"
                      % (row["rank"], (row["username"] or "?")[:22], row["score"],
                         cm.canonical_country(row["country"])[:14],
                         (row["pitch_hook"] or "")[:70]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
