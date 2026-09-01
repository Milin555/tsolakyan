"""Runs the 13-point checklist against every built demo.

    python _demo/verify_demos.py             # checks 1-12, local
    python _demo/verify_demos.py --live      # adds check 13 against the Pages URL
    python _demo/verify_demos.py --only slug

Writes _demo/DEMO_FAILURES.md. Exit code 1 if any demo fails.
"""
import argparse, io, json, os, re, sys, urllib.parse, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from demo_config import load, LEAKED, BASE

# Asset paths legitimately keep the template's original filenames. Renaming
# them is what broke the first build, so they are stripped before scanning.
PATH_ATTR = re.compile(r'(?:src|href|srcset|data-src)\s*=\s*["\'][^"\']*["\']', re.I)
URL_FN = re.compile(r'url\([^)]*\)', re.I)


def strip_paths(t):
    return URL_FN.sub("", PATH_ATTR.sub("", t))

OUT_ROOT = os.path.join(BASE, "_sites")
SKIP = {".git", "__pycache__"}
MAX_MB = 32


def walk_files(root, exts=None):
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in SKIP]
        for f in fn:
            if exts is None or f.lower().endswith(exts):
                yield os.path.join(dp, f)


def check_static(cfg):
    """Checks 1-5, 8, 9, 12. Returns list of (id, name, ok, detail)."""
    root = os.path.join(OUT_ROOT, cfg["slug"])
    res = []
    if not os.path.isdir(root):
        return [(0, "folder exists", False, "not built")]

    html = list(walk_files(root, (".html",)))
    text = list(walk_files(root, (".html", ".css", ".js", ".json", ".xml", ".txt")))

    # 1 - token scrub
    hits = {}
    for p in text:
        raw = io.open(p, encoding="utf-8", errors="ignore").read()
        t = strip_paths(raw) if p.endswith((".html", ".css")) else raw
        for tok in LEAKED:
            if tok in t:
                hits.setdefault(tok, []).append(os.path.relpath(p, root))
    res.append((1, "token scrub", not hits,
                "; ".join(f"{k} in {len(v)} file(s) e.g. {v[0]}" for k, v in list(hits.items())[:4])))

    idx = os.path.join(root, "index.html")
    home = io.open(idx, encoding="utf-8", errors="ignore").read() if os.path.exists(idx) else ""

    # 2 - practice name
    res.append((2, "practice name on home", cfg["practice"] in home,
                "" if cfg["practice"] in home else f"'{cfg['practice']}' absent from index.html"))

    # 3 - doctor name
    if cfg["doctor"]:
        bare = re.sub(r"^(Dr\.?|Doctor)\s+", "", cfg["doctor"]).strip()
        found = any(bare in io.open(p, encoding="utf-8", errors="ignore").read() for p in html)
        res.append((3, "doctor name present", found, "" if found else f"'{bare}' absent from all pages"))
    else:
        res.append((3, "doctor name present", True, "n/a - practice has no named owner"))

    # 4 - city
    if cfg["city"]:
        city = cfg["city"].split(",")[0].split("(")[0].strip()
        found = any(city in io.open(p, encoding="utf-8", errors="ignore").read() for p in html)
        res.append((4, "city present", found, "" if found else f"'{city}' absent"))
    else:
        res.append((4, "city present", True, "n/a"))

    # 5 - contact
    ok_mail = bool(cfg["email"]) and any(
        cfg["email"] in io.open(p, encoding="utf-8", errors="ignore").read() for p in html)
    res.append((5, "contact swapped", ok_mail,
                "" if ok_mail else f"{cfg['email']} not found on any page"))

    # 8 - noindex
    missing = [os.path.basename(p) for p in html
               if "noindex" not in io.open(p, encoding="utf-8", errors="ignore").read()]
    res.append((8, "noindex on every page", not missing,
                f"{len(missing)} page(s) missing e.g. {missing[:3]}" if missing else ""))

    # 9 - disclosure
    missing = [os.path.basename(p) for p in html
               if "Concept proposal prepared for" not in io.open(p, encoding="utf-8", errors="ignore").read()]
    res.append((9, "concept disclosure", not missing,
                f"{len(missing)} page(s) missing" if missing else ""))

    # 14 - embedded maps must point at this practice, not the template's clinic.
    # Scanned raw: the map lives in an iframe src, which strip_paths removes.
    THIRD_PARTY_MAP = ["Neofytos", "Nikodimou", "Limassol", "Boutique Dental Clinic"]
    map_hits, map_pages = [], 0
    for p in html:
        raw = io.open(p, encoding="utf-8", errors="ignore").read()
        if "maps.google" not in raw and "google.com/maps" not in raw:
            continue
        map_pages += 1
        for tok in THIRD_PARTY_MAP:
            if tok in raw:
                map_hits.append(f"{os.path.basename(p)}:{tok}")
    res.append((14, "maps point at this practice", not map_hits,
                "; ".join(map_hits[:3]) if map_hits else f"{map_pages} page(s) with a map"))

    # 15 - the footer strapline is not a duplicate of the practice name
    dup = []
    for p in html:
        raw = io.open(p, encoding="utf-8", errors="ignore").read()
        i = raw.lower().rfind("<footer")
        if i < 0:
            continue
        spans = re.findall(r'<span style="[^"]*">([^<]*)</span>', raw[i:i + 1600])
        norm = [s.strip().lower() for s in spans if s.strip()]
        if len(norm) != len(set(norm)):
            dup.append(os.path.basename(p))
    res.append((15, "footer strapline not duplicated", not dup,
                f"{len(dup)} page(s) e.g. {dup[:2]}" if dup else ""))

    # 16 - no hardcoded map short link may survive. A short link hides its
    # destination, so checks 1 and 14 both read it as clean while it quietly
    # routes to the template's own clinic.
    short = []
    for p in html:
        raw = io.open(p, encoding="utf-8", errors="ignore").read()
        for tok in ("maps.app.goo.gl", "goo.gl/maps", "g.page/"):
            if tok in raw:
                short.append(f"{os.path.basename(p)}:{tok}")
    res.append((16, "no hardcoded map short links", not short,
                "; ".join(short[:3])))

    # 17 - a directions link, where present, targets this practice
    wrong = []
    for p in html:
        raw = io.open(p, encoding="utf-8", errors="ignore").read()
        for m in re.finditer(r'/maps/dir/\?api=1&destination=([^"&]*)', raw):
            dest = urllib.parse.unquote(m.group(1))
            # Compare against the scraped address where we have one. Two
            # prospects list more than one office, so the address they publish
            # need not sit in the first city named in the research file.
            if cfg.get("street"):
                ok = cfg["street"].strip().lower() in dest.strip().lower()
            else:
                key = (cfg["city"] or cfg["practice"]).split(",")[0].split("(")[0].strip()
                ok = (not key) or key.lower() in dest.lower()
            if not ok:
                wrong.append(f"{os.path.basename(p)}:{dest[:40]}")
    res.append((17, "directions target this practice", not wrong,
                "; ".join(wrong[:3])))

    # 12 - size
    size = sum(os.path.getsize(p) for p in walk_files(root)) / 1e6
    res.append((12, "repo size", size <= MAX_MB, f"{size:.1f} MB (limit {MAX_MB})"))
    return res


def check_browser(cfg):
    """Checks 6, 7, 11 in a real browser."""
    from playwright.sync_api import sync_playwright
    import pathlib
    root = pathlib.Path(OUT_ROOT) / cfg["slug"]
    pages = ["index.html", "about.html", "service.html", "booking.html"]
    pages = [p for p in pages if (root / p).exists()]

    errs, broken, hscroll = [], [], []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for name in pages:
            pg = b.new_context(viewport={"width": 1440, "height": 900},
                               reduced_motion="reduce").new_page()
            msgs = []
            pg.on("console", lambda m: msgs.append(m) if m.type == "error" else None)
            pg.on("pageerror", lambda e: msgs.append(e))
            try:
                pg.goto((root / name).as_uri(), wait_until="load", timeout=25000)
                pg.wait_for_timeout(900)
                bad = pg.evaluate(
                    "() => [...document.images].filter(i => i.complete && i.naturalWidth === 0)"
                    ".map(i => i.currentSrc || i.src).slice(0, 5)")
                if bad:
                    broken.append((name, bad))
            except Exception as e:
                errs.append((name, str(e)[:90]))
            if msgs:
                errs.append((name, f"{len(msgs)} console error(s)"))
            pg.close()

        pg = b.new_context(viewport={"width": 390, "height": 844},
                           is_mobile=True, has_touch=True, reduced_motion="reduce").new_page()
        try:
            pg.goto((root / "index.html").as_uri(), wait_until="load", timeout=25000)
            pg.wait_for_timeout(700)
            if pg.evaluate("document.documentElement.scrollWidth > window.innerWidth + 1"):
                over = pg.evaluate(
                    "() => [...document.querySelectorAll('*')].filter(e => "
                    "e.getBoundingClientRect().right > window.innerWidth + 1)"
                    ".slice(0,3).map(e => e.tagName + '.' + (e.className||'').toString().slice(0,30))")
                hscroll = over or ["unattributed"]
        except Exception as e:
            errs.append(("index.html@390", str(e)[:90]))
        pg.close()
        b.close()

    return [
        (6, "pages load clean", not errs, "; ".join(f"{n}: {d}" for n, d in errs[:3])),
        (7, "no broken images", not broken,
         "; ".join(f"{n}: {len(b)} broken e.g. {b[0][-40:]}" for n, b in broken[:2])),
        (11, "no h-scroll at 390", not hscroll, ", ".join(map(str, hscroll[:3]))),
    ]


def check_distinct(rows):
    """Check 10 - every demo is the Lura build in Lura's palette.

    This check used to demand the opposite, a unique template+theme per
    prospect. The rotation was the wrong call: it dragged in three other
    templates' real practitioner photos and fought their native styling.
    """
    odd = []
    for r in rows:
        if r["template"] != "Lura Dentist":
            odd.append((r["slug"], "template " + r["template"]))
        elif r["colours"]["accent"].upper() != "#24A3B1":
            odd.append((r["slug"], "accent " + r["colours"]["accent"]))
    return odd


def check_live(cfg, owner="Milin555"):
    url = f"https://{owner.lower()}.github.io/{cfg['slug']}/"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            return (13, "live 200", r.status == 200, f"{url} -> {r.status}")
    except Exception as e:
        return (13, "live 200", False, f"{url} -> {str(e)[:60]}")


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--only")
    ap.add_argument("--no-browser", action="store_true")
    a = ap.parse_args()

    rows = load()
    dupes = check_distinct(rows)
    if a.only:
        rows = [r for r in rows if r["slug"] == a.only]

    report, total_fail = [], 0
    for cfg in rows:
        res = check_static(cfg)
        if not a.no_browser and os.path.isdir(os.path.join(OUT_ROOT, cfg["slug"])):
            try:
                res += check_browser(cfg)
            except Exception as e:
                res.append((6, "pages load clean", False, f"browser check errored: {str(e)[:70]}"))
        res.append((10, "Lura template and palette", not dupes,
                    "; ".join(f"{x}: {y}" for x, y in dupes[:3])))
        if a.live:
            res.append(check_live(cfg))

        fails = [r for r in res if not r[2]]
        total_fail += len(fails)
        mark = "PASS" if not fails else f"FAIL x{len(fails)}"
        print(f"{cfg['rank']:2} {cfg['slug'][:34]:36} {mark}")
        for i, name, ok, detail in fails:
            print(f"      {i:2} {name}: {detail}")
        report.append((cfg, res))

    with io.open(os.path.join(BASE, "_demo", "DEMO_FAILURES.md"), "w", encoding="utf-8") as f:
        f.write("# Demo checklist results\n\n")
        f.write(f"{len(rows)} demo(s) checked. {total_fail} failing check(s).\n\n")
        for cfg, res in report:
            fails = [r for r in res if not r[2]]
            f.write(f"## {cfg['rank']}. {cfg['practice']} (`{cfg['slug']}`)\n\n")
            if not fails:
                f.write("All checks pass.\n\n")
                continue
            f.write("| # | Check | Detail |\n|---|---|---|\n")
            for i, name, ok, detail in fails:
                f.write(f"| {i} | {name} | {detail} |\n")
            f.write("\n")

    print(f"\n{total_fail} failing check(s) across {len(rows)} demo(s)")
    sys.exit(1 if total_fail else 0)
