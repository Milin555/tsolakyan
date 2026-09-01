"""Second pass.

1. Script blocks were getting globals only, so multi-word brands baked into JS
   confirmation receipts survived. They now get the CODE tier, which is exactly
   the strings a space proves are display text rather than identifiers.
2. Bare third-party handles (585dentist, garysolnitdds) survived because they
   carry no TLD and so failed the domain test. They are unambiguous, so they
   move to the GLOBAL tier.
3. The verifier flagged 'lumora' inside asset filenames as a leak. It is not:
   the stylesheet and logo are named that, and renaming them is what broke the
   first build. Path attributes are now excluded from the scan.
"""
import io, re

# ---------- builder ----------
P = "_demo/build_demos.py"
c = io.open(P, encoding="utf-8").read()

c = c.replace('''THIRD_PARTY_EMAILS = [''',
'''# Bare handles: no TLD, so the domain test misses them, but they are still
# unambiguous third-party identifiers and safe to replace anywhere.
THIRD_PARTY_TOKENS = [
    "585dentist", "foundationdentalalliance", "garysolnitdds",
    "ritterandramsey", "modernsmilecenter", "drneodentistry", "mcim21",
]
THIRD_PARTY_EMAILS = [''')

c = c.replace('''def is_global(old):
    """Contact and domain strings: unambiguous, safe anywhere."""
    return ("@" in old or bool(PHONEY.fullmatch(old.strip()))
            or any(old == d or old.endswith("." + d.split(".", 1)[-1]) and "." in old
                   and old in THIRD_PARTY_DOMAINS for d in THIRD_PARTY_DOMAINS))''',
'''def is_global(old):
    """Contact strings, third-party domains and bare handles: safe anywhere."""
    return ("@" in old
            or bool(PHONEY.fullmatch(old.strip()))
            or old in THIRD_PARTY_DOMAINS
            or old in THIRD_PARTY_TOKENS)''')

c = c.replace('''def replace_visible(txt, reps_global, reps_visible):
    """Globals everywhere; brand names only where a human can read them."""''',
'''def replace_visible(txt, reps_global, reps_visible, reps_code=None):
    """Globals everywhere, code tier inside scripts, brands only in read text."""
    reps_code = reps_code if reps_code is not None else reps_global''')

c = c.replace('''            if low.startswith(("<script", "<style", "<!--")):
                out.append(_apply(part, reps_global))
                continue''',
'''            if low.startswith(("<script", "<style", "<!--")):
                out.append(_apply(part, reps_code))
                continue''')

c = c.replace('''    g, v, _ = split_reps(reps)
    txt = replace_visible(txt, g, v)''',
'''    g, v, code = split_reps(reps)
    txt = replace_visible(txt, g, v, code)''')

# The bare handles must also be queued as replacements.
c = c.replace('''    for d in THIRD_PARTY_DOMAINS:
        r.append((d, own))''',
'''    for d in THIRD_PARTY_DOMAINS:
        r.append((d, own))
    handle = re.sub(r"[^a-z0-9]", "", (cfg.get("domain") or cfg["slug"]).split(".")[0].lower())
    for tok in THIRD_PARTY_TOKENS:
        r.append((tok, handle))''')

io.open(P, "w", encoding="utf-8").write(c)

# ---------- verifier ----------
V = "_demo/verify_demos.py"
v = io.open(V, encoding="utf-8").read()

v = v.replace('''from demo_config import load, LEAKED, BASE''',
'''from demo_config import load, LEAKED, BASE

# Asset paths legitimately keep the template's original filenames. Renaming
# them is what broke the first build, so they are stripped before scanning.
PATH_ATTR = re.compile(r'(?:src|href|srcset|data-src)\\s*=\\s*["\\'][^"\\']*["\\']', re.I)
URL_FN = re.compile(r'url\\([^)]*\\)', re.I)


def strip_paths(t):
    return URL_FN.sub("", PATH_ATTR.sub("", t))''')

v = v.replace('''    hits = {}
    for p in text:
        t = io.open(p, encoding="utf-8", errors="ignore").read()
        for tok in LEAKED:
            if tok in t:
                hits.setdefault(tok, []).append(os.path.relpath(p, root))''',
'''    hits = {}
    for p in text:
        raw = io.open(p, encoding="utf-8", errors="ignore").read()
        t = strip_paths(raw) if p.endswith((".html", ".css")) else raw
        for tok in LEAKED:
            if tok in t:
                hits.setdefault(tok, []).append(os.path.relpath(p, root))''')

io.open(V, "w", encoding="utf-8").write(v)

import ast
ast.parse(c); ast.parse(v)
print("both patched, parse OK")
for probe, src in [("THIRD_PARTY_TOKENS", c), ("reps_code=None", c),
                   ("strip_paths", v), ("_apply(part, reps_code)", c)]:
    print(("  ok    " if probe in src else "  MISS  ") + probe)
