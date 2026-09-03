"""
fix_all_live.py - clone every deployed demo, run fix_demo.py over it, push back.

Why this exists
---------------
All 21 deployed demos were reskinned from "Foundation Dental Retreats", a dental
COACHING business. The homepage reskins cleanly, so the fault is invisible until a
prospect clicks Book an appointment - and then they see four real strangers listed
as the practice's dentists (Dr. Jim Arnold "CEO & Mastermind Coach", Dr. Gary
Solnit "Prosthodontist Partner", Debra Englehardt-Nash, Dr. Kathryn Alderman) and
services called "Buy/Sell Advisory" and "Transitions Program".

Verified live on all 21 sites, 2 Sep 2026. None had ever been sent to a prospect,
which is the only piece of luck in this story.

Usage
-----
    python3 fix_all_live.py --dry-run     # clone + fix + report, never push
    python3 fix_all_live.py --go          # clone + fix + commit + push
    python3 fix_all_live.py --go --only waimea-dental-studio

Each repo is committed as a normal revision, so `git revert` on the demo repo
undoes it if anything looks wrong.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys

OWNER = "Milin555"
BASE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(BASE, "_live_fix")
FIXER = os.path.join(BASE, "fix_demo.py")

REPOS = [
    "waimea-dental-studio", "art-of-aesthetics-dental-studio", "veneer-school",
    "smilesketch-vegas", "hampshire-meadow-family-pediatric",
    "cosmetic-dentistry-of-san-antonio", "the-grove-family-dental",
    "my-smile-miami", "ocean-vibe-dental", "circle-c-dental",
    "austin-cosmetic-implant-dentistry", "brickell-avenue-dentistry",
    "diamond-dental-cookstown", "esthetique-dentistry-of-ashburn",
    "rise-modern-dentistry", "flourish-dental-boutique",
    "smile-first-pediatric-dentistry", "didcot-dental-studio",
    "adore-dental", "ingalls-family-dental", "Dr.neo",
]

# Anything on this list appearing in a fixed build is a hard stop.
FORBIDDEN = [
    "Jim Arnold", "Gary Solnit", "Englehardt-Nash", "Kathryn Alderman",
    "Emilie Drumm", "Emman Collins", "Marcus Rishi", "Daniel Ahmed",
    "Buy/Sell Advisory", "Transitions Program", "Mastermind",
    "Accountability & Board", "Superheroes Behind",
    # Source-template businesses. Any of these means the demo was never
    # reskinned - Dr.neo shipped as 100% "Foundation Dental Alliance",
    # including that company's real phone and email.
    "Foundation Dental Alliance", "foundationdentalalliance", "310-888-1850",
    "Ritter & Ramsey", "Ritter and Ramsey", "Modern Smile Center",
    "Lura Dental", "The Beverly Hills Center", "Boutique Dental Clinic",
]


def run(cmd, cwd=None, timeout=420):
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                           timeout=timeout)
        return r.returncode == 0, (r.stdout + r.stderr).strip()
    except subprocess.TimeoutExpired:
        return False, "timeout"


def verify(d):
    """Return (ok, problems). Runs after the fixer, before any push."""
    problems = []
    import glob
    pages = glob.glob(os.path.join(d, "*.html"))
    if not pages:
        return False, ["no html files at all"]
    if not os.path.exists(os.path.join(d, "index.html")):
        problems.append("index.html missing")
    for f in pages:
        s = open(f, encoding="utf-8", errors="replace").read()
        base = os.path.basename(f)
        for bad in FORBIDDEN:
            if bad.lower() in s.lower():
                problems.append(f"{base}: still contains '{bad}'")
        for tag in ("div", "section"):
            o = len(re.findall(r"<" + tag + r"[\s>]", s))
            c = len(re.findall(r"</" + tag + r">", s))
            if o != c:
                problems.append(f"{base}: unbalanced <{tag}> {o}/{c}")
        for dead in ("apply.html", "retreats.html", "doctor-"):
            if f'href="{dead}' in s:
                problems.append(f"{base}: dead link to {dead}")
        if len(s) < 2000:
            problems.append(f"{base}: suspiciously small ({len(s)}b)")
    return not problems, problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--go", action="store_true", help="actually commit and push")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", help="single repo name")
    a = ap.parse_args()
    if not a.go and not a.dry_run:
        print(__doc__)
        sys.exit(1)

    repos = [a.only] if a.only else REPOS
    os.makedirs(WORK, exist_ok=True)
    ok_n = fail_n = skip_n = 0
    failures = []

    for i, repo in enumerate(repos, 1):
        print(f"\n[{i}/{len(repos)}] {repo}")
        d = os.path.join(WORK, repo)
        if os.path.isdir(d):
            shutil.rmtree(d, ignore_errors=True)
        url = f"https://github.com/{OWNER}/{repo}.git"
        good, out = run(["git", "clone", "--depth", "1", url, d])
        if not good:
            print(f"    CLONE FAILED: {out[:110]}")
            fail_n += 1
            failures.append((repo, "clone"))
            continue

        good, out = run([sys.executable, FIXER, d])
        changed = [l.strip() for l in out.splitlines()
                   if l.strip().startswith(("delete", "-", "title"))]
        print(f"    {len(changed)} change(s)")

        ok, problems = verify(d)
        if not ok:
            print("    VERIFY FAILED - not pushing:")
            for p in problems[:6]:
                print(f"      ! {p}")
            fail_n += 1
            failures.append((repo, problems[0] if problems else "verify"))
            continue
        print("    verify: clean")

        if not a.go:
            skip_n += 1
            print("    (dry run - not pushed)")
            continue

        run(["git", "add", "-A"], cwd=d)
        good, out = run(["git", "-c", "user.name=Milin555",
                         "-c", "user.email=dholiyamilin@gmail.com", "commit", "-m",
                         "Remove source-template content that belonged to another business\n\n"
                         "The template was a reskin of a dental coaching business. Its staff\n"
                         "and services survived into About, Booking and the doctor pages.\n"
                         "Removes those, the coaching-only pages, and gives each page its\n"
                         "own title."], cwd=d)
        if "nothing to commit" in out.lower():
            print("    already clean, nothing to push")
            skip_n += 1
            continue
        good, out = run(["git", "push", "origin", "HEAD"], cwd=d)
        if good:
            print(f"    PUSHED -> https://{OWNER.lower()}.github.io/{repo}/")
            ok_n += 1
        else:
            print(f"    PUSH FAILED: {out[:110]}")
            fail_n += 1
            failures.append((repo, "push"))

    print(f"\n{'='*60}\n  pushed {ok_n}   skipped {skip_n}   failed {fail_n}")
    for r, why in failures:
        print(f"    FAILED {r}: {why}")
    print("  GitHub Pages takes a minute or two to serve the new build.")


if __name__ == "__main__":
    main()
