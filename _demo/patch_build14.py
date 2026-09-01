"""Address splitting was losing the street number.

split_address cut at the first comma, so "65-1230 Mamalahoa Hwy., Suite A21
Waimea, HI 96743" became street "65-1230 Mamalahoa Hwy." and locality "Suite
A21 Waimea, HI 96743" - the suite ended up in the town. Cut at the locality
instead: find the "Town, ST 12345" tail and treat everything before it as the
street line.

An older rule also mapped each whole template address to the bare city, which
competed with the new fragment rules and won on length. It now maps to the
practice's full address.
"""
import io, ast

P = "_demo/build_demos.py"
c = io.open(P, encoding="utf-8").read()

c = c.replace('''def split_address(cfg):
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
    return full, city''',
'''LOCALITY_RE = re.compile(
    r"([A-Z][\\w .'\\-]{2,28},?\\s+"
    r"(?:[A-Z]{2}\\s+\\d{5}(?:-\\d{4})?"                    # US  Waimea, HI 96743
    r"|(?:NSW|VIC|QLD|WA|SA|TAS|ACT|NT)\\s+\\d{4}"          # AU
    r"|[A-Z]{1,2}\\d{1,2}[A-Z]?\\s*\\d[A-Z]{2}))\\s*$")      # UK postcode


def split_address(cfg):
    """(street line, locality). Cut at the town, not at the first comma."""
    full = re.sub(r"\\s+", " ", (cfg.get("street") or "")).strip().rstrip(",")
    city = cfg.get("city") or cfg.get("country") or ""
    if not full:
        return city, city
    m = LOCALITY_RE.search(full)
    if m:
        street = full[:m.start()].strip().rstrip(",").strip()
        return (street or city), m.group(1).strip()
    parts = [p.strip() for p in full.split(",") if p.strip()]
    if len(parts) >= 2:
        return ", ".join(parts[:-1]), parts[-1]
    return full, city''')

# The old whole-address rule pointed at the bare city and outranked the
# fragments on length. Point it at the real address instead.
c = c.replace('''    # City, where the template names one.
    for a in t.get("addresses", []) or []:
        if cfg["city"]:
            r.append((a, cfg["city"]))''',
'''    # Whole template addresses map to the practice's real one.
    _full = (cfg.get("street") or "").strip()
    for a in t.get("addresses", []) or []:
        if _full:
            r.append((a, _full))
        elif cfg["city"]:
            r.append((a, cfg["city"]))''')

# Removing a suite number outright leaves a double space in the markup.
c = c.replace('''    for frag in ("Suite 330", "Suite 200", "Floor 3"):
        r.append((frag, ""))''',
'''    for frag in ("Suite 330, ", "Suite 200, ", "Floor 3, ",
                 "Suite 330 ", "Suite 200 ", "Floor 3 "):
        r.append((frag, ""))''')

io.open(P, "w", encoding="utf-8").write(c)
ast.parse(c)
print("patched, parses OK")
for probe, label in [("LOCALITY_RE", "locality-aware split"),
                     ("r.append((a, _full))", "whole address maps to real"),
                     ('"Suite 330, "', "suite removal keeps spacing")]:
    print(("  ok    " if probe in c else "  MISS  ") + label)
