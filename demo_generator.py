#!/usr/bin/env python3
"""
demo_generator.py - turn one lead into a live, personalised demo site.

The operator currently reskins a dental template by hand: ~20 minutes per
prospect. This does the same job in ~20 seconds, and - more importantly -
refuses to ship the ones that would look bad.

    scrape their brand -> pick a template -> reskin -> QUALITY GATE -> deploy

The quality gate is the point. A bad demo is worse than no demo: it proves to
the prospect you cannot do better than what they already have. Anything that
fails the gate goes to demos_needs_review.json and is never deployed.

USAGE
    python demo_generator.py --lead-username drjameslittler
    python demo_generator.py --lead-username drjameslittler --go
    python demo_generator.py --from-queue queue.csv --limit 10
    python demo_generator.py --from-queue queue.csv --limit 10 --go

--dry-run is the DEFAULT. Nothing is created on GitHub without --go.

OUTPUTS
    demos.json                {username: live_url}          <- campaign contract
    demos_meta.json           {username: {full build record}}
    demos_needs_review.json   [{username, reasons, ...}]
    demo_builds/{slug}/       the built site
    assets_cache/{slug}/      scraped page + downloaded assets

SAFETY
    - Deploys only to NEW repos named demo-{slug}, marked with [outreach-demo]
      in the description. If a repo of that name exists and is not ours, the
      lead is skipped loudly. We never push to a repo we did not create.
    - Minimum 3s between gh calls.
    - Never sends email. Never touches campaign_manager.py.
"""

import argparse
import colorsys
import csv
import io
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

try:
    from PIL import Image
    HAVE_PIL = True
except Exception:                                            # pragma: no cover
    HAVE_PIL = False


# --------------------------------------------------------------------------
# paths / constants
# --------------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OWNER = "Milin555"                                  # same as deploy_all.py
LEADS_CSV = os.path.join(BASE_DIR, "data", "dental_leads_targeted.csv")
BUILD_ROOT = os.path.join(BASE_DIR, "demo_builds")
CACHE_ROOT = os.path.join(BASE_DIR, "assets_cache")
DEMOS_JSON = os.path.join(BASE_DIR, "demos.json")
DEMOS_META_JSON = os.path.join(BASE_DIR, "demos_meta.json")
NEEDS_REVIEW_JSON = os.path.join(BASE_DIR, "demos_needs_review.json")

REPO_MARKER = "[outreach-demo]"                     # proves the repo is ours
GH_MIN_INTERVAL = 3.0                               # seconds between gh calls
HTTP_TIMEOUT = 15
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

# A link-in-bio hop is not a website. The lead still has no site of their own.
LINK_IN_BIO_HOSTS = ("linktr.ee", "bit.ly", "linkin.bio", "beacons.ai",
                     "taplink.cc", "taplink.at", "msha.ke", "wa.me",
                     "linktree", "campsite.bio", "solo.to", "lnk.bio",
                     "flowcode.com", "tinyurl.com", "shorturl.at", "cutt.ly",
                     "bio.link", "allmylinks.com", "koji.to", "many.link")

# Hosts that are somebody ELSE'S brand. Scraping these builds a demo out of a
# charity's or a manufacturer's identity and hands it to a dentist - the single
# most embarrassing failure this tool could have.
THIRD_PARTY_HOSTS = (
    # charity / fundraising
    "justgiving.com", "gofundme.com", "mind.org.uk", "cancerresearchuk.org",
    "fundraise.cancerresearchuk.org", "virginmoneygiving.com", "crowdfunder.co.uk",
    "gogetfunding.com", "givey.com", "gettingpersonal.co.uk",
    # manufacturer / brand directories
    "invisalign.co.uk", "invisalign.com", "invisalign.com.au", "straumann.com",
    "alignertech.com", "smilefast.com", "enlightensmiles.com", "boutiquewhitening.com",
    # practice directories / aggregators / review sites
    "yell.com", "yelp.com", "yelp.co.uk", "checkatrade.com", "trustpilot.com",
    "google.com", "goo.gl", "maps.app.goo.gl", "g.page", "business.site",
    "nhs.uk", "healthgrades.com", "zocdoc.com", "whatclinic.com", "topdoctors.co.uk",
    "doctify.com", "bark.com", "thomsonlocal.com", "cylex-uk.co.uk", "freeindex.co.uk",
    "hotfrog.co.uk", "scoot.co.uk", "192.com", "opencare.com", "dentaldepartures.com",
    # booking / social / marketplace
    "eventbrite.co.uk", "eventbrite.com", "calendly.com", "acuityscheduling.com",
    "treatwell.co.uk", "fresha.com", "booksy.com", "phorest.com", "setmore.com",
    "facebook.com", "instagram.com", "twitter.com", "x.com", "linkedin.com",
    "youtube.com", "tiktok.com", "pinterest.com", "etsy.com", "amazon.co.uk",
    "shopify.com", "gumroad.com", "patreon.com", "eventzilla.net",
    # publishing / misc
    "wordpress.com", "blogspot.com", "medium.com", "wixsite.com/blank",
    "sites.google.com", "issuu.com", "dropbox.com", "drive.google.com",
)

SEGMENT_OWN_SITE = "own_site"
SEGMENT_LINK_IN_BIO = "link_in_bio"
SEGMENT_THIRD_PARTY = "third_party_link"
SEGMENT_NO_WEBSITE = "no_website"

# Instagram's public web endpoint. Works without a login as long as the app id
# header is present; this is what makes the 11k no-website leads workable.
IG_APP_ID = "936619743392459"
IG_PROFILE_API = ("https://i.instagram.com/api/v1/users/web_profile_info/"
                  "?username={username}")

STOP_TOKENS = {"the", "and", "dental", "dentist", "dentistry", "clinic", "care",
               "practice", "surgery", "centre", "center", "health", "smile",
               "smiles", "group", "ltd", "limited", "uk", "com", "co", "www",
               "aesthetics", "aesthetic", "medical", "studio", "doctor", "dr"}


def registrable_host(url):
    try:
        host = urllib.parse.urlparse(normalise_url(url)).netloc.lower()
    except Exception:
        return ""
    return host[4:] if host.startswith("www.") else host


def host_core(url):
    """'www.rosedental.co.uk/x' -> 'rosedental'"""
    host = registrable_host(url)
    if not host:
        return ""
    parts = host.split(".")
    multi = {"co", "com", "org", "net", "gov", "ac"}
    if len(parts) >= 3 and parts[-2] in multi:
        return re.sub(r'[^a-z0-9]', '', parts[-3])
    if len(parts) >= 2:
        return re.sub(r'[^a-z0-9]', '', parts[-2])
    return re.sub(r'[^a-z0-9]', '', host)


def identity_tokens(*strings):
    toks = set()
    for s in strings:
        for t in re.split(r'[^a-z0-9]+', (s or "").lower()):
            if len(t) >= 4 and t not in STOP_TOKENS:
                toks.add(t)
    return toks


def domain_plausible(url, *identity_strings):
    """
    Does this domain plausibly belong to this practice? Compares the domain
    core against tokens from the practice name, the IG username and anything
    else we know. Deliberately generous - a false 'implausible' costs us a
    good lead, so we only need ONE signal to agree.
    """
    core = host_core(url)
    if not core:
        return False
    toks = identity_tokens(*identity_strings)
    if not toks:
        return True                       # nothing to compare against
    squashed = "".join(sorted(toks))
    for t in toks:
        if t in core or core in t:
            return True
    # also compare the whole identity string with separators removed
    for s in identity_strings:
        flat = re.sub(r'[^a-z0-9]', '', (s or "").lower())
        if flat and (flat in core or core in flat):
            return True
    del squashed
    return False


def classify_lead(lead):
    """
    (segment, url). Decided BEFORE any scraping, so a third-party link never
    gets its brand assets harvested.
    """
    raw = (lead.get("Website") or "").strip()
    if not raw:
        return SEGMENT_NO_WEBSITE, ""
    url = normalise_url(raw)
    host = registrable_host(url)
    if not host:
        return SEGMENT_NO_WEBSITE, ""
    if any(h in host for h in LINK_IN_BIO_HOSTS):
        return SEGMENT_LINK_IN_BIO, url
    if any(host == h or host.endswith("." + h) or h in host
           for h in THIRD_PARTY_HOSTS):
        return SEGMENT_THIRD_PARTY, url
    return SEGMENT_OWN_SITE, url


FREEMAIL = {"gmail.com", "yahoo.com", "yahoo.co.uk", "hotmail.com", "hotmail.co.uk",
            "outlook.com", "live.com", "icloud.com", "aol.com", "mail.com",
            "btinternet.com", "me.com", "msn.com", "googlemail.com", "protonmail.com"}


def ownership_evidence(lead, brand, html):
    """
    Does this website actually belong to this lead?

    Guessing from the domain name alone is not good enough - 'Dr Goros' trades
    as estedent.co.uk and 'Dr Zamena' as themedicalspa.co.uk, both legitimate.
    So look for hard evidence on the page instead, and only call it a third
    party when NOTHING ties the site to the lead.
    """
    ev = []
    url = brand.get("final_url") or lead.get("Website") or ""
    core = host_core(url)
    low = (html or "").lower()

    email = (lead.get("Email") or "").strip().lower()
    if email and "@" in email:
        dom = email.rsplit("@", 1)[1]
        if dom not in FREEMAIL and host_core("http://" + dom) == core:
            ev.append("lead's email domain is this website's domain")
        if email in low:
            ev.append("the site publishes the lead's email address")

    digits = re.sub(r'\D', '', lead.get("Phone") or "")
    if len(digits) >= 9:
        page_digits = re.sub(r'\D', '', low)
        if digits[-9:] in page_digits:
            ev.append("the site publishes the lead's phone number")

    user = (lead.get("Username") or "").strip().lower()
    if user and f"instagram.com/{user}" in low:
        ev.append("the site links to the lead's Instagram account")

    if domain_plausible(url, lead.get("Name"), lead.get("Username"),
                        brand.get("name")):
        ev.append("domain matches the practice or account name")

    if brand.get("name") and identity_tokens(brand["name"]) & identity_tokens(
            lead.get("Name"), lead.get("Username")):
        ev.append("scraped business name matches the lead")

    return ev


# --------------------------------------------------------------------------
# console safety - cp1252 console, never let a unicode char kill the run
# --------------------------------------------------------------------------

def say(msg=""):
    try:
        print(msg)
    except UnicodeEncodeError:
        print(str(msg).encode("ascii", "replace").decode("ascii"))
    sys.stdout.flush()


def warn(msg):
    say("    ! " + str(msg))


# --------------------------------------------------------------------------
# subprocess helper - same shape as deploy_all.py run()
# --------------------------------------------------------------------------

_last_gh_call = [0.0]


def run(cmd, cwd=None, timeout=180):
    """Run a command, hand back (ok, output). Mirrors deploy_all.run()."""
    try:
        res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                             timeout=timeout, shell=False,
                             encoding="utf-8", errors="replace")
        out = (res.stdout or "") + (res.stderr or "")
        return res.returncode == 0, out.strip()
    except subprocess.TimeoutExpired:
        return False, "timed out"
    except FileNotFoundError:
        return False, f"command not found: {cmd[0]}"


def gh(args, cwd=None, timeout=180):
    """Rate-limited gh call. Never less than GH_MIN_INTERVAL between calls."""
    wait = GH_MIN_INTERVAL - (time.time() - _last_gh_call[0])
    if wait > 0:
        time.sleep(wait)
    ok, out = run(["gh"] + args, cwd=cwd, timeout=timeout)
    _last_gh_call[0] = time.time()
    return ok, out


# --------------------------------------------------------------------------
# colour maths
# --------------------------------------------------------------------------

def hex_to_rgb(h):
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) == 8:                                  # #rrggbbaa
        h = h[:6]
    if len(h) != 6:
        return None
    try:
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        return None


def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*(max(0, min(255, int(round(c))))
                                          for c in rgb))


def rgb_to_hls(rgb):
    r, g, b = (c / 255.0 for c in rgb)
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return h, l, s


def hls_to_hex(h, l, s):
    r, g, b = colorsys.hls_to_rgb(h % 1.0, max(0.0, min(1.0, l)),
                                  max(0.0, min(1.0, s)))
    return rgb_to_hex((r * 255, g * 255, b * 255))


def rel_luminance(rgb):
    def ch(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(hex_a, hex_b):
    """WCAG contrast ratio between two hex colours. 1.0 .. 21.0"""
    ra, rb = hex_to_rgb(hex_a), hex_to_rgb(hex_b)
    if not ra or not rb:
        return 0.0
    la, lb = rel_luminance(ra), rel_luminance(rb)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def is_neutral(hex_c, sat_floor=0.15):
    """White, black or grey - i.e. carries no brand signal."""
    rgb = hex_to_rgb(hex_c)
    if not rgb:
        return True
    _, l, s = rgb_to_hls(rgb)
    return s < sat_floor or l > 0.94 or l < 0.05


def darken_to_contrast(hex_c, against="#ffffff", target=4.5,
                       l_floor=0.06, l_ceiling=0.45):
    """
    Keep the brand hue+saturation, walk lightness down until it reads as text
    on `against`. Returns (hex, achieved_contrast). If the hue cannot reach
    `target` inside the allowed lightness band, returns the best it managed so
    the gate can reject it honestly rather than silently faking a pass.
    """
    rgb = hex_to_rgb(hex_c)
    if not rgb:
        return "#111111", contrast("#111111", against)
    h, _, s = rgb_to_hls(rgb)
    s = max(0.12, min(0.92, s))
    best, best_c = None, -1.0
    l = l_ceiling
    while l >= l_floor - 1e-9:
        cand = hls_to_hex(h, l, s)
        c = contrast(cand, against)
        if c > best_c:
            best, best_c = cand, c
        if c >= target:
            return cand, c
        l -= 0.01
    return best, best_c


def accent_shade(hex_c, light_bg="#ffffff", dark_bg="#0b1f22", floor=3.0):
    """
    Accent has to survive on BOTH surfaces - the template paints primary-500
    on white cards and on the dark hero. Find the lightness that maximises the
    weaker of the two contrasts.
    """
    rgb = hex_to_rgb(hex_c)
    if not rgb:
        return "#1c91a1"
    h, _, s = rgb_to_hls(rgb)
    s = max(0.30, min(0.95, s))
    best, best_score = None, -1.0
    l = 0.20
    while l <= 0.62:
        cand = hls_to_hex(h, l, s)
        score = min(contrast(cand, light_bg), contrast(cand, dark_bg))
        if score > best_score:
            best, best_score = cand, score
        l += 0.01
    return best


def build_palette(primary_hex, accent_hex):
    """
    Map two scraped brand colours onto the template's token ramp.

    primary-900 is BOTH the body text colour on white AND the hero/footer
    background behind white text, so it has to be genuinely dark - the stock
    template ships #011f23, about 18:1 against white. Deriving it at only the
    4.5:1 minimum produces a washed-out mid-tone hero AND squeezes the accent
    into a band where it cannot contrast with either surface. Aim for 10:1.
    """
    p900, c900 = darken_to_contrast(primary_hex, "#ffffff", target=10.0,
                                    l_floor=0.05, l_ceiling=0.26)
    h9, l9, s9 = rgb_to_hls(hex_to_rgb(p900))

    p800 = hls_to_hex(h9, max(0.04, l9 - 0.03), s9)
    p700 = hls_to_hex(h9, min(0.30, l9 + 0.06), s9 * 0.95)

    p500 = accent_shade(accent_hex or primary_hex, "#ffffff", p900)
    h5, l5, s5 = rgb_to_hls(hex_to_rgb(p500))
    p600 = hls_to_hex(h5, max(0.10, l5 - 0.07), s5)
    p400 = hls_to_hex(h5, min(0.72, l5 + 0.14), s5 * 0.62)

    # tinted neutrals so even the pale surfaces feel like their brand
    n50 = hls_to_hex(h5, 0.965, min(0.55, s5 * 0.55))
    n100 = hls_to_hex(h5, 0.955, min(0.45, s5 * 0.45))
    n200 = hls_to_hex(h5, 0.925, min(0.42, s5 * 0.42))
    n300 = hls_to_hex(h5, 0.875, min(0.38, s5 * 0.38))

    return {
        "primary-900": p900, "primary-800": p800, "primary-700": p700,
        "primary-600": p600, "primary-500": p500, "primary-400": p400,
        "neutral-50": n50, "neutral-100": n100,
        "neutral-200": n200, "neutral-300": n300,
        "_contrast_text_on_white": round(c900, 2),
        "_contrast_white_on_hero": round(contrast("#ffffff", p900), 2),
        "_contrast_accent_on_white": round(contrast(p500, "#ffffff"), 2),
        "_contrast_accent_on_hero": round(contrast(p500, p900), 2),
    }


# --------------------------------------------------------------------------
# image helpers
# --------------------------------------------------------------------------

SVG_DIM_RE = re.compile(rb'(?:width|height)\s*=\s*["\']?\s*([0-9.]+)', re.I)
SVG_VIEWBOX_RE = re.compile(
    rb'viewBox\s*=\s*["\']\s*[-0-9.]+[,\s]+[-0-9.]+[,\s]+([0-9.]+)[,\s]+([0-9.]+)',
    re.I)


def image_dims(data, url=""):
    """(width, height) for raster via PIL, or parsed out of the SVG source."""
    if data[:200].lstrip()[:5].lower().startswith(b"<?xml") or b"<svg" in data[:600].lower():
        m = SVG_VIEWBOX_RE.search(data[:4000])
        if m:
            try:
                return int(float(m.group(1))), int(float(m.group(2)))
            except ValueError:
                pass
        dims = SVG_DIM_RE.findall(data[:1500])
        if len(dims) >= 2:
            try:
                return int(float(dims[0])), int(float(dims[1]))
            except ValueError:
                pass
        return 512, 512                    # vector: resolution independent
    if not HAVE_PIL:
        return 0, 0
    try:
        im = Image.open(io.BytesIO(data))
        return im.size
    except Exception:
        return 0, 0


def is_svg(data, url=""):
    head = data[:600].lower()
    return b"<svg" in head or url.lower().split("?")[0].endswith(".svg")


def image_profile(data):
    """
    (mean_luminance, dominant_non_neutral_hex, alpha_fraction) for a raster.
    Used to decide whether a logo needs a light chip behind it, and to mine the
    logo for the brand colour - usually a better signal than the CSS.
    """
    if not HAVE_PIL:
        return 0.5, None, 0.0
    try:
        im = Image.open(io.BytesIO(data))
        im = im.convert("RGBA")
        im.thumbnail((120, 120))
        px = list(im.getdata())
    except Exception:
        return 0.5, None, 0.0

    opaque = [p for p in px if p[3] > 40]
    if not opaque:
        return 0.5, None, 1.0
    alpha_frac = 1.0 - (len(opaque) / max(1, len(px)))

    lum = sum(rel_luminance(p[:3]) for p in opaque) / len(opaque)

    buckets = {}
    for r, g, b, _a in opaque:
        hx = rgb_to_hex((r, g, b))
        if is_neutral(hx, sat_floor=0.22):
            continue
        key = rgb_to_hex((r // 24 * 24 + 12, g // 24 * 24 + 12, b // 24 * 24 + 12))
        buckets[key] = buckets.get(key, 0) + 1
    dominant = None
    if buckets:
        dominant = max(buckets.items(), key=lambda kv: kv[1])[0]
        # only trust it if it is a real presence, not a stray antialias pixel
        if buckets[dominant] < len(opaque) * 0.02:
            dominant = None
    return lum, dominant, alpha_frac


# --------------------------------------------------------------------------
# scraping
# --------------------------------------------------------------------------

# Names that are really a CMS default, not a business. Wix ships "Mysite",
# WordPress ships "Just another WordPress site" - shipping either as the
# prospect's brand (and as the repo slug) is worse than not shipping.
GENERIC_NAME_WORDS = {
    "home", "welcome", "index", "untitled", "dentist", "dental", "clinic",
    "website", "coming soon", "under construction", "page", "default",
    "mysite", "my site", "site", "home page", "homepage", "new page",
    "untitled page", "wix site", "my website", "new site", "test",
    "just another wordpress site", "web page", "landing page",
    "domain default page", "parked domain", "index of",
}

SERVICE_VOCAB = [
    ("Dental Implants", ["implant"]),
    ("Teeth Whitening", ["whiten", "bleach"]),
    ("Porcelain Veneers", ["veneer"]),
    ("Invisalign", ["invisalign", "clear aligner", "aligner"]),
    ("Orthodontics", ["orthodont", "braces"]),
    ("Composite Bonding", ["bonding", "composite"]),
    ("Root Canal Treatment", ["root canal", "endodont"]),
    ("Crowns & Bridges", ["crown", "bridge"]),
    ("Dentures", ["denture"]),
    ("Hygiene & Cleaning", ["hygien", "scale and polish", "cleaning"]),
    ("Preventive Dentistry", ["preventive", "preventative", "check-up", "checkup"]),
    ("Cosmetic Dentistry", ["cosmetic", "smile makeover"]),
    ("Emergency Dentistry", ["emergency"]),
    ("Facial Aesthetics", ["facial aesthetic", "botox", "dermal filler", "anti-wrinkle"]),
    ("Children's Dentistry", ["children", "paediatric", "pediatric", "kids"]),
    ("Periodontics", ["periodont", "gum disease"]),
    ("Oral Surgery", ["oral surgery", "extraction", "wisdom tooth"]),
    ("Sedation Dentistry", ["sedation", "nervous patient"]),
]

# Meta descriptions that are the CMS's placeholder, not the practice's words.
# Shipping "Dr Nikita BDS | Name of your web site" as the demo title is exactly
# the kind of thing that makes a prospect think you did not look at it.
GENERIC_TEXT_MARKERS = (
    "name of your web site", "site description", "your description here",
    "just another wordpress site", "add a description", "description goes here",
    "this is my site description", "an awesome website", "my blog",
    "web site created using", "enter your description", "sample description",
    "lorem ipsum", "coming soon", "under construction", "default description",
    "website description", "insert your description", "page description",
    "welcome to our website", "welcome to my website", "wix website",
    "html5 template", "free website template", "bootstrap template",
)


def is_generic_text(text):
    low = (text or "").strip().lower()
    if not low or len(low) < 4:
        return True
    return any(m in low for m in GENERIC_TEXT_MARKERS)


PHONE_RE = re.compile(
    r'(?:\+?\d{1,3}[\s.\-]?)?(?:\(\d{2,5}\)|\d{2,5})[\s.\-]?\d{3,4}[\s.\-]?\d{3,4}')
EMAIL_RE = re.compile(r'[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}')


def normalise_url(raw):
    raw = (raw or "").strip()
    if not raw:
        return ""
    if not raw.startswith(("http://", "https://")):
        raw = "http://" + raw
    return raw


def session():
    s = requests.Session()
    s.headers.update({"User-Agent": UA,
                      "Accept-Language": "en-GB,en;q=0.9",
                      # brotli is not in the stdlib and a surprising number of
                      # sites serve it; asking for gzip only avoids a decode
                      # failure that would look like an unreachable site
                      "Accept-Encoding": "gzip, deflate",
                      "Accept": "text/html,application/xhtml+xml,*/*;q=0.8"})
    return s


def fetch(sess, url, binary=False, timeout=HTTP_TIMEOUT, max_bytes=6_000_000):
    try:
        r = sess.get(url, timeout=timeout, allow_redirects=True,
                     stream=binary, verify=True)
    except requests.exceptions.SSLError:
        try:                                   # expired certs are common here
            r = sess.get(url, timeout=timeout, allow_redirects=True,
                         stream=binary, verify=False)
        except Exception:
            return None
    except Exception:
        return None
    if r.status_code >= 400:
        return None
    if binary:
        buf = b""
        for chunk in r.iter_content(65536):
            buf += chunk
            if len(buf) > max_bytes:
                break
        r._demo_bytes = buf
    return r


class Brand(dict):
    """Plain dict so it serialises straight to JSON."""
    __getattr__ = dict.get


def _clean_name(txt):
    if not txt:
        return ""
    txt = re.sub(r'\s+', ' ', txt).strip()
    txt = txt.strip(' -|:–—·')
    return txt


def name_from_title(title):
    """Titles are 'Brand | Tagline' or 'Tagline - Brand'. Take the brandy half."""
    if not title:
        return ""
    parts = [p.strip() for p in re.split(r'\s*[|–—·•]\s*|\s+-\s+', title) if p.strip()]
    if not parts:
        return ""
    cands = [p for p in parts if 2 < len(p) <= 60]
    if not cands:
        return _clean_name(parts[0])[:60]
    # prefer the shortest chunk that is not a pure generic word
    cands.sort(key=len)
    for c in cands:
        if c.lower() not in GENERIC_NAME_WORDS:
            return _clean_name(c)
    return _clean_name(cands[0])


def extract_colours_from_css(text, weights):
    """Tally every colour in a CSS blob, weighting brand-ish properties up."""
    for m in re.finditer(r'(background(?:-color)?|border(?:-color)?|fill|stroke|color)\s*:\s*([^;{}]{1,120})',
                         text, re.I):
        prop, val = m.group(1).lower(), m.group(2)
        w = 3 if prop.startswith("background") else 2
        for hx in re.findall(r'#[0-9a-fA-F]{3,8}\b', val):
            c = hex_to_rgb(hx)
            if c:
                weights[rgb_to_hex(c)] = weights.get(rgb_to_hex(c), 0) + w
        for r_, g_, b_ in re.findall(r'rgba?\(\s*(\d{1,3})\s*[, ]\s*(\d{1,3})\s*[, ]\s*(\d{1,3})', val):
            hx = rgb_to_hex((int(r_), int(g_), int(b_)))
            weights[hx] = weights.get(hx, 0) + w


def score_logo_candidate(url, source, w, h, data):
    """Higher is better."""
    score = 0.0
    src_score = {"img-logo": 60, "link-logo": 50, "apple-touch-icon": 30,
                 "mask-icon": 28, "og-image": 18, "icon": 12, "header-img": 22}
    score += src_score.get(source, 5)
    low = url.lower()
    if "logo" in low:
        score += 25
    if is_svg(data, url):
        score += 40
    elif low.split("?")[0].endswith(".png"):
        score += 18
    elif low.split("?")[0].endswith((".jpg", ".jpeg")):
        score += 6
    elif low.split("?")[0].endswith(".ico"):
        score -= 25
    score += min(30, max(w, h) / 20.0)
    if max(w, h) < 100:
        score -= 60
    if "favicon" in low:
        score -= 12
    if w and h and (w / max(h, 1) > 12 or h / max(w, 1) > 12):
        score -= 30                              # a rule, not a logo
    return score


def scrape_brand(lead, cache_dir, refresh=False, segment=None):
    """
    Everything we can learn about this practice from their own website.
    Returns a Brand dict. Never raises - a dead site is data, not an error.
    """
    os.makedirs(cache_dir, exist_ok=True)
    cache_file = os.path.join(cache_dir, "brand.json")
    if os.path.exists(cache_file) and not refresh:
        try:
            with open(cache_file, encoding="utf-8") as fh:
                cached = Brand(json.load(fh))
            if cached.get("_schema") == 3:
                return cached
        except Exception:
            pass

    brand = Brand({
        "_schema": 3,
        "username": lead.get("Username", ""),
        "lead_name": lead.get("Name", ""),
        "website": lead.get("Website", ""),
        "country": lead.get("Country", ""),
        "reachable": False, "final_url": "", "name": "", "tagline": "",
        "phone": "", "email": "", "address": "", "services": [],
        "primary": "", "accent": "", "colour_source": "",
        "logo_file": "", "logo_w": 0, "logo_h": 0, "logo_source": "",
        "logo_is_dark": False, "logo_alpha": 0.0,
        "hero_file": "", "hero_w": 0, "hero_h": 0,
        "photos": [], "usable_images": 0,
        "instagram_used": False, "notes": [],
        "segment": segment or SEGMENT_OWN_SITE,
        "scraped_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    })

    if segment is None:
        segment, _ = classify_lead(lead)
        brand["segment"] = segment

    url = normalise_url(lead.get("Website", ""))
    if segment == SEGMENT_NO_WEBSITE:
        brand["notes"].append("lead has no website - building from Instagram only")
        url = ""
    elif segment == SEGMENT_LINK_IN_BIO:
        brand["notes"].append(
            f"website is a link-in-bio hop ({registrable_host(url)}), not their "
            f"own site - building from Instagram only")
        url = ""
    elif segment == SEGMENT_THIRD_PARTY:
        brand["notes"].append(
            f"website points at a third party ({registrable_host(url)}) that does "
            f"not belong to this practice - NOT scraping it")
        url = ""

    sess = session()
    soup, html, base = None, "", ""

    if url:
        r = fetch(sess, url)
        if r is None and url.startswith("http://"):
            r = fetch(sess, "https://" + url[7:])
        if r is not None:
            brand["reachable"] = True
            brand["final_url"] = r.url
            base = r.url
            html = r.text or ""
            try:
                with open(os.path.join(cache_dir, "page.html"), "w",
                          encoding="utf-8") as fh:
                    fh.write(html)
            except Exception:
                pass
            soup = BeautifulSoup(html, "lxml")
        else:
            brand["notes"].append(f"site unreachable: {url}")

    # ---- text facts -----------------------------------------------------
    if soup is not None:
        title = soup.title.get_text() if soup.title else ""
        og_site = soup.find("meta", property="og:site_name")
        og_title = soup.find("meta", property="og:title")
        desc = soup.find("meta", attrs={"name": "description"})
        og_desc = soup.find("meta", property="og:description")

        # schema.org is the most reliable source when present
        ld_name = ld_phone = ld_addr = ""
        for tag in soup.find_all("script", type="application/ld+json"):
            try:
                blob = json.loads(tag.string or "{}")
            except Exception:
                continue
            stack = blob if isinstance(blob, list) else [blob]
            while stack:
                node = stack.pop()
                if isinstance(node, list):
                    stack.extend(node)
                    continue
                if not isinstance(node, dict):
                    continue
                if "@graph" in node:
                    stack.extend(node["@graph"] if isinstance(node["@graph"], list) else [node["@graph"]])
                t = str(node.get("@type", "")).lower()
                if any(k in t for k in ("dentist", "localbusiness", "organization",
                                        "medicalbusiness", "health")):
                    ld_name = ld_name or _clean_name(str(node.get("name", "")))
                    ld_phone = ld_phone or str(node.get("telephone", "") or "")
                    addr = node.get("address")
                    if isinstance(addr, dict) and not ld_addr:
                        bits = [addr.get("streetAddress"), addr.get("addressLocality"),
                                addr.get("addressRegion"), addr.get("postalCode")]
                        ld_addr = _clean_name(", ".join(
                            _clean_name(str(b)) for b in bits if b))
                    elif isinstance(addr, str) and not ld_addr:
                        ld_addr = _clean_name(addr)

        name = (ld_name
                or _clean_name(og_site["content"] if og_site and og_site.get("content") else "")
                or name_from_title(title)
                or name_from_title(og_title["content"] if og_title and og_title.get("content") else ""))
        if not name or name.lower().strip() in GENERIC_NAME_WORDS:
            h1 = soup.find("h1")
            cand = _clean_name(h1.get_text()) if h1 else ""
            if cand and cand.lower().strip() not in GENERIC_NAME_WORDS:
                name = cand
            else:
                brand["notes"].append(
                    f"site title is a CMS default ('{name or cand}') - falling "
                    f"back to the lead record")
                name = ""
        brand["name"] = (name or "")[:120]

        tag = ""
        for src in (desc, og_desc):
            if src and src.get("content"):
                tag = _clean_name(src["content"])
                break
        if not tag:
            h2 = soup.find(["h2", "h3"])
            tag = _clean_name(h2.get_text()) if h2 else ""
        tag = re.split(r'(?<=[.!?])\s+', tag)[0] if tag else ""
        if is_generic_text(tag):
            brand["notes"].append(
                f"meta description is a CMS default ('{tag[:40]}') - dropped")
            tag = ""
        brand["tagline"] = tag[:160]

        # phone: tel: links win, then visible text
        tels = []
        for a in soup.select('a[href^="tel:"]'):
            t = urllib.parse.unquote(a["href"][4:]).strip()
            if len(re.sub(r'\D', '', t)) >= 7:
                tels.append(t)
        page_text = soup.get_text(" ", strip=True)
        if not tels:
            for m in PHONE_RE.finditer(page_text[:20000]):
                cand = m.group(0).strip()
                digits = re.sub(r'\D', '', cand)
                if 9 <= len(digits) <= 15:
                    tels.append(cand)
                    break
        brand["phone"] = _clean_name(ld_phone or (tels[0] if tels else ""))

        mails = [urllib.parse.unquote(a["href"][7:]).split("?")[0].strip()
                 for a in soup.select('a[href^="mailto:"]')]
        mails = [m for m in mails if EMAIL_RE.fullmatch(m)]
        if not mails:
            mails = [m for m in EMAIL_RE.findall(page_text[:30000])
                     if not m.lower().endswith((".png", ".jpg", ".gif", ".webp"))]
        brand["email"] = mails[0] if mails else ""

        addr = ld_addr
        if not addr:
            a_tag = soup.find("address")
            if a_tag:
                addr = _clean_name(a_tag.get_text(" ", strip=True))
        brand["address"] = _clean_name(addr)[:160]

        # services from nav + headings + link text
        hay = " ".join(
            [a.get_text(" ", strip=True) for a in soup.find_all("a")][:400] +
            [h.get_text(" ", strip=True) for h in soup.find_all(["h1", "h2", "h3", "h4"])][:120]
        ).lower()
        found = []
        for label, keys in SERVICE_VOCAB:
            if any(k in hay for k in keys):
                found.append(label)
        brand["services"] = found[:8]

    if soup is not None and segment == SEGMENT_OWN_SITE:
        brand["ownership_evidence"] = ownership_evidence(lead, brand, html)
        if not brand["ownership_evidence"]:
            brand["segment"] = segment = SEGMENT_THIRD_PARTY
            brand["notes"].append(
                f"nothing on {registrable_host(brand.get('final_url') or '')} ties "
                f"it to this lead - treating as a third-party link")

    # fall back to the CSV for contact details the site did not give up
    if not brand["phone"] and lead.get("Phone"):
        brand["phone"] = _clean_name(lead["Phone"])
        brand["notes"].append("phone from lead CSV")
    if not brand["email"] and lead.get("Email"):
        brand["email"] = lead["Email"].strip()
        brand["notes"].append("email from lead CSV")
    if not brand["name"] and lead.get("Name"):
        brand["name"] = _clean_name(lead["Name"])
        brand["notes"].append("name from lead CSV")

    # ---- colours --------------------------------------------------------
    weights = {}
    theme_hex = ""
    if soup is not None:
        tc = soup.find("meta", attrs={"name": "theme-color"})
        if tc and tc.get("content"):
            rgb = hex_to_rgb(tc["content"])
            if rgb:
                theme_hex = rgb_to_hex(rgb)

        for st in soup.find_all("style"):
            extract_colours_from_css(st.string or "", weights)
        for el in soup.select("[style]")[:600]:
            extract_colours_from_css(el.get("style", ""), weights)

        sheets = []
        for link in soup.find_all("link", rel=True):
            rels = [r.lower() for r in (link.get("rel") or [])]
            if "stylesheet" in rels and link.get("href"):
                sheets.append(urllib.parse.urljoin(base, link["href"]))
        for href in sheets[:5]:
            if "font" in href.lower():
                continue
            rr = fetch(sess, href, timeout=10)
            if rr is not None and rr.text:
                extract_colours_from_css(rr.text[:900000], weights)

    # ---- logo -----------------------------------------------------------
    candidates = []                                   # (url, source)
    if soup is not None:
        for img in soup.find_all("img"):
            blob = " ".join(filter(None, [
                img.get("src", ""), img.get("alt", ""), img.get("title", ""),
                " ".join(img.get("class") or []), img.get("id", "")])).lower()
            src = img.get("src") or img.get("data-src") or ""
            if not src or src.startswith("data:"):
                continue
            full = urllib.parse.urljoin(base, src)
            if "logo" in blob or "brand" in blob:
                candidates.append((full, "img-logo"))
        header = soup.find(["header", "nav"])
        if header:
            for img in header.find_all("img")[:4]:
                src = img.get("src") or img.get("data-src") or ""
                if src and not src.startswith("data:"):
                    candidates.append((urllib.parse.urljoin(base, src), "header-img"))
        for link in soup.find_all("link", rel=True):
            rels = " ".join(link.get("rel") or []).lower()
            href = link.get("href")
            if not href:
                continue
            full = urllib.parse.urljoin(base, href)
            if "apple-touch-icon" in rels:
                candidates.append((full, "apple-touch-icon"))
            elif "mask-icon" in rels:
                candidates.append((full, "mask-icon"))
            elif "icon" in rels:
                candidates.append((full, "logo" in href.lower() and "link-logo" or "icon"))
        og_img = soup.find("meta", property="og:image")
        if og_img and og_img.get("content"):
            candidates.append((urllib.parse.urljoin(base, og_img["content"]), "og-image"))
        if base:
            candidates.append((urllib.parse.urljoin(base, "/favicon.ico"), "icon"))

    seen, uniq = set(), []
    for u, s in candidates:
        if u in seen:
            continue
        seen.add(u)
        uniq.append((u, s))
    uniq = uniq[:10]

    best = None
    if uniq:
        with ThreadPoolExecutor(max_workers=6) as pool:
            futs = {pool.submit(fetch, sess, u, True, 12): (u, s) for u, s in uniq}
            for fut in as_completed(futs):
                u, s = futs[fut]
                try:
                    rr = fut.result()
                except Exception:
                    rr = None
                if rr is None:
                    continue
                data = getattr(rr, "_demo_bytes", b"")
                if len(data) < 90:
                    continue
                w, h = image_dims(data, u)
                sc = score_logo_candidate(u, s, w, h, data)
                if best is None or sc > best[0]:
                    best = (sc, u, s, w, h, data)

    if best:
        _sc, u, s, w, h, data = best
        ext = ".svg" if is_svg(data, u) else os.path.splitext(
            urllib.parse.urlparse(u).path)[1].lower() or ".png"
        if ext not in (".svg", ".png", ".jpg", ".jpeg", ".webp", ".gif", ".ico"):
            ext = ".png"
        if ext == ".ico" and HAVE_PIL:                 # convert ico -> png
            try:
                im = Image.open(io.BytesIO(data)).convert("RGBA")
                buf = io.BytesIO()
                im.save(buf, "PNG")
                data, ext = buf.getvalue(), ".png"
                w, h = im.size
            except Exception:
                pass
        path = os.path.join(cache_dir, "logo" + ext)
        with open(path, "wb") as fh:
            fh.write(data)
        brand["logo_file"] = path
        brand["logo_w"], brand["logo_h"] = w, h
        brand["logo_source"] = s
        brand["logo_url"] = u
        if ext != ".svg":
            lum, dom, alpha = image_profile(data)
            brand["logo_is_dark"] = lum < 0.45
            brand["logo_alpha"] = round(alpha, 3)
            if dom and not is_neutral(dom, 0.22):
                weights[dom] = weights.get(dom, 0) + 40      # trust the logo
                brand["colour_source"] = "logo"
        else:
            svg_txt = data.decode("utf-8", "replace")
            brand["logo_is_dark"] = False
            for hx in re.findall(r'#[0-9a-fA-F]{3,6}\b', svg_txt[:20000]):
                rgb = hex_to_rgb(hx)
                if rgb and not is_neutral(rgb_to_hex(rgb), 0.22):
                    weights[rgb_to_hex(rgb)] = weights.get(rgb_to_hex(rgb), 0) + 25
                    brand["colour_source"] = "logo-svg"
    else:
        brand["notes"].append("no logo candidate downloaded")

    # decide primary + accent
    if theme_hex and not is_neutral(theme_hex, 0.18):
        weights[theme_hex] = weights.get(theme_hex, 0) + 35
        brand["colour_source"] = brand["colour_source"] or "theme-color"

    chromatic = {c: w for c, w in weights.items() if not is_neutral(c, 0.16)}
    if chromatic:
        ranked = sorted(chromatic.items(), key=lambda kv: -kv[1])
        primary = ranked[0][0]
        ph, _pl, _ps = rgb_to_hls(hex_to_rgb(primary))
        accent = ""
        for c, _w in ranked[1:]:
            ch, _cl, _cs = rgb_to_hls(hex_to_rgb(c))
            if min(abs(ch - ph), 1 - abs(ch - ph)) > 0.06:
                accent = c
                break
        brand["primary"] = primary
        brand["accent"] = accent or primary
        brand["colour_source"] = brand["colour_source"] or "css"
        brand["colour_candidates"] = [{"hex": c, "weight": w} for c, w in ranked[:8]]
    else:
        brand["colour_candidates"] = []
        brand["notes"].append("no non-neutral colour found on site")

    # ---- photos ---------------------------------------------------------
    photo_urls = []
    if soup is not None:
        for img in soup.find_all("img"):
            src = (img.get("src") or img.get("data-src") or "")
            if not src or src.startswith("data:"):
                continue
            blob = (src + " " + " ".join(img.get("class") or []) + " " +
                    (img.get("alt") or "")).lower()
            if "logo" in blob or "icon" in blob or "sprite" in blob:
                continue
            photo_urls.append(urllib.parse.urljoin(base, src))
        for m in re.finditer(r'background-image\s*:\s*url\((["\']?)([^)"\']+)\1\)',
                             html or "", re.I):
            u = m.group(2)
            if not u.startswith("data:"):
                photo_urls.append(urllib.parse.urljoin(base, u))
        og_img = soup.find("meta", property="og:image")
        if og_img and og_img.get("content"):
            photo_urls.append(urllib.parse.urljoin(base, og_img["content"]))

    photo_urls = list(dict.fromkeys(photo_urls))[:18]
    photos = []
    if photo_urls:
        with ThreadPoolExecutor(max_workers=8) as pool:
            futs = {pool.submit(fetch, sess, u, True, 12): u for u in photo_urls}
            for fut in as_completed(futs):
                u = futs[fut]
                try:
                    rr = fut.result()
                except Exception:
                    rr = None
                if rr is None:
                    continue
                data = getattr(rr, "_demo_bytes", b"")
                if len(data) < 4000 or is_svg(data, u):
                    continue
                w, h = image_dims(data, u)
                if w < 400 or h < 250:
                    continue
                photos.append({"url": u, "w": w, "h": h, "bytes": len(data),
                               "data": data})

    photos.sort(key=lambda p: -(p["w"] * p["h"]))
    saved = []
    for i, p in enumerate(photos[:6]):
        ext = os.path.splitext(urllib.parse.urlparse(p["url"]).path)[1].lower()
        if ext not in (".jpg", ".jpeg", ".png", ".webp"):
            ext = ".jpg"
        path = os.path.join(cache_dir, f"photo{i}{ext}")
        try:
            with open(path, "wb") as fh:
                fh.write(p["data"])
        except Exception:
            continue
        saved.append({"file": path, "url": p["url"], "w": p["w"], "h": p["h"]})
    brand["photos"] = saved
    brand["usable_images"] = len(saved)

    hero = next((p for p in saved if p["w"] >= 800 and p["w"] >= p["h"] * 1.15), None)
    if hero:
        brand["hero_file"] = hero["file"]
        brand["hero_w"], brand["hero_h"] = hero["w"], hero["h"]

    # ---- Instagram fallback --------------------------------------------
    need_logo = not brand.get("logo_file")
    if lead.get("Username") and (brand["usable_images"] < 2 or need_logo
                                 or segment != SEGMENT_OWN_SITE):
        scrape_instagram(sess, lead["Username"], cache_dir, brand,
                         want_logo=need_logo)
        brand["instagram_used"] = True

    try:
        with open(cache_file, "w", encoding="utf-8") as fh:
            json.dump(brand, fh, indent=2, ensure_ascii=False)
    except Exception:
        pass
    return brand


def ig_profile(username, timeout=20, tries=2):
    """
    Instagram's public web_profile_info endpoint. No login needed, but the
    x-ig-app-id header is mandatory or it 400s.

    Measured on a random 30-lead sample of the no-website segment:
      200 usable ......... 47%   (37% of all leads also had >=2 post photos)
      400 server error ... 37%   persistent per-account, not rate limiting,
                                 not fixable without an authenticated session
      404 gone ........... 17%   account deleted or renamed since the scrape

    Set IG_SESSIONID in the environment to send a logged-in cookie, which
    lifts the 400s. Returns (user_dict_or_None, human_readable_status).
    """
    s = requests.Session()
    s.headers.update({
        "User-Agent": UA, "Accept": "*/*", "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-GB,en;q=0.9", "x-ig-app-id": IG_APP_ID,
        "Referer": "https://www.instagram.com/",
    })
    sid = os.environ.get("IG_SESSIONID", "").strip()
    if sid:
        s.cookies.set("sessionid", sid, domain=".instagram.com")

    last = "no response"
    for attempt in range(tries):
        try:
            r = s.get(IG_PROFILE_API.format(username=urllib.parse.quote(username)),
                      timeout=timeout)
        except Exception as e:
            last = f"network error ({type(e).__name__})"
            time.sleep(1.5 * (attempt + 1))
            continue
        if r.status_code == 200:
            try:
                user = r.json().get("data", {}).get("user")
            except Exception:
                return None, "instagram returned malformed JSON"
            if user:
                return user, "ok"
            return None, "instagram returned an empty profile"
        if r.status_code == 404:
            return None, ("instagram account no longer exists under this "
                          "username (404) - the lead data is stale")
        if r.status_code == 400:
            return None, ("instagram refuses this profile to anonymous clients "
                          "(400). Set IG_SESSIONID to read it" if not sid else
                          "instagram rejected the request even with IG_SESSIONID")
        if r.status_code in (401, 403):
            return None, f"instagram denied access ({r.status_code})"
        last = f"instagram HTTP {r.status_code}"
        time.sleep(1.5 * (attempt + 1))
    return None, last


def looks_like_logo(data):
    """
    A profile picture is often a photograph of the dentist, not a logo. Logos
    are flat: few distinct colours, often a lot of transparent or uniform
    background. Photographs are not. Returns (is_logo, distinct_colour_count).
    """
    if not HAVE_PIL:
        return True, 0
    try:
        im = Image.open(io.BytesIO(data)).convert("RGB")
        im.thumbnail((96, 96))
        px = list(im.getdata())
    except Exception:
        return True, 0
    buckets = set()
    for r, g, b in px:
        buckets.add((r // 32, g // 32, b // 32))
    return len(buckets) <= 45, len(buckets)


def scrape_instagram(sess, username, cache_dir, brand, want_logo=False):
    """
    Build brand assets straight from Instagram. This is the ONLY source for the
    ~11k leads with no website or only a link-in-bio, so it has to do real work:
    display name, bio, profile picture and recent post photos.
    """
    user, status = ig_profile(username)
    if not user:
        brand["notes"].append(f"instagram: {status}")
        brand["instagram_status"] = status
        return 0
    brand["instagram_status"] = "ok"

    brand["ig_followers"] = (user.get("edge_followed_by") or {}).get("count")
    full_name = _clean_name(user.get("full_name") or "")
    bio = _clean_name(user.get("biography") or "")

    if not brand.get("name") and full_name:
        brand["name"] = full_name[:120]
        brand["notes"].append("name from Instagram profile")
    if not brand.get("tagline") and bio:
        first = re.split("[.!|~" + chr(10) + chr(13) + "]", bio)[0].strip()
        brand["tagline"] = (first or bio)[:160]
        brand["notes"].append("tagline from Instagram bio")
    if not brand.get("services") and bio:
        low = bio.lower()
        brand["services"] = [label for label, keys in SERVICE_VOCAB
                             if any(k in low for k in keys)][:8]
        if brand["services"]:
            brand["notes"].append("services from Instagram bio")
    if not brand.get("email"):
        m = EMAIL_RE.search(bio)
        if m:
            brand["email"] = m.group(0)

    # profile picture -> logo candidate
    pic = user.get("profile_pic_url_hd") or user.get("profile_pic_url")
    if want_logo and pic:
        rr = fetch(sess, pic, binary=True, timeout=15)
        if rr is not None:
            data = getattr(rr, "_demo_bytes", b"")
            w, h = image_dims(data, pic)
            if data and max(w, h) >= 100:
                is_logo, ncol = looks_like_logo(data)
                path = os.path.join(cache_dir, "logo.jpg")
                with open(path, "wb") as fh:
                    fh.write(data)
                brand["logo_file"] = path
                brand["logo_w"], brand["logo_h"] = w, h
                brand["logo_source"] = "instagram-avatar"
                brand["logo_url"] = pic
                brand["logo_is_photo"] = not is_logo
                brand["logo_colours"] = ncol
                lum, dom, alpha = image_profile(data)
                brand["logo_is_dark"] = lum < 0.45
                brand["logo_alpha"] = round(alpha, 3)
                if dom and not is_neutral(dom, 0.22) and not brand.get("primary"):
                    brand["primary"] = dom
                    brand["accent"] = dom
                    brand["colour_source"] = "instagram-avatar"
                brand["notes"].append(
                    f"logo from Instagram avatar ({w}x{h}, "
                    f"{'flat/logo-like' if is_logo else 'looks like a PHOTO'})")

    # recent posts -> photos
    edges = (user.get("edge_owner_to_timeline_media") or {}).get("edges") or []
    urls = []
    for e in edges[:12]:
        node = e.get("node") or {}
        if node.get("is_video"):
            continue
        u = node.get("display_url")
        if u:
            urls.append(u)
    n = 0
    for i, u in enumerate(urls[:8]):
        rr = fetch(sess, u, binary=True, timeout=15)
        if rr is None:
            continue
        data = getattr(rr, "_demo_bytes", b"")
        w, h = image_dims(data, u)
        if w < 500:
            continue
        path = os.path.join(cache_dir, f"ig{i}.jpg")
        with open(path, "wb") as fh:
            fh.write(data)
        brand["photos"].append({"file": path, "url": u, "w": w, "h": h,
                                "source": "instagram"})
        n += 1
        if not brand.get("primary"):
            _lum, dom, _a = image_profile(data)
            if dom and not is_neutral(dom, 0.25):
                brand["primary"] = brand["accent"] = dom
                brand["colour_source"] = "instagram-photo"

    brand["usable_images"] = len(brand["photos"])
    if not brand.get("hero_file"):
        hero = next((p for p in brand["photos"]
                     if p["w"] >= 800 and p["w"] >= p["h"] * 1.15), None)
        if hero:
            brand["hero_file"] = hero["file"]
            brand["hero_w"], brand["hero_h"] = hero["w"], hero["h"]
    if n:
        brand["notes"].append(f"instagram supplied {n} photo(s)")
    else:
        brand["notes"].append("instagram: no usable post photos")
    return n


# --------------------------------------------------------------------------
# templates
# --------------------------------------------------------------------------
#
# All four "templates" are the same Webflow export ("Lumora") that the operator
# hand-reskinned for four different practices. That means:
#   * identical CSS token ramp   -> one colour strategy works on all of them
#   * identical page set / class names
#   * each carries the LEFTOVER brand strings of every practice it passed
#     through (Ritter's phone is still sitting inside the Lura build, etc).
# So the reskin is: scrub every known template brand string, then repaint.

TEMPLATES = {
    "Gary Solnit Dentist": {
        "logo_style": "svg-wordmark",
        "hue_pref": (0.06, 0.14),          # gold / warm
        "sub": "GENERAL &amp; COSMETIC DENTISTRY",
    },
    "Lura Dentist": {
        "logo_style": "img",
        "hue_pref": (0.55, 0.70),          # blue / indigo
        "sub": "MODERN FAMILY DENTISTRY",
    },
    "Modern Smile Center Dentist": {
        "logo_style": "svg-wordmark",
        "hue_pref": (0.45, 0.55),          # teal / cyan
        "sub": "GENERAL &amp; COSMETIC DENTISTRY",
    },
    "Ritter Ramsey Dentist": {
        "logo_style": "svg-wordmark",
        "hue_pref": (0.90, 0.06),          # red / pink / neutral wrap-around
        "sub": "ESTHETIC &amp; COSMETIC DENTISTRY",
    },
}

# Every brand string any of the four templates still contains. All of these
# MUST be gone from a shipped demo - a leftover is a leak of another client.
TEMPLATE_BRAND_NAMES = [
    "Drs. Ritter & Ramsey, DDS", "Drs. Ritter & Ramsey", "Ritter & Ramsey",
    "Ritter and Ramsey", "Ritter &amp; Ramsey", "Ritter Ramsey",
    "RITTER &amp; RAMSEY", "RITTER & RAMSEY", "RITTER RAMSEY",
    "Gary S. Solnit, DDS, MS", "Gary S. Solnit", "Gary Solnit", "GARY SOLNIT",
    "THE BEVERLY HILLS CENTER", "The Beverly Hills Center",
    "Foundation Dental Alliance Dentistry", "Foundation Dental Alliance",
    "FOUNDATION DENTAL ALLIANCE",
    "Modern Smile Center", "MODERN SMILE CENTER",
    "585dentist", "585 Dentist", "Lura Dental", "Lura Dentist",
    "Boutique Dental Clinic",
]

# Named people the templates still carry. These become neutral placeholders,
# NOT the practice name - "Dorridge Dental / Cosmetic Dentist" reads wrong in
# a team card.
TEMPLATE_DOCTOR_NAMES = [
    "Dr. Robert G. Ritter", "Dr. Robert Ritter", "Dr. Rob Ritter",
    "Dr. Christopher Ramsey", "Dr. Chris Ramsey", "Dr. Isabelle Ritter",
    "Drs. Gary Solnit", "Dr. Gary Solnit",
    "Dr. Emilie Drumm", "Dr Emilie Drumm", "Emilie Drumm",
    "Dr. Daniel Ahmed", "Dr Daniel Ahmed",
    "Dr. Emman Collins", "Dr Emman Collins",
    "Dr. Marcus Rishi", "Dr Marcus Rishi",
    "Dr. Neofytos Ioannides", "Dr Neofytos Ioannides", "Neofytos Ioannides",
    "Dr. Neo", "Dr Neo",
]

TEMPLATE_TAGLINES = [
    "FOR AESTHETIC &amp; RESTORATIVE DENTISTRY",
    "FOR AESTHETIC AND RESTORATIVE DENTISTRY",
    "ESTHETIC &amp; COSMETIC DENTISTRY",
    "ESTHETIC AND COSMETIC DENTISTRY",
    "GENERAL &amp; COSMETIC DENTISTRY",
    "GENERAL AND COSMETIC DENTISTRY",
    "FAMILY DENTISTRY",
]
TEMPLATE_PHONES = ["561-626-6667", "310-888-1850", "(281) 516-7100",
                   "281-516-7100", "+357 70005758", "+35770005758",
                   "357 70005758"]
TEMPLATE_EMAILS = ["info@ritterandramsey.com", "info@garysolnitdds.com",
                   "info@foundationdentalalliance.com", "drneodentistry@gmail.com",
                   "mcim21@gmail.com", "edrumm@585dentist.com"]
TEMPLATE_STREETS = [
    "9675 Brighton Way, Suite 330", "500 University Blvd, Ste 109",
    "500 University Blvd, Suite 109", "1610 Pines Drive, Suite 270",
    "8850 Six Pines Drive, Suite 270", "9675 Brighton Way",
    "500 University Blvd", "Pines Drive, Suite 270",
]
TEMPLATE_LOCALITIES = [
    "Jupiter, FL 33458", "Jupiter, FL 90210", "Beverly Hills, CA 90210",
    "The Woodlands, TX 77380", "The Woodlands, TX",
]
TEMPLATE_ADDRESSES = TEMPLATE_STREETS + TEMPLATE_LOCALITIES
TEMPLATE_CITY_WORDS = ["Jupiter", "Beverly Hills", "The Woodlands"]

# Team cards keep neutral placeholder people. Slot 1 becomes the prospect's own
# clinician when the lead row clearly names one, which is worth a lot on a demo.
PLACEHOLDER_DOCTORS = ["Dr. A. Whitfield", "Dr. J. Marchetti", "Dr. S. Okafor",
                       "Dr. L. Hartley", "Dr. R. Baptiste"]

# Filenames that carry another practice's identity.
LEAK_FILENAME_RE = re.compile(
    r'(ritter|ramsey|solnit|drumm|ahmed|collins|rishi|ioannid|beverly|585|'
    r'smilifye|dr_neo)', re.I)


# Bios refer to people by surname alone ("Dr. Ritter qualified in 1994..."), so
# the surnames need their own mapping or the copy reads as somebody else's.
SURNAME_MAP = {
    "Ritter": "Whitfield", "Ramsey": "Marchetti", "Solnit": "Okafor",
    "Drumm": "Hartley", "Ioannides": "Baptiste", "Neofytos": "Baptiste",
    "Rishi": "Marchetti", "Ahmed": "Hartley", "Collins": "Okafor",
}


def doctor_for(template_doctor, brand):
    """Stable placeholder person for a template doctor name."""
    person = _clean_name(brand.get("lead_name") or "")
    idx = TEMPLATE_DOCTOR_NAMES.index(template_doctor) % len(PLACEHOLDER_DOCTORS)
    if idx == 0 and re.match(r'^(dr\.?|doctor)\s', person, re.I) and len(person) <= 40:
        return person
    return PLACEHOLDER_DOCTORS[idx]

# hard-coded accent hexes the operator painted into the inline SVG logos
TEMPLATE_HARDCODED_ACCENTS = ["#B59A57", "#b59a57"]


def pick_template(brand):
    """
    Match template to brand. Structurally they are the same file, so the only
    honest differentiators are logo treatment and stated house tone.
    Deterministic, so a re-run picks the same one.
    """
    name = (brand.get("name") or "").strip()
    primary = brand.get("primary") or ""

    # A long practice name will not fit the SVG wordmark; the img-logo build
    # handles a wide logo far better.
    if len(name) > 26:
        return "Lura Dentist", "long name -> img-logo layout"

    rgb = hex_to_rgb(primary) if primary else None
    if rgb:
        h, _l, _s = rgb_to_hls(rgb)
        for tname, cfg in TEMPLATES.items():
            lo, hi = cfg["hue_pref"]
            inside = (lo <= h <= hi) if lo <= hi else (h >= lo or h <= hi)
            if inside:
                return tname, f"hue {h:.2f} matches {tname} house tone"
    return "Ritter Ramsey Dentist", "default (cleanest hero markup)"


# --------------------------------------------------------------------------
# build
# --------------------------------------------------------------------------

def force_rmtree(path):
    """
    Windows marks git object files read-only, so plain rmtree leaves the
    directory half-deleted and the next copytree fails with WinError 183.
    """
    def on_error(func, p, _exc):
        try:
            os.chmod(p, 0o700)
            func(p)
        except Exception:
            pass
    if os.path.exists(path):
        shutil.rmtree(path, onerror=on_error)
    for _ in range(5):
        if not os.path.exists(path):
            return
        time.sleep(0.2)
        shutil.rmtree(path, onerror=on_error)


def slugify(text, fallback="demo"):
    s = re.sub(r'[^a-z0-9]+', '-', (text or "").lower()).strip('-')
    s = re.sub(r'-{2,}', '-', s)
    return (s or fallback)[:48].strip('-')


POSTCODE_RE = re.compile(
    r'^(?:[A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2}|\d{5}(?:-\d{4})?|'
    r'[A-Z]{2,3}\s*\d{4}|\d{4})$', re.I)
COUNTRY_WORDS = {"united kingdom", "uk", "england", "scotland", "wales",
                 "united states", "usa", "us", "australia", "canada",
                 "ireland", "new zealand", "great britain"}


STREET_TYPE_RE = re.compile(
    r'\b(?:road|rd|street|st|avenue|ave|lane|ln|way|drive|dr|close|court|ct|'
    r'place|pl|square|sq|parade|terrace|hill|park|row|gardens|gdns|crescent|'
    r'boulevard|blvd|highway|hwy|parkway|pkwy)\b\.?\s+(.+)$', re.I)


def _strip_postal_noise(part):
    part = re.sub(r'\b(?:united kingdom|great britain|england|scotland|wales|'
                  r'northern ireland|united states|usa|u\.s\.a\.|australia|'
                  r'canada|ireland|new zealand|uk)\b', '', part, flags=re.I)
    part = re.sub(r'\b[A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2}\b', '', part, flags=re.I)
    part = re.sub(r'\b\d{5}(?:-\d{4})?\b', '', part)
    part = re.sub(r'\b[A-Z]{2,3}\s+\d{4}\b', '', part)
    part = re.sub(r'\b(?:suite|ste|unit|apt|floor|level)\s*\.?\s*\d+\w*\b',
                  '', part, flags=re.I)
    return re.sub(r'\s{2,}', ' ', part).strip(' ,.-')


def city_from_address(address):
    """
    The template H1 reads '<City> Cosmetic & Restorative Dentistry', so this
    has to return a town - not a street, not a postcode, not a country. Getting
    it wrong produces a two-line H1 with a house number in it.
    """
    if not address:
        return ""
    parts = [_strip_postal_noise(p) for p in re.split(r'[,\n]', address)]
    parts = [p for p in parts if p]

    # a clean town: letters only, short
    for p in reversed(parts):
        if not re.search(r'\d', p) and 2 < len(p) <= 40 and len(p.split()) <= 4:
            return p
    # "647 London Road Westcliff-On-Sea" -> the bit after the street type
    for p in reversed(parts):
        m = STREET_TYPE_RE.search(p)
        if m:
            tail = m.group(1).strip(' ,.-')
            if 2 < len(tail) <= 40 and not re.search(r'\d', tail):
                return tail
    for p in reversed(parts):
        q = re.sub(r'^\d+\s+', '', p).strip()
        if q and not re.search(r'\d', q) and 2 < len(q) <= 40:
            return q
    return ""


def street_from_address(address):
    """First line of their address, for the footer's street slot."""
    if not address:
        return ""
    for p in [x.strip() for x in re.split(r'[,\n]', address) if x.strip()]:
        if re.search(r'\d', p) or STREET_TYPE_RE.search(p):
            return p[:60]
    return (address.split(",")[0] or "").strip()[:60]


def locality_from_address(address, country=""):
    """City + postcode, for the footer's 'Jupiter, FL 90210' slot."""
    if not address:
        return country or ""
    city = city_from_address(address)
    codes = (re.findall(r'\b[A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2}\b', address, re.I)
             or re.findall(r'\b\d{5}(?:-\d{4})?\b', address)
             or re.findall(r'\b[A-Z]{2,3}\s+\d{4}\b', address))
    bits = [b for b in (city, codes[0] if codes else "") if b]
    return ", ".join(bits) or (country or "")


def trim_words(text, limit):
    """Cut to `limit` chars on a word boundary - no titles ending mid-word."""
    text = _clean_name(text or "")
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0].rstrip(" ,;:-")
    # a title ending "...safe, comfortable and" reads like a truncation bug
    dangling = {"and", "or", "the", "a", "an", "with", "for", "of", "to", "in",
                "at", "on", "we", "our", "is", "are", "that", "which", "by",
                "from", "as", "but", "so"}
    words = cut.split()
    while words and words[-1].lower().strip(",;:-") in dangling:
        words.pop()
    return " ".join(words).rstrip(" ,;:-") or cut or text[:limit]


def unique_slug(name, username, meta):
    """
    demo-{slug} is a repo name, so it has to be unique across leads. Two
    practices really can both be called "Smile Clinic", and a Wix default title
    collides constantly - a collision would point one prospect at another
    prospect's demo.
    """
    slug = slugify(name)
    if len(slug) < 4:
        slug = slugify(username)
    taken = {v.get("slug"): u for u, v in (meta or {}).items()}
    if taken.get(slug) not in (None, username):
        slug = f"{slug}-{slugify(username)}"[:48].strip('-')
    return slug or slugify(username) or "demo"


ASSET_REF_RE = re.compile(r'(?:\.\./|assets/)(?:img|js|css)/[A-Za-z0-9_.\-/%@]+')


def collect_asset_refs(build_dir):
    """Every assets/... path still referenced by any html/css/js in the build."""
    refs = set()
    for dirpath, dirnames, filenames in os.walk(build_dir):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for fn in filenames:
            if not fn.endswith((".html", ".css", ".js")):
                continue
            p = os.path.join(dirpath, fn)
            try:
                with open(p, encoding="utf-8", errors="replace") as fh:
                    txt = fh.read()
            except Exception:
                continue
            for m in ASSET_REF_RE.findall(txt):
                m = m.split("?")[0].split("#")[0]
                if m.startswith("../"):
                    m = "assets/" + m[3:]
                refs.add(m.replace("\\", "/"))
    return refs


def prune_unused_assets(build_dir):
    """
    The templates ship ~56 MB, of which ~8 MB is actually referenced. Pruning
    turns a 60-second push into a 5-second one, which is the difference between
    a 20-second demo and a 90-second one.
    """
    refs = collect_asset_refs(build_dir)
    removed = removed_bytes = 0
    assets = os.path.join(build_dir, "assets")
    for dirpath, _dirnames, filenames in os.walk(assets):
        for fn in filenames:
            p = os.path.join(dirpath, fn)
            rel = os.path.relpath(p, build_dir).replace("\\", "/")
            if rel in refs:
                continue
            try:
                sz = os.path.getsize(p)
                os.remove(p)
                removed += 1
                removed_bytes += sz
            except Exception:
                pass
    for dirpath, dirnames, filenames in os.walk(assets, topdown=False):
        if not dirnames and not filenames:
            try:
                os.rmdir(dirpath)
            except Exception:
                pass
    return removed, removed_bytes


def esc(text):
    return (str(text).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def xml_esc(text):
    return (str(text).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def wordmark_svg(name, sub, height=48, anchor="start"):
    """The template's own logo treatment, re-lettered with their name."""
    name = xml_esc(name.upper())
    size = 14.5
    if len(name) > 18:
        size = 12.0
    if len(name) > 24:
        size = 10.0
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 70" '
        f'style="height:{height}px;width:auto;max-width:280px;display:block;'
        f'color:#ffffff" fill="none">'
        f'<path d="M 22 25 C 23 17, 26 11, 31 11 C 36 11, 39 16, 42 20 C 45 16, '
        f'48 11, 53 11 C 58 11, 61 17, 62 25 C 63 32, 61 38, 59 43 C 57 47, 55 51, '
        f'55 54 C 52 50, 49 46, 47 43 C 44 40, 41 40, 39 43 C 36 46, 33 50, 31 54 '
        f'C 31 51, 29 47, 27 43 C 24 38, 22 32, 22 25 Z" fill="none" '
        f'stroke="var(--brand-accent,#B59A57)" stroke-width="2" '
        f'stroke-linejoin="round" stroke-linecap="round"/>'
        f'<line x1="72" y1="14" x2="72" y2="52" stroke="var(--brand-accent,#B59A57)" stroke-width="1.2"/>'
        f'<text x="84" y="32" font-family="Sora, Inter, sans-serif" '
        f'font-size="{size}" font-weight="700" letter-spacing="0.5" '
        f'fill="currentColor">{name}</text>'
        f'<text x="84" y="47" font-family="Sora, Inter, sans-serif" '
        f'font-size="6.8" font-weight="600" letter-spacing="0.8" '
        f'fill="currentColor">{sub}</text></svg>'
    )


def logo_img_html(rel_src, alt, dark_logo, height=44):
    """
    Both logo slots sit on a dark background. A dark logo on a dark navbar is
    invisible - that is one of the classic ways an auto-reskin looks broken -
    so a dark logo gets a light chip behind it.
    """
    chip = ("background:#ffffff;padding:8px 14px;border-radius:10px;"
            if dark_logo else "")
    return (f'<img src="{rel_src}" alt="{esc(alt)} logo" '
            f'style="height:{height}px;width:auto;max-width:260px;'
            f'object-fit:contain;display:block;{chip}"/>')


def brand_css(pal, hero_rel=None, story_fix=True):
    lines = [
        "/* generated by demo_generator.py - prospect brand palette */",
        ":root{",
    ]
    for k in ("primary-900", "primary-800", "primary-700", "primary-600",
              "primary-500", "primary-400", "neutral-50", "neutral-100",
              "neutral-200", "neutral-300"):
        lines.append(f"  --primitive-color--{k}: {pal[k]} !important;")
    lines.append(f"  --brand-accent: {pal['primary-500']};")
    lines.append(f"  --brand-primary: {pal['primary-900']};")
    lines.append("}")
    if hero_rel:
        p9 = hex_to_rgb(pal["primary-900"])
        lines.append(
            ".section_hero.is-home-hero{"
            f"background-image:linear-gradient(rgba({p9[0]},{p9[1]},{p9[2]},.74),"
            f"rgba({p9[0]},{p9[1]},{p9[2]},.88)),url('{hero_rel}') !important;"
            "background-size:cover !important;background-position:center !important;"
            "background-repeat:no-repeat !important;}")
        lines.append(".home-hero_image{opacity:.28 !important;}")
    if story_fix:
        lines.append(".our-story_item-image,.home-value_image,.about-hero_image"
                     "{object-fit:cover !important;width:100% !important;"
                     "height:100% !important;}")
    return "\n".join(lines) + "\n"


def build_demo(lead, brand, template, slug, force=False):
    """Copy the template, repaint it, scrub every foreign brand string."""
    build_dir = os.path.join(BUILD_ROOT, slug)
    src_dir = os.path.join(BASE_DIR, template)
    if not os.path.isdir(src_dir):
        raise RuntimeError(f"template folder missing: {template}")

    force_rmtree(build_dir)
    os.makedirs(BUILD_ROOT, exist_ok=True)
    shutil.copytree(
        src_dir, build_dir,
        ignore=shutil.ignore_patterns(".git", "variant-blue", "__pycache__",
                                      "*.pyc", "*.mp4", "*.mov", "*.zip"))

    img_dir = os.path.join(build_dir, "assets", "img")
    css_dir = os.path.join(build_dir, "assets", "css")
    os.makedirs(img_dir, exist_ok=True)
    os.makedirs(css_dir, exist_ok=True)

    report = {"swapped": [], "template": template}

    name = (brand.get("name") or lead.get("Name") or "").strip()
    phone = (brand.get("phone") or "").strip()
    email = (brand.get("email") or "").strip()
    address = (brand.get("address") or "").strip()
    tagline = (brand.get("tagline") or "").strip()
    sub = TEMPLATES[template]["sub"]
    short_tagline = trim_words(tagline, 58)

    pal = build_palette(brand.get("primary") or "#1f4f57",
                        brand.get("accent") or brand.get("primary") or "#1f4f57")
    report["palette"] = pal

    # ---- assets: logo -----------------------------------------------------
    logo_rel = None
    if brand.get("logo_file") and os.path.exists(brand["logo_file"]):
        ext = os.path.splitext(brand["logo_file"])[1]
        dst = os.path.join(img_dir, "brand-logo" + ext)
        shutil.copyfile(brand["logo_file"], dst)
        logo_rel = "assets/img/brand-logo" + ext
        report["swapped"].append("logo")

    # ---- assets: hero + photos -------------------------------------------
    hero_rel = None
    if brand.get("hero_file") and os.path.exists(brand["hero_file"]) \
            and brand.get("hero_w", 0) >= 800:
        ext = os.path.splitext(brand["hero_file"])[1] or ".jpg"
        shutil.copyfile(brand["hero_file"], os.path.join(img_dir, "brand-hero" + ext))
        hero_rel = "../img/brand-hero" + ext
        report["swapped"].append("hero image")

    story_map = {}
    good_photos = [p for p in brand.get("photos", [])
                   if p.get("w", 0) >= 700 and os.path.exists(p.get("file", ""))
                   and p.get("file") != brand.get("hero_file")]
    for i, p in enumerate(good_photos[:3]):
        ext = os.path.splitext(p["file"])[1] or ".jpg"
        fn = f"brand-photo-{i + 1}{ext}"
        shutil.copyfile(p["file"], os.path.join(img_dir, fn))
        story_map[f"gen_our-story-image-{i + 1}.jpg"] = fn
    if story_map:
        report["swapped"].append(f"{len(story_map)} story photo(s)")

    with open(os.path.join(css_dir, "brand.css"), "w", encoding="utf-8") as fh:
        fh.write(brand_css(pal, hero_rel))

    # ---- rename files that carry another practice's name ------------------
    # doctor-rob-ritter.html and dr_ritter.jpg leak just as loudly as body copy
    # does, and they are the kind of thing an eyeball review misses.
    rename_map = {}
    docs = sorted(f for f in os.listdir(build_dir)
                  if re.match(r'^doctor-.+\.html$', f))
    for i, f in enumerate(docs, 1):
        rename_map[f] = f"doctor-{i}.html"
    imgs = sorted(f for f in os.listdir(img_dir) if LEAK_FILENAME_RE.search(f))
    for i, f in enumerate(imgs, 1):
        rename_map[f] = f"team-{i}{os.path.splitext(f)[1]}"
    for old, new in rename_map.items():
        src_p = os.path.join(build_dir if old.endswith(".html") else img_dir, old)
        dst_p = os.path.join(build_dir if old.endswith(".html") else img_dir, new)
        try:
            os.replace(src_p, dst_p)
        except Exception:
            pass
    if rename_map:
        report["renamed_files"] = len(rename_map)

    # where the demo's social buttons should point
    ig_url = (f"https://www.instagram.com/{lead.get('Username')}/"
              if lead.get("Username") else (brand.get("final_url") or "#"))
    social_url = brand.get("final_url") or ig_url
    map_query = urllib.parse.quote(f"{name}, {address}" if address else name)
    city = city_from_address(address) or (brand.get("country") or "your area")
    addr_street = street_from_address(address)
    addr_locality = locality_from_address(address, brand.get("country") or "")

    surname_map = dict(SURNAME_MAP)
    person = _clean_name(brand.get("lead_name") or "")
    m_person = re.match(r'^(?:dr\.?|doctor)\s+(.+)$', person, re.I)
    if m_person:
        parts = m_person.group(1).split()
        if parts and parts[-1].isalpha() and 2 < len(parts[-1]) <= 20:
            for k in ("Ritter", "Solnit"):          # the primary doctor slot
                surname_map[k] = parts[-1]

    # ---- rewrite every html page -----------------------------------------
    nav_logo = (logo_img_html(logo_rel, name, brand.get("logo_is_dark"), 44)
                if logo_rel else wordmark_svg(name, sub, 48))
    foot_logo = (logo_img_html(logo_rel, name, brand.get("logo_is_dark"), 52)
                 if logo_rel else wordmark_svg(name, sub, 52))

    pages = [f for f in os.listdir(build_dir) if f.endswith(".html")]
    for fn in pages:
        p = os.path.join(build_dir, fn)
        with open(p, encoding="utf-8", errors="replace") as fh:
            html = fh.read()

        # 1. logo slots
        html = re.sub(r'(<a[^>]*class="[^"]*navbar_logo[^"]*"[^>]*>).*?(</a>)',
                      lambda m: m.group(1) + nav_logo + m.group(2),
                      html, flags=re.S)
        html = re.sub(r'(<a[^>]*class="[^"]*footer_brand[^"]*"[^>]*>).*?(</a>)',
                      lambda m: m.group(1) + foot_logo + m.group(2),
                      html, flags=re.S)

        # 2. renamed files (doctor pages, team photos)
        for old, new in rename_map.items():
            html = html.replace(old, new)

        # 3. brand strings - longest first so "Ritter & Ramsey" beats "Ritter"
        for old in sorted(TEMPLATE_DOCTOR_NAMES, key=len, reverse=True):
            if old in html:
                html = html.replace(old, doctor_for(old, brand))
        for old in sorted(TEMPLATE_BRAND_NAMES, key=len, reverse=True):
            if old in html:
                repl = name.upper() if old.isupper() else name
                html = html.replace(old, esc(repl) if "&" in repl else repl)
        for old in sorted(TEMPLATE_TAGLINES, key=len, reverse=True):
            html = html.replace(old, sub)

        # social + map links should point at THEM, not at the template's client
        html = re.sub(r'https?://(?:www\.)?instagram\.com/[A-Za-z0-9_.\-]*/?',
                      ig_url, html)
        html = re.sub(
            r'https?://(?:www\.)?(?:twitter|x|facebook|linkedin|youtube|tiktok)'
            r'\.com/[A-Za-z0-9_.\-/]*', social_url, html)
        html = re.sub(r'(maps\.google\.com/maps\?q=).*?(?=&amp;t=|&t=|["\'])',
                      lambda m: m.group(1) + map_query, html)

        # surnames left in body copy ("Dr. Ritter qualified in 1994...")
        for old_sn, new_sn in surname_map.items():
            html = re.sub(r'\b' + re.escape(old_sn) + r'\b', new_sn, html)

        # 3. contact details
        for old in TEMPLATE_PHONES:
            html = html.replace(old, phone or "Book online")
        if not phone:
            # never ship a dead "tel:Book online" link
            html = re.sub(r'href="tel:[^"]*"', 'href="booking.html"', html)
        for old in TEMPLATE_EMAILS:
            html = html.replace(old, email or "hello@example.com")
        # The footer is "<practice><br><street><br><city, postcode>". Pasting
        # the full address into both slots printed it twice.
        for old in sorted(TEMPLATE_STREETS, key=len, reverse=True):
            html = html.replace(old, addr_street or address or "")
        for old in sorted(TEMPLATE_LOCALITIES, key=len, reverse=True):
            html = html.replace(old, addr_locality)
        for old in sorted(TEMPLATE_ADDRESSES, key=len, reverse=True):
            html = html.replace(old, address or (brand.get("country") or ""))
        for old in TEMPLATE_CITY_WORDS:
            html = re.sub(r'\b' + re.escape(old) + r'\b', city, html)

        # 4. hard-coded template accent
        for old in TEMPLATE_HARDCODED_ACCENTS:
            html = html.replace(old, pal["primary-500"])

        # 6. head: title/meta + brand.css
        title = (f"{name} | {short_tagline}" if short_tagline
                 else f"{name} | Dental Care")
        html = re.sub(r'<title>.*?</title>', f'<title>{esc(title[:110])}</title>',
                      html, count=1, flags=re.S)
        if tagline:
            html = re.sub(r'(<meta content=")[^"]*(" name="description"/?>)',
                          lambda m: m.group(1) + esc(tagline) + m.group(2), html)
            html = re.sub(r'(<meta content=")[^"]*(" property="og:description"/?>)',
                          lambda m: m.group(1) + esc(tagline) + m.group(2), html)
        html = re.sub(r'(<meta content=")[^"]*(" property="og:title"/?>)',
                      lambda m: m.group(1) + esc(title[:110]) + m.group(2), html)
        share_img = (hero_rel.replace("../", "assets/") if hero_rel
                     else (logo_rel or ""))
        if share_img:
            html = re.sub(r'(<meta content=")[^"]*(" property="og:image"/?>)',
                          lambda m: m.group(1) + share_img + m.group(2), html)
            html = re.sub(r'(<meta content=")[^"]*(" name="twitter:image"/?>)',
                          lambda m: m.group(1) + share_img + m.group(2), html)
        if logo_rel:
            html = re.sub(r'<link href="[^"]*" rel="shortcut icon"[^>]*/?>',
                          f'<link href="{logo_rel}" rel="shortcut icon"/>', html)
            html = re.sub(r'<link href="[^"]*" rel="apple-touch-icon"[^>]*/?>',
                          f'<link href="{logo_rel}" rel="apple-touch-icon"/>', html)
        if "assets/css/brand.css" not in html:
            html = html.replace(
                "</head>",
                '    <link href="assets/css/brand.css" rel="stylesheet" '
                'type="text/css"/>\n</head>', 1)

        # 7. hero + story imagery
        if hero_rel:
            local = hero_rel.replace("../", "assets/")
            html = re.sub(r'(<img[^>]*class="home-hero_image"[^>]*src=")[^"]*(")',
                          lambda m: m.group(1) + local + m.group(2), html)
            html = re.sub(r'(<img[^>]*src=")[^"]*("[^>]*class="home-hero_image")',
                          lambda m: m.group(1) + local + m.group(2), html)
        for old, new in story_map.items():
            html = html.replace(old, new)

        # 8. services: relabel the four service cards with what they actually do
        svcs = brand.get("services") or []
        if len(svcs) >= 4:
            for old, new in zip(["Preventive dentistry", "Cosmetic dentistry",
                                 "Restorative treatments", "Strategic Inner Circle",
                                 "Orthodontic treatments"], svcs):
                html = html.replace(">" + old + "<", ">" + esc(new) + "<")
            report_key = "services"
            if report_key not in report["swapped"]:
                report["swapped"].append(report_key)
        else:
            html = html.replace(">Strategic Inner Circle<", ">Orthodontics<")

        with open(p, "w", encoding="utf-8") as fh:
            fh.write(html)

    # tighten the repo before it is ever pushed
    n_removed, bytes_removed = prune_unused_assets(build_dir)
    report["pruned_files"] = n_removed
    report["pruned_mb"] = round(bytes_removed / 1e6, 1)
    report["build_mb"] = round(
        sum(os.path.getsize(os.path.join(dp, f))
            for dp, _dn, fns in os.walk(build_dir) for f in fns) / 1e6, 1)
    return build_dir, report


# --------------------------------------------------------------------------
# QUALITY GATE
# --------------------------------------------------------------------------

LEAK_PATTERNS = [
    ("ritterandramsey", "leftover template email domain"),
    ("garysolnitdds", "leftover template email domain"),
    ("foundationdentalalliance", "leftover template email domain"),
    ("drneodentistry", "leftover template email"),
    ("585dentist", "leftover template brand"),
    ("Ritter", "leftover template practice name"),
    ("Solnit", "leftover template practice name"),
    ("Ramsey", "leftover template practice name"),
    ("561-626-6667", "leftover template phone"),
    ("310-888-1850", "leftover template phone"),
    ("(281) 516-7100", "leftover template phone"),
    ("Beverly Hills", "leftover template city"),
]
# NB: a bare "}}" is legal minified CSS, so only real handlebars-style pairs
# count as an unreplaced token.
TOKEN_PATTERNS = [r'\{\{[^{}]{0,80}\}\}', r'\bTOKEN\b', r'\bTODO_BRAND\b',
                  r'%%[A-Z_]+%%', r'\$\{[A-Z_]+\}', r'\bLOREM_BRAND\b']


def quality_gate(brand, build_dir, report):
    """
    Return (passed, reasons). Every reason is a sentence the operator can act
    on. Nothing here is advisory - any reason means the demo is not deployed.
    """
    reasons = []
    name = (brand.get("name") or "").strip()

    if brand.get("segment") == SEGMENT_THIRD_PARTY and brand.get("reachable"):
        reasons.append(
            f"THIRD PARTY LINK: nothing on {registrable_host(brand.get('final_url') or '')} "
            f"identifies it as this lead's site (no matching email, phone, "
            f"Instagram link or name). Reskinning it would show the prospect "
            f"somebody else's brand.")

    if brand.get("segment") == SEGMENT_OWN_SITE and not brand.get("reachable"):
        reasons.append(f"SITE UNREACHABLE: {brand.get('website')} did not respond, "
                       f"so there was no brand to scrape")

    # --- business name ---
    if not name:
        reasons.append("BUSINESS NAME MISSING: nothing usable scraped from the site or the lead row")
    else:
        if re.match(r'^(https?://|www\.)', name, re.I) or re.search(
                r'\.(com|co\.uk|net|org|io|uk|au)\b', name, re.I):
            reasons.append(f"BUSINESS NAME IS A URL: '{name[:60]}'")
        if len(name) > 60:
            reasons.append(f"BUSINESS NAME TOO LONG: {len(name)} chars > 60 ('{name[:50]}...')")
        if name.lower() in GENERIC_NAME_WORDS:
            reasons.append(f"BUSINESS NAME IS GENERIC: '{name}'")

    # --- logo ---
    lf = brand.get("logo_file") or ""
    if not lf or not os.path.exists(lf):
        reasons.append("LOGO MISSING: no logo could be downloaded from their site")
    else:
        w, h = brand.get("logo_w", 0), brand.get("logo_h", 0)
        if max(w, h) < 100:
            reasons.append(f"LOGO TOO SMALL: {w}x{h}px (needs 100px on the long edge)")
        src = brand.get("logo_source", "")
        low = (brand.get("logo_url") or "").lower()
        if src == "icon" and max(w, h) < 180:
            reasons.append(f"LOGO IS A GENERIC FAVICON ONLY: {os.path.basename(low)} at {w}x{h}px")
        if "favicon.ico" in low:
            reasons.append("LOGO IS A GENERIC FAVICON ONLY: fell back to /favicon.ico")
        if brand.get("logo_is_photo"):
            reasons.append(
                f"LOGO IS A PHOTOGRAPH, NOT A LOGO: the Instagram avatar has "
                f"{brand.get('logo_colours')} distinct colours - dropping a "
                f"cropped selfie into the navbar looks worse than no demo")

    # --- colours ---
    primary, accent = brand.get("primary"), brand.get("accent")
    if not primary:
        reasons.append("COLOUR EXTRACTION FAILED: no non-neutral colour found "
                       "(site is pure white/black/grey or CSS unreadable)")
    elif is_neutral(primary, 0.16):
        reasons.append(f"COLOUR EXTRACTION FAILED: only neutral found ({primary})")
    else:
        pal = report.get("palette") or build_palette(primary, accent or primary)
        c_text = pal["_contrast_text_on_white"]
        c_hero = pal["_contrast_white_on_hero"]
        c_acc_l = pal["_contrast_accent_on_white"]
        c_acc_d = pal["_contrast_accent_on_hero"]
        if c_text < 4.5:
            reasons.append(f"COLOUR CONTRAST FAIL: brand colour as body text on the "
                           f"template's white background is {c_text}:1, needs 4.5:1")
        if c_hero < 4.5:
            reasons.append(f"COLOUR CONTRAST FAIL: white hero text on the brand "
                           f"colour is {c_hero}:1, needs 4.5:1")
        if max(c_acc_l, c_acc_d) < 3.0:
            reasons.append(f"COLOUR CONTRAST FAIL: accent is invisible on both "
                           f"surfaces ({c_acc_l}:1 light / {c_acc_d}:1 dark)")

    # --- images ---
    usable = brand.get("usable_images", 0)
    if usable < 2:
        reasons.append(f"NOT ENOUGH IMAGES: {usable} usable image(s) found on their "
                       f"site or Instagram, need 2")

    # --- unreplaced tokens / foreign brand leakage ---
    leaks = {}
    tokens = set()
    bad_files = []
    for dirpath, dirnames, filenames in os.walk(build_dir):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for fn in filenames:
            if LEAK_FILENAME_RE.search(fn):
                bad_files.append(fn)
            if not fn.endswith((".html", ".css")):
                continue
            p = os.path.join(dirpath, fn)
            try:
                with open(p, encoding="utf-8", errors="replace") as fh:
                    txt = fh.read()
            except Exception:
                continue
            for pat in TOKEN_PATTERNS:
                if re.search(pat, txt):
                    tokens.add(f"{pat} in {fn}")
            for needle, why in LEAK_PATTERNS:
                if needle.lower() in txt.lower():
                    leaks.setdefault(f"{needle} ({why})", set()).add(fn)
    if bad_files:
        reasons.append("TEMPLATE FILENAME LEAK: " + ", ".join(sorted(set(bad_files))[:5]))
    if tokens:
        reasons.append("UNREPLACED TEMPLATE TOKEN: " + "; ".join(sorted(tokens)[:4]))
    if leaks:
        detail = "; ".join(f"{k} in {len(v)} file(s)"
                           for k, v in sorted(leaks.items())[:4])
        reasons.append("UNREPLACED TEMPLATE CONTENT (another practice's details "
                       "would ship): " + detail)

    return (len(reasons) == 0), reasons


# --------------------------------------------------------------------------
# deploy
# --------------------------------------------------------------------------

def repo_exists(repo):
    ok, out = gh(["repo", "view", f"{OWNER}/{repo}", "--json",
                  "name,description,visibility"])
    if not ok:
        return None
    try:
        return json.loads(out)
    except Exception:
        return None


def enable_pages(repo, branch="main"):
    ok, out = gh(["api", "--method", "POST", f"repos/{OWNER}/{repo}/pages",
                  "-f", f"source[branch]={branch}", "-f", "source[path]=/"])
    if ok:
        return True, "enabled"
    if "already exists" in out.lower() or "409" in out:
        return True, "already enabled"
    return False, out[:200]


def pages_url(repo):
    ok, out = gh(["api", f"repos/{OWNER}/{repo}/pages", "-q", ".html_url"])
    if ok and out.startswith("http"):
        return out.strip()
    return None


def deploy(build_dir, slug, name, update=False):
    """
    Create a NEW repo demo-{slug}, push, enable Pages. Returns (url, note).

    If a repo of that name already exists we only ever touch it when its
    description carries our marker - otherwise it is somebody else's repo and
    we stop.
    """
    repo = f"demo-{slug}"
    desc = f"{REPO_MARKER} Personalised demo site for {name}"[:250]

    info = repo_exists(repo)
    if info is not None:
        if REPO_MARKER not in (info.get("description") or ""):
            return None, (f"REFUSED: {OWNER}/{repo} already exists and is NOT one "
                          f"of ours (no {REPO_MARKER} marker). Not touching it.")
        if not update:
            url = pages_url(repo) or f"https://{OWNER.lower()}.github.io/{repo}/"
            return url, "already deployed (idempotent skip)"
    else:
        ok, out = gh(["repo", "create", f"{OWNER}/{repo}", "--public",
                      "--description", desc])
        if not ok:
            return None, f"repo create failed: {out[:200]}"

    git_dir = os.path.join(build_dir, ".git")
    if os.path.isdir(git_dir):
        force_rmtree(git_dir)

    for cmd in (["git", "init", "-b", "main"],
                ["git", "add", "-A"],
                ["git", "-c", "user.name=Milin555",
                 "-c", "user.email=dholiyamilin@gmail.com",
                 "commit", "-m", f"Demo site for {name}"]):
        ok, out = run(cmd, cwd=build_dir)
        if not ok and cmd[1] != "commit":
            return None, f"{' '.join(cmd[:2])} failed: {out[:160]}"

    run(["git", "remote", "remove", "origin"], cwd=build_dir)
    ok, out = run(["git", "remote", "add", "origin",
                   f"https://github.com/{OWNER}/{repo}.git"], cwd=build_dir)
    ok, out = run(["git", "push", "-u", "--force", "origin", "main"],
                  cwd=build_dir, timeout=420)
    if not ok:
        return None, f"push failed: {out[:200]}"

    ok, msg = enable_pages(repo, "main")
    if not ok:
        return None, f"Pages failed: {msg}"

    url = pages_url(repo) or f"https://{OWNER.lower()}.github.io/{repo}/"
    return url, "deployed"


def verify_live(url, brand, tries=10, delay=12):
    """Fetch the published page and check their brand actually made it."""
    sess = session()
    for i in range(tries):
        r = fetch(sess, url, timeout=20)
        if r is not None and r.text and len(r.text) > 5000:
            html = r.text
            checks = {
                "name_present": (brand.get("name", "") or "").split()[0].lower()
                                in html.lower() if brand.get("name") else False,
                "logo_present": "brand-logo" in html or "navbar_logo" in html,
                "brand_css": "assets/css/brand.css" in html,
                "no_tokens": not any(re.search(p, html) for p in TOKEN_PATTERNS),
                "no_leaks": not any(n.lower() in html.lower()
                                    for n, _ in LEAK_PATTERNS),
            }
            return True, checks
        time.sleep(delay)
    return False, {}


# --------------------------------------------------------------------------
# records
# --------------------------------------------------------------------------

def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as fh:
                return json.load(fh)
        except Exception:
            pass
    return default


def save_json(path, obj):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False)


def strip_bytes(obj):
    """brand dicts carry raw image bytes in memory; never serialise those."""
    if isinstance(obj, dict):
        return {k: strip_bytes(v) for k, v in obj.items() if k != "data"}
    if isinstance(obj, list):
        return [strip_bytes(v) for v in obj]
    return obj


# --------------------------------------------------------------------------
# leads
# --------------------------------------------------------------------------

def load_leads(path):
    csv.field_size_limit(10 ** 7)
    with open(path, encoding="utf-8", errors="replace", newline="") as fh:
        return list(csv.DictReader(fh))


def find_lead(username, leads_path=LEADS_CSV):
    for row in load_leads(leads_path):
        if (row.get("Username") or "").strip().lower() == username.strip().lower():
            return row
    return None


def queue_rows(path, limit):
    rows = load_leads(path)
    out = []
    canon = {"username": "Username", "name": "Name", "email": "Email",
             "phone": "Phone", "website": "Website", "country": "Country",
             "category": "Category", "followers": "Followers",
             "following": "Following", "bio": "Bio"}
    for r in rows:
        # queue.csv comes from ranker.py and may use lowercase headers; without
        # this the username lands empty on every rejection record
        for k in list(r.keys()):
            lk = (k or "").strip().lower()
            if lk in canon and not (r.get(canon[lk]) or "").strip():
                r[canon[lk]] = r.get(k) or ""
        if not (r.get("Username") or "").strip():
            continue
        out.append(r)
        if limit and len(out) >= limit:
            break
    return out


# --------------------------------------------------------------------------
# one lead, end to end
# --------------------------------------------------------------------------

def reject(review, lead, reasons, **extra):
    """
    Every rejection must be joinable back to the lead. Username and email are
    written on EVERY record - without them the operator cannot tell which
    prospect failed or follow up by hand, which is the whole point of the file.
    """
    rec = {
        "username": (lead.get("Username") or "").strip(),
        "name": lead.get("Name") or "",
        "email": (lead.get("Email") or "").strip(),
        "phone": (lead.get("Phone") or "").strip(),
        "country": lead.get("Country") or "",
        "website": (lead.get("Website") or "").strip(),
        "reasons": reasons,
        "reason_codes": sorted({reason_code(r) for r in reasons}),
        "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    rec.update(extra)
    review.append(rec)
    return rec


REASON_CODES = [
    ("THIRD PARTY", "third_party_link"),
    ("BUSINESS NAME", "business_name"),
    ("LOGO", "logo"),
    ("COLOUR CONTRAST", "colour_contrast"),
    ("COLOUR EXTRACTION", "colour_extraction"),
    ("NOT ENOUGH IMAGES", "images"),
    ("UNREPLACED TEMPLATE TOKEN", "token"),
    ("UNREPLACED TEMPLATE CONTENT", "template_leak"),
    ("TEMPLATE FILENAME LEAK", "template_leak"),
    ("SITE UNREACHABLE", "unreachable"),
    ("BUILD FAILED", "build_error"),
    ("DEPLOY FAILED", "deploy_error"),
    ("UNEXPECTED ERROR", "error"),
]


def reason_code(reason):
    for prefix, code in REASON_CODES:
        if reason.upper().startswith(prefix):
            return code
    return "other"


def process(lead, args, demos, meta, review):
    username = (lead.get("Username") or "").strip()
    say("")
    say("=" * 72)
    say(f"  {username}  |  {(lead.get('Name') or '')[:44]}")
    say("=" * 72)

    if username in demos and not args.force:
        say(f"    SKIP: already has a demo -> {demos[username]}")
        return "skipped"

    segment, seg_url = classify_lead(lead)
    say(f"    segment    : {segment}")

    if segment == SEGMENT_THIRD_PARTY:
        host = registrable_host(seg_url)
        r = (f"THIRD PARTY LINK: Website is {host}, which is a directory / "
             f"charity / aggregator or is unrelated to '{lead.get('Name') or username}'. "
             f"Building from it would put somebody else's branding in front of "
             f"this prospect.")
        say(f"      REJECT REASON: {r}")
        reject(review, lead, [r], segment=segment)
        return "rejected"

    cache_dir = os.path.join(CACHE_ROOT, slugify(username))
    t0 = time.time()
    brand = scrape_brand(lead, cache_dir, refresh=args.refresh, segment=segment)

    say(f"    site       : {brand.get('final_url') or lead.get('Website') or '(none)'}"
        f"  [{'reachable' if brand.get('reachable') else 'UNREACHABLE'}]")
    say(f"    name       : {brand.get('name') or '(none)'}")
    say(f"    tagline    : {(brand.get('tagline') or '(none)')[:70]}")
    say(f"    phone/email: {brand.get('phone') or '-'}  /  {brand.get('email') or '-'}")
    say(f"    address    : {(brand.get('address') or '-')[:70]}")
    say(f"    services   : {', '.join(brand.get('services') or []) or '(none found)'}")
    say(f"    colours    : primary={brand.get('primary') or '-'} "
        f"accent={brand.get('accent') or '-'} (via {brand.get('colour_source') or '-'})")
    lf = brand.get("logo_file")
    say(f"    logo       : {os.path.basename(lf) if lf else '(none)'} "
        f"{brand.get('logo_w')}x{brand.get('logo_h')} via {brand.get('logo_source') or '-'}"
        f"{' [dark -> chip]' if brand.get('logo_is_dark') else ''}")
    say(f"    images     : {brand.get('usable_images')} usable"
        f"{' (instagram fallback used)' if brand.get('instagram_used') else ''}"
        f"{'  hero ' + str(brand.get('hero_w')) + 'px' if brand.get('hero_file') else ''}")
    for n in brand.get("notes", []):
        say(f"    note       : {n}")

    template, why = pick_template(brand)
    say(f"    template   : {template}  ({why})")

    slug = unique_slug(brand.get("name") or username or "demo", username, meta)
    say(f"    slug       : demo-{slug}")

    try:
        build_dir, report = build_demo(lead, brand, template, slug)
    except Exception as e:
        say(f"    BUILD FAILED: {e}")
        reject(review, lead, [f"BUILD FAILED: {e}"], segment=segment,
               scraped_name=brand.get("name"), template=template)
        return "error"

    pal = report["palette"]
    say(f"    palette    : text {pal['primary-900']} ({pal['_contrast_text_on_white']}:1 on white) "
        f"accent {pal['primary-500']} ({pal['_contrast_accent_on_white']}:1 light / "
        f"{pal['_contrast_accent_on_hero']}:1 dark)")
    say(f"    build      : {report['build_mb']} MB "
        f"(pruned {report['pruned_files']} unused files, {report['pruned_mb']} MB)")
    say(f"    replaced   : {', '.join(report['swapped']) or 'colours + text only'}")

    passed, reasons = quality_gate(brand, build_dir, report)
    say(f"    gate       : {'PASS' if passed else 'REJECT'}  ({time.time() - t0:.1f}s)")
    if not passed:
        for r in reasons:
            say(f"      REJECT REASON: {r}")
        reject(review, lead, reasons,
               segment=segment, scraped_name=brand.get("name"),
               final_url=brand.get("final_url"), slug=slug, template=template,
               build_dir=build_dir,
               measured={
                   "logo_px": f"{brand.get('logo_w')}x{brand.get('logo_h')}",
                   "logo_source": brand.get("logo_source") or None,
                   "logo_is_photo": brand.get("logo_is_photo"),
                   "usable_images": brand.get("usable_images"),
                   "primary": brand.get("primary") or None,
                   "accent": brand.get("accent") or None,
                   "colour_source": brand.get("colour_source") or None,
                   "contrast": {k.lstrip("_"): v for k, v in pal.items()
                                if k.startswith("_")},
                   "reachable": brand.get("reachable"),
               },
               brand=strip_bytes({k: v for k, v in brand.items()
                                  if k not in ("colour_candidates",)}))
        if args.discard_rejected:
            force_rmtree(build_dir)
        return "rejected"

    if not args.go:
        say(f"    WOULD DEPLOY -> https://{OWNER.lower()}.github.io/demo-{slug}/")
        say(f"    (dry run - nothing created. open {build_dir}\\index.html to eyeball it)")
        return "would_deploy"

    say("    deploying  ...")
    url, note = deploy(build_dir, slug, brand.get("name") or username,
                       update=args.force)
    if not url:
        say(f"    DEPLOY FAILED: {note}")
        reject(review, lead, [f"DEPLOY FAILED: {note}"], segment=segment,
               scraped_name=brand.get("name"), slug=slug, template=template)
        return "error"

    say(f"    LIVE       : {url}  ({note})")
    demos[username] = url
    meta[username] = {
        "url": url, "slug": slug, "repo": f"{OWNER}/demo-{slug}",
        "template": template, "name": brand.get("name"),
        "website": brand.get("final_url") or lead.get("Website"),
        "primary": brand.get("primary"), "accent": brand.get("accent"),
        "palette": {k: v for k, v in pal.items() if not k.startswith("_")},
        "contrast": {k: v for k, v in pal.items() if k.startswith("_")},
        "logo_source": brand.get("logo_source"),
        "logo_px": f"{brand.get('logo_w')}x{brand.get('logo_h')}",
        "usable_images": brand.get("usable_images"),
        "replaced": report["swapped"], "build_mb": report["build_mb"],
        "built_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    save_json(DEMOS_JSON, demos)
    save_json(DEMOS_META_JSON, meta)

    if args.verify:
        say("    verifying live page (Pages needs a minute to build) ...")
        ok, checks = verify_live(url, brand)
        if ok:
            say("    verify     : " + ", ".join(f"{k}={v}" for k, v in checks.items()))
            meta[username]["verified"] = checks
            save_json(DEMOS_META_JSON, meta)
        else:
            say("    verify     : page not serving yet - check again in a minute")
    return "deployed"


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(
        description="Scrape a prospect's brand, reskin a dental template, "
                    "quality-gate it, deploy it to GitHub Pages.")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--lead-username", help="one lead, by Instagram username")
    src.add_argument("--from-queue", help="CSV of leads (queue.csv or the lead file)")
    ap.add_argument("--limit", type=int, default=10, help="batch size for --from-queue")
    ap.add_argument("--go", action="store_true",
                    help="actually create repos and deploy (default is dry run)")
    ap.add_argument("--dry-run", action="store_true",
                    help="explicit no-op default; kept for symmetry with the other scripts")
    ap.add_argument("--input", default=LEADS_CSV, help="lead CSV for --lead-username")
    ap.add_argument("--refresh", action="store_true", help="ignore the scrape cache")
    ap.add_argument("--force", action="store_true",
                    help="rebuild and re-push a demo we already made")
    ap.add_argument("--verify", action="store_true",
                    help="after deploy, fetch the live URL and check the brand landed")
    ap.add_argument("--discard-rejected", action="store_true",
                    help="delete build dirs of rejected demos instead of keeping them")
    ap.add_argument("--template", help="force a specific template folder name")
    args = ap.parse_args()

    if args.dry_run:
        args.go = False

    os.makedirs(BUILD_ROOT, exist_ok=True)
    os.makedirs(CACHE_ROOT, exist_ok=True)

    say("=" * 72)
    say("  DEMO GENERATOR - scrape brand -> reskin -> quality gate -> deploy")
    say("=" * 72)
    if not args.go:
        say("  DRY RUN (default). Nothing will be created on GitHub.")
        say("  Re-run with --go to actually deploy.")
    else:
        ok, _ = gh(["auth", "status"])
        if not ok:
            say("ERROR: gh is not authenticated. Run: gh auth login")
            sys.exit(1)
        say(f"  LIVE MODE. gh authenticated as {OWNER}. "
            f"Deploying to NEW repos named demo-*.")

    if args.template:
        global TEMPLATES
        if args.template not in TEMPLATES:
            say(f"ERROR: unknown template '{args.template}'. "
                f"Choose from: {', '.join(TEMPLATES)}")
            sys.exit(1)

    if args.lead_username:
        lead = find_lead(args.lead_username, args.input)
        if not lead:
            say(f"ERROR: no lead with Username '{args.lead_username}' in {args.input}")
            sys.exit(1)
        leads = [lead]
    else:
        leads = queue_rows(args.from_queue, args.limit)
        say(f"  {len(leads)} lead(s) from {args.from_queue}")

    demos = load_json(DEMOS_JSON, {})
    meta = load_json(DEMOS_META_JSON, {})
    review = load_json(NEEDS_REVIEW_JSON, [])
    review = [r for r in review
              if r.get("username") not in {(l.get("Username") or "") for l in leads}]

    if args.template:
        orig_pick = globals()["pick_template"]
        globals()["pick_template"] = lambda b: (args.template, "forced by --template")

    counts = {}
    for lead in leads:
        try:
            outcome = process(lead, args, demos, meta, review)
        except KeyboardInterrupt:
            say("\ninterrupted")
            break
        except Exception as e:                      # never let one lead kill a batch
            say(f"    UNEXPECTED ERROR: {type(e).__name__}: {e}")
            reject(review, lead,
                   [f"UNEXPECTED ERROR: {type(e).__name__}: {e}"])
            outcome = "error"
        counts[outcome] = counts.get(outcome, 0) + 1

    save_json(DEMOS_JSON, demos)
    save_json(DEMOS_META_JSON, meta)
    dedup, seen_u = [], set()
    for r in reversed(review):                  # keep the most recent verdict
        u = r.get("username")
        if u in seen_u:
            continue
        seen_u.add(u)
        dedup.append(r)
    review = list(reversed(dedup))
    save_json(NEEDS_REVIEW_JSON, strip_bytes(review))

    say("")
    say("=" * 72)
    say("  SUMMARY")
    say("=" * 72)
    total = sum(counts.values())
    for k in ("deployed", "would_deploy", "rejected", "skipped", "error"):
        if counts.get(k):
            say(f"  {k:<14} {counts[k]}")
    if total:
        shipped = counts.get("deployed", 0) + counts.get("would_deploy", 0)
        say(f"  gate pass rate {shipped}/{total} "
            f"({100.0 * shipped / total:.0f}%)")
    # failure histogram - which check killed how many, so a bad pass rate can be
    # diagnosed as "scraper broken" vs "threshold wrong" vs "leads unusable"
    batch_users = {(l.get("Username") or "").strip() for l in leads}
    batch_rejects = [r for r in review if r.get("username") in batch_users]
    if batch_rejects:
        hist, seg_hist = {}, {}
        for r in batch_rejects:
            for code in r.get("reason_codes") or ["other"]:
                hist[code] = hist.get(code, 0) + 1
            seg_hist[r.get("segment") or "?"] = seg_hist.get(r.get("segment") or "?", 0) + 1
        say("")
        say("  WHY LEADS WERE REJECTED (a lead can fail more than one check)")
        for code, n in sorted(hist.items(), key=lambda kv: -kv[1]):
            say(f"    {code:<20} {n:>3}")
        say("  BY SEGMENT")
        for seg, n in sorted(seg_hist.items(), key=lambda kv: -kv[1]):
            say(f"    {seg:<20} {n:>3}")

    say("")
    say(f"  demos.json             {len(demos)} live URL(s)")
    say(f"  demos_needs_review.json {len(review)} lead(s) need a human")
    if not args.go and counts.get("would_deploy"):
        say("")
        say("  Nothing was deployed. Re-run the same command with --go.")


if __name__ == "__main__":
    main()
