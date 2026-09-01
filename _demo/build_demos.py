"""Builds one personalised demo site per prospect from a template.

Deterministic and non-interactive: reads demo_config.py, token_map.json and
_demo/copy/<slug>.json, and writes ../<slug>/ ready to commit.

    python _demo/build_demos.py            # dry run, reports what would change
    python _demo/build_demos.py --go       # write the folders
    python _demo/build_demos.py --go --only waimea-dental-studio
"""
import argparse, io, json, os, re, shutil, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from demo_config import load, LEAKED, BASE

DEMO = os.path.join(BASE, "_demo")
COPY = os.path.join(DEMO, "copy")
OUT_ROOT = os.path.join(BASE, "_sites")
TEXT_EXT = (".html", ".css", ".js", ".json", ".xml", ".txt", ".webmanifest", ".svg")
SKIP_DIRS = {".git", "__pycache__", "node_modules"}

JPG_MAX_KB, JPG_MAX_PX, JPG_Q = 300, 1600, 82


def load_token_map():
    p = os.path.join(DEMO, "token_map.json")
    if os.path.exists(p):
        return json.load(io.open(p, encoding="utf-8"))
    return {}


def ignore(dirname, names):
    out = [n for n in names if n in SKIP_DIRS or n.startswith("variant-")]
    return set(out)


def optimise_images(root):
    """Recompress oversized JPEGs in place. Returns (files, bytes saved)."""
    try:
        from PIL import Image
    except ImportError:
        return 0, 0
    n = saved = 0
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        for f in fn:
            if not f.lower().endswith((".jpg", ".jpeg")):
                continue
            p = os.path.join(dp, f)
            before = os.path.getsize(p)
            if before < JPG_MAX_KB * 1024:
                continue
            try:
                im = Image.open(p)
                im = im.convert("RGB")
                if max(im.size) > JPG_MAX_PX:
                    im.thumbnail((JPG_MAX_PX, JPG_MAX_PX), Image.LANCZOS)
                im.save(p, "JPEG", quality=JPG_Q, optimize=True, progressive=True)
                after = os.path.getsize(p)
                if after < before:
                    n += 1; saved += before - after
            except Exception:
                pass
    return n, saved



def prune_unused(root, min_bytes=200 * 1024):
    """Drop media no HTML/CSS/JS refers to. The Webflow exports carry ~33 MB of
    it, including a 12 MB video nothing links to. Conservative: only files over
    min_bytes, and check 7 catches any mistake."""
    refs = []
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        for f in fn:
            if f.endswith((".html", ".css", ".js", ".json", ".xml")):
                try:
                    refs.append(io.open(os.path.join(dp, f), encoding="utf-8",
                                        errors="ignore").read())
                except Exception:
                    pass
    blob = "\n".join(refs)
    n = freed = 0
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        for f in fn:
            if not f.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".mp4", ".mov")):
                continue
            p = os.path.join(dp, f)
            try:
                s = os.path.getsize(p)
            except OSError:
                continue
            if s < min_bytes or f in blob:
                continue
            try:
                os.remove(p); n += 1; freed += s
            except OSError:
                pass
    return n, freed



# Domains and inboxes belonging to real third parties. Leaving any of these on
# a demo would send the prospect to a competitor and expose a stranger's inbox.
THIRD_PARTY_DOMAINS = [
    "585dentist.com", "www.585dentist.com",
    "foundationdentalalliance.com", "www.foundationdentalalliance.com",
    "garysolnitdds.com", "www.garysolnitdds.com",
    "ritterandramsey.com", "www.ritterandramsey.com",
    "modernsmilecenter.com", "www.modernsmilecenter.com",
]
# Bare handles: no TLD, so the domain test misses them, but they are still
# unambiguous third-party identifiers and safe to replace anywhere.
THIRD_PARTY_TOKENS = [
    "585dentist", "foundationdentalalliance", "garysolnitdds",
    "ritterandramsey", "modernsmilecenter", "drneodentistry", "mcim21",
]

# Identifier pairs safe to rename wholesale: the definition and every call site
# live in the same files, and the name carries a previous brand.
IDENT_RENAMES = [("lumoraLead", "submitLead")]

# SVG path data admits no parentheses. Two attributes per template carry one,
# so the browser rejects the path and logs an error.
BAD_PATH = re.compile(r'(\sd=")([^"]*[()][^"]*)(")')


def repair_svg_paths(txt):
    def fix(m):
        return m.group(1) + m.group(2).replace("(", " ").replace(")", " ") + m.group(3)
    return BAD_PATH.sub(fix, txt)
THIRD_PARTY_EMAILS = [
    "edrumm@585dentist.com", "info@foundationdentalalliance.com",
    "info@garysolnitdds.com", "mcim21@gmail.com",
    "info@ritterandramsey.com", "drneodentistry@gmail.com",
    "john@example.com",
]

SPLIT_RE = re.compile(r"(<script[\s\S]*?</script>|<style[\s\S]*?</style>|<!--[\s\S]*?-->|<[^>]+>)", re.I)
ATTR_RE = re.compile(r'((?:alt|title|aria-label|placeholder|content)\s*=\s*)(["\'])(.*?)\2', re.I)
PATHY = re.compile(r'(^\s*(https?:|/|\./|\.\./))|(\.(css|js|jpg|jpeg|png|webp|svg|mp4|ico|woff2?)\b)', re.I)
PHONEY = re.compile(r"[+()\d][\d\s().-]{6,}$")


def _apply(s, reps):
    for old, new in reps:
        s = s.replace(old, new)
    return s


def is_global(old):
    """Contact strings, third-party domains and bare handles: safe anywhere."""
    return ("@" in old
            or bool(PHONEY.fullmatch(old.strip()))
            or old in THIRD_PARTY_DOMAINS
            or old in THIRD_PARTY_TOKENS
            or any(old == a for a, _ in IDENT_RENAMES))


def split_reps(reps):
    g = [(o, n) for o, n in reps if is_global(o)]
    gset = {o for o, _ in g}
    v = [(o, n) for o, n in reps if o not in gset]
    code = g + [(o, n) for o, n in v if " " in o]
    return g, v, code


def replace_visible(txt, reps_global, reps_visible, reps_code=None):
    """Globals everywhere, code tier inside scripts, brands only in read text."""
    reps_code = reps_code if reps_code is not None else reps_global
    out = []
    for part in SPLIT_RE.split(txt):
        if not part:
            continue
        if part.startswith("<"):
            low = part[:8].lower()
            if low.startswith(("<script", "<style", "<!--")):
                out.append(_apply(part, reps_code))
                continue
            part = _apply(part, reps_global)

            def attr(m):
                val = m.group(3)
                if PATHY.search(val):
                    return m.group(0)
                return m.group(1) + m.group(2) + _apply(val, reps_visible) + m.group(2)

            out.append(ATTR_RE.sub(attr, part))
        else:
            out.append(_apply(_apply(part, reps_global), reps_visible))
    return "".join(out)


WORDMARK = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} 42" width="{w}" height="42">\n'
    '    <text x="0" y="20" font-family="sans-serif" font-weight="800" '
    'font-size="{fs}" fill="{c1}">{name}</text>\n'
    '    <text x="0" y="36" font-family="sans-serif" font-weight="500" '
    'font-size="{ts}" letter-spacing="1" fill="{c2}">{tag}</text>\n'
    '</svg>\n'
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


# Verified generic stock: clinical scenes and models, no identifiable
# practitioner from any of the source practices. Checked by eye.
HERO_POOL = [
    "gen_dentist-examining-patients-teeth-close-up_1.jpg",
    "gen_hero-2.jpg",
    "gen_home-value-image.jpg",
    "gen_blog-image-6.jpg",
    "gen_hero-3.jpg",
]
HERO_SRC_DIR = os.path.join(BASE, "Lura Dentist", "assets", "img")
HERO_IMG_RE = re.compile(r'<img\b[^>]*class="[^"]*home-hero_image[^"]*"[^>]*>', re.I)


CLIENT_ROOT = os.path.join(BASE, "_demo", "client_assets")


def client_file(cfg, kind, i=0):
    """Path to a scraped asset, or None. kind is 'heroes' or 'people'."""
    items = (cfg.get("assets") or {}).get(kind) or []
    if i >= len(items):
        return None
    p = os.path.join(CLIENT_ROOT, cfg["slug"], items[i]["file"])
    return p if os.path.exists(p) else None


def ensure_hero(dst, cfg, rank):
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
            rel = os.path.relpath(img_dir, dp).replace("\\", "/")
            out = txt
            for i, tag in enumerate(tags):
                new_src = rel + "/" + names[i % len(names)]
                t = re.sub(r'\ssrcset="[^"]*"', "", tag)
                t = re.sub(r'\ssizes="[^"]*"', "", t)
                if 'src="' in t:
                    t = re.sub(r'src="[^"]*"', 'src="' + new_src + '"', t, count=1)
                else:
                    t = t.rstrip("/>").rstrip() + ' src="' + new_src + '"/>'
                t = re.sub(r'\sloading="lazy"', ' loading="eager"', t) if i == 0 else t
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


def neutralise_portraits(dst, cfg):
    """Their own dentist where we have them, generic staff photos otherwise.

    Either way the template's own named practitioners are gone.
    """
    try:
        from PIL import Image
    except ImportError:
        return 0
    img_dir = os.path.join(dst, "assets", "img")
    if not os.path.isdir(img_dir):
        return 0

    # Order matters: the client's own dentist belongs on the page that carries
    # their name, not on whichever filename happens to sort first.
    lead_img, other_imgs = None, []
    tmpl_lead = cfg.get("_lead_tmpl") or ""
    for f in sorted(os.listdir(dst)):
        if not f.startswith("doctor-") or not f.endswith(".html"):
            continue
        txt = io.open(os.path.join(dst, f), encoding="utf-8", errors="ignore").read()
        imgs = [s for s in re.findall(r'src="[^"]*?/?([^"/]+\.(?:jpg|jpeg|png|webp))"', txt, re.I)
                if "logo" not in s.lower() and "favicon" not in s.lower()]
        if not imgs:
            continue
        is_lead = (cfg["doctor"] and cfg["doctor"] in txt) or (tmpl_lead and tmpl_lead in txt)
        if is_lead and lead_img is None:
            lead_img = imgs[0]
        else:
            other_imgs.extend(imgs)

    wanted = ([lead_img] if lead_img else []) + [i for i in dict.fromkeys(other_imgs)
                                                 if i != lead_img]

    n = 0
    for i, name in enumerate(wanted):
        p = os.path.join(img_dir, name)
        if not os.path.exists(p):
            continue
        src = client_file(cfg, "people", i)
        if src:
            cfg["_people_from_client"] = cfg.get("_people_from_client", 0) + 1
        elif name.startswith("gen_"):
            continue          # already generic, nothing to gain
        else:
            src = os.path.join(HERO_SRC_DIR, TEAM_POOL[(cfg["rank"] + i) % len(TEAM_POOL)])
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
    return n


def clear_dir(path):
    """Empty a directory without removing it.

    On Windows the directory itself stays locked while any process has it as a
    working directory, so rmtree() raises even though the contents are free.
    Preserve .git so a redeploy keeps the repo's history and remote.
    """
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)
        return
    for name in os.listdir(path):
        if name == ".git":
            continue
        p = os.path.join(path, name)
        try:
            if os.path.isdir(p) and not os.path.islink(p):
                shutil.rmtree(p)
            else:
                os.remove(p)
        except OSError:
            pass


_NOT_STREET = (
    r"(?!(?:Street|St|Road|Rd|Avenue|Ave|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way|"
    r"Highway|Hwy|Parkway|Pkwy|Place|Pl|Court|Ct|Suite|Ste|Unit|Floor|Fl)\b)"
    r"[A-Z][A-Za-z.'\-]+"
)

LOCALITY_RE = re.compile(
    "(" + _NOT_STREET + r"(?:\s+" + _NOT_STREET + r"){0,2},?\s+"
    r"(?:[A-Z]{2}|[A-Z][a-z]+|NSW|VIC|QLD|TAS|ACT)\s+\d{4,5}(?:-\d{4})?"
    "|" + _NOT_STREET + r"(?:\s+" + _NOT_STREET + r"){0,2},?\s+"
    r"[A-Z]{1,2}\d{1,2}[A-Z]?\s*\d[A-Z]{2})"
)

SUITE_RE = re.compile(r"^((?:Suite|Ste\.?|Unit|Floor|Fl\.?|#)\s*[\w-]+)\s+(.*)$", re.I)


def split_address(cfg):
    """(street line, locality).

    The town is the last locality-shaped run in the string, never the first.
    """
    full = re.sub(r"\s+", " ", (cfg.get("street") or "")).strip().rstrip(",")
    city = cfg.get("city") or cfg.get("country") or ""
    if not full:
        return city, city

    last = None
    for m in LOCALITY_RE.finditer(full):
        last = m
    if last:
        street = full[:last.start()].strip().rstrip(",").strip()
        loc = last.group(0).strip()
        sm = SUITE_RE.match(loc)          # a suite belongs on the street line
        if sm:
            street = (street + ", " + sm.group(1)).strip(" ,")
            loc = sm.group(2).strip()
        return (street or city), loc

    parts = [p.strip() for p in full.split(",") if p.strip()]
    if len(parts) >= 3:
        return ", ".join(parts[:-2]), ", ".join(parts[-2:])
    if len(parts) == 2:
        return parts[0], parts[1]
    return full, city


def build_replacements(cfg, tmap, copy):
    """Ordered list of (old, new). Longest first so substrings do not pre-empt."""
    t = tmap.get(cfg["template"], {})
    r = []

    practice = cfg["practice"]
    # Brand names, longest first.
    brands = sorted([b["text"] for b in t.get("brand_names", [])], key=len, reverse=True)
    for b in brands:
        r.append((b, practice))
    # Display forms only. The lowercase form is deliberately excluded: it is
    # the stylesheet filename and a JS function name, not visible text.
    for b in ["Foundation Dental Alliance", "Lumora", "LUMORA"]:
        r.append((b, practice))

    # Every third-party domain the half-finished templates still point at.
    # These must not survive in any href, and they are safe to swap wholesale.
    own = cfg.get("domain") or (cfg["slug"] + ".com")
    for d in THIRD_PARTY_DOMAINS:
        r.append((d, own))
    for old, new in IDENT_RENAMES:
        r.append((old, new))
    handle = re.sub(r"[^a-z0-9]", "", (cfg.get("domain") or cfg["slug"]).split(".")[0].lower())
    for tok in THIRD_PARTY_TOKENS:
        r.append((tok, handle))
    for e in THIRD_PARTY_EMAILS:
        r.append((e, cfg["email"] or "hello@" + own))
    # Template addresses, fragment by fragment. They are split across tags in
    # the markup, so replacing the assembled string never matched anything.
    street, locality = split_address(cfg)
    own_addr = (cfg.get("street") or "").lower()

    def _safe(frag):
        """Skip a template fragment that also sits inside the real address.

        Replacements run in sequence over one string, so a fragment that
        appears in text an earlier rule just inserted would be rewritten a
        second time.
        """
        return frag.lower() not in own_addr

    for frag in ("9675 Brighton Way, Suite 330", "9675 Brighton Way",
                 "123 Smile Avenue, Suite 200", "123 Smile Avenue",
                 "456 Bright Dental Blvd, Floor 3", "456 Bright Dental Blvd",
                 "45 King's Road", "45 King\u2019s Road"):
        if _safe(frag):
            r.append((frag, street))
    for frag in ("Beverly Hills, CA 90210", "Beverly Hills, California",
                 "Beverly Hills, CA", "Beverly Hills",
                 "New York, NY 10001", "New York, NY", "New York",
                 "Los Angeles, CA 90001", "Los Angeles, CA", "Los Angeles",
                 "Chelsea, SW3 5UZ", "SW3 5UZ", "Chelsea"):
        if _safe(frag):
            r.append((frag, locality))
    for frag in ("Suite 330, ", "Suite 200, ", "Floor 3, ",
                 "Suite 330 ", "Suite 200 ", "Floor 3 ",
                 "Suite 330", "Suite 200", "Floor 3"):
        r.append((frag, ""))

    # The template's dentists, mapped onto the ones who actually work there.
    for tmpl, real in (cfg.get("_doc_map") or {}).items():
        r.append((tmpl, re.sub(r"^(Dr\.?|Doctor)\s+", "", real).strip()))
        r.append(("Dr. " + tmpl, real))

    # The template's own geography, which survives in every meta description.
    _city = cfg["city"] or cfg["country"] or ""
    if _city:
        r.append(("Limassol, Cyprus", _city))
        r.append(("Limassol", _city))
    if cfg["country"]:
        r.append(("Cyprus Dental Association", cfg["country"] + " Dental Association"))
        r.append(("Cyprus", cfg["country"]))
    r.append(("University of Leipzig, Germany", "To be supplied by the practice"))
    r.append(("University of Leipzig", "To be supplied by the practice"))

    # Brands hidden inside JS confirmation receipts - invisible until submit.
    for b in ["LUMORA CLINIC CAREERS", "PANNU DENTAL GROUP",
              "Dr. Neo Boutique Dental Clinic", "Dr. Neo Boutique Dental",
              "Dr. Neo Dentistry"]:
        r.append((b, practice))

    # Contact details.
    for e in t.get("emails", []) or []:
        r.append((e, cfg["email"] or "hello@" + cfg["slug"] + ".com"))
    r.append(("edrumm@585dentist.com", cfg["email"] or "hello@example.org"))
    r.append(("info@foundationdentalalliance.com", cfg["email"] or "hello@example.org"))
    r.append(("john@example.com", cfg["email"] or "hello@example.org"))
    # Template numbers belong to real third parties and must always go.
    tmpl_phones = (t.get("phones", []) or []) + [
        "310-888-1850", "tel:310-888-1850",
        "+357 70005758", "tel:+357 70005758", "tel:+35770005758", "+35770005758",
    ]
    fallback = cfg["email"] or ("hello@" + own)
    for ph in tmpl_phones:
        if ph.startswith("tel:"):
            r.append((ph, ("tel:" + re.sub(r"[^\d+]", "", cfg["phone"]))
                      if cfg["phone"] else "mailto:" + fallback))
        else:
            r.append((ph, cfg["phone"] or fallback))

    # Lead doctor.
    docs = t.get("doctor_names", []) or []
    if cfg["doctor"] and docs:
        lead = docs[0]["name"] if isinstance(docs[0], dict) else docs[0]
        bare = re.sub(r"^(Dr\.?|Doctor)\s+", "", cfg["doctor"]).strip()
        r.append((lead, bare))
        r.append(("Dr. " + lead, cfg["doctor"]))

    # Copy blocks.
    if copy:
        pairs = [("hero_h1", t.get("hero_h1")), ("hero_sub", t.get("hero_sub")),
                 ("about_heading", t.get("about_heading")), ("about_body", t.get("about_body")),
                 ("footer_tagline", t.get("footer_tagline"))]
        for key, old in pairs:
            new = copy.get(key)
            if old and new:
                r.append((old, new.replace("\n\n", " ")))
        old_svcs = t.get("service_names") or []
        new_svcs = [s["name"] for s in copy.get("services", [])]
        for old, new in zip(old_svcs, new_svcs):
            r.append((old, new))

    # Whole template addresses map to the practice's real one.
    _full = (cfg.get("street") or "").strip()
    for a in t.get("addresses", []) or []:
        if _full:
            r.append((a, _full))
        elif cfg["city"]:
            r.append((a, cfg["city"]))

    seen, out = set(), []
    for old, new in r:
        # `new` may legitimately be "" - removing a template suite number is a
        # real instruction, not a missing value. Only `old` must be truthy.
        if old and new is not None and old != new and old not in seen:
            seen.add(old); out.append((old, new))
    return sorted(out, key=lambda x: len(x[0]), reverse=True)


THEME_CSS = """
/* Practice palette */
:root {{
  --accent: {accent};
  --accent-dark: {accent_dk};
  --accent-soft: {soft};
  --accent-warm: {warm};
}}
a[class*="button"], .button, button[type="submit"], input[type="submit"],
[class*="btn"]:not([class*="text"]) {{
  background-color: {accent} !important;
  border-color: {accent} !important;
}}
a[class*="button"]:hover, .button:hover, [class*="btn"]:not([class*="text"]):hover {{
  background-color: {accent_dk} !important;
  border-color: {accent_dk} !important;
}}
[class*="section"][class*="dark"], footer[class*="footer"] {{
  background-color: {accent_dk} !important;
}}
[class*="tag"], [class*="badge"], [class*="eyebrow"] {{ color: {accent} !important; }}
::selection {{ background: {accent}; color: #fff; }}
"""

DISCLOSURE = (
    '<div style="background:#f4f4f6;color:#55565f;font:400 12px/1.6 system-ui,-apple-system,'
    'Segoe UI,sans-serif;padding:14px 20px;text-align:center;border-top:1px solid #e2e2e8">'
    'Concept proposal prepared for {practice} by Milin Dholiya. Not affiliated with, '
    'endorsed by, or an official site of {practice}. Imagery and any team profiles other '
    'than {doctor_note} are placeholder content for layout purposes.'
    '</div>'
)

NOINDEX = '<meta name="robots" content="noindex, nofollow">'


SMALL_SPAN = re.compile(
    r'(<span style="[^"]*font-size:\s*13px[^"]*uppercase[^"]*">)([^<]*)(</span>)', re.I)
MAP_Q = re.compile(r'(maps\.google\.com/maps\?q=)([^&"\']*)', re.I)


def fix_footer_strapline(txt, cfg):
    """The footer's small uppercase span is a strapline, not a second logo."""
    tag = (cfg["city"] or cfg["country"] or "").upper()
    if not tag:
        return txt
    return SMALL_SPAN.sub(lambda m: m.group(1) + tag + m.group(3), txt)


SHORTLINK_RE = re.compile(
    r'href="(https?://(?:maps\.app\.goo\.gl|goo\.gl/maps|g\.page)/[^"]*)"', re.I)
DIRS_RE = re.compile(r'href="(https?://[^"]*google\.[^"]*/maps/dir[^"]*)"', re.I)


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


def fix_maps(txt, cfg):
    """Point every embedded map at this practice, not the template's clinic."""
    import urllib.parse
    where = cfg.get("street") or ", ".join(
        x for x in (cfg["practice"], cfg["city"], cfg["country"]) if x)
    q = urllib.parse.quote(where)
    return MAP_Q.sub(lambda m: m.group(1) + q, txt)


BIO_RE = re.compile(r'(<p[^>]*class="[^"]*about-hero_para[^"]*"[^>]*>)(.*?)(</p>)', re.S | re.I)
BODY_RE = re.compile(r'(<p[^>]*class="[^"]*body-text-18px[^"]*"[^>]*>)(.*?)(</p>)', re.S | re.I)


def _specialty_clause(cfg):
    """The researched specialty as prose. Kept whole: cutting at the first
    semicolon turned a full list into the fragment 'general and cosmetic'."""
    s = (cfg.get("specialty") or "").strip().rstrip(".")
    if not s:
        return None
    s = s.replace(";", ",")
    if len(s) > 150:
        s = s[:147].rsplit(",", 1)[0]
    return s[0].lower() + s[1:] if not s[:2].isupper() else s


CRED_RE = re.compile(
    r'(<strong>\s*(?:DDS Degree|Degree|Certifications?|Education|Qualifications?|'
    r'Experience|License|Memberships?)\s*:?\s*</strong>)([^<]*)', re.I)


def scrub_credentials(txt, cfg):
    """No qualification, school or membership is asserted for a real dentist."""
    return CRED_RE.sub(lambda m: m.group(1) + " To be supplied by the practice.", txt)


def rewrite_doctor_bio(txt, cfg, is_lead):
    """Replace template biography with statements the research supports.

    Nothing here asserts a degree, a school, a year or an award. Every clause
    comes from business_name, city or specialty in the prospect record.
    """
    practice, city = cfg["practice"], cfg["city"]
    spec = _specialty_clause(cfg)

    who = cfg.get("_page_doctor") or (cfg["doctor"] if is_lead else None)
    if who:
        where = f" in {city}" if city else ""
        role = "the lead dentist" if is_lead else "a dentist"
        p1 = f"{who} is {role} at {practice}{where}."
        p2 = (f"The practice provides {spec}." if spec
              else f"{practice} provides general and cosmetic dental care.")
        p3 = "Full biography and credentials to be supplied by the practice."
    else:
        p1 = f"Team profile placeholder for {practice}."
        p2 = (f"{practice} provides {spec}." if spec
              else f"{practice} provides general and cosmetic dental care.")
        p3 = "Names, photographs and biographies to be supplied by the practice."

    txt = BIO_RE.sub(lambda m: m.group(1) + p1 + m.group(3), txt, count=1)
    seen = [0]

    def body(m):
        seen[0] += 1
        return m.group(1) + (p2 if seen[0] == 1 else p3) + m.group(3) if seen[0] <= 2 else m.group(0)
    return BODY_RE.sub(body, txt)


def process_html(txt, cfg, reps):
    g, v, code = split_reps(reps)
    txt = replace_visible(txt, g, v, code)
    txt = repair_svg_paths(txt)
    if cfg.get("_page_is_doctor"):
        txt = rewrite_doctor_bio(txt, cfg, cfg.get("_page_is_lead", False))
        txt = scrub_credentials(txt, cfg)
    txt = fix_footer_strapline(txt, cfg)
    txt = fix_maps(txt, cfg)
    txt = fix_directions(txt, cfg)

    if "noindex" not in txt:
        txt = re.sub(r"(<head[^>]*>)", r"\1\n" + NOINDEX, txt, count=1, flags=re.I)

    if cfg.get("_meta_title") and re.search(r"<title>.*?</title>", txt, re.S | re.I):
        txt = re.sub(r"<title>.*?</title>",
                     "<title>" + cfg["_meta_title"] + "</title>", txt, count=1, flags=re.S | re.I)
    if cfg.get("_meta_desc"):
        txt = re.sub(r'(<meta\s+name=["\']description["\']\s+content=)["\'].*?["\']',
                     r'\1"' + cfg["_meta_desc"].replace('"', "&quot;") + '"',
                     txt, count=1, flags=re.I | re.S)

    if "Concept proposal prepared for" not in txt and "</body>" in txt:
        doc = cfg["doctor"] or "the named lead dentist"
        d = DISCLOSURE.format(practice=cfg["practice"], doctor_note=doc)
        txt = txt.replace("</body>", d + "\n</body>", 1)
    return txt


def build_one(cfg, tmap, go):
    slug = cfg["slug"]
    src = os.path.join(BASE, cfg["template"])
    dst = os.path.join(OUT_ROOT, slug)

    cpath = os.path.join(COPY, slug + ".json")
    copy = json.load(io.open(cpath, encoding="utf-8")) if os.path.exists(cpath) else None
    if copy:
        cfg["_meta_title"] = copy.get("meta_title")
        cfg["_meta_desc"] = copy.get("meta_desc")

    # Which of the template's dentists becomes the client's named lead.
    _docs = (tmap.get(cfg["template"], {}).get("doctor_names") or [])
    if _docs and cfg["doctor"]:
        _d = _docs[0]
        cfg["_lead_tmpl"] = _d["name"] if isinstance(_d, dict) else _d
    else:
        cfg["_lead_tmpl"] = None

    _tmpl_names = []
    for _d in (tmap.get(cfg["template"], {}).get("doctor_names") or []):
        _tmpl_names.append(_d["name"] if isinstance(_d, dict) else _d)
    _real = list(cfg.get("real_doctors") or [])
    if cfg["doctor"] and not any(cfg["doctor"] in x for x in _real):
        _real.insert(0, cfg["doctor"])
    cfg["_doc_map"] = {t: _real[i] for i, t in enumerate(_tmpl_names) if i < len(_real)}

    reps = build_replacements(cfg, tmap, copy)
    if not go:
        return {"slug": slug, "replacements": len(reps), "copy": bool(copy), "built": False}

    os.makedirs(OUT_ROOT, exist_ok=True)
    clear_dir(dst)
    shutil.copytree(src, dst, ignore=ignore, dirs_exist_ok=True)

    changed = 0
    for dp, dn, fn in os.walk(dst):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        for f in fn:
            if not f.lower().endswith(TEXT_EXT):
                continue
            p = os.path.join(dp, f)
            try:
                txt = io.open(p, encoding="utf-8", errors="ignore").read()
            except Exception:
                continue
            if f.endswith(".html"):
                cfg["_page_is_doctor"] = f.startswith("doctor-")
                tmpl_lead = cfg.get("_lead_tmpl") or ""
                cfg["_page_is_lead"] = bool(tmpl_lead) and tmpl_lead in txt
                cfg["_page_doctor"] = None
                for _t, _r in (cfg.get("_doc_map") or {}).items():
                    if _t and _t in txt:
                        cfg["_page_doctor"] = _r
                        break
                new = process_html(txt, cfg, reps)
            elif f.endswith((".css", ".js")):
                new = functools_reduce(txt, split_reps(reps)[2])
            else:
                new = functools_reduce(txt, reps)
            if new != txt:
                io.open(p, "w", encoding="utf-8").write(new)
                changed += 1

    # Palette override, last so it wins.
    css_dir = os.path.join(dst, "assets", "css")
    if os.path.isdir(css_dir):
        theme = os.path.join(css_dir, "practice-theme.css")
        io.open(theme, "w", encoding="utf-8").write(THEME_CSS.format(**cfg["colours"]))
        for dp, dn, fn in os.walk(dst):
            dn[:] = [d for d in dn if d not in SKIP_DIRS]
            for f in fn:
                if not f.endswith(".html"):
                    continue
                p = os.path.join(dp, f)
                txt = io.open(p, encoding="utf-8", errors="ignore").read()
                if "practice-theme.css" in txt:
                    continue
                rel = os.path.relpath(css_dir, dp).replace("\\", "/")
                link = '<link rel="stylesheet" href="%s/practice-theme.css">' % rel
                txt = txt.replace("</head>", link + "\n</head>", 1)
                io.open(p, "w", encoding="utf-8").write(txt)

    nhero = ensure_hero(dst, cfg, cfg["rank"])
    nport = neutralise_portraits(dst, cfg)
    nlogo = write_wordmarks(dst, cfg)
    npruned, freed = prune_unused(dst)
    nimg, saved = optimise_images(dst)

    io.open(os.path.join(dst, "README.md"), "w", encoding="utf-8").write(
        "# %s\n\nConcept website proposal.\n\n"
        "Prepared for %s in %s.\n\n"
        "This is an unaffiliated design proposal, not an official site of the practice. "
        "Every page is set to noindex. Photography and any team profiles other than %s "
        "are placeholder content shown for layout only.\n\n"
        "Contact: Milin Dholiya, dholiyamilin@gmail.com\n"
        % (cfg["practice"], cfg["practice"], cfg["city"] or cfg["country"],
           cfg["doctor"] or "the lead dentist"))

    size = sum(os.path.getsize(os.path.join(dp, f))
               for dp, dn, fn in os.walk(dst) if not any(s in dp for s in SKIP_DIRS)
               for f in fn)
    return {"slug": slug, "replacements": len(reps), "copy": bool(copy),
            "files_changed": changed, "hero": nhero,
            "hero_src": "client" if cfg.get("_hero_from_client") else "stock",
            "portraits": nport, "faces": cfg.get("_people_from_client", 0),
            "logos": nlogo, "pruned": npruned,
            "saved_mb": round((saved + freed) / 1e6, 1), "imgs": nimg,
            "size_mb": round(size / 1e6, 1), "built": True}


def functools_reduce(txt, reps):
    for old, new in reps:
        txt = txt.replace(old, new)
    return txt


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--go", action="store_true")
    ap.add_argument("--only")
    a = ap.parse_args()

    tmap = load_token_map()
    if not tmap:
        print("token_map.json missing - run the mapping agent first"); sys.exit(1)

    rows = load()
    if a.only:
        rows = [r for r in rows if r["slug"] == a.only]

    for cfg in rows:
        res = build_one(cfg, tmap, a.go)
        print(" ".join(f"{k}={v}" for k, v in res.items()))
    print("\n%s %d demo(s)" % ("built" if a.go else "planned", len(rows)))
