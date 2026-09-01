"""
demo_sanitize.py - final safety pass over a built demo before it is shipped.

demo_generator.py does the reskin. This does the last mile: the classes of
mistake that survive a reskin and get an email deleted by a real dentist.

Four bug classes found in live builds on 2026-08-22:

  1. twitter:title was never rewritten (og:title was), so it still carried
     "Rose Dental, DDS, MS | ..." - US credentials pinned to a UK practice.
  2. <title> was fed a truncated meta description:
     "Rose Dental | At Rose Dental, we offer patients a safe, comfortable"
     - cut off mid-sentence, 67 chars.
  3. Template clinical claims survived. The source template belongs to a
     prosthodontist, so every build asserted "is a premier prosthodontist".
     That is a false clinical claim about a real practice.
  4. Stray real person names from the source template survived in team cards
     and image alt text.

Usage:
    python demo_sanitize.py --all                 # report on every build
    python demo_sanitize.py --all --fix           # rewrite in place
    python demo_sanitize.py --slug rose-dental --fix
    python demo_sanitize.py --all --fix --strip-social-proof
"""

import argparse
import io
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
BUILDS = os.path.join(BASE, "demo_builds")

# --- credentials -----------------------------------------------------------
# US/other credentials that must never be auto-attached to a practice we did
# not verify. A UK dentist holds BDS, not DDS/DMD/MS - seeing "DDS, MS" on
# their own name is an instant tell that the page is a template.
CRED = r"(?:DDS|DMD|MS|MSD|BDS|FACP|FAGD|MAGD|DDS\.?|D\.D\.S\.?|D\.M\.D\.?)"
CRED_SUFFIX = re.compile(r",\s*" + CRED + r"(?:\s*,\s*" + CRED + r")*\b")

# --- clinical specialty claims --------------------------------------------
# Only assert a specialty if the lead's own Category says so. Otherwise this
# is the template's owner's specialty leaking onto someone else's practice.
SPECIALTY = re.compile(
    r"\b(?:premier\s+|leading\s+|award[- ]winning\s+)?"
    r"(prosthodontist|orthodontist|endodontist|periodontist|oral surgeon|"
    r"maxillofacial surgeon|pedodontist|paediatric dentist|pediatric dentist)\b",
    re.I,
)

# --- people who are not the prospect --------------------------------------
STRAY_PEOPLE = [
    "Dr. L. Hartley", "Dr L. Hartley", "L. Hartley", "Hartley",
    "Dr. Sai Gathani", "Dr Sai Gathani", "Sai Gathani", "Gathani",
    "Dr. Robert G. Ritter", "Dr. Robert Ritter", "Dr. Rob Ritter",
    "Dr. Christopher Ramsey", "Dr. Chris Ramsey", "Dr. Isabelle Ritter",
    "Dr. Gary Solnit", "Gary S. Solnit", "Gary Solnit",
    "Dr. Emilie Drumm", "Dr. Neofytos Ioannides", "Dr. Neo",
]

# Social-proof blocks are template-invented. Sending a dentist a page carrying
# fabricated patient testimonials attributed to their practice is not a
# cosmetic problem - it is putting words in their mouth.
SOCIAL_PROOF_MARKERS = ["testimonial", "review_", "reviews_", "quote_card"]



CITY_HINT = re.compile(
    r"<h1[^>]*>\s*([A-Z][A-Za-z'\-]+(?:[- ][A-Z][A-Za-z'\-]+){0,3})\s+"
    r"(?:Cosmetic|Restorative|Family|General|Implant|Aesthetic|Emergency|Private)",
    re.I)
POSTCODE_CITY = re.compile(
    r"([A-Z][A-Za-z'\-]+(?:[- ][A-Z][A-Za-z'\-]+){0,2}),?\s+"
    r"[A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2}")



# A candidate must look like a place, not a person, a country, or the practice.
NOT_A_CITY = {
    "united kingdom", "england", "scotland", "wales", "northern ireland",
    "great britain", "uk", "united states", "usa", "america", "australia",
    "canada", "ireland", "the", "our", "your", "welcome to", "home",
    "dental", "dentist", "dentistry", "clinic", "practice", "surgery",
    "cosmetic", "aesthetic", "private", "family", "general",
}
PERSON_PREFIX = ("dr ", "dr. ", "doctor ", "mr ", "mr. ", "mrs ", "ms ", "prof ", "miss ")


def plausible_city(c, business=""):
    """Reject people, countries, and the practice name itself."""
    if not c:
        return False
    lc = c.strip().lower()
    if lc in NOT_A_CITY:
        return False
    if lc.startswith(PERSON_PREFIX):
        return False
    if business and lc in business.strip().lower():
        return False
    if not (2 < len(c) <= 28):
        return False
    return True


def city_from_html(html, business=""):
    """Best-effort city when demos_meta.json has none. Never guesses wildly."""
    m = POSTCODE_CITY.search(html)          # UK postcode is the strongest signal
    if m:
        c = m.group(1).strip()
        if plausible_city(c, business):
            return c
    m = CITY_HINT.search(html)              # then the H1 pattern
    if m:
        c = m.group(1).strip()
        if plausible_city(c, business):
            return c
    return ""


def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def build_title(business, city, category=""):
    """A real title: 'Rose Dental | Dentist in Westcliff-On-Sea'. 50-60 chars."""
    business = (business or "").strip().rstrip(",. ")
    business = CRED_SUFFIX.sub("", business)
    city = (city or "").strip().rstrip(",. ")
    noun = "Dentist"
    c = (category or "").lower()
    for k, v in [("ortho", "Orthodontist"), ("pediatric", "Pediatric Dentist"),
                 ("cosmetic", "Cosmetic Dentist"), ("implant", "Implant Dentist")]:
        if k in c:
            noun = v
            break
    t = f"{business} | {noun} in {city}" if city else f"{business} | {noun}"
    if len(t) > 62:
        t = f"{business} | {noun}"
    return t[:62]


def sanitize(html, business="", city="", category="", strip_social=False):
    """Return (html, findings). findings is a list of human-readable strings."""
    found = []
    orig = html
    if not city:
        city = city_from_html(html, business)
        if city:
            found.append(f"derived city from page: {city}")

    # 1. credentials attached to the business name, anywhere (meta, alt, body)
    hits = CRED_SUFFIX.findall(html)
    if hits:
        html = CRED_SUFFIX.sub("", html)
        found.append(f"stripped {len(hits)} credential suffix(es) e.g. '{hits[0]}'")

    # 2. twitter:title / twitter:description - the tags og: handling missed
    title = build_title(business, city, category)
    for prop in ("twitter:title", "og:title"):
        pat = re.compile(r'(<meta content=")[^"]*("\s+(?:name|property)="' + re.escape(prop) + r'"\s*/?>)')
        if pat.search(html):
            html = pat.sub(lambda m: m.group(1) + esc(title) + m.group(2), html)
            found.append(f"rewrote {prop}")

    # 3. <title> - must not be a truncated description
    m = re.search(r"<title>([^<]*)</title>", html)
    if m:
        old = m.group(1)
        bad = len(old) > 62 or not old.strip() or (
            len(old) > 45 and old.rstrip()[-1] not in ".!?" and " we " in old.lower()
        )
        if bad:
            html = re.sub(r"<title>[^<]*</title>", f"<title>{esc(title)}</title>", html, count=1)
            found.append(f"rewrote <title> (was {len(old)} chars, truncated mid-sentence)")

    # 4. clinical specialty claims not supported by the lead's own category
    cat = (category or "").lower()
    def spec_sub(mo):
        word = mo.group(1)
        if word.lower().split()[-1] in cat:
            return mo.group(0)          # their own category claims it - keep
        return "dental practice"
    n_before = len(SPECIALTY.findall(html))
    if n_before:
        html2 = SPECIALTY.sub(spec_sub, html)
        removed = n_before - len(SPECIALTY.findall(html2))
        if removed:
            html = html2
            found.append(f"neutralised {removed} unverified specialty claim(s)")

    # 5. stray real people from the source template
    for name in sorted(STRAY_PEOPLE, key=len, reverse=True):
        if name in html:
            c = html.count(name)
            html = html.replace(name, "Our Clinical Team" if name.startswith("Dr") else "Our Team")
            found.append(f"removed stray person '{name}' x{c}")

    # 6. optional: strip invented social proof entirely
    if strip_social:
        for mark in SOCIAL_PROOF_MARKERS:
            c = len(re.findall(mark, html, re.I))
            if c:
                found.append(f"social-proof marker '{mark}' present x{c} (manual removal advised)")

    return html, found


def audit_only(html):
    """Report residual risk without changing anything."""
    risks = []
    if CRED_SUFFIX.search(html):
        risks.append("CREDENTIALS still present")
    for prop in ("twitter:title",):
        m = re.search(r'<meta content="([^"]*)"\s+name="' + prop + r'"', html)
        if m and CRED_SUFFIX.search(m.group(1)):
            risks.append(f"{prop} carries credentials")
    m = re.search(r"<title>([^<]*)</title>", html)
    if m and len(m.group(1)) > 62:
        risks.append(f"<title> {len(m.group(1))} chars (too long / truncated)")
    for name in STRAY_PEOPLE:
        if name in html:
            risks.append(f"stray person: {name}")
    if SPECIALTY.search(html):
        risks.append("specialty claim present - verify against lead Category")
    if re.search(r"\{\{|__[A-Z_]+__", html):
        risks.append("UNREPLACED TOKEN")
    return risks


def lead_facts(slug):
    """Pull business/city/category for a slug out of demos_meta.json if present."""
    p = os.path.join(BASE, "demos_meta.json")
    if not os.path.exists(p):
        return {}
    try:
        meta = json.load(io.open(p, encoding="utf-8"))
    except Exception:
        return {}
    recs = meta.values() if isinstance(meta, dict) else meta
    for r in recs:
        if not isinstance(r, dict):
            continue
        if r.get("slug") == slug or r.get("username") == slug:
            return r
    return {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--slug")
    ap.add_argument("--fix", action="store_true", help="rewrite in place (default: report only)")
    ap.add_argument("--strip-social-proof", action="store_true")
    a = ap.parse_args()

    if not os.path.isdir(BUILDS):
        print(f"no demo_builds/ at {BUILDS}", file=sys.stderr)
        return 1

    slugs = [a.slug] if a.slug else sorted(
        d for d in os.listdir(BUILDS) if os.path.isdir(os.path.join(BUILDS, d))
    )
    if not slugs:
        print("no builds found", file=sys.stderr)
        return 1

    total_fixed = 0
    for slug in slugs:
        d = os.path.join(BUILDS, slug)
        pages = [f for f in os.listdir(d) if f.endswith(".html")]
        facts = lead_facts(slug)
        biz = facts.get("business") or facts.get("name") or slug.replace("-", " ").title()
        city = facts.get("city") or ""
        cat = facts.get("category") or ""
        print(f"\n=== {slug}  ({len(pages)} pages)  biz={biz!r} city={city!r}")
        for page in pages:
            p = os.path.join(d, page)
            html = io.open(p, encoding="utf-8", errors="replace").read()
            if a.fix:
                new, found = sanitize(html, biz, city, cat, a.strip_social_proof)
                if new != html:
                    io.open(p, "w", encoding="utf-8").write(new)
                    total_fixed += 1
                for f in found:
                    print(f"    [{page}] {f}")
                residual = audit_only(new)
            else:
                residual = audit_only(html)
            for r in residual:
                print(f"    [{page}] RESIDUAL RISK: {r}")

    print(f"\n{'FIXED' if a.fix else 'AUDITED'} - {len(slugs)} builds"
          + (f", {total_fixed} files rewritten" if a.fix else ""))
    if not a.fix:
        print("run again with --fix to apply")
    return 0


if __name__ == "__main__":
    sys.exit(main())
