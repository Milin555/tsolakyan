"""The street/locality split was cutting in the wrong place.

LOCALITY_RE took the first match, so "101 East Street Hadley, MA 01035" split
as street "101" and locality "East Street Hadley, MA 01035". The town is
always the last locality-shaped run in an address, not the first, so scan and
keep the rightmost. Also handles spelled-out states ("Glendale, Arizona
85308") and Australian states, neither of which the two-letter pattern caught.
"""
import io, ast

P = "_demo/build_demos.py"
c = io.open(P, encoding="utf-8").read()

start = c.index("LOCALITY_RE = re.compile(")
end = c.index("def build_replacements(cfg, tmap, copy):")

new = '''LOCALITY_RE = re.compile(
    r"([A-Z][A-Za-z.'\\-]+(?:\\s+[A-Z][A-Za-z.'\\-]+){0,2},?\\s+"
    r"(?:[A-Z]{2}|[A-Z][a-z]+|NSW|VIC|QLD|TAS|ACT)\\s+\\d{4,5}(?:-\\d{4})?"      # US / AU
    r"|[A-Z][A-Za-z.'\\-]+(?:\\s+[A-Z][A-Za-z.'\\-]+){0,2},?\\s+"
    r"[A-Z]{1,2}\\d{1,2}[A-Z]?\\s*\\d[A-Z]{2})")                                 # UK postcode

SUITE_RE = re.compile(r"^((?:Suite|Ste\\.?|Unit|Floor|Fl\\.?|#)\\s*[\\w-]+)\\s+(.*)$", re.I)


def split_address(cfg):
    """(street line, locality).

    The town is the last locality-shaped run in the string, never the first.
    """
    full = re.sub(r"\\s+", " ", (cfg.get("street") or "")).strip().rstrip(",")
    city = cfg.get("city") or cfg.get("country") or ""
    if not full:
        return city, city

    last = None
    for m in LOCALITY_RE.finditer(full):
        last = m
    if last:
        street = full[:last.start()].strip().rstrip(",").strip()
        loc = last.group(0).strip()
        sm = SUITE_RE.match(loc)          # a suite belongs on the street line
        if sm:
            street = (street + ", " + sm.group(1)).strip(" ,")
            loc = sm.group(2).strip()
        return (street or city), loc

    parts = [p.strip() for p in full.split(",") if p.strip()]
    if len(parts) >= 3:
        return ", ".join(parts[:-2]), ", ".join(parts[-2:])
    if len(parts) == 2:
        return parts[0], parts[1]
    return full, city


'''
c = c[:start] + new + c[end:]
io.open(P, "w", encoding="utf-8").write(c)
ast.parse(c)
print("split rewritten, parses OK")
