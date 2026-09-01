"""Four corrections to the doctor pages.

1. Lead page was detected from the filename, but the filenames are the
   template's own dentists. The page that now displays the client's dentist is
   whichever one held the template's lead, so detect on content.
2. The specialty clause was cut at the first semicolon, so "General and
   cosmetic; digital dentistry, guided implant surgery" became the fragment
   "general and cosmetic".
3. Limassol and Cyprus survive in every meta, og and twitter description on
   the doctor pages, none of which the copy pass touches.
4. A credentials panel asserts a DDS from the University of Leipzig and
   membership of the Cyprus Dental Association, attached to a real named
   dentist. Those become an explicit to-be-supplied line.
"""
import io, ast

P = "_demo/build_demos.py"
c = io.open(P, encoding="utf-8").read()

# 1 - detect the lead page by the template doctor it used to carry
c = c.replace('''                cfg["_page_is_doctor"] = f.startswith("doctor-")
                lead = cfg["doctor"] or ""
                bare = re.sub(r"^(Dr\\.?|Doctor)\\s+", "", lead).strip()
                cfg["_page_is_lead"] = bool(bare) and bare.split()[-1].lower() in f.lower()''',
'''                cfg["_page_is_doctor"] = f.startswith("doctor-")
                tmpl_lead = cfg.get("_lead_tmpl") or ""
                cfg["_page_is_lead"] = bool(tmpl_lead) and tmpl_lead in txt''')

c = c.replace('''    reps = build_replacements(cfg, tmap, copy)''',
'''    # Which of the template's dentists becomes the client's named lead.
    _docs = (tmap.get(cfg["template"], {}).get("doctor_names") or [])
    if _docs and cfg["doctor"]:
        _d = _docs[0]
        cfg["_lead_tmpl"] = _d["name"] if isinstance(_d, dict) else _d
    else:
        cfg["_lead_tmpl"] = None

    reps = build_replacements(cfg, tmap, copy)''')

# 2 - keep the whole specialty, just tidy the punctuation
c = c.replace('''def _specialty_clause(cfg):
    """First clause of the researched specialty, lowercased to read as prose."""
    s = (cfg.get("specialty") or "").split(";")[0].strip().rstrip(".")
    if not s:
        return None
    return s[0].lower() + s[1:] if s[:2].isupper() is False else s.lower()''',
'''def _specialty_clause(cfg):
    """The researched specialty as prose. Kept whole: cutting at the first
    semicolon turned a full list into the fragment 'general and cosmetic'."""
    s = (cfg.get("specialty") or "").strip().rstrip(".")
    if not s:
        return None
    s = s.replace(";", ",")
    if len(s) > 150:
        s = s[:147].rsplit(",", 1)[0]
    return s[0].lower() + s[1:] if not s[:2].isupper() else s''')

# 3 and 4 - scrub the Cyprus geography and the invented credentials
c = c.replace('''def rewrite_doctor_bio(txt, cfg, is_lead):''',
'''CRED_RE = re.compile(
    r'(<strong>\\s*(?:DDS Degree|Degree|Certifications?|Education|Qualifications?|'
    r'Experience|License|Memberships?)\\s*:?\\s*</strong>)([^<]*)', re.I)


def scrub_credentials(txt, cfg):
    """No qualification, school or membership is asserted for a real dentist."""
    return CRED_RE.sub(lambda m: m.group(1) + " To be supplied by the practice.", txt)


def rewrite_doctor_bio(txt, cfg, is_lead):''')

c = c.replace('''    if cfg.get("_page_is_doctor"):
        txt = rewrite_doctor_bio(txt, cfg, cfg.get("_page_is_lead", False))''',
'''    if cfg.get("_page_is_doctor"):
        txt = rewrite_doctor_bio(txt, cfg, cfg.get("_page_is_lead", False))
        txt = scrub_credentials(txt, cfg)''')

# Geography replacements belong in the global tier: they appear inside meta
# content attributes, which the brand tier deliberately does not touch.
c = c.replace('''    # Brands hidden inside JS confirmation receipts - invisible until submit.''',
'''    # The template's own geography, which survives in every meta description.
    _city = cfg["city"] or cfg["country"] or ""
    if _city:
        r.append(("Limassol, Cyprus", _city))
        r.append(("Limassol", _city))
    if cfg["country"]:
        r.append(("Cyprus Dental Association", cfg["country"] + " Dental Association"))
        r.append(("Cyprus", cfg["country"]))
    r.append(("University of Leipzig, Germany", "To be supplied by the practice"))
    r.append(("University of Leipzig", "To be supplied by the practice"))

    # Brands hidden inside JS confirmation receipts - invisible until submit.''')

io.open(P, "w", encoding="utf-8").write(c)
ast.parse(c)
print("patched, parses OK")
for probe, label in [("_lead_tmpl", "lead detected by content"),
                     ("scrub_credentials", "credentials scrubbed"),
                     ('"Limassol, Cyprus"', "geography replaced"),
                     ('s.replace(";", ",")', "specialty kept whole")]:
    print(("  ok    " if probe in c else "  MISS  ") + label)
