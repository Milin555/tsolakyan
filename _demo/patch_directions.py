"""Get Directions still sent people to the template's clinic.

The button links to a hardcoded Google short link, maps.app.goo.gl/XTcLv...,
which resolves to the original practice. Nothing caught it: a short link
contains no address, no place name and no country, so both the token scan and
the map check read it as clean. Anyone clicking Get Directions on any of the
twenty demos was routed to a stranger's front door.

Every such link is rebuilt as a real directions URL against the practice's own
address. Where no street address was found the destination is the practice
name plus city, which is what Google resolves best without one.
"""
import io, ast

P = "_demo/build_demos.py"
c = io.open(P, encoding="utf-8").read()

c = c.replace('''def fix_maps(txt, cfg):''',
'''SHORTLINK_RE = re.compile(
    r'href="(https?://(?:maps\\.app\\.goo\\.gl|goo\\.gl/maps|g\\.page)/[^"]*)"', re.I)
DIRS_RE = re.compile(r'href="(https?://[^"]*google\\.[^"]*/maps/dir[^"]*)"', re.I)


def directions_url(cfg):
    """A directions link to this practice, not to the template's."""
    import urllib.parse
    dest = cfg.get("street") or ", ".join(
        x for x in (cfg["practice"], cfg["city"], cfg["country"]) if x)
    return ("https://www.google.com/maps/dir/?api=1&destination="
            + urllib.parse.quote(dest))


def fix_directions(txt, cfg):
    """Rewrite hardcoded short links and stale directions URLs."""
    url = directions_url(cfg)
    txt = SHORTLINK_RE.sub('href="' + url + '"', txt)
    return DIRS_RE.sub('href="' + url + '"', txt)


def fix_maps(txt, cfg):''', 1)

c = c.replace('''    txt = fix_maps(txt, cfg)''',
'''    txt = fix_maps(txt, cfg)
    txt = fix_directions(txt, cfg)''')

io.open(P, "w", encoding="utf-8").write(c)
ast.parse(c)

# ---------- verifier: check 16 ----------
V = "_demo/verify_demos.py"
v = io.open(V, encoding="utf-8").read()

v = v.replace('''    # 12 - size''',
'''    # 16 - no hardcoded map short link may survive. A short link hides its
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
        for m in re.finditer(r'/maps/dir/\\?api=1&destination=([^"&]*)', raw):
            dest = urllib.parse.unquote(m.group(1))
            key = (cfg["city"] or cfg["practice"]).split(",")[0].split("(")[0].strip()
            if key and key.lower() not in dest.lower():
                wrong.append(f"{os.path.basename(p)}:{dest[:40]}")
    res.append((17, "directions target this practice", not wrong,
                "; ".join(wrong[:3])))

    # 12 - size''')

v = v.replace("import argparse, io, json, os, re, sys, urllib.request",
              "import argparse, io, json, os, re, sys, urllib.parse, urllib.request")

io.open(V, "w", encoding="utf-8").write(v)
ast.parse(v)

print("patched, parse OK")
for probe, src, label in [("fix_directions", c, "directions rewriter"),
                          ("SHORTLINK_RE", c, "short link matcher"),
                          ("no hardcoded map short links", v, "check 16"),
                          ("directions target this practice", v, "check 17")]:
    print(("  ok    " if probe in src else "  MISS  ") + label)
