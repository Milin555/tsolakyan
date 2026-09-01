"""Two image problems the token checks could never catch.

1. Two of the four templates ship a hero <img> with no src at all, so those
   demos opened on a flat black band. The third uses hero_bg.jpg, which is a
   photograph of the two real dentists who own the source practice. Sending a
   prospect a page headed by two strangers presented as their own team is
   worse than sending nothing.

2. The doctor pages carry real named practitioners' headshots.

Heroes now come from a verified-generic pool, rotated so demos differ.
Portraits become a neutral panel in the practice's own accent colour. On a
concept site that reads as "photograph to be supplied", which is honest,
rather than passing off someone else's face.
"""
import io, ast

P = "_demo/build_demos.py"
c = io.open(P, encoding="utf-8").read()

c = c.replace('''def clear_dir(path):''',
'''# Verified generic stock: clinical scenes and models, no identifiable
# practitioner from any of the source practices. Checked by eye.
HERO_POOL = [
    "gen_dentist-examining-patients-teeth-close-up_1.jpg",
    "gen_hero-2.jpg",
    "gen_home-value-image.jpg",
    "gen_blog-image-6.jpg",
    "gen_hero-3.jpg",
]
HERO_SRC_DIR = os.path.join(BASE, "Lura Dentist", "assets", "img")
HERO_IMG_RE = re.compile(r'<img\\b[^>]*class="[^"]*home-hero_image[^"]*"[^>]*>', re.I)


def ensure_hero(dst, cfg, rank):
    """Guarantee a hero photograph, and make sure it is a generic one."""
    img_dir = os.path.join(dst, "assets", "img")
    os.makedirs(img_dir, exist_ok=True)
    pick = HERO_POOL[rank % len(HERO_POOL)]
    src = os.path.join(HERO_SRC_DIR, pick)
    if not os.path.exists(src):
        return None
    target_name = "gen_hero_main.jpg"
    shutil.copyfile(src, os.path.join(img_dir, target_name))

    changed = 0
    for dp, dn, fn in os.walk(dst):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        for f in fn:
            if not f.endswith(".html"):
                continue
            p = os.path.join(dp, f)
            txt = io.open(p, encoding="utf-8", errors="ignore").read()
            m = HERO_IMG_RE.search(txt)
            if not m:
                continue
            tag = m.group(0)
            rel = os.path.relpath(img_dir, dp).replace("\\\\", "/")
            new_src = rel + "/" + target_name
            if 'src="' in tag:
                new_tag = re.sub(r'src="[^"]*"', 'src="' + new_src + '"', tag, count=1)
            else:
                new_tag = tag[:-1].rstrip("/") + ' src="' + new_src + '" alt="' + \\
                          cfg["practice"] + '" />'
            if new_tag != tag:
                io.open(p, "w", encoding="utf-8").write(txt.replace(tag, new_tag, 1))
                changed += 1

    # Some templates point the hero at a photograph of the real owners.
    for name in ("hero_bg.jpg", "hero-bg.jpg"):
        p = os.path.join(img_dir, name)
        if os.path.exists(p):
            shutil.copyfile(src, p)
            changed += 1
    return changed


def neutralise_portraits(dst, cfg):
    """Replace named practitioners' headshots with a themed placeholder."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return 0
    img_dir = os.path.join(dst, "assets", "img")
    if not os.path.isdir(img_dir):
        return 0

    wanted = set()
    for f in os.listdir(dst):
        if not f.startswith("doctor-") or not f.endswith(".html"):
            continue
        txt = io.open(os.path.join(dst, f), encoding="utf-8", errors="ignore").read()
        for s in re.findall(r'src="[^"]*?/?([^"/]+\\.(?:jpg|jpeg|png|webp))"', txt, re.I):
            if "logo" in s.lower() or "favicon" in s.lower() or s.startswith("gen_"):
                continue
            wanted.add(s)

    accent = cfg["colours"]["accent_dk"]
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
    return n


def clear_dir(path):''', 1)

c = c.replace('''    nlogo = write_wordmarks(dst, cfg)''',
'''    nhero = ensure_hero(dst, cfg, cfg["rank"])
    nport = neutralise_portraits(dst, cfg)
    nlogo = write_wordmarks(dst, cfg)''')

c = c.replace('''            "files_changed": changed, "logos": nlogo, "pruned": npruned,''',
              '''            "files_changed": changed, "hero": nhero, "portraits": nport,
            "logos": nlogo, "pruned": npruned,''')

io.open(P, "w", encoding="utf-8").write(c)
ast.parse(c)
print("patched, parses OK")
for probe in ["HERO_POOL", "ensure_hero", "neutralise_portraits", "nhero"]:
    print(("  ok    " if probe in c else "  MISS  ") + probe)
