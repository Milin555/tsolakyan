"""The hero swap was silently doing nothing visible.

Setting src on the hero <img> is not enough: the tag also carries a srcset
listing seven widths of the original stock photo, and the browser picks from
srcset in preference to src. The client's photograph was being written to disk,
referenced, and then ignored at render time.

The hero is also a four-image carousel, not a single image, so one replacement
was never going to be enough. All four slots now take the client's own
photographs, cycling if they have fewer than four, and falling back to the Lura
stock set only for slots the client cannot fill.
"""
import io, ast

P = "_demo/build_demos.py"
c = io.open(P, encoding="utf-8").read()

old_start = c.index("def ensure_hero(dst, cfg, rank):")
old_end = c.index("def neutralise_portraits(dst, cfg):")

new_fn = '''def ensure_hero(dst, cfg, rank):
    """Fill every hero carousel slot, preferring the client's own photographs.

    Strips srcset and sizes on each slot. Leaving them in place means the
    browser keeps loading the template's stock photo no matter what src says.
    """
    img_dir = os.path.join(dst, "assets", "img")
    os.makedirs(img_dir, exist_ok=True)

    # Client photographs first, in the order the scrape ranked them.
    picks = []
    for i in range(4):
        p = client_file(cfg, "heroes", i)
        if p:
            picks.append(p)
    cfg["_hero_from_client"] = bool(picks)

    # Top up from the Lura stock set so every slot has something.
    k = 0
    while len(picks) < 4:
        stock = os.path.join(HERO_SRC_DIR, HERO_POOL[(rank + k) % len(HERO_POOL)])
        k += 1
        if os.path.exists(stock):
            picks.append(stock)
        elif k > len(HERO_POOL):
            break
    if not picks:
        return 0

    names = []
    for i, srcp in enumerate(picks):
        name = "gen_hero_c%d.jpg" % (i + 1)
        try:
            shutil.copyfile(srcp, os.path.join(img_dir, name))
            names.append(name)
        except OSError:
            pass
    if not names:
        return 0

    changed = 0
    for dp, dn, fn in os.walk(dst):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        for f in fn:
            if not f.endswith(".html"):
                continue
            p = os.path.join(dp, f)
            txt = io.open(p, encoding="utf-8", errors="ignore").read()
            tags = HERO_IMG_RE.findall(txt)
            if not tags:
                continue
            rel = os.path.relpath(img_dir, dp).replace("\\\\", "/")
            out = txt
            for i, tag in enumerate(tags):
                new_src = rel + "/" + names[i % len(names)]
                t = re.sub(r'\\ssrcset="[^"]*"', "", tag)
                t = re.sub(r'\\ssizes="[^"]*"', "", t)
                if 'src="' in t:
                    t = re.sub(r'src="[^"]*"', 'src="' + new_src + '"', t, count=1)
                else:
                    t = t.rstrip("/>").rstrip() + ' src="' + new_src + '"/>'
                t = re.sub(r'\\sloading="lazy"', ' loading="eager"', t) if i == 0 else t
                out = out.replace(tag, t, 1)
            if out != txt:
                io.open(p, "w", encoding="utf-8").write(out)
                changed += len(tags)

    # Some layouts point the hero at a photograph of the real owners.
    for name in ("hero_bg.jpg", "hero-bg.jpg"):
        q = os.path.join(img_dir, name)
        if os.path.exists(q):
            shutil.copyfile(picks[0], q)
            changed += 1
    return changed


'''
c = c[:old_start] + new_fn + c[old_end:]
io.open(P, "w", encoding="utf-8").write(c)
ast.parse(c)
print("ensure_hero rewritten, parses OK")
for probe in ['srcset="[^"]*"', "gen_hero_c%d.jpg", "HERO_IMG_RE.findall"]:
    print(("  ok    " if probe in c else "  MISS  ") + probe)
