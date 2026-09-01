"""Two address bugs.

1. `Dr` is in the street-suffix list for "Fairway Dr", which also makes it
   match "Dr Sandra" and "Dr. Pennington". Four practices got a sentence about
   a dentist stored as their street address. The fix is not to drop `Dr` -
   real addresses use it - but to require every candidate to run through to a
   locality: a town with a state and ZIP, or a UK postcode. Prose never does.

2. The Beverly Hills practice would have had its address mangled. Replacements
   apply in sequence over one string, so the rule mapping the template's
   "Beverly Hills" to that client's locality would fire again on the real
   address just inserted, giving "Beverly Hills, CA 90212, CA 90212". Any
   template fragment that also occurs in the client's own address is skipped.
"""
import io, ast

# ---------- scraper ----------
F = "_demo/fetch_client_details.py"
f = io.open(F, encoding="utf-8").read()

f = f.replace('''def pick_address(text, country):
    """The most complete address-looking run in the page text."""
    cands = []
    for m in re.finditer(STREET, text):
        seg = text[m.start():m.start() + 170]
        tail = None
        for pat in (US_TAIL, AU_TAIL):
            t = re.search(pat, seg)
            if t:
                tail = seg[:t.end()]; break
        if not tail:
            t = re.search(UK_PC, seg)
            if t:
                tail = seg[:t.end()]
        cands.append(clean(tail or m.group(0)))
    if not cands:
        for pat in (US_TAIL, AU_TAIL):
            m = re.search(pat, text)
            if m:
                cands.append(clean(m.group(0)))
    if not cands:
        return None
    # Longest wins: it is the one that carried through to the postcode.
    cands.sort(key=len, reverse=True)
    best = cands[0]
    return best if 12 <= len(best) <= 140 else None''',
'''JUNK_ADDR = re.compile(
    r"(review|whatsapp|access|book now|call us|follow|instagram|facebook|"
    r"rating|star|award|hygienist|welcome|open|hours|am\\b|pm\\b|\\?|!)", re.I)


def pick_address(text, country):
    """The most complete address-looking run that reaches a real locality.

    Requiring the locality is what separates an address from a sentence that
    happens to contain "Dr".
    """
    cands = []
    for m in re.finditer(STREET, text):
        seg = text[m.start():m.start() + 170]
        tail = None
        for pat in (US_TAIL, AU_TAIL, UK_PC):
            t = re.search(pat, seg)
            if t:
                tail = seg[:t.end()]
                break
        if tail:                       # no locality, no address
            cands.append(clean(tail))

    if not cands:                      # locality on its own still beats nothing
        for pat in (US_TAIL, AU_TAIL):
            for m in re.finditer(pat, text):
                cands.append(clean(m.group(0)))

    cands = [c for c in cands if 12 <= len(c) <= 140 and not JUNK_ADDR.search(c)]
    if not cands:
        return None
    cands.sort(key=len, reverse=True)
    return cands[0]''')

io.open(F, "w", encoding="utf-8").write(f)
ast.parse(f)

# ---------- builder ----------
P = "_demo/build_demos.py"
c = io.open(P, encoding="utf-8").read()

c = c.replace('''    street, locality = split_address(cfg)
    for frag in ("9675 Brighton Way, Suite 330", "9675 Brighton Way",''',
'''    street, locality = split_address(cfg)
    own_addr = (cfg.get("street") or "").lower()

    def _safe(frag):
        """Skip a template fragment that also sits inside the real address.

        Replacements run in sequence over one string, so a fragment that
        appears in text an earlier rule just inserted would be rewritten a
        second time.
        """
        return frag.lower() not in own_addr

    for frag in ("9675 Brighton Way, Suite 330", "9675 Brighton Way",''')

c = c.replace('''                 "45 King's Road", "45 King\\u2019s Road"):
        r.append((frag, street))''',
'''                 "45 King's Road", "45 King\\u2019s Road"):
        if _safe(frag):
            r.append((frag, street))''')

c = c.replace('''                 "Chelsea, SW3 5UZ", "SW3 5UZ", "Chelsea"):
        r.append((frag, locality))''',
'''                 "Chelsea, SW3 5UZ", "SW3 5UZ", "Chelsea"):
        if _safe(frag):
            r.append((frag, locality))''')

io.open(P, "w", encoding="utf-8").write(c)
ast.parse(c)

print("patched, parse OK")
for probe, src, label in [("JUNK_ADDR", f, "junk address filter"),
                          ("if tail:", f, "locality required"),
                          ("def _safe", c, "self-collision guard")]:
    print(("  ok    " if probe in src else "  MISS  ") + label)
