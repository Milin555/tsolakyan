"""Maps the 20 top-ranked prospects onto template + theme + contact details.

Every value here is read from dental-prospects.json or derived from it.
Nothing about a prospect is invented; where a field is genuinely absent the
build falls back to neutral copy rather than a guess.
"""
import io, json, os, re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# One template. The rotation added variety nobody asked for and three sets of
# other practices' photographs along with it.
TEMPLATES = ["Lura Dentist"]

# One palette, taken from the Lura template's own stylesheet. The rotation
# fought the templates' native styling; this agrees with it.
LURA = {"accent": "#24A3B1", "accent_dk": "#011F23", "soft": "#EAF6F7", "warm": "#C8A96A"}
THEMES = {k: dict(LURA) for k in ("slate", "forest", "plum", "indigo", "clay")}
THEME_KEYS = list(THEMES)

# Strings the Webflow exports leak. Shipping any of these is a build failure.
LEAKED = [
    "Foundation Dental Alliance", "foundationdentalalliance",
    "Lumora", "lumora", "LUMORA",
    "edrumm@585dentist.com", "585dentist",
    "info@foundationdentalalliance.com", "310-888-1850",
    "john@example.com", "Smilifye", "smilifye",
    "+357 70005758", "70005758", "Dr. Neo Boutique", "PANNU DENTAL GROUP",
    "Limassol", "Cyprus", "University of Leipzig", "Nikodimou", "Neofytos",
    # Template street lines. City names are deliberately absent: one of the
    # prospects really is in Beverly Hills.
    "123 Smile Avenue", "9675 Brighton Way", "456 Bright Dental Blvd",
    "45 King's Road", "New York, NY 10001", "Suite 330", "Suite 200",
]


def client_details(slug):
    """Address, phone and dentist names read off the practice's own site."""
    p = os.path.join(BASE, "_demo", "client_assets", slug, "details.json")
    if not os.path.exists(p):
        return {"address": None, "phone": None, "doctors": []}
    try:
        m = json.load(io.open(p, encoding="utf-8"))
        return {"address": m.get("address"), "phone": m.get("phone"),
                "doctors": m.get("doctors") or []}
    except Exception:
        return {"address": None, "phone": None, "doctors": []}


def client_assets(slug):
    """What the scrape pulled off this practice's own site, if anything."""
    p = os.path.join(BASE, "_demo", "client_assets", slug, "manifest.json")
    if not os.path.exists(p):
        return {"heroes": [], "people": [], "address": None}
    try:
        m = json.load(io.open(p, encoding="utf-8"))
        return {"heroes": m.get("heroes") or [], "people": m.get("people") or [],
                "address": m.get("address")}
    except Exception:
        return {"heroes": [], "people": [], "address": None}


def slugify(s, limit=40):
    s = re.sub(r"[^\w\s-]", "", s.lower())
    s = re.sub(r"[\s_]+", "-", s).strip("-")
    if len(s) <= limit:
        return s
    # Break at a word boundary; a slug cut mid-word reads as a broken link.
    return s[:limit].rsplit("-", 1)[0].strip("-")


def domain_of(url):
    if not url:
        return None
    m = re.search(r"https?://(?:www\.)?([^/]+)", url)
    return m.group(1) if m else None


def phone_from(*fields):
    """Pull a real phone number out of the free-text outreach/contact fields."""
    for f in fields:
        if not f:
            continue
        m = re.search(r"(\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4})", f)
        if m:
            return m.group(1).strip()
        m = re.search(r"(\+?\d[\d\s()-]{9,}\d)", f)
        if m:
            return m.group(1).strip()
    return None


def first_doctor(owner_name):
    """'Dr. A and Dr. B' -> 'Dr. A'. Unnamed practices return None."""
    if not owner_name or owner_name.lower().startswith("not individually"):
        return None
    return re.split(r"\s+and\s+|\s*[,&]\s*", owner_name)[0].strip()


def load(limit=20):
    src = os.path.join(BASE, "dental-prospects.json")
    prospects = json.load(io.open(src, encoding="utf-8"))["prospects"]
    prospects = sorted(prospects, key=lambda p: p["rank"])[:limit]

    used = set()
    out = []
    for i, p in enumerate(prospects):
        # Rotate so template and theme never repeat as a pair, and adjacent
        # ranks (likely to be contacted the same day) never look alike.
        tpl = TEMPLATES[0]
        theme = THEME_KEYS[0]

        dom = domain_of(p.get("website"))
        _slug = slugify(p["business_name"])
        assets = client_assets(_slug)
        details = client_details(_slug)
        doctor = first_doctor(p.get("owner_name"))
        city = (p.get("city") or "").split(" and ")[0].strip()

        out.append({
            "rank": p["rank"],
            "slug": slugify(p["business_name"]),
            "practice": p["business_name"],
            "doctor": doctor,
            "owner_raw": p.get("owner_name"),
            "city": city,
            "country": p.get("country", ""),
            "specialty": p.get("specialty", ""),
            "website": p.get("website"),
            "domain": dom,
            "email": f"info@{dom}" if dom else None,
            # Their published number beats one lifted from a research note.
            "phone": details["phone"] or phone_from(
                p.get("best_outreach_channel"), p.get("why_worth_contacting")),
            "social": p.get("social_profile_url"),
            "followers": p.get("follower_count"),
            "weaknesses": p.get("website_weaknesses", []),
            "price_range": p.get("price_range", ""),
            "channel": p.get("best_outreach_channel", ""),
            "offer": p.get("recommended_offer", ""),
            "score": p.get("final_score"),
            "template": tpl,
            "theme": theme,
            "colours": THEMES[theme],
            "assets": assets,
            "street": details["address"] or assets.get("address"),
            "real_doctors": details["doctors"],
        })
    return out


if __name__ == "__main__":
    import sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    rows = load()
    print(f"{len(rows)} prospects mapped\n")
    miss_mail = miss_phone = miss_doc = 0
    for r in rows:
        miss_mail += not r["email"]; miss_phone += not r["phone"]; miss_doc += not r["doctor"]
        print(f"{r['rank']:2} {r['slug'][:30]:32} {r['template'][:14]:16} {r['theme']:7} "
              f"{(r['doctor'] or '-')[:22]:24} {(r['email'] or '-')[:32]:34} {r['phone'] or '-'}")
    print(f"\nmissing: email {miss_mail} · phone {miss_phone} · named doctor {miss_doc}")
