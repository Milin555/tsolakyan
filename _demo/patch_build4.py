"""Last two build fixes.

1. lumoraLead() is a leftover function name in an onsubmit attribute and its
   definition. Harmless to a visitor but it is the previous brand sitting in
   the source of a page we are asking a dentist to inspect. Renaming both
   occurrences together is safe because the pair is self-contained.

2. Every template ships two malformed SVG path attributes, where a '(' sits
   where a separator belongs. Parentheses are not legal in path data, so the
   browser rejects the path and logs an error. Pre-existing upstream, but it
   surfaces in the console of a site we are pitching, so it gets repaired.
"""
import io, ast

P = "_demo/build_demos.py"
c = io.open(P, encoding="utf-8").read()

c = c.replace('''THIRD_PARTY_TOKENS = [
    "585dentist", "foundationdentalalliance", "garysolnitdds",
    "ritterandramsey", "modernsmilecenter", "drneodentistry", "mcim21",
]''',
'''THIRD_PARTY_TOKENS = [
    "585dentist", "foundationdentalalliance", "garysolnitdds",
    "ritterandramsey", "modernsmilecenter", "drneodentistry", "mcim21",
]

# Identifier pairs safe to rename wholesale: the definition and every call site
# live in the same files, and the name carries a previous brand.
IDENT_RENAMES = [("lumoraLead", "submitLead")]

# SVG path data admits no parentheses. Two attributes per template carry one,
# so the browser rejects the path and logs an error.
BAD_PATH = re.compile(r'(\\sd=")([^"]*[()][^"]*)(")')


def repair_svg_paths(txt):
    def fix(m):
        return m.group(1) + m.group(2).replace("(", " ").replace(")", " ") + m.group(3)
    return BAD_PATH.sub(fix, txt)''')

c = c.replace('''    handle = re.sub(r"[^a-z0-9]", "", (cfg.get("domain") or cfg["slug"]).split(".")[0].lower())''',
'''    for old, new in IDENT_RENAMES:
        r.append((old, new))
    handle = re.sub(r"[^a-z0-9]", "", (cfg.get("domain") or cfg["slug"]).split(".")[0].lower())''')

# Identifier renames must reach onsubmit="..." and script bodies, so treat them
# as global rather than as brand text.
c = c.replace('''            or old in THIRD_PARTY_TOKENS)''',
'''            or old in THIRD_PARTY_TOKENS
            or any(old == a for a, _ in IDENT_RENAMES))''')

c = c.replace('''def process_html(txt, cfg, reps):
    g, v, code = split_reps(reps)
    txt = replace_visible(txt, g, v, code)''',
'''def process_html(txt, cfg, reps):
    g, v, code = split_reps(reps)
    txt = replace_visible(txt, g, v, code)
    txt = repair_svg_paths(txt)''')

io.open(P, "w", encoding="utf-8").write(c)
ast.parse(c)
print("patched, parses OK")
for probe in ["IDENT_RENAMES", "repair_svg_paths", "BAD_PATH"]:
    print(("  ok    " if probe in c else "  MISS  ") + probe)
