"""Pulls each prospect's own photographs and real address off their live site.

A demo carrying the practice's own team photo and their own building is a
different pitch from one carrying stock. Where their site has nothing usable,
the build falls back to the Lura sample imagery. It never borrows another
practice's real people.

Also lifts the street address out of schema.org markup where present, so the
embedded map points at the actual clinic rather than a city centroid.

    python _demo/fetch_client_assets.py            # all 20
    python _demo/fetch_client_assets.py --only slug
"""
import argparse, io, json, os, re, sys, urllib.parse, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from demo_config import load, BASE

OUT = os.path.join(BASE, "_demo", "client_assets")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

TEAM_HINT = re.compile(r"(dr[-_. ]|doctor|dentist|team|staff|meet|about|dds|dmd|provider|founder)", re.I)
JUNK = re.compile(r"(logo|icon|favicon|sprite|badge|award|placeholder|blank|spacer|arrow|"
                  r"facebook|instagram|twitter|yelp|google|pixel|tracking|banner-ad)", re.I)


def abs_url(base, u):
    try:
        return urllib.parse.urljoin(base, u)
    except Exception:
        return None


def harvest(page, url):
    """Every image the page actually rendered, with its true pixel size."""
    return page.evaluate("""() => {
      const out = [];
      const push = (src, w, h, alt, top) => {
        if (!src || src.startsWith('data:')) return;
        out.push({src, w, h, alt: alt || '', top});
      };
      document.querySelectorAll('img').forEach(i => {
        const r = i.getBoundingClientRect();
        push(i.currentSrc || i.src, i.naturalWidth, i.naturalHeight, i.alt, r.top + scrollY);
      });
      document.querySelectorAll('*').forEach(e => {
        const bg = getComputedStyle(e).backgroundImage;
        if (!bg || bg === 'none') return;
        const m = bg.match(/url\\(["']?(.*?)["']?\\)/);
        if (!m) return;
        const r = e.getBoundingClientRect();
        if (r.width < 300 || r.height < 200) return;
        push(m[1], Math.round(r.width), Math.round(r.height), e.className || '', r.top + scrollY);
      });
      return out;
    }""")


def schema_address(page):
    """Street address from schema.org markup, which most clinic sites carry."""
    try:
        blocks = page.eval_on_selector_all(
            'script[type="application/ld+json"]', "els => els.map(e => e.textContent)")
    except Exception:
        return None
    for b in blocks or []:
        try:
            data = json.loads(b)
        except Exception:
            continue
        stack = [data]
        while stack:
            n = stack.pop()
            if isinstance(n, list):
                stack.extend(n); continue
            if not isinstance(n, dict):
                continue
            a = n.get("address")
            if isinstance(a, dict) and a.get("streetAddress"):
                parts = [a.get("streetAddress"), a.get("addressLocality"),
                         a.get("addressRegion"), a.get("postalCode")]
                return ", ".join(str(x) for x in parts if x)
            stack.extend(v for v in n.values() if isinstance(v, (dict, list)))
    return None


def download(url, dest, referer=None):
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": UA, "Accept": "image/avif,image/webp,image/*,*/*;q=0.8",
            **({"Referer": referer} if referer else {})})
        with urllib.request.urlopen(req, timeout=25) as r:
            data = r.read()
        if len(data) < 12000:          # thumbnails and tracking pixels
            return False
        io.open(dest, "wb").write(data)
        return True
    except Exception:
        return False


def classify(imgs):
    """Split rendered images into hero candidates and portrait candidates."""
    heroes, people = [], []
    for im in imgs:
        src, w, h = im["src"], im.get("w") or 0, im.get("h") or 0
        if not src or w < 300 or h < 200:
            continue
        blob = src + " " + str(im.get("alt", ""))
        if JUNK.search(blob):
            continue
        ratio = w / h if h else 0
        if ratio >= 1.35 and w >= 900:
            heroes.append((w * h, im))
        elif 0.55 <= ratio <= 1.25 and min(w, h) >= 320 and TEAM_HINT.search(blob):
            people.append((w * h, im))
    heroes.sort(key=lambda t: (-t[0], t[1].get("top", 0)))
    people.sort(key=lambda t: -t[0])
    return [i for _, i in heroes], [i for _, i in people]


def fetch_one(pw, cfg, max_hero=2, max_people=4):
    slug, site = cfg["slug"], cfg["website"]
    d = os.path.join(OUT, slug)
    os.makedirs(d, exist_ok=True)
    man = {"slug": slug, "website": site, "heroes": [], "people": [],
           "address": None, "error": None}
    if not site:
        man["error"] = "no website recorded"
        return man

    b = pw.chromium.launch()
    ctx = b.new_context(user_agent=UA, viewport={"width": 1440, "height": 1000},
                        ignore_https_errors=True)
    try:
        page = ctx.new_page()
        page.goto(site, wait_until="domcontentloaded", timeout=40000)
        page.wait_for_timeout(2500)
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(1800)

        imgs = harvest(page, site)
        man["address"] = schema_address(page)

        # A team page is where the portraits actually live.
        links = page.eval_on_selector_all(
            "a[href]", "els => els.map(e => e.href)") or []
        team = [l for l in links if re.search(
            r"(meet|team|about|our-doctors?|staff|dentists?)", l, re.I)][:2]
        for t in team:
            try:
                page.goto(t, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(2000)
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(1200)
                imgs += harvest(page, t)
                man["address"] = man["address"] or schema_address(page)
            except Exception:
                pass

        seen, uniq = set(), []
        for im in imgs:
            u = abs_url(site, im["src"])
            if not u or u in seen:
                continue
            seen.add(u); im["src"] = u; uniq.append(im)

        heroes, people = classify(uniq)
        for i, im in enumerate(heroes[:max_hero]):
            p = os.path.join(d, f"hero-{i+1}.jpg")
            if download(im["src"], p, site):
                man["heroes"].append({"file": os.path.basename(p), "src": im["src"],
                                      "w": im["w"], "h": im["h"]})
        for i, im in enumerate(people[:max_people]):
            p = os.path.join(d, f"person-{i+1}.jpg")
            if download(im["src"], p, site):
                man["people"].append({"file": os.path.basename(p), "src": im["src"],
                                      "w": im["w"], "h": im["h"]})
    except Exception as e:
        man["error"] = str(e)[:140]
    finally:
        try:
            ctx.close(); b.close()
        except Exception:
            pass

    io.open(os.path.join(d, "manifest.json"), "w", encoding="utf-8").write(
        json.dumps(man, indent=2))
    return man


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--only")
    a = ap.parse_args()

    from playwright.sync_api import sync_playwright
    rows = load()
    if a.only:
        rows = [r for r in rows if r["slug"] == a.only]
    os.makedirs(OUT, exist_ok=True)

    got_h = got_p = got_a = 0
    with sync_playwright() as pw:
        for cfg in rows:
            m = fetch_one(pw, cfg)
            got_h += bool(m["heroes"]); got_p += bool(m["people"]); got_a += bool(m["address"])
            print(f"{cfg['rank']:2} {cfg['slug'][:32]:34} "
                  f"hero {len(m['heroes'])} · people {len(m['people'])} · "
                  f"addr {'yes' if m['address'] else 'no '} "
                  f"{('· ' + m['error']) if m['error'] else ''}")
    print(f"\n{got_h}/{len(rows)} with a hero · {got_p}/{len(rows)} with portraits · "
          f"{got_a}/{len(rows)} with a street address")
