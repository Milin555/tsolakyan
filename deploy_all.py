"""
deploy_all.py - Put all 7 finished demos on the public internet.

Seven completed sites are sitting on your desktop with zero live URLs. Every
outreach channel needs a link. This is the blocker.

Uses the GitHub CLI (already authenticated as Milin555) to push any uncommitted
work and enable GitHub Pages on each repo. Free, no signup, no build step -
these are static HTML sites.

Usage:
    python deploy_all.py              # show what would happen
    python deploy_all.py --go         # actually deploy
    python deploy_all.py --go --public  # also flip private repos public

Note: GitHub Pages cannot serve a private repo on a free account. The two
private repos stay dark unless you pass --public.
"""

import argparse
import json
import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OWNER = "Milin555"

PROJECTS = [
    ("Gary Solnit Dentist",         "Gary-S.-Solnit-DDS-MS", "Gary Solnit DDS - cosmetic dentistry"),
    ("Lura Dentist",                "Dr.neo",                "Lura Dental - modern clinic"),
    ("Modern Smile Center Dentist", "modernsmilecenter",     "Modern Smile Center"),
    ("Ritter Ramsey Dentist",       "ritterandramsey",       "Ritter & Ramsey - aesthetic dentistry"),
    ("saidharanx-demo",             "saidharanx-catalogue",  "E-commerce product catalogue"),
    ("dr-jim-arnold-hub",           "Dr.-Jim-Arnold",        "Coaching / course landing page"),
    ("dr-ritter-academy",           "dr-ritter-academy",     "Course platform - Kajabi style"),
]


def run(cmd, cwd=None, check=False):
    """Run a command and hand back (ok, output)."""
    try:
        res = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, timeout=120, shell=False
        )
        out = (res.stdout or "") + (res.stderr or "")
        if check and res.returncode != 0:
            return False, out.strip()
        return res.returncode == 0, out.strip()
    except subprocess.TimeoutExpired:
        return False, "timed out"
    except FileNotFoundError:
        return False, f"command not found: {cmd[0]}"


def check_prereqs():
    ok, out = run(["gh", "auth", "status"])
    if not ok:
        print("ERROR: gh is not authenticated. Run:  gh auth login")
        return False
    print(f"GitHub CLI authenticated as {OWNER}")
    return True


def repo_visibility(repo):
    ok, out = run(["gh", "repo", "view", f"{OWNER}/{repo}", "--json", "visibility",
                   "-q", ".visibility"])
    return out.strip().upper() if ok else "UNKNOWN"


def pages_url(repo):
    ok, out = run(["gh", "api", f"repos/{OWNER}/{repo}/pages", "-q", ".html_url"])
    if ok and out.startswith("http"):
        return out.strip()
    return None


def default_branch(repo):
    ok, out = run(["gh", "repo", "view", f"{OWNER}/{repo}", "--json", "defaultBranchRef",
                   "-q", ".defaultBranchRef.name"])
    return out.strip() if ok and out.strip() else "main"


def push_pending(folder):
    """Commit and push anything uncommitted so Pages serves current work."""
    path = os.path.join(BASE_DIR, folder)
    ok, out = run(["git", "status", "--porcelain"], cwd=path)
    if not ok:
        return False, "not a git repo"
    if not out.strip():
        return True, "clean"

    run(["git", "add", "-A"], cwd=path)
    run(["git", "commit", "-m", "Prepare demo for deployment"], cwd=path)
    ok, out = run(["git", "push"], cwd=path)
    return ok, "pushed" if ok else f"push failed: {out[:120]}"


def make_public(repo):
    return run(["gh", "repo", "edit", f"{OWNER}/{repo}", "--visibility", "public",
                "--accept-visibility-change-consequences"])


def enable_pages(repo, branch):
    """Turn on GitHub Pages serving from the repo root."""
    ok, out = run([
        "gh", "api", "--method", "POST", f"repos/{OWNER}/{repo}/pages",
        "-f", f"source[branch]={branch}", "-f", "source[path]=/",
    ])
    if ok:
        return True, "enabled"
    if "already exists" in out.lower() or "409" in out:
        return True, "already enabled"
    return False, out[:150]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--go", action="store_true", help="actually deploy")
    parser.add_argument("--public", action="store_true",
                        help="flip private repos to public (required for Pages)")
    args = parser.parse_args()

    print("=" * 64)
    print("  DEPLOY ALL DEMOS -> live URLs")
    print("=" * 64)

    if not check_prereqs():
        sys.exit(1)

    if not args.go:
        print("\nDRY RUN - nothing will change. Re-run with --go\n")

    results = []

    for folder, repo, desc in PROJECTS:
        print(f"\n--- {folder}")
        path = os.path.join(BASE_DIR, folder)

        if not os.path.isdir(path):
            print("    folder missing - skipped")
            results.append((folder, repo, None, "folder missing"))
            continue

        vis = repo_visibility(repo)
        existing = pages_url(repo)
        print(f"    repo: {repo} ({vis})")

        if existing:
            print(f"    ALREADY LIVE: {existing}")
            results.append((folder, repo, existing, "already live"))
            continue

        if vis == "PRIVATE" and not args.public:
            print("    PRIVATE - Pages needs a public repo. Re-run with --public")
            results.append((folder, repo, None, "private, skipped"))
            continue

        if not args.go:
            print("    would: push -> enable Pages")
            results.append((folder, repo, None, "dry run"))
            continue

        if vis == "PRIVATE" and args.public:
            ok, out = make_public(repo)
            print(f"    visibility -> public: {'ok' if ok else out[:100]}")

        ok, msg = push_pending(folder)
        print(f"    git: {msg}")

        branch = default_branch(repo)
        ok, msg = enable_pages(repo, branch)
        if not ok:
            print(f"    Pages FAILED: {msg}")
            results.append((folder, repo, None, msg))
            continue

        url = pages_url(repo) or f"https://{OWNER.lower()}.github.io/{repo}/"
        print(f"    LIVE: {url}")
        results.append((folder, repo, url, "deployed"))

    print("\n" + "=" * 64)
    print("  RESULTS")
    print("=" * 64)

    live = [r for r in results if r[2]]
    for folder, repo, url, status in results:
        mark = "OK " if url else "-- "
        print(f"{mark} {folder:<32} {url or status}")

    print(f"\n{len(live)}/{len(PROJECTS)} live")

    if live:
        out_file = os.path.join(BASE_DIR, "LIVE_LINKS.md")
        with open(out_file, "w", encoding="utf-8") as fh:
            fh.write("# Live Demo Links\n\n")
            fh.write("Paste these into DMs, contact forms and proposals.\n\n")
            for folder, repo, url, _ in results:
                if url:
                    desc = next(d for f, r, d in PROJECTS if f == folder)
                    fh.write(f"- **{folder}** — {desc}\n  {url}\n\n")
        print(f"Saved: {out_file}")

    if args.go and live:
        print("\nPages takes 1-2 minutes to build. Open a link to confirm.")


if __name__ == "__main__":
    main()
