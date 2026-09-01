"""The doctor pages were the worst thing left in the build.

Each one carried the template's original biography with the client's dentist's
name pasted over it. So the page for a real, named, licensed dentist claimed a
Doctor of Dental Surgery from the University of Leipzig and finished by
locating the practice in Limassol, Cyprus. Inventing a qualification for a
named clinician is the one mistake that could actually cause them a problem,
quite apart from killing the pitch on sight.

Bios are now built only from fields verified in the research file: the
practice name, the city, and the specialty string. The lead dentist's page
gets their own headshot where the scrape found one. Other profiles say plainly
that they are placeholders rather than pretending to be people.
"""
import io, ast

# ---------- config: catch the Cyprus copy ----------
D = "_demo/demo_config.py"
d = io.open(D, encoding="utf-8").read()
d = d.replace('''    "+357 70005758", "70005758", "Dr. Neo Boutique", "PANNU DENTAL GROUP",
]''',
'''    "+357 70005758", "70005758", "Dr. Neo Boutique", "PANNU DENTAL GROUP",
    "Limassol", "Cyprus", "University of Leipzig", "Nikodimou", "Neofytos",
]''')
io.open(D, "w", encoding="utf-8").write(d)
ast.parse(d)

# ---------- builder ----------
P = "_demo/build_demos.py"
c = io.open(P, encoding="utf-8").read()

c = c.replace('''def process_html(txt, cfg, reps):''',
'''BIO_RE = re.compile(r'(<p[^>]*class="[^"]*about-hero_para[^"]*"[^>]*>)(.*?)(</p>)', re.S | re.I)
BODY_RE = re.compile(r'(<p[^>]*class="[^"]*body-text-18px[^"]*"[^>]*>)(.*?)(</p>)', re.S | re.I)


def _specialty_clause(cfg):
    """First clause of the researched specialty, lowercased to read as prose."""
    s = (cfg.get("specialty") or "").split(";")[0].strip().rstrip(".")
    if not s:
        return None
    return s[0].lower() + s[1:] if s[:2].isupper() is False else s.lower()


def rewrite_doctor_bio(txt, cfg, is_lead):
    """Replace template biography with statements the research supports.

    Nothing here asserts a degree, a school, a year or an award. Every clause
    comes from business_name, city or specialty in the prospect record.
    """
    practice, city = cfg["practice"], cfg["city"]
    spec = _specialty_clause(cfg)

    if is_lead and cfg["doctor"]:
        where = f" in {city}" if city else ""
        p1 = f"{cfg['doctor']} is the lead dentist at {practice}{where}."
        p2 = (f"The practice provides {spec}." if spec
              else f"{practice} provides general and cosmetic dental care.")
        p3 = ("Full biography and credentials to be supplied by the practice.")
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


def process_html(txt, cfg, reps):''', 1)

# Hook it in, only on doctor pages.
c = c.replace('''    txt = fix_footer_strapline(txt, cfg)''',
'''    if cfg.get("_page_is_doctor"):
        txt = rewrite_doctor_bio(txt, cfg, cfg.get("_page_is_lead", False))
    txt = fix_footer_strapline(txt, cfg)''')

# Mark doctor pages, and which one is the lead, as we walk the tree.
c = c.replace('''            if f.endswith(".html"):
                new = process_html(txt, cfg, reps)''',
'''            if f.endswith(".html"):
                cfg["_page_is_doctor"] = f.startswith("doctor-")
                lead = cfg["doctor"] or ""
                bare = re.sub(r"^(Dr\\.?|Doctor)\\s+", "", lead).strip()
                cfg["_page_is_lead"] = bool(bare) and bare.split()[-1].lower() in f.lower()
                new = process_html(txt, cfg, reps)''')

io.open(P, "w", encoding="utf-8").write(c)
ast.parse(c)
print("patched, parse OK")
for probe, src, label in [("rewrite_doctor_bio", c, "bio rewriter"),
                          ("_page_is_lead", c, "lead page detection"),
                          ('"Limassol", "Cyprus"', d, "Cyprus in scanned tokens")]:
    print(("  ok    " if probe in src else "  MISS  ") + label)
