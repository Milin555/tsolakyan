# -*- coding: utf-8 -*-
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COPY = os.path.join(ROOT, "_demo", "copy")

src = json.load(open(os.path.join(ROOT, "dental-prospects.json"), encoding="utf-8"))["prospects"]
by_rank = {p["rank"]: p for p in src}

REQ = ["slug", "rank", "practice", "meta_title", "meta_desc", "hero_h1", "hero_sub",
       "cta_primary", "cta_secondary", "about_heading", "about_body", "services",
       "footer_tagline", "why_this_angle"]

BANNED = ["elevate", "unlock", "journey", "seamless", "cutting-edge", "cutting edge",
          "state-of-the-art", "state of the art", "nestled", "we understand that"]

SLUGS = ["cosmetic-dentistry-of-san-antonio", "the-grove-family-dental", "my-smile-miami",
         "ocean-vibe-dental", "circle-c-dental"]

fails = []
for slug in SLUGS:
    path = os.path.join(COPY, slug + ".json")
    if not os.path.exists(path):
        fails.append((slug, "file missing")); continue
    raw = open(path, encoding="utf-8").read()
    try:
        d = json.loads(raw)
    except Exception as e:
        fails.append((slug, "invalid JSON: %s" % e)); continue

    def bad(msg): fails.append((slug, msg))

    for k in REQ:
        if k not in d: bad("missing key %s" % k)
    if "—" in raw or "–" in raw: bad("em/en dash present")
    if "!" in raw: bad("exclamation mark present")
    if len(d.get("hero_h1", "")) >= 55: bad("hero_h1 %d chars" % len(d["hero_h1"]))
    if len(d.get("meta_desc", "")) >= 155: bad("meta_desc %d chars" % len(d["meta_desc"]))
    if len(d.get("hero_sub", "")) >= 110: bad("hero_sub %d chars" % len(d["hero_sub"]))
    if len(d.get("about_heading", "")) >= 60: bad("about_heading %d chars" % len(d["about_heading"]))
    if len(d.get("footer_tagline", "")) >= 70: bad("footer_tagline %d chars" % len(d["footer_tagline"]))
    words = len(re.findall(r"[A-Za-z'\-]+", d.get("about_body", "")))
    if words >= 90: bad("about_body %d words" % words)
    if "\n\n" not in d.get("about_body", ""): bad("about_body not two paragraphs")
    svcs = d.get("services", [])
    if len(svcs) != 4: bad("services count %d" % len(svcs))
    for s in svcs:
        if "name" not in s or "blurb" not in s: bad("service missing keys")
        elif len(s["blurb"]) >= 110: bad("blurb %d chars: %s" % (len(s["blurb"]), s["name"]))

    p = by_rank[d["rank"]]
    if d["practice"] != p["business_name"]: bad("practice name mismatch")
    if d["slug"] != slug: bad("slug mismatch")

    # numbers must appear in source record
    srctext = json.dumps(p, ensure_ascii=False)
    for num in set(re.findall(r"\d+", raw)):
        if num == str(d["rank"]):
            continue
        if num not in srctext: bad("number %s not in source" % num)

    low = raw.lower()
    for b in BANNED:
        if b in low: bad("banned phrase: %s" % b)

    # ALL CAPS words (3+ letters)
    for w in re.findall(r"\b[A-Z]{3,}\b", raw):
        if w not in ("CEREC", "CBCT", "TX", "FL", "AZ", "USA"): bad("all caps: %s" % w)

    # unnamed practices must not use a name
    if p["owner_name"].lower().startswith("not individually"): bad("check: unnamed owner")
    else:
        # sanity: surname used should match owner_name
        pass

if fails:
    print("FAIL")
    for s, m in fails: print(" ", s, "->", m)
    sys.exit(1)
print("ALL 5 PASS")
for slug in SLUGS:
    d = json.load(open(os.path.join(COPY, slug + ".json"), encoding="utf-8"))
    print("rank %2d  %-34s h1(%d): %s" % (d["rank"], slug, len(d["hero_h1"]), d["hero_h1"]))
