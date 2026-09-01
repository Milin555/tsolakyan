"""Creates a public repo per demo, pushes it, and turns on GitHub Pages.

    python _demo/deploy_demos.py             # dry run
    python _demo/deploy_demos.py --go
    python _demo/deploy_demos.py --go --only waimea-dental-studio

Safe to re-run: existing repos are updated, not recreated.
"""
import argparse, io, json, os, subprocess, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from demo_config import load, BASE

OUT_ROOT = os.path.join(BASE, "_sites")
OWNER = "Milin555"
AUTHOR = ("Milin Dholiya", "dholiyamilin@gmail.com")


def run(cmd, cwd=None, check=True, quiet=False):
    r = subprocess.run(cmd, cwd=cwd, shell=isinstance(cmd, str),
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check and r.returncode != 0 and not quiet:
        raise RuntimeError(f"{cmd}\n{r.stdout}\n{r.stderr}")
    return r


def repo_exists(name):
    return run(["gh", "repo", "view", f"{OWNER}/{name}", "--json", "name"],
               check=False, quiet=True).returncode == 0


def deploy_one(cfg, go):
    slug, root = cfg["slug"], os.path.join(OUT_ROOT, cfg["slug"])
    url = f"https://{OWNER.lower()}.github.io/{slug}/"
    if not os.path.isdir(root):
        return {"slug": slug, "status": "not built", "url": None}
    if not go:
        return {"slug": slug, "status": "would deploy", "url": url}

    if not os.path.isdir(os.path.join(root, ".git")):
        run(["git", "init", "-q", "-b", "main"], cwd=root)

    gi = os.path.join(root, ".gitignore")
    if not os.path.exists(gi):
        io.open(gi, "w", encoding="utf-8").write("__pycache__/\n.DS_Store\nThumbs.db\n")

    run(["git", "add", "-A"], cwd=root)
    msg = (f"{cfg['practice']} website concept\n\n"
           f"Static site concept for {cfg['practice']}"
           + (f" in {cfg['city']}" if cfg["city"] else "") + ".\n"
           "Unaffiliated design proposal. Every page is noindex and carries a\n"
           "concept notice in the footer.")
    r = run(["git", "-c", f"user.name={AUTHOR[0]}", "-c", f"user.email={AUTHOR[1]}",
             "commit", "-q", "-m", msg], cwd=root, check=False)
    committed = r.returncode == 0

    if not repo_exists(slug):
        run(["gh", "repo", "create", f"{OWNER}/{slug}", "--public",
             "--description", f"{cfg['practice']} - website concept"], check=True)
        time.sleep(1.5)

    remotes = run(["git", "remote"], cwd=root).stdout.split()
    remote_url = f"https://github.com/{OWNER}/{slug}.git"
    if "origin" not in remotes:
        run(["git", "remote", "add", "origin", remote_url], cwd=root)
    else:
        run(["git", "remote", "set-url", "origin", remote_url], cwd=root)

    p = run(["git", "push", "-u", "origin", "main", "--force"], cwd=root, check=False)
    if p.returncode != 0:
        return {"slug": slug, "status": "push failed: " + p.stderr.strip()[:90], "url": None}

    # Pages. Fails harmlessly if already enabled.
    run(["gh", "api", "-X", "POST", f"repos/{OWNER}/{slug}/pages",
         "-f", "source[branch]=main", "-f", "source[path]=/"], check=False, quiet=True)

    return {"slug": slug, "status": "deployed" + ("" if committed else " (no new commit)"),
            "url": url}


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--go", action="store_true")
    ap.add_argument("--only")
    a = ap.parse_args()

    rows = load()
    if a.only:
        rows = [r for r in rows if r["slug"] == a.only]

    results = []
    for cfg in rows:
        try:
            res = deploy_one(cfg, a.go)
        except Exception as e:
            res = {"slug": cfg["slug"], "status": "error: " + str(e)[:100], "url": None}
        results.append((cfg, res))
        print(f"{cfg['rank']:2} {res['slug'][:34]:36} {res['status'][:40]:42} {res['url'] or ''}")

    if a.go:
        with io.open(os.path.join(BASE, "LIVE_LINKS_20.md"), "w", encoding="utf-8") as f:
            f.write("# 20 personalised dental demos\n\n")
            f.write("Pages can take a couple of minutes to go live after the first push.\n\n")
            f.write("| # | Practice | City | Live link | Outreach channel |\n")
            f.write("|---|---|---|---|---|\n")
            for cfg, res in results:
                if res["url"]:
                    f.write(f"| {cfg['rank']} | {cfg['practice']} | {cfg['city']} | "
                            f"{res['url']} | {cfg['channel'][:44]} |\n")
        print("\nwrote LIVE_LINKS_20.md")
