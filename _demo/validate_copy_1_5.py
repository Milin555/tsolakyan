# -*- coding: utf-8 -*-
"""Validates the copy JSON files for ranks 1-5 against dental-prospects.json."""
import io, json, os, re, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COPY = os.path.join(BASE, "_demo", "copy")

RANKS = [1, 2, 3, 4, 5]
REQUIRED = ["slug", "rank", "practice", "meta_title", "meta_desc", "hero_h1",
            "hero_sub", "cta_primary", "cta_secondary", "about_heading",
            "about_body", "services", "footer_tagline", "why_this_angle"]

BANNED = ["elevate", "unlock", "journey", "seamless", "cutting-edge",
          "cutting edge", "state-of-the-art", "state of the art", "nestled",
          "we understand that"]

prospects = {p["rank"]: p for p in
             json.load(io.open(os.path.join(BASE, "dental-prospects.json"),
                               encoding="utf-8"))["prospects"]}

fails = []
for rank in RANKS:
    p = prospects[rank]
    src_blob = json.dumps(p, ensure_ascii=False)
    src_nums = set(re.findall(r"\d+", src_blob))

    matches = [f for f in os.listdir(COPY)
               if json.load(io.open(os.path.join(COPY, f), encoding="utf-8"))["rank"] == rank]
    if len(matches) != 1:
        fails.append("rank %s: expected 1 file, found %s" % (rank, matches))
        continue
    path = os.path.join(COPY, matches[0])
    try:
        c = json.load(io.open(path, encoding="utf-8"))
    except Exception as e:
        fails.append("rank %s: invalid JSON (%s)" % (rank, e))
        continue

    def bad(msg):
        fails.append("rank %s (%s): %s" % (rank, matches[0], msg))

    for k in REQUIRED:
        if k not in c or c[k] in (None, "", []):
            bad("missing key %r" % k)

    # every string in the copy, flattened
    text_parts = []
    for k, v in c.items():
        if isinstance(v, str):
            text_parts.append(v)
        elif isinstance(v, list):
            for it in v:
                text_parts.extend(str(x) for x in it.values())
    blob = " ".join(text_parts)

    if "—" in blob or "–" in blob:
        bad("contains an em dash or en dash")
    if "!" in blob:
        bad("contains an exclamation mark")
    low = blob.lower()
    for w in BANNED:
        if w in low:
            bad("AI-tell phrase %r" % w)
    for word in re.findall(r"\b[A-Z]{4,}\b", blob):
        if word not in ("UFC",):
            bad("ALL CAPS token %r" % word)

    if len(c.get("hero_h1", "")) >= 55:
        bad("hero_h1 is %s chars" % len(c["hero_h1"]))
    if len(c.get("hero_sub", "")) >= 110:
        bad("hero_sub is %s chars" % len(c["hero_sub"]))
    if len(c.get("meta_desc", "")) >= 155:
        bad("meta_desc is %s chars" % len(c["meta_desc"]))
    if len(c.get("about_heading", "")) >= 60:
        bad("about_heading is %s chars" % len(c["about_heading"]))
    if len(c.get("footer_tagline", "")) >= 70:
        bad("footer_tagline is %s chars" % len(c["footer_tagline"]))

    svc = c.get("services", [])
    if len(svc) != 4:
        bad("has %s services, expected 4" % len(svc))
    for s in svc:
        if set(s) != {"name", "blurb"}:
            bad("service keys %s" % sorted(s))
        if len(s.get("blurb", "")) >= 110:
            bad("service blurb %r is %s chars" % (s.get("name"), len(s["blurb"])))

    body = c.get("about_body", "")
    if "\n\n" not in body:
        bad("about_body has no paragraph break")
    if len(body.split()) > 90:
        bad("about_body is %s words" % len(body.split()))

    # names: unnamed practices must not carry a person's name
    owner = (p.get("owner_name") or "")
    if owner.lower().startswith("not individually"):
        if re.search(r"\bDr\.?\b", blob):
            bad("uses a doctor title for an unnamed practice")

    # numbers must exist in the source record
    for n in re.findall(r"\d+", blob):
        if n not in src_nums:
            bad("number %r not present in source JSON" % n)

    # spelling convention
    country = p.get("country", "")
    if country == "UK":
        for us in ["center", "color", "specialize", "specializ", "personalize", "enrollment", "practicing"]:
            if us in low:
                bad("US spelling %r on a UK practice" % us)
    else:
        for uk in ["centre", "colour", "specialise", "specialis", "personalise", "enrolment", "practising"]:
            if uk in low:
                bad("UK spelling %r on a %s practice" % (uk, country))

    print("rank %-2s %-42s h1=%-2s meta=%-3s svc=%s about=%sw" % (
        rank, c.get("slug"), len(c.get("hero_h1", "")), len(c.get("meta_desc", "")),
        len(svc), len(body.split())))

print()
if fails:
    print("FAILURES (%d):" % len(fails))
    for f in fails:
        print(" -", f)
    sys.exit(1)
print("all 5 files pass")
