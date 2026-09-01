"""The town name must not itself be a street word.

"101 East Street Hadley, MA 01035" matched with "East Street Hadley" as the
town, leaving "101" as the entire street line. Excluding street suffixes from
the locality's name words makes "Hadley, MA 01035" the only valid reading.
"""
import io, ast

P = "_demo/build_demos.py"
c = io.open(P, encoding="utf-8").read()

start = c.index("LOCALITY_RE = re.compile(")
end = c.index("SUITE_RE = re.compile(")

new = '''_NOT_STREET = (
    r"(?!(?:Street|St|Road|Rd|Avenue|Ave|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way|"
    r"Highway|Hwy|Parkway|Pkwy|Place|Pl|Court|Ct|Suite|Ste|Unit|Floor|Fl)\\b)"
    r"[A-Z][A-Za-z.'\\-]+"
)

LOCALITY_RE = re.compile(
    "(" + _NOT_STREET + r"(?:\\s+" + _NOT_STREET + r"){0,2},?\\s+"
    r"(?:[A-Z]{2}|[A-Z][a-z]+|NSW|VIC|QLD|TAS|ACT)\\s+\\d{4,5}(?:-\\d{4})?"
    "|" + _NOT_STREET + r"(?:\\s+" + _NOT_STREET + r"){0,2},?\\s+"
    r"[A-Z]{1,2}\\d{1,2}[A-Z]?\\s*\\d[A-Z]{2})"
)

'''

c = c[:start] + new + c[end:]
io.open(P, "w", encoding="utf-8").write(c)
ast.parse(c)
print("locality regex tightened, parses OK")
