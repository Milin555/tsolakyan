"""Four fixes.

1. COLOUR - drop the five-palette rotation. Every demo now uses Lura's own
   teal, which is the one that actually looked right.

2. PORTRAITS - the initials panel was a cop-out. The asset folder already has
   six AI-generated dental staff portraits, so use those instead. Still not a
   real person from any source practice, but it looks like a finished site.

3. FOOTER - the brand block has two spans, a large name and a small uppercase
   strapline. Both were being replaced with the practice name, so the footer
   read "Waimea Dental Studio / WAIMEA DENTAL STUDIO". The small one becomes
   the city, matching the logo wordmark.

4. MAP - every booking and careers page embeds a Google Map pointing at
   "Dr. Neofytos Ioannides - Boutique Dental Clinic, Limassol", a real clinic
   in Cyprus. It survived because it lives in an iframe src, which the token
   scan strips before checking. Now points at the prospect's own city.
"""
import io, ast

# ---------- config: one palette for all ----------
D = "_demo/demo_config.py"
d = io.open(D, encoding="utf-8").read()
d = d.replace('''# Five palettes. Each is a full accent set so a demo reads as designed, not tinted.
THEMES = {
    "slate":   {"accent": "#2F4858", "accent_dk": "#1E2F3A", "soft": "#EEF2F4", "warm": "#C8A96A"},
    "forest":  {"accent": "#2C5545", "accent_dk": "#1B3A2E", "soft": "#EDF3F0", "warm": "#C9A227"},
    "plum":    {"accent": "#4A2F52", "accent_dk": "#321F38", "soft": "#F3EEF5", "warm": "#C08552"},
    "indigo":  {"accent": "#2E3A78", "accent_dk": "#1D2650", "soft": "#EEF0F8", "warm": "#C6A15B"},
    "clay":    {"accent": "#7A4436", "accent_dk": "#552E24", "soft": "#F6EFEB", "warm": "#B08968"},
}''',
'''# One palette, taken from the Lura template's own stylesheet. The rotation
# fought the templates' native styling; this agrees with it.
LURA = {"accent": "#24A3B1", "accent_dk": "#011F23", "soft": "#EAF6F7", "warm": "#C8A96A"}
THEMES = {k: dict(LURA) for k in ("slate", "forest", "plum", "indigo", "clay")}''')
io.open(D, "w", encoding="utf-8").write(d)
ast.parse(d)

# ---------- builder ----------
P = "_demo/build_demos.py"
c = io.open(P, encoding="utf-8").read()

c = c.replace('''def neutralise_portraits(dst, cfg):
    """Replace named practitioners' headshots with a themed placeholder."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return 0''',
'''TEAM_POOL = ["gen_team-image-%d.jpg" % i for i in range(1, 7)]


def neutralise_portraits(dst, cfg):
    """Swap named practitioners' headshots for generic clinical portraits."""
    try:
        from PIL import Image
    except ImportError:
        return 0''')

c = c.replace('''    accent = cfg["colours"]["accent_dk"]
    soft = cfg["colours"]["soft"]
    initials = "".join(w[0] for w in re.sub(r"^Dr\\.?\\s+", "", cfg["doctor"] or cfg["practice"]).split()[:2]).upper()

    n = 0
    for name in wanted:
        p = os.path.join(img_dir, name)
        if not os.path.exists(p):
            continue
        try:
            w, h = Image.open(p).size
        except Exception:
            w, h = 800, 1000
        im = Image.new("RGB", (w, h), accent)
        d = ImageDraw.Draw(im)
        size = max(48, int(min(w, h) * 0.28))
        try:
            font = ImageFont.truetype("arialbd.ttf", size)
        except Exception:
            try:
                font = ImageFont.truetype("arial.ttf", size)
            except Exception:
                font = ImageFont.load_default()
        bb = d.textbbox((0, 0), initials, font=font)
        d.text(((w - (bb[2] - bb[0])) / 2 - bb[0], (h - (bb[3] - bb[1])) / 2 - bb[1]),
               initials, fill=soft, font=font)
        try:
            im.save(p, quality=88)
            n += 1
        except Exception:
            pass
    return n''',
'''    n = 0
    for i, name in enumerate(sorted(wanted)):
        p = os.path.join(img_dir, name)
        if not os.path.exists(p):
            continue
        pick = TEAM_POOL[(cfg["rank"] + i) % len(TEAM_POOL)]
        src = os.path.join(HERO_SRC_DIR, pick)
        if not os.path.exists(src):
            continue
        try:
            w, h = Image.open(p).size
            im = Image.open(src).convert("RGB")
            # Fill the original frame so the page layout does not shift.
            sr, tr = im.width / im.height, w / h
            if sr > tr:
                nw = int(im.height * tr)
                im = im.crop(((im.width - nw) // 2, 0, (im.width + nw) // 2, im.height))
            else:
                nh = int(im.width / tr)
                im = im.crop((0, (im.height - nh) // 2, im.width, (im.height + nh) // 2))
            im = im.resize((w, h), Image.LANCZOS)
            im.save(p, quality=88)
            n += 1
        except Exception:
            pass
    return n''')

# Footer strapline and the Cyprus map.
c = c.replace('''    txt = repair_svg_paths(txt)''',
'''    txt = repair_svg_paths(txt)
    txt = fix_footer_strapline(txt, cfg)
    txt = fix_maps(txt, cfg)''')

c = c.replace('''def process_html(txt, cfg, reps):''',
'''SMALL_SPAN = re.compile(
    r'(<span style="[^"]*font-size:\\s*13px[^"]*uppercase[^"]*">)([^<]*)(</span>)', re.I)
MAP_Q = re.compile(r'(maps\\.google\\.com/maps\\?q=)([^&"\\']*)', re.I)


def fix_footer_strapline(txt, cfg):
    """The footer's small uppercase span is a strapline, not a second logo."""
    tag = (cfg["city"] or cfg["country"] or "").upper()
    if not tag:
        return txt
    return SMALL_SPAN.sub(lambda m: m.group(1) + tag + m.group(3), txt)


def fix_maps(txt, cfg):
    """Point every embedded map at this practice, not the template's clinic."""
    import urllib.parse
    where = ", ".join(x for x in (cfg["practice"], cfg["city"], cfg["country"]) if x)
    q = urllib.parse.quote(where)
    return MAP_Q.sub(lambda m: m.group(1) + q, txt)


def process_html(txt, cfg, reps):''', 1)

io.open(P, "w", encoding="utf-8").write(c)
ast.parse(c)

print("patched, parse OK")
for probe, src in [("LURA =", d), ("TEAM_POOL", c), ("fix_footer_strapline", c),
                   ("fix_maps", c), ("ImageDraw", c)]:
    mark = "ok    " if probe in src else "MISS  "
    if probe == "ImageDraw":
        mark = "ok    (removed)" if probe not in src else "MISS  still present"
    print("  " + mark + " " + probe)
