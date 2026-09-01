"""Lura only, and the client's own photographs.

The template rotation was a mistake. Four different layouts meant four sets of
quirks to chase, and three of them carried other practices' real people. Every
demo is now the Lura build in Lura's own teal.

Imagery now prefers what the client already has:
  hero      their site's hero or clinic interior  -> else Lura's stock
  portrait  their own dentist's headshot          -> else Lura's AI staff photos
Never another practice's real face, in either branch.

The map takes the street address from their schema.org markup when the scrape
found one, so it lands on the building rather than the town.
"""
import io, ast

# ---------- config: one template, one palette ----------
D = "_demo/demo_config.py"
d = io.open(D, encoding="utf-8").read()

d = d.replace('''TEMPLATES = ["Lura Dentist", "Gary Solnit Dentist",
             "Modern Smile Center Dentist", "Ritter Ramsey Dentist"]''',
'''# One template. The rotation added variety nobody asked for and three sets of
# other practices' photographs along with it.
TEMPLATES = ["Lura Dentist"]''')

d = d.replace('''        tpl = TEMPLATES[i % len(TEMPLATES)]
        theme = THEME_KEYS[(i // len(TEMPLATES)) % len(THEME_KEYS)]
        assert (tpl, theme) not in used, f"collision at rank {p['rank']}"
        used.add((tpl, theme))''',
'''        tpl = TEMPLATES[0]
        theme = THEME_KEYS[0]''')

# Street address from the scrape, for the map.
d = d.replace('''        dom = domain_of(p.get("website"))''',
'''        dom = domain_of(p.get("website"))
        assets = client_assets(slugify(p["business_name"]))''')

d = d.replace('''            "colours": THEMES[theme],
        })''',
'''            "colours": THEMES[theme],
            "assets": assets,
            "street": assets.get("address"),
        })''')

d = d.replace('''def slugify(s, limit=40):''',
'''def client_assets(slug):
    """What the scrape pulled off this practice's own site, if anything."""
    p = os.path.join(BASE, "_demo", "client_assets", slug, "manifest.json")
    if not os.path.exists(p):
        return {"heroes": [], "people": [], "address": None}
    try:
        m = json.load(io.open(p, encoding="utf-8"))
        return {"heroes": m.get("heroes") or [], "people": m.get("people") or [],
                "address": m.get("address")}
    except Exception:
        return {"heroes": [], "people": [], "address": None}


def slugify(s, limit=40):''')

io.open(D, "w", encoding="utf-8").write(d)
ast.parse(d)

# ---------- builder: prefer client imagery ----------
P = "_demo/build_demos.py"
c = io.open(P, encoding="utf-8").read()

c = c.replace('''CLIENT_DIR_PLACEHOLDER''', '')  # no-op guard

c = c.replace('''def ensure_hero(dst, cfg, rank):
    """Guarantee a hero photograph, and make sure it is a generic one."""
    img_dir = os.path.join(dst, "assets", "img")
    os.makedirs(img_dir, exist_ok=True)
    pick = HERO_POOL[rank % len(HERO_POOL)]
    src = os.path.join(HERO_SRC_DIR, pick)
    if not os.path.exists(src):
        return None''',
'''CLIENT_ROOT = os.path.join(BASE, "_demo", "client_assets")


def client_file(cfg, kind, i=0):
    """Path to a scraped asset, or None. kind is 'heroes' or 'people'."""
    items = (cfg.get("assets") or {}).get(kind) or []
    if i >= len(items):
        return None
    p = os.path.join(CLIENT_ROOT, cfg["slug"], items[i]["file"])
    return p if os.path.exists(p) else None


def ensure_hero(dst, cfg, rank):
    """Their own hero if the scrape found one, otherwise the Lura sample."""
    img_dir = os.path.join(dst, "assets", "img")
    os.makedirs(img_dir, exist_ok=True)

    # Prefer a clinic interior over an abstract shot: index 1 is usually the
    # room, index 0 is often a brand image. Fall back through both, then stock.
    src = client_file(cfg, "heroes", 1) or client_file(cfg, "heroes", 0)
    cfg["_hero_from_client"] = bool(src)
    if not src:
        src = os.path.join(HERO_SRC_DIR, HERO_POOL[rank % len(HERO_POOL)])
    if not os.path.exists(src):
        return None''')

c = c.replace('''def neutralise_portraits(dst, cfg):
    """Swap named practitioners' headshots for generic clinical portraits."""''',
'''def neutralise_portraits(dst, cfg):
    """Their own dentist where we have them, generic staff photos otherwise.

    Either way the template's own named practitioners are gone.
    """''')

c = c.replace('''        pick = TEAM_POOL[(cfg["rank"] + i) % len(TEAM_POOL)]
        src = os.path.join(HERO_SRC_DIR, pick)
        if not os.path.exists(src):
            continue''',
'''        src = client_file(cfg, "people", i)
        if src:
            cfg["_people_from_client"] = cfg.get("_people_from_client", 0) + 1
        else:
            src = os.path.join(HERO_SRC_DIR, TEAM_POOL[(cfg["rank"] + i) % len(TEAM_POOL)])
        if not os.path.exists(src):
            continue''')

# Map on the real street address when we have it.
c = c.replace('''    where = ", ".join(x for x in (cfg["practice"], cfg["city"], cfg["country"]) if x)''',
'''    where = cfg.get("street") or ", ".join(
        x for x in (cfg["practice"], cfg["city"], cfg["country"]) if x)''')

c = c.replace('''            "files_changed": changed, "hero": nhero, "portraits": nport,''',
'''            "files_changed": changed, "hero": nhero,
            "hero_src": "client" if cfg.get("_hero_from_client") else "stock",
            "portraits": nport, "faces": cfg.get("_people_from_client", 0),''')

io.open(P, "w", encoding="utf-8").write(c)
ast.parse(c)

print("patched, parse OK")
for probe, src, label in [
        ('TEMPLATES = ["Lura Dentist"]', d, "single template"),
        ("client_assets", d, "config reads manifest"),
        ("client_file", c, "builder reads client assets"),
        ('cfg.get("street")', c, "map uses street address")]:
    print(("  ok    " if probe in src else "  MISS  ") + label)
