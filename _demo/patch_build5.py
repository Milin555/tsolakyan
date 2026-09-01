"""The logo was the one thing every prospect sees first, and it still carried
the previous brand.

The wordmark lives in an SVG asset as plain <text>, and .svg was not in the
list of scanned extensions, so nothing touched it. Two fixes:

1. Scan .svg like any other text file.
2. Regenerate the wordmark per practice, sized to fit. A straight text swap
   would push "Hampshire Meadow Family & Pediatric Dentistry" well past the
   280px viewBox, so the font size is solved for the name length and the
   canvas widened when the name needs it.
"""
import io, ast

P = "_demo/build_demos.py"
c = io.open(P, encoding="utf-8").read()

c = c.replace('TEXT_EXT = (".html", ".css", ".js", ".json", ".xml", ".txt", ".webmanifest")',
              'TEXT_EXT = (".html", ".css", ".js", ".json", ".xml", ".txt", ".webmanifest", ".svg")')

c = c.replace('''def clear_dir(path):''',
'''WORDMARK = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} 42" width="{w}" height="42">\\n'
    '    <text x="0" y="20" font-family="sans-serif" font-weight="800" '
    'font-size="{fs}" fill="{c1}">{name}</text>\\n'
    '    <text x="0" y="36" font-family="sans-serif" font-weight="500" '
    'font-size="{ts}" letter-spacing="1" fill="{c2}">{tag}</text>\\n'
    '</svg>\\n'
)

# Rough advance width of bold sans at 1px, averaged over mixed-case text.
_ADV, _ADV_CAPS = 0.56, 0.62


def _esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def write_wordmarks(dst, cfg):
    """Rewrite every text-bearing logo SVG with the practice's own wordmark."""
    img = os.path.join(dst, "assets", "img")
    if not os.path.isdir(img):
        return 0
    name = cfg["practice"]
    tag = (cfg["city"] or cfg["country"] or "").upper()
    n = 0
    for f in os.listdir(img):
        if not f.lower().endswith(".svg"):
            continue
        p = os.path.join(img, f)
        try:
            cur = io.open(p, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        if "<text" not in cur or "viewBox" not in cur:
            continue

        fills = re.findall(r'fill="(#[0-9a-fA-F]{3,8})"', cur)
        c1 = fills[0] if fills else "#111827"
        c2 = fills[1] if len(fills) > 1 else c1

        target = 268.0
        fs = 18.0
        if len(name) * _ADV * fs > target:
            fs = max(11.0, target / (len(name) * _ADV))
        ts = 9.0
        if tag and len(tag) * _ADV_CAPS * ts > target:
            ts = max(6.5, target / (len(tag) * _ADV_CAPS))

        w = int(max(280, len(name) * _ADV * fs + 12, len(tag) * _ADV_CAPS * ts + 12))
        io.open(p, "w", encoding="utf-8").write(WORDMARK.format(
            w=w, fs=round(fs, 1), ts=round(ts, 1), c1=c1, c2=c2,
            name=_esc(name), tag=_esc(tag)))
        n += 1
    return n


def clear_dir(path):''', 1)

c = c.replace('''    npruned, freed = prune_unused(dst)''',
              '''    nlogo = write_wordmarks(dst, cfg)
    npruned, freed = prune_unused(dst)''')

c = c.replace('''            "files_changed": changed, "pruned": npruned,''',
              '''            "files_changed": changed, "logos": nlogo, "pruned": npruned,''')

io.open(P, "w", encoding="utf-8").write(c)
ast.parse(c)
print("patched, parses OK")
for probe in ["write_wordmarks", 'TEXT_EXT = (".html"', "WORDMARK", "nlogo"]:
    print(("  ok    " if probe in c else "  MISS  ") + probe)
print(("  ok    " if '".svg")' in c else "  MISS  ") + "svg in TEXT_EXT")
