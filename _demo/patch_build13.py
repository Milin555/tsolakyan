"""Real location and real people, everywhere.

Three template addresses still sit in the demos, split across tags so the
whole-string replacement never matched: 123 Smile Avenue in New York, 456
Bright Dental Blvd in Los Angeles, 9675 Brighton Way in Beverly Hills. They
are replaced fragment by fragment with what the practice actually publishes.

The team pages also keep the template's four invented dentists. Where the
scrape found the real ones, they go in, and each profile says only what the
research supports.
"""
import io, ast

# ---------- config: load the scraped details ----------
D = "_demo/demo_config.py"
d = io.open(D, encoding="utf-8").read()

d = d.replace('''def client_assets(slug):''',
'''def client_details(slug):
    """Address, phone and dentist names read off the practice's own site."""
    p = os.path.join(BASE, "_demo", "client_assets", slug, "details.json")
    if not os.path.exists(p):
        return {"address": None, "phone": None, "doctors": []}
    try:
        m = json.load(io.open(p, encoding="utf-8"))
        return {"address": m.get("address"), "phone": m.get("phone"),
                "doctors": m.get("doctors") or []}
    except Exception:
        return {"address": None, "phone": None, "doctors": []}


def client_assets(slug):''')

d = d.replace('''        assets = client_assets(slugify(p["business_name"]))''',
'''        _slug = slugify(p["business_name"])
        assets = client_assets(_slug)
        details = client_details(_slug)''')

d = d.replace('''            "phone": phone_from(p.get("best_outreach_channel"), p.get("why_worth_contacting")),''',
'''            # Their published number beats one lifted from a research note.
            "phone": details["phone"] or phone_from(
                p.get("best_outreach_channel"), p.get("why_worth_contacting")),''')

d = d.replace('''            "assets": assets,
            "street": assets.get("address"),''',
'''            "assets": assets,
            "street": details["address"] or assets.get("address"),
            "real_doctors": details["doctors"],''')

io.open(D, "w", encoding="utf-8").write(d)
ast.parse(d)

# ---------- builder ----------
P = "_demo/build_demos.py"
c = io.open(P, encoding="utf-8").read()

c = c.replace('''    # The template's own geography, which survives in every meta description.''',
'''    # Template addresses, fragment by fragment. They are split across tags in
    # the markup, so replacing the assembled string never matched anything.
    street, locality = split_address(cfg)
    for frag in ("9675 Brighton Way, Suite 330", "9675 Brighton Way",
                 "123 Smile Avenue, Suite 200", "123 Smile Avenue",
                 "456 Bright Dental Blvd, Floor 3", "456 Bright Dental Blvd",
                 "45 King's Road", "45 King\\u2019s Road"):
        r.append((frag, street))
    for frag in ("Beverly Hills, CA 90210", "Beverly Hills, California",
                 "Beverly Hills, CA", "Beverly Hills",
                 "New York, NY 10001", "New York, NY", "New York",
                 "Los Angeles, CA 90001", "Los Angeles, CA", "Los Angeles",
                 "Chelsea, SW3 5UZ", "SW3 5UZ", "Chelsea"):
        r.append((frag, locality))
    for frag in ("Suite 330", "Suite 200", "Floor 3"):
        r.append((frag, ""))

    # The template's dentists, mapped onto the ones who actually work there.
    for tmpl, real in (cfg.get("_doc_map") or {}).items():
        r.append((tmpl, re.sub(r"^(Dr\\.?|Doctor)\\s+", "", real).strip()))
        r.append(("Dr. " + tmpl, real))

    # The template's own geography, which survives in every meta description.''')

c = c.replace('''def build_replacements(cfg, tmap, copy):''',
'''def split_address(cfg):
    """(street line, locality) from the scraped address, or sensible stand-ins."""
    full = (cfg.get("street") or "").strip()
    city = cfg.get("city") or cfg.get("country") or ""
    if not full:
        return city, city
    m = re.match(r"^(.*?),\\s*([^,]*(?:\\d{5}|\\d{4}|[A-Z]{1,2}\\d).*)$", full)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    parts = [p.strip() for p in full.split(",") if p.strip()]
    if len(parts) >= 2:
        return ", ".join(parts[:-1]), parts[-1]
    return full, city


def build_replacements(cfg, tmap, copy):''', 1)

# Map template dentists onto real ones before replacements are built.
c = c.replace('''    reps = build_replacements(cfg, tmap, copy)''',
'''    _tmpl_names = []
    for _d in (tmap.get(cfg["template"], {}).get("doctor_names") or []):
        _tmpl_names.append(_d["name"] if isinstance(_d, dict) else _d)
    _real = list(cfg.get("real_doctors") or [])
    if cfg["doctor"] and not any(cfg["doctor"] in x for x in _real):
        _real.insert(0, cfg["doctor"])
    cfg["_doc_map"] = {t: _real[i] for i, t in enumerate(_tmpl_names) if i < len(_real)}

    reps = build_replacements(cfg, tmap, copy)''')

# Each doctor page states only what we can support, under the right name.
c = c.replace('''                cfg["_page_is_doctor"] = f.startswith("doctor-")
                tmpl_lead = cfg.get("_lead_tmpl") or ""
                cfg["_page_is_lead"] = bool(tmpl_lead) and tmpl_lead in txt''',
'''                cfg["_page_is_doctor"] = f.startswith("doctor-")
                tmpl_lead = cfg.get("_lead_tmpl") or ""
                cfg["_page_is_lead"] = bool(tmpl_lead) and tmpl_lead in txt
                cfg["_page_doctor"] = None
                for _t, _r in (cfg.get("_doc_map") or {}).items():
                    if _t and _t in txt:
                        cfg["_page_doctor"] = _r
                        break''')

c = c.replace('''    if is_lead and cfg["doctor"]:
        where = f" in {city}" if city else ""
        p1 = f"{cfg['doctor']} is the lead dentist at {practice}{where}."''',
'''    who = cfg.get("_page_doctor") or (cfg["doctor"] if is_lead else None)
    if who:
        where = f" in {city}" if city else ""
        role = "the lead dentist" if is_lead else "a dentist"
        p1 = f"{who} is {role} at {practice}{where}."''')

c = c.replace('''        p3 = ("Full biography and credentials to be supplied by the practice.")''',
'''        p3 = "Full biography and credentials to be supplied by the practice."''')

io.open(P, "w", encoding="utf-8").write(c)
ast.parse(c)

print("patched, parse OK")
for probe, src, label in [("client_details", d, "config reads details.json"),
                          ("split_address", c, "address splitter"),
                          ("_doc_map", c, "template dentists mapped to real"),
                          ("_page_doctor", c, "per-page dentist name")]:
    print(("  ok    " if probe in src else "  MISS  ") + label)
