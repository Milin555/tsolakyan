"""Repairs the dedup regex and tightens the name filter.

Two heredoc round-trips turned the \\b word boundaries into literal backspace
bytes, so the fragment check was searching for control characters and never
matched. Also require a full name: a bare surname is no use on a profile page.
"""
import io, ast

P = "_demo/fetch_client_details.py"
c = io.open(P, encoding="utf-8").read()

BS = chr(8)
broken = 'if any(n != k and re.search(r"' + BS + '" + re.escape(n) + r"' + BS + '", k) for k in docs):'
fixed = 'if any(n != k and re.search(r"\\b" + re.escape(n) + r"\\b", k) for k in docs):'

if broken in c:
    c = c.replace(broken, fixed)
    print("  repaired the backspace regex")
else:
    # Fall back to a byte-level scrub in case the shape differs slightly.
    if BS in c:
        c = c.replace(BS, "\\b")
        print("  scrubbed stray backspace bytes")
    else:
        print("  nothing to repair")

c = c.replace('''        out["doctors"] = ["Dr. " + n for n in docs[:6]]''',
'''        # A surname alone is no use on a profile page; keep one only if the
        # site never gave a full name for anyone.
        full = [n for n in docs if len(n.split()) >= 2]
        out["doctors"] = ["Dr. " + n for n in (full or docs)[:6]]''')

io.open(P, "w", encoding="utf-8").write(c)
ast.parse(c)
print("parses OK ·", "backspace bytes remaining:", c.count(BS))
