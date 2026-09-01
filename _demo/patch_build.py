"""Makes replacement context-aware, in three tiers.

Blind str.replace() over whole files rewrote a stylesheet filename
(lumora.css -> 'waimea dental studio.css') and a JavaScript identifier
(lumoraLead), breaking the stylesheet and the lead form. But being too timid
is just as bad: the templates carry a previous practice's live domain in href
attributes (585dentist.com x145) and two brand names inside JS form receipts
that never render until a visitor submits, so no visual check catches them.

So:
  GLOBAL  domains, emails, phones - applied everywhere, including paths and
          code. These are exactly the strings that must not survive anywhere.
  VISIBLE brand display names - text nodes and readable attributes only, never
          paths, tag names, script or style bodies.
  CODE    GLOBAL plus any brand string containing a space. A space cannot
          appear in a JS identifier or an unencoded filename, so a multi-word
          brand inside a script is always a display string and safe to swap.
"""
import io, re

P = "_demo/build_demos.py"
c = io.open(P, encoding="utf-8").read()

# 1 - the lowercase form is an asset name and a JS identifier, never visible text
c = c.replace('''    # Fallbacks in case the map missed a casing variant.
    for b in ["Foundation Dental Alliance", "Lumora", "LUMORA", "lumora"]:
        r.append((b, practice if b[0].isupper() else practice.lower()))''',
'''    # Display forms only. The lowercase form is deliberately excluded: it is
    # the stylesheet filename and a JS function name, not visible text.
    for b in ["Foundation Dental Alliance", "Lumora", "LUMORA"]:
        r.append((b, practice))

    # Every third-party domain the half-finished templates still point at.
    # These must not survive in any href, and they are safe to swap wholesale.
    own = cfg.get("domain") or (cfg["slug"] + ".com")
    for d in THIRD_PARTY_DOMAINS:
        r.append((d, own))
    for e in THIRD_PARTY_EMAILS:
        r.append((e, cfg["email"] or "hello@" + own))
    # Brands hidden inside JS confirmation receipts - invisible until submit.
    for b in ["LUMORA CLINIC CAREERS", "PANNU DENTAL GROUP",
              "Dr. Neo Boutique Dental Clinic", "Dr. Neo Boutique Dental",
              "Dr. Neo Dentistry"]:
        r.append((b, practice))''')

helpers = '''
# Domains and inboxes belonging to real third parties. Leaving any of these on
# a demo would send the prospect to a competitor and expose a stranger's inbox.
THIRD_PARTY_DOMAINS = [
    "585dentist.com", "www.585dentist.com",
    "foundationdentalalliance.com", "www.foundationdentalalliance.com",
    "garysolnitdds.com", "www.garysolnitdds.com",
    "ritterandramsey.com", "www.ritterandramsey.com",
    "modernsmilecenter.com", "www.modernsmilecenter.com",
]
THIRD_PARTY_EMAILS = [
    "edrumm@585dentist.com", "info@foundationdentalalliance.com",
    "info@garysolnitdds.com", "mcim21@gmail.com",
    "info@ritterandramsey.com", "drneodentistry@gmail.com",
    "john@example.com",
]

SPLIT_RE = re.compile(r"(<script[\\s\\S]*?</script>|<style[\\s\\S]*?</style>|<!--[\\s\\S]*?-->|<[^>]+>)", re.I)
ATTR_RE = re.compile(r'((?:alt|title|aria-label|placeholder|content)\\s*=\\s*)(["\\'])(.*?)\\2', re.I)
PATHY = re.compile(r'(^\\s*(https?:|/|\\./|\\.\\./))|(\\.(css|js|jpg|jpeg|png|webp|svg|mp4|ico|woff2?)\\b)', re.I)
PHONEY = re.compile(r"[+()\\d][\\d\\s().-]{6,}$")


def _apply(s, reps):
    for old, new in reps:
        s = s.replace(old, new)
    return s


def is_global(old):
    """Contact and domain strings: unambiguous, safe anywhere."""
    return ("@" in old or bool(PHONEY.fullmatch(old.strip()))
            or any(old == d or old.endswith("." + d.split(".", 1)[-1]) and "." in old
                   and old in THIRD_PARTY_DOMAINS for d in THIRD_PARTY_DOMAINS))


def split_reps(reps):
    g = [(o, n) for o, n in reps if is_global(o)]
    gset = {o for o, _ in g}
    v = [(o, n) for o, n in reps if o not in gset]
    code = g + [(o, n) for o, n in v if " " in o]
    return g, v, code


def replace_visible(txt, reps_global, reps_visible):
    """Globals everywhere; brand names only where a human can read them."""
    out = []
    for part in SPLIT_RE.split(txt):
        if not part:
            continue
        if part.startswith("<"):
            low = part[:8].lower()
            if low.startswith(("<script", "<style", "<!--")):
                out.append(_apply(part, reps_global))
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

'''
c = c.replace("def build_replacements(", helpers + "\ndef build_replacements(", 1)

c = c.replace('''def process_html(txt, cfg, reps):
    for old, new in reps:
        txt = txt.replace(old, new)
''',
'''def process_html(txt, cfg, reps):
    g, v, _ = split_reps(reps)
    txt = replace_visible(txt, g, v)
''')

c = c.replace('''            new = process_html(txt, cfg, reps) if f.endswith(".html") else \\
                  functools_reduce(txt, reps)''',
'''            if f.endswith(".html"):
                new = process_html(txt, cfg, reps)
            elif f.endswith((".css", ".js")):
                new = functools_reduce(txt, split_reps(reps)[2])
            else:
                new = functools_reduce(txt, reps)''')

io.open(P, "w", encoding="utf-8").write(c)

import ast
ast.parse(c)
print("patched, parses OK")
for probe in ["THIRD_PARTY_DOMAINS", "replace_visible", "split_reps",
              'for b in ["Foundation Dental Alliance", "Lumora", "LUMORA"]',
              "LUMORA CLINIC CAREERS"]:
    print(("  ok    " if probe in c else "  MISS  ") + probe)
