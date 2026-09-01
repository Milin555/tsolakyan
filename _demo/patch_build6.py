"""Three prospects have no phone number anywhere in the research, so the build
left the template's own number in place. That number belongs to a real third
party, which is worse than having no number at all.

Inventing one is not an option. Where no number is known, the contact slot
falls back to that practice's email and the tel: link becomes mailto:, which
is honest and still works.

Also pulls the stray Cyprus number the templates all carry into the scanned
token list, since nothing was checking for it.
"""
import io, ast

# ---------- builder ----------
P = "_demo/build_demos.py"
c = io.open(P, encoding="utf-8").read()

c = c.replace('''    if cfg["phone"]:
        for ph in (t.get("phones", []) or []) + ["310-888-1850"]:
            r.append((ph, cfg["phone"]))''',
'''    # Template numbers belong to real third parties and must always go.
    tmpl_phones = (t.get("phones", []) or []) + [
        "310-888-1850", "tel:310-888-1850",
        "+357 70005758", "tel:+357 70005758", "tel:+35770005758", "+35770005758",
    ]
    fallback = cfg["email"] or ("hello@" + own)
    for ph in tmpl_phones:
        if ph.startswith("tel:"):
            r.append((ph, ("tel:" + re.sub(r"[^\\d+]", "", cfg["phone"]))
                      if cfg["phone"] else "mailto:" + fallback))
        else:
            r.append((ph, cfg["phone"] or fallback))''')

io.open(P, "w", encoding="utf-8").write(c)
ast.parse(c)

# ---------- config ----------
D = "_demo/demo_config.py"
d = io.open(D, encoding="utf-8").read()
d = d.replace('''    "john@example.com", "Smilifye", "smilifye",
]''',
'''    "john@example.com", "Smilifye", "smilifye",
    "+357 70005758", "70005758", "Dr. Neo Boutique", "PANNU DENTAL GROUP",
]''')
io.open(D, "w", encoding="utf-8").write(d)
ast.parse(d)

print("patched, parse OK")
for probe, src in [("tmpl_phones", c), ("mailto:", c), ("70005758", d), ("PANNU", d)]:
    print(("  ok    " if probe in src else "  MISS  ") + probe)
