# -*- coding: utf-8 -*-
"""pipeline.py - orchestrate the outreach machine end to end.

    python pipeline.py --country "United Kingdom" --limit 50

    leads.csv
       -> [0] SEGMENT     real site / link-in-bio / no website
       -> [1] scanner.py  (real sites only - the rest have nothing to scan)
       -> [2] ranker.py   -> queue.csv
       -> [3] demo_generator.py -> demos.json
       -> [4] STAGE       drafts in the CRM

THIS SCRIPT NEVER SENDS EMAIL. It stages drafts and prints the command the
operator runs to send. Demo deployment is also opt-in (--deploy-demos).

If scanner.py or demo_generator.py do not exist yet (they are built by other
agents), the pipeline degrades: it says so, does what it still can, and never
invents results it did not measure.
"""

import argparse
import csv
import json
import os
import re
import subprocess
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import campaign_manager as cm
import ranker

csv.field_size_limit(10 ** 7)

ROOT = os.path.dirname(os.path.abspath(__file__))
WORK_DIR = os.path.join(ROOT, "pipeline_work")
DEFAULT_LEADS = os.path.join(ROOT, "data", "dental_leads_targeted.csv")
SCANNER = os.path.join(ROOT, "scanner.py")
DEMO_GENERATOR = os.path.join(ROOT, "demo_generator.py")
SCAN_RESULTS = os.path.join(ROOT, "scan_results.json")
QUEUE_CSV = os.path.join(ROOT, "queue.csv")
NEEDS_REVIEW = os.path.join(ROOT, "demos_needs_review.json")

LINK_IN_BIO_TOKENS = ("linktr.ee", "bit.ly", "wa.me", "beacons", "msha.ke",
                      "campsite", "linkin.bio", "lnk.bio", "taplink", "solo.to",
                      "tinyurl", "shorturl", "facebook.com", "instagram.com", "youtu")

SEVERITY_WEIGHT = {"critical": 30, "high": 15, "medium": 8, "low": 3}


def ascii_safe(text):
    """The console is cp1252: never let a child process' emoji kill the run."""
    return str(text).encode("ascii", "replace").decode("ascii")


def say(text=""):
    print(ascii_safe(text))


def rule(char="-"):
    say(char * 57)


# ==========================================
# [0] SEGMENT
# ==========================================

def segment_of_website(website):
    site = (website or "").strip().lower()
    if not site:
        return "no_website"
    if any(token in site for token in LINK_IN_BIO_TOKENS):
        return "link_in_bio"
    return "real_site"


def select_candidates(leads_path, country, limit, pool_multiplier,
                      include_restricted, suppression, bounced, sent_log):
    """One pass over the lead CSV -> the candidate pool, split by segment.

    Only 18,330 of 29,931 leads have a real website domain. The other ~11,600
    (6,543 with no website at all, ~5,058 link-in-bio only) have nothing for the
    scanner to fetch, so they are routed straight to the demo generator.
    """
    pool_cap = max(limit, limit * max(1, pool_multiplier))
    buckets = {"real_site": [], "link_in_bio": [], "no_website": []}
    stats = {"rows": 0, "country_match": 0, "no_email": 0, "restricted_country": 0,
             "likely_canada": 0, "suppressed": 0, "bounced_list": 0,
             "already_emailed": 0, "considered": 0}

    with open(leads_path, "r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            stats["rows"] += 1
            if not ranker.country_matches(row.get("Country"), country):
                continue
            stats["country_match"] += 1

            email = (row.get("Email") or "").strip()
            if not email or "@" not in email:
                stats["no_email"] += 1
                continue

            reason, _ = cm.restriction_reason(row, include_restricted)
            if reason:
                stats[reason] += 1
                continue

            low = email.lower()
            if low in suppression:
                stats["suppressed"] += 1
                continue
            if low in bounced:
                stats["bounced_list"] += 1
                continue
            if low in sent_log:
                stats["already_emailed"] += 1
                continue

            segment = segment_of_website(row.get("Website"))
            if len(buckets[segment]) >= pool_cap:
                continue
            row["_segment"] = segment
            buckets[segment].append(row)
            stats["considered"] += 1

            direct = len(buckets["no_website"]) + len(buckets["link_in_bio"])
            if len(buckets["real_site"]) >= pool_cap and direct >= pool_cap:
                break

    return buckets, stats


# ==========================================
# [1] SCAN
# ==========================================

def offline_record(row, provisional=False):
    """A scan record built from the lead row alone - no network involved.

    Used for leads with no real website (nothing to fetch). Every fault here is
    a fact taken straight from the lead data, not a guess.
    """
    segment = row.get("_segment") or segment_of_website(row.get("Website"))
    website = (row.get("Website") or "").strip()
    faults = []

    if segment == "no_website":
        faults.append({
            "code": "NO_WEBSITE", "severity": "critical",
            "evidence": "lead record has no website at all",
        })
    elif segment == "link_in_bio":
        faults.append({
            "code": "LINK_IN_BIO_ONLY", "severity": "critical",
            "evidence": "only web presence is %s" % website,
        })
        faults.append({
            "code": "NO_BOOKING", "severity": "high",
            "evidence": "a link-in-bio page has no booking flow",
        })

    score = min(100, sum(SEVERITY_WEIGHT.get(f["severity"], 0) for f in faults))
    return {
        "username": row.get("Username", ""),
        "name": row.get("Name", ""),
        "email": row.get("Email", ""),
        "country": row.get("Country", ""),
        "website": website,
        "final_url": "",
        "scanned_at": datetime.now().isoformat(timespec="seconds"),
        "reachable": None,
        "faults": faults,
        "platform": "link-in-bio" if segment == "link_in_bio" else "none",
        "score": score,
        "pitch_hook": "",
        "source": "pipeline_offline" + ("_fallback" if provisional else ""),
        "provisional": bool(provisional),
    }


def write_scan_input(rows, path):
    fields = ["Username", "Name", "Category", "Email", "Phone", "Website",
              "Country", "Followers", "Following", "Bio"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fields})
    return path


def stream_subprocess(cmd, timeout, label):
    """Run a child script, echoing its output.

    Returns (returncode, ok, lines) - lines are kept so the caller can read the
    child's own summary numbers.
    """
    say("  $ " + " ".join(cmd))
    captured = []
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    try:
        proc = subprocess.Popen(cmd, cwd=ROOT, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True,
                                encoding="utf-8", errors="replace", env=env)
    except OSError as e:
        say("  %s could not start: %s" % (label, e))
        return -1, False, captured
    try:
        for line in proc.stdout:
            captured.append(line.rstrip())
            say("    | " + line.rstrip())
        proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        say("  %s timed out after %ds - killed." % (label, timeout))
        return -1, False, captured
    return proc.returncode, proc.returncode == 0, captured


def run_scanner(site_rows, args):
    """Returns (records, mode) where mode is 'scanner' | 'fallback' | 'skipped'."""
    if not site_rows:
        say("  No real-website leads in the pool - nothing to scan.")
        return [], "skipped"

    if not os.path.exists(SCANNER):
        say("  DEGRADED: scanner.py does not exist yet (another agent is building it).")
        say("            %d lead(s) with a real website cannot be checked, so they are"
            % len(site_rows))
        say("            HELD, not rejected. Re-run this pipeline once scanner.py lands.")
        return [], "fallback"

    scan_input = write_scan_input(site_rows, os.path.join(WORK_DIR, "scan_input.csv"))
    scan_out = os.path.join(WORK_DIR, "scan_results_sites.json")
    cmd = [args.python, SCANNER,
           "--input", scan_input,
           "--output", scan_out,
           "--limit", str(len(site_rows)),
           "--workers", str(args.workers)]
    code, ok, _ = stream_subprocess(cmd, args.scan_timeout, "scanner.py")
    if not ok:
        say("  DEGRADED: scanner.py exited with code %s. Treating its leads as HELD." % code)
        return [], "fallback"
    try:
        records = ranker.load_scan_results(scan_out)
    except SystemExit as e:
        say("  DEGRADED: scanner.py produced no readable output (%s). Leads HELD." % e)
        return [], "fallback"
    say("  scanner.py returned %d record(s)." % len(records))
    return records, "scanner"


# ==========================================
# [3] DEMOS
# ==========================================

def run_demo_generator(args, queue_rows):
    """Returns (built, rejected, mode)."""
    if not queue_rows:
        return 0, 0, "skipped"
    if args.no_demos:
        say("  --no-demos: demo generation skipped (existing demos.json still used).")
        return 0, 0, "skipped"
    if not os.path.exists(DEMO_GENERATOR):
        say("  DEGRADED: demo_generator.py does not exist yet (another agent is building it).")
        say("            0 demos built. Drafts will be staged WITHOUT a demo link and")
        say("            campaign_manager.py will refuse to send them until demos exist.")
        return 0, 0, "missing"

    before = set(cm.load_demos())
    review_before = len(load_review_entries())
    cmd = [args.python, DEMO_GENERATOR, "--from-queue", QUEUE_CSV,
           "--limit", str(len(queue_rows))]
    if args.deploy_demos:
        cmd.append("--go")
    else:
        say("  Demo generator runs in ITS dry-run mode (no deploy). Add --deploy-demos to build for real.")
    code, ok, out = stream_subprocess(cmd, args.demo_timeout, "demo_generator.py")
    if not ok:
        say("  DEGRADED: demo_generator.py exited with code %s. Counting 0 demos built." % code)
        return 0, 0, "failed"

    after = cm.load_demos()
    queued_usernames = {cm.normalise_username(r.get("username")) for r in queue_rows}
    built = len([u for u in after if u in queued_usernames and u not in before])
    rejected = rejected_from_output(out)
    if rejected is None:
        rejected = count_rejected(queued_usernames, review_before)
    return built, rejected, "ok"


def rejected_from_output(lines):
    """demo_generator.py prints its own quality-gate tally; trust that first.

    Its demos_needs_review.json entries often carry an empty username and the
    file dedupes across runs, so neither joining nor file growth counts a
    re-run correctly.
    """
    for line in reversed(lines or []):
        match = re.search(r"gate pass rate\s+(\d+)\s*/\s*(\d+)", line)
        if match:
            passed, total = int(match.group(1)), int(match.group(2))
            return max(0, total - passed)
    for line in reversed(lines or []):
        match = re.match(r"\s*rejected\s+(\d+)\s*$", line)
        if match:
            return int(match.group(1))
    return None


def load_review_entries():
    """Entries in demos_needs_review.json (quality-gate rejections)."""
    if not os.path.exists(NEEDS_REVIEW):
        return []
    try:
        with open(NEEDS_REVIEW, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return []
    if isinstance(data, dict):
        return [{"username": k} for k in data]
    if isinstance(data, list):
        return [e for e in data if isinstance(e, dict)]
    return []


def count_rejected(queued_usernames, review_before=0):
    """Quality-gate rejections belonging to THIS run.

    demo_generator.py writes some review entries with an empty username, so
    matching on username alone under-counts. Fall back to the growth of the
    review file across this run, and take whichever is larger.
    """
    entries = load_review_entries()
    by_username = len([e for e in entries
                       if cm.normalise_username(e.get("username")) in queued_usernames])
    by_growth = max(0, len(entries) - review_before)
    return max(by_username, by_growth)


# ==========================================
# [4] STAGE DRAFTS (never sends)
# ==========================================

def stage_drafts(queue_rows, demos, crm_path, do_write=True):
    """Upsert queue rows into the CRM as Status=Draft, Step=0. Idempotent."""
    existing = cm.read_crm()
    by_email = {}
    for row in existing:
        key = (row.get("Email") or "").strip().lower()
        if key:
            by_email.setdefault(key, row)

    stats = {"new": 0, "updated": 0, "skipped_existing_active": 0,
             "with_demo": 0, "without_demo": 0}
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for row in queue_rows:
        email = (row.get("email") or "").strip()
        if not email:
            continue
        username = cm.normalise_username(row.get("username"))
        demo_url = demos.get(username, "") or (row.get("demo_url") or "")
        if demo_url:
            stats["with_demo"] += 1
        else:
            stats["without_demo"] += 1

        current = by_email.get(email.lower())
        if current:
            status = (current.get("Status") or "").strip().lower()
            step = str(current.get("Step") or "0").strip()
            if status in cm.DEAD_STATUSES or (step.isdigit() and int(step) > 0):
                stats["skipped_existing_active"] += 1
                continue
            current["Demo_URL"] = demo_url
            current["Pitch_Hook"] = row.get("pitch_hook", "")
            current["Fault_Score"] = row.get("score", "")
            current["Staged_At"] = now
            if not (current.get("Status") or "").strip():
                current["Status"] = "Draft"
            stats["updated"] += 1
            continue

        draft = {
            "Email": email,
            "Name": row.get("name", ""),
            "Category": "",
            "Phone": row.get("phone", ""),
            "Website": row.get("website", ""),
            "Country": row.get("country", ""),
            "Username": row.get("username", ""),
            "Step": "0",
            "Last_Sent_Date": "",
            "Assigned_Sender": "",
            "Status": "Draft",
            "Demo_URL": demo_url,
            "Pitch_Hook": row.get("pitch_hook", ""),
            "Fault_Score": row.get("score", ""),
            "Staged_At": now,
        }
        existing.append(draft)
        by_email[email.lower()] = draft
        stats["new"] += 1

    if do_write and (stats["new"] or stats["updated"]):
        backup = crm_path + ".backup-" + datetime.now().strftime("%Y%m%d-%H%M%S")
        if os.path.exists(crm_path):
            with open(crm_path, "r", encoding="utf-8-sig", newline="") as src:
                data = src.read()
            with open(backup, "w", encoding="utf-8", newline="") as dst:
                dst.write(data)
            say("  CRM backed up to %s" % os.path.basename(backup))
        cm.write_crm(existing, crm_path)
    elif not do_write:
        say("  --no-stage: CRM not written.")

    return stats


# ==========================================
# MAIN
# ==========================================

def build_arg_parser():
    p = argparse.ArgumentParser(
        description="Orchestrate scanner -> ranker -> demo generator -> staged CRM drafts. "
                    "Never sends email.")
    p.add_argument("--country", default=None, help='e.g. "United Kingdom".')
    p.add_argument("--limit", type=int, default=50, help="How many leads to stage (default 50).")
    p.add_argument("--min-score", type=int, default=1,
                   help="Minimum fault score to enter the queue (default 1).")
    p.add_argument("--input", default=DEFAULT_LEADS, help="Lead CSV.")
    p.add_argument("--workers", type=int, default=20, help="Scanner workers.")
    p.add_argument("--pool-multiplier", type=int, default=3,
                   help="Scan this many times --limit so the ranker has a choice (default 3).")
    p.add_argument("--deploy-demos", action="store_true",
                   help="Let demo_generator.py actually build and deploy demos.")
    p.add_argument("--include-restricted", action="store_true",
                   help="Include Canada/EU leads (CASL & GDPR risk). Off by default.")
    p.add_argument("--no-stage", action="store_true", help="Do everything except write the CRM.")
    p.add_argument("--no-demos", action="store_true",
                   help="Skip the demo generator (re-rank and re-stage only).")
    p.add_argument("--scan-timeout", type=int, default=1800, help="Seconds (default 1800).")
    p.add_argument("--demo-timeout", type=int, default=3600, help="Seconds (default 3600).")
    p.add_argument("--python", default=sys.executable, help="Python interpreter for child scripts.")
    return p


def main(argv=None):
    args = build_arg_parser().parse_args(argv)
    os.makedirs(WORK_DIR, exist_ok=True)
    started = datetime.now()

    say("=========================================================")
    say("  OUTREACH PIPELINE  (stages drafts - NEVER sends email)")
    say("=========================================================")
    say("  country: %s | limit: %d | min-score: %d | deploy demos: %s"
        % (args.country or "(any)", args.limit, args.min_score,
           "YES" if args.deploy_demos else "no"))
    say("")

    if not os.path.exists(args.input):
        say("Lead file not found: %s" % args.input)
        return 1

    suppression = cm.load_line_list(cm.SUPPRESSION_FILE, "suppression list")
    bounced = cm.load_line_list(cm.BOUNCED_FILE, "bounce list")
    sent_log = cm.load_sent_log()

    # ---------- [0] SEGMENT ----------
    say("[0/4] SEGMENT")
    buckets, seg_stats = select_candidates(
        args.input, args.country, args.limit, args.pool_multiplier,
        args.include_restricted, suppression, bounced, sent_log)
    direct_rows = buckets["no_website"] + buckets["link_in_bio"]
    say("  rows read ...................... %d" % seg_stats["rows"])
    say("  matched country ................ %d" % seg_stats["country_match"])
    say("  dropped - no email ............. %d" % seg_stats["no_email"])
    say("  dropped - Canada/EU by country . %d" % seg_stats["restricted_country"])
    say("  dropped - likely Canada (heur.). %d" % seg_stats["likely_canada"])
    say("  dropped - suppressed / bounced . %d / %d"
        % (seg_stats["suppressed"], seg_stats["bounced_list"]))
    say("  dropped - already emailed ...... %d" % seg_stats["already_emailed"])
    say("  pool: real site %d -> scanner | no website %d + link-in-bio %d -> demo generator"
        % (len(buckets["real_site"]), len(buckets["no_website"]), len(buckets["link_in_bio"])))
    say("")

    # ---------- [1] SCAN ----------
    say("[1/4] SCAN")
    scanned_records, scan_mode = run_scanner(buckets["real_site"], args)
    held_for_scan = len(buckets["real_site"]) if scan_mode == "fallback" else 0
    direct_records = [offline_record(r) for r in direct_rows]
    records = list(scanned_records) + direct_records
    with open(SCAN_RESULTS, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=1, ensure_ascii=False)
    faults_found = sum(len(r.get("faults") or []) for r in records)
    leads_with_faults = len([r for r in records if r.get("faults")])
    say("  scan records written ........... %d -> %s"
        % (len(records), os.path.basename(SCAN_RESULTS)))
    say("  leads with >=1 fault ........... %d (%d faults total)"
        % (leads_with_faults, faults_found))
    say("")

    # ---------- [2] RANK ----------
    say("[2/4] RANK")
    rank_cmd = [args.python, os.path.join(ROOT, "ranker.py"),
                "--input", SCAN_RESULTS, "--output", QUEUE_CSV,
                "--leads", args.input, "--min-score", str(args.min_score),
                "--limit", str(args.limit), "--require-email"]
    if args.country:
        rank_cmd += ["--country", args.country]
    if args.include_restricted:
        rank_cmd.append("--include-restricted")
    code, ok, _ = stream_subprocess(rank_cmd, 600, "ranker.py")
    if not ok:
        say("  ranker.py failed (exit %s). Stopping before staging." % code)
        return 1
    queue_rows = ranker.read_queue(QUEUE_CSV)
    say("")

    # ---------- [3] DEMOS ----------
    say("[3/4] DEMOS")
    demos_built, demos_rejected, demo_mode = run_demo_generator(args, queue_rows)
    demos = cm.load_demos()
    say("  demos available for queue ...... %d"
        % len([r for r in queue_rows
               if cm.normalise_username(r.get("username")) in demos]))
    say("")

    # ---------- [4] STAGE ----------
    say("[4/4] STAGE DRAFTS (no email is sent)")
    stage_stats = stage_drafts(queue_rows, demos, cm.CRM_FILE, do_write=not args.no_stage)
    staged = stage_stats["new"] + stage_stats["updated"]
    say("  new drafts ..................... %d" % stage_stats["new"])
    say("  existing rows refreshed ........ %d" % stage_stats["updated"])
    say("  left alone (already in flight) . %d" % stage_stats["skipped_existing_active"])
    say("")

    # ---------- SUMMARY ----------
    rule("=")
    say("  scanned %d | faults found %d | demos built %d | rejected %d | staged %d"
        % (len(records), faults_found, demos_built, demos_rejected, staged))
    rule("=")
    say("  EMAILS SENT BY THIS PIPELINE: 0  (it never sends)")
    say("  segments: no website %d | link-in-bio %d | real site %d"
        % (len(buckets["no_website"]), len(buckets["link_in_bio"]),
           len(buckets["real_site"])))
    if held_for_scan:
        say("  HELD (scanner.py unavailable, real websites unchecked): %d" % held_for_scan)
    if demo_mode in ("missing", "failed"):
        say("  staged WITHOUT a demo link: %d - campaign_manager.py will SKIP these"
            % stage_stats["without_demo"])
    if not args.include_restricted:
        say("")
        say("  WARNING: US/Canada cannot be separated by the Country field")
        say("           ('United States / Canada' is one merged value on 26,820 leads).")
        say("           %d lead(s) excluded here by the Canada heuristic (.ca email or"
            % seg_stats["likely_canada"])
        say("           website, Canadian area code, Canadian place name) and %d by an"
            % seg_stats["restricted_country"])
        say("           explicit Canada/EU country value. The heuristic is imperfect -")
        say("           it misses unsignalled Canadian leads. CASL liability remains.")
    say("")
    say("  queue:  %s" % QUEUE_CSV)
    say("  scans:  %s" % SCAN_RESULTS)
    say("  CRM:    %s" % cm.CRM_FILE)
    say("  elapsed: %ds" % int((datetime.now() - started).total_seconds()))
    rule("=")
    say("  NEXT STEPS (nothing has been emailed):")
    say("    1. Review the staged drafts:")
    say('       python campaign_manager.py --max-sends %d' % args.limit)
    say("    2. Eyeball every demo link in queue.csv before you send anything.")
    say("    3. Then, and only then, send for real:")
    say('       python campaign_manager.py --send --max-sends %d'
        % min(args.limit, cm.CONSUMER_GMAIL_SAFE_LIMIT))
    if args.limit > cm.CONSUMER_GMAIL_SAFE_LIMIT:
        say("       (over %d on consumer Gmail also needs --i-know-the-risk)"
            % cm.CONSUMER_GMAIL_SAFE_LIMIT)
    rule("=")
    return 0


if __name__ == "__main__":
    sys.exit(main())
