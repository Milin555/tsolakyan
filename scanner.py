#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
scanner.py -- Stage [1] of the Outreach Machine.

Reads the lead CSV, scans each lead's website, detects faults, scores the lead
and writes scan_results.json per the contract in BUILD_MASTER_PROMPT.md (SS2).

Usage:
    python scanner.py --limit 20 --country "United Kingdom"
    python scanner.py --country "United Kingdom" --workers 25 --output scan_results.json
    python scanner.py --limit 200            (any country)

Notes:
  - stdlib + requests + beautifulsoup4 only. No Playwright.
  - Everything is written UTF-8. Nothing non-ASCII is printed to the console.
  - Resume-safe: every completed lead is cached to scan_cache.json.
"""

import argparse
import csv
import json
import os
import re
import socket
import ssl
import sys
import threading
import time
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

warnings.filterwarnings("ignore")
try:
    import urllib3
    urllib3.disable_warnings()
except Exception:
    pass

csv.field_size_limit(10 ** 7)

# --------------------------------------------------------------------------
# CONFIG
# --------------------------------------------------------------------------

ROOT = os.path.dirname(os.path.abspath(__file__))
DEFAULT_INPUT = os.path.join(ROOT, "data", "dental_leads_targeted.csv")
DEFAULT_OUTPUT = os.path.join(ROOT, "scan_results.json")
DEFAULT_CACHE = os.path.join(ROOT, "scan_cache.json")

CONNECT_TIMEOUT = 6
READ_TIMEOUT = 10
TIMEOUT = (CONNECT_TIMEOUT, READ_TIMEOUT)
ASSET_TIMEOUT = (5, 6)
DNS_TIMEOUT = 6

MAX_HTML_BYTES = 3_000_000
MAX_IMAGES_CHECKED = 10
MAX_LINKS_CHECKED = 15
ASSET_TIME_BUDGET = 22          # seconds spent on image/link probing per site
SSL_EXPIRY_WARN_DAYS = 30
THIN_BODY_CHARS = 500
# Load time is measured while 25 scans run in parallel over one connection, so
# it is a floor, not a benchmark. Only flag genuinely awful times.
SLOW_LOAD_SECONDS = 12.0
HARD_FETCH_CAP = 30.0           # absolute wall-clock ceiling on one page fetch

USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.9",
    "Cache-Control": "no-cache",
}

SEVERITY_WEIGHT = {"critical": 30, "high": 15, "medium": 8, "low": 3}

# Hosts that are NOT a real website ---------------------------------------
AGGREGATORS = {
    "linktr.ee": "linktr.ee", "linkin.bio": "linkin.bio", "lnk.bio": "lnk.bio",
    "bio.link": "bio.link", "beacons.ai": "beacons.ai", "taplink.cc": "taplink.cc",
    "msha.ke": "milkshake", "campsite.bio": "campsite.bio", "solo.to": "solo.to",
    "allmylinks.com": "allmylinks", "komi.io": "komi", "shorby.com": "shorby",
    "stan.store": "stan.store", "flowcode.com": "flowcode", "linkr.bio": "linkr.bio",
    "linktree.com": "linktr.ee", "hoo.be": "hoo.be", "znap.link": "znap.link",
    "direct.me": "direct.me", "liinks.co": "liinks", "instabio.cc": "instabio",
    "linklist.bio": "linklist.bio", "linkme.bio": "linkme.bio",
    "beacons.page": "beacons.ai", "milkshake.app": "milkshake",
    "many.link": "many.link", "contactin.bio": "contactin.bio",
    "linkbio.co": "linkbio.co", "bio.fm": "bio.fm", "withkoji.com": "koji",
}
SHORTENERS = {
    "bit.ly": "bit.ly", "tinyurl.com": "tinyurl", "cutt.ly": "cutt.ly",
    "rb.gy": "rb.gy", "t.co": "t.co", "goo.gl": "goo.gl", "ow.ly": "ow.ly",
    "is.gd": "is.gd", "shorturl.at": "shorturl.at", "rebrand.ly": "rebrand.ly",
    "buff.ly": "buff.ly", "lnkd.in": "lnkd.in", "lcl.md": "lcl.md",
    "bityli.com": "bityli", "shrtco.de": "shrtco.de", "s.id": "s.id",
    "urlz.fr": "urlz.fr", "tiny.cc": "tiny.cc",
}
MESSENGERS = {
    "wa.me": "WhatsApp link", "api.whatsapp.com": "WhatsApp link",
    "whats.link": "WhatsApp link", "wa.link": "WhatsApp link",
    "chat.whatsapp.com": "WhatsApp link", "web.whatsapp.com": "WhatsApp link",
    "m.me": "Messenger link", "t.me": "Telegram link",
    "mywhats.net": "WhatsApp link", "walink.co": "WhatsApp link",
    "wa.link": "WhatsApp link", "whatsapp.com": "WhatsApp link",
}
SOCIAL_ONLY = {
    "facebook.com": "Facebook page", "www.facebook.com": "Facebook page",
    "m.facebook.com": "Facebook page", "fb.com": "Facebook page",
    "fb.me": "Facebook page", "instagram.com": "Instagram profile",
    "www.instagram.com": "Instagram profile", "youtube.com": "YouTube channel",
    "www.youtube.com": "YouTube channel", "youtu.be": "YouTube channel",
    "tiktok.com": "TikTok profile", "www.tiktok.com": "TikTok profile",
    "twitter.com": "Twitter profile", "x.com": "X profile",
    "linkedin.com": "LinkedIn page", "www.linkedin.com": "LinkedIn page",
    "sites.google.com": "Google Sites page",
    "business.site": "Google Business site",
    "g.page": "Google Business profile",
    "maps.app.goo.gl": "Google Maps pin",
}
# Third-party pages that are somebody else's product, not the lead's website
THIRD_PARTY = {
    "justgiving.com": "JustGiving fundraising page",
    "gofundme.com": "GoFundMe page",
    "eventbrite.com": "Eventbrite listing",
    "eventbrite.co.uk": "Eventbrite listing",
    "docs.google.com": "Google Doc/Form",
    "forms.gle": "Google Form",
    "drive.google.com": "Google Drive link",
    "app.smilevirtual.com": "third-party virtual consult page",
    "smilevirtual.com": "third-party virtual consult page",
    "calendly.com": "bare Calendly page",
    "wa.business": "WhatsApp link",
    "amazon.com": "Amazon listing",
    "etsy.com": "Etsy shop",
    "patreon.com": "Patreon page",
    "shopee.com": "marketplace listing",
    "sites.google.com": "Google Sites page",
    "invisalign.com": "Invisalign provider profile",
    "invisalign.co.uk": "Invisalign provider profile",
    "invisalign.com.au": "Invisalign provider profile",
    "providerbio.invisalign.com": "Invisalign provider profile",
    "gmail.com": "email address in the website field",
    "outlook.com": "email address in the website field",
    "yahoo.com": "email address in the website field",
    "hotmail.com": "email address in the website field",
}
BINARY_EXT = (".pdf", ".jpg", ".jpeg", ".png", ".gif", ".webp", ".doc", ".docx",
              ".zip", ".mp4", ".mov", ".xls", ".xlsx", ".ppt", ".pptx", ".csv")

MULTI_TLDS = {
    "co.uk", "org.uk", "me.uk", "ltd.uk", "plc.uk", "net.uk", "ac.uk", "gov.uk",
    "com.au", "net.au", "org.au", "co.nz", "com.br", "co.za", "com.sg",
    "co.in", "com.mx", "com.tr", "co.il", "com.my", "co.id", "com.ph",
    "co.jp", "or.jp", "ne.jp", "com.hk", "com.tw",
}

BOOKING_KEYWORDS = [
    "calendly", "nexhealth", "zocdoc", "localmed", "setmore", "acuityscheduling",
    "acuity", "dentrix", "opendental", "open dental", "simplifeye", "flexbooker",
    "squarespace-scheduling", "schedulicity", "appointmentcore", "dentalintel",
    "yapi", "revenuewell", "lighthouse360", "solutionreach", "carestack",
    "denticon", "curve dental", "practo", "dentally", "book now", "book online",
    "book an appointment", "book appointment", "request an appointment",
    "request appointment", "make an appointment", "schedule an appointment",
    "schedule online", "book a consultation", "book consultation",
    "online booking", "booking", "appointments",
]
BOOKING_STRONG = [
    "calendly", "nexhealth", "zocdoc", "localmed", "setmore", "acuityscheduling",
    "schedulicity", "simplifeye", "flexbooker", "dentally", "carestack",
    "book online", "book now", "book an appointment", "request an appointment",
    "online booking", "schedule an appointment",
]

TESTIMONIAL_KEYWORDS = [
    "testimonial", "testimonials", "what our patients say", "patient stories",
    "patient reviews", "our reviews", "read our reviews", "google reviews",
    "trustpilot", "reviews.io", "5-star", "5 star", "what people say",
    "client reviews", "happy patients", "patient feedback",
]
BEFORE_AFTER_KEYWORDS = [
    "before and after", "before & after", "before-and-after", "before/after",
    "before after", "smile gallery", "smile makeover gallery", "case study",
    "case studies", "transformation", "our work", "smile transformations",
]

SOCIAL_PLATFORMS = {
    "facebook": ["facebook.com", "fb.com", "fb.me"],
    "instagram": ["instagram.com"],
    "twitter": ["twitter.com", "x.com"],
    "linkedin": ["linkedin.com"],
    "youtube": ["youtube.com", "youtu.be"],
    "tiktok": ["tiktok.com"],
    "pinterest": ["pinterest."],
}

# Platform fingerprints, most specific first ------------------------------
PLATFORM_SIGNATURES = [
    ("ProSites", ["prosites.com", "prosites.net", "prositesdev", "/prosites/",
                  "prosite-", "cdn.prosites"]),
    ("PBHS", ["pbhs.com", "pbhswebsite", "cdn.pbhs", "pbhsdev", "/pbhs/"]),
    ("Officite", ["officite.com", "officite.net", "cdn.officite", "/officite/",
                  "officitedev"]),
    ("Dentalfone", ["dentalfone.com", "dentalfone.net", "dentalfone"]),
    ("Optimized360", ["optimized360", "o360.io", "cdn.o360", "/o360/", "op360"]),
    ("Dental Nexus", ["dentalnexus"]),
    ("TeleVox", ["televox.com"]),
    ("Sesame Communications", ["sesamecommunications", "sesamehub", "sesame24-7"]),
    ("Great Dental Websites", ["greatdentalwebsites"]),
    ("Wix", ["wix.com", "wixstatic.com", "wixsite.com", "parastorage.com",
             "wix-code", "x-wix-"]),
    ("Squarespace", ["squarespace.com", "static1.squarespace", "sqsp.net",
                     "squarespace-cdn"]),
    ("Webflow", ["webflow.com", "assets.website-files.com",
                 "cdn.prod.website-files.com", "webflow.io"]),
    ("Duda", ["irp.cdn-website.com", "static.cdn-website.com", "dudaone",
              "d.la4-c1-", "duda_website"]),
    ("GoDaddy", ["wsimg.com", "godaddysites.com", "godaddy.com",
                 "godaddy website builder"]),
    ("Shopify", ["cdn.shopify.com", "myshopify.com", "shopifycdn"]),
    ("Weebly", ["weebly.com", "weeblysite.com", "editmysite.com"]),
    ("Google Sites", ["sites.google.com", "gstatic.com/sites", "startpage.google"]),
    ("HubSpot CMS", ["hs-sites.com", "hubspot.net", "hs-scripts.com"]),
    ("Joomla", ["/media/jui/", "joomla!", "com_content", "/media/system/js/"]),
    ("Drupal", ["/sites/default/files", "drupal.js", "drupal.settings"]),
    ("Next.js", ["/_next/static", "__next_data__", "__next_f"]),
    ("Nuxt", ["__nuxt__", "/_nuxt/"]),
    ("Gatsby", ["gatsby-", "___gatsby"]),
    ("WordPress", ["wp-content", "wp-includes", "wp-json", "wordpress",
                   "/xmlrpc.php"]),
]
SPA_SIGNATURES = ["/assets/index-", "vite", "react-dom", "id=\"root\"",
                  "id='root'", "ng-version", "vue.js", "__vue__", "id=\"app\""]

# --------------------------------------------------------------------------
# REGEXES
# --------------------------------------------------------------------------

# Deliberately conservative: a bare run of digits is NOT a phone number.
# Accept international (+..), US (xxx-xxx-xxxx) and UK/AU/NZ (leading 0) forms.
RE_PHONE = re.compile(
    r"(?<![\d/])("
    r"\+\d{1,3}[\s.()-]{0,2}(?:\d[\s.()-]{0,2}){7,13}\d"       # +44 20 7946 0958
    r"|\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}"                       # (212) 555-0147
    r"|\(?0\d{1,4}\)?[\s.-]?\d{3,4}[\s.-]?\d{3,4}"              # 020 7946 0958
    r")(?![\d/])")
RE_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
RE_COPYRIGHT = re.compile(
    r"(?:\u00a9|&copy;|copyright|\(c\))\s*(?:[A-Za-z .,'&-]{0,40}?)"
    r"(?:(\d{4})\s*(?:-|\u2013|\u2014|to)\s*)?(\d{4})",
    re.IGNORECASE)
RE_YEAR = re.compile(r"\b(19|20)\d{2}\b")
RE_WP_THEME = re.compile(r"wp-content/themes/([A-Za-z0-9_.-]+)", re.IGNORECASE)
RE_GENERATOR = re.compile(
    r'<meta[^>]+name=["\']generator["\'][^>]+content=["\']([^"\']+)["\']',
    re.IGNORECASE)

PLACEHOLDER_EMAILS = ("example.com", "yourdomain", "domain.com", "email.com",
                      "sentry.io", "wixpress.com", "@2x", "@3x", ".png", ".jpg",
                      ".gif", ".svg", ".webp")

# --------------------------------------------------------------------------
# HELPERS
# --------------------------------------------------------------------------

_dns_cache = {}
_dns_lock = threading.Lock()
_local = threading.local()


def log(msg):
    """stderr, ASCII-safe (console is cp1252)."""
    try:
        sys.stderr.write(str(msg).encode("ascii", "replace").decode("ascii") + "\n")
        sys.stderr.flush()
    except Exception:
        pass


def now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def session():
    s = getattr(_local, "sess", None)
    if s is None:
        s = requests.Session()
        s.headers.update(HEADERS)
        # Each hop can cost connect+read, so this is the main driver of the
        # worst-case wall clock for one lead. Keep it short.
        s.max_redirects = 5
        adapter = requests.adapters.HTTPAdapter(pool_connections=4,
                                                pool_maxsize=8, max_retries=0)
        s.mount("http://", adapter)
        s.mount("https://", adapter)
        _local.sess = s
    return s


def normalise_url(raw):
    """Return (url, host) or (None, None) if it is not a usable URL."""
    if not raw:
        return None, None
    u = str(raw).strip().strip('"').strip("'").strip()
    u = u.replace("\\", "/").replace(" ", "")
    if not u or u.lower() in ("n/a", "na", "none", "null", "-", "#"):
        return None, None
    u = re.sub(r"^(https?):/{1,}", r"\1://", u, flags=re.IGNORECASE)
    if not re.match(r"^https?://", u, re.IGNORECASE):
        if "@" in u.split("/")[0] and "." in u:
            return None, None          # looks like an email address
        u = "https://" + u.lstrip("/")
    try:
        p = urlparse(u)
    except Exception:
        return None, None
    host = (p.hostname or "").lower().strip(".")
    if not host or "." not in host:
        return None, None
    if not host.isascii():
        try:                       # non-ASCII / IDN domain -> punycode
            host = host.encode("idna").decode("ascii")
        except Exception:
            return None, None
    if not re.match(r"^[a-z0-9.-]+\.[a-z0-9-]{2,24}$", host):
        return None, None
    path = p.path or "/"
    url = "%s://%s%s" % (p.scheme.lower(), host + (":%d" % p.port if p.port else ""), path)
    if p.query:
        url += "?" + p.query
    return url, host


def base_and_www(host):
    if host.startswith("www."):
        return host[4:], host
    return host, "www." + host


def is_registrable(host):
    """True when host looks like a top-level registrable domain (not a subdomain)."""
    parts = host.split(".")
    if len(parts) == 2:
        return True
    if len(parts) == 3 and ".".join(parts[-2:]) in MULTI_TLDS:
        return True
    return False


def resolves(host):
    with _dns_lock:
        if host in _dns_cache:
            return _dns_cache[host]
    ok, err = True, ""
    try:
        socket.getaddrinfo(host, 443, proto=socket.IPPROTO_TCP)
    except socket.gaierror as e:
        ok, err = False, "NXDOMAIN" if getattr(e, "errno", None) in (
            socket.EAI_NONAME, -2, 11001) else ("DNS error: %s" % e.strerror or str(e))
    except Exception as e:
        ok, err = False, "DNS error: %s" % type(e).__name__
    with _dns_lock:
        _dns_cache[host] = (ok, err)
    return ok, err


def ssl_info(host):
    """Return dict: valid, error_kind, expires (date str), days_left."""
    out = {"valid": False, "error_kind": None, "expires": None, "days_left": None}
    ctx = ssl.create_default_context()
    try:
        with socket.create_connection((host, 443), timeout=CONNECT_TIMEOUT) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ss:
                cert = ss.getpeercert()
        out["valid"] = True
        na = cert.get("notAfter") if cert else None
        if na:
            exp = datetime.strptime(na, "%b %d %H:%M:%S %Y %Z").replace(
                tzinfo=timezone.utc)
            out["expires"] = exp.date().isoformat()
            out["days_left"] = (exp - datetime.now(timezone.utc)).days
    except ssl.SSLCertVerificationError as e:
        msg = str(e).lower()
        if "expired" in msg:
            out["error_kind"] = "expired"
        elif "hostname mismatch" in msg or "doesn't match" in msg or "match either of" in msg:
            out["error_kind"] = "hostname_mismatch"
        elif "self-signed" in msg or "self signed" in msg:
            out["error_kind"] = "self_signed"
        elif "unable to get local issuer" in msg or "chain" in msg:
            out["error_kind"] = "incomplete_chain"
        else:
            out["error_kind"] = "invalid"
        out["detail"] = str(e)[:160]
    except ssl.SSLError as e:
        out["error_kind"] = "ssl_error"
        out["detail"] = str(e)[:160]
    except (socket.timeout, TimeoutError):
        out["error_kind"] = "timeout"
    except Exception as e:
        out["error_kind"] = "no_https_port"
        out["detail"] = type(e).__name__
    return out


def fetch(url, verify=True, identity=False):
    """GET with redirects, size-capped. Returns dict or raises."""
    s = session()
    t0 = time.time()
    extra = {"Accept-Encoding": "identity"} if identity else None
    r = s.get(url, timeout=TIMEOUT, allow_redirects=True, stream=True,
              verify=verify, headers=extra)
    raw = b""
    try:
        for chunk in r.iter_content(65536):
            if chunk:
                raw += chunk
            if len(raw) >= MAX_HTML_BYTES:
                break
            if time.time() - t0 > HARD_FETCH_CAP:
                break      # a slow trickle must never become a 200s hang
    except (requests.exceptions.ContentDecodingError, requests.exceptions.ChunkedEncodingError):
        # Server advertises gzip/br but sends something else. Real browsers
        # cope; urllib3 does not. Retry asking for no compression at all.
        try:
            r.close()
        except Exception:
            pass
        if not identity:
            return fetch(url, verify=verify, identity=True)
        raise
    finally:
        try:
            r.close()
        except Exception:
            pass
    elapsed = time.time() - t0
    enc = r.encoding or r.apparent_encoding or "utf-8"
    try:
        text = raw.decode(enc, errors="replace")
    except (LookupError, TypeError):
        text = raw.decode("utf-8", errors="replace")
    chain = [{"status": h.status_code, "url": h.url} for h in r.history]
    return {
        "status": r.status_code,
        "final_url": r.url,
        "html": text,
        "bytes": len(raw),
        "elapsed": elapsed,
        "chain": chain,
        "headers": {k.lower(): v for k, v in r.headers.items()},
    }


def probe(url, deadline):
    """HEAD (fallback ranged GET) an asset. Returns (alive, status_or_err).

    Only 404/410 and 5xx count as DEAD. 401/403/429/999 are bot-protection or
    rate-limiting, not broken links - claiming those in a cold email would be
    wrong, so they are treated as alive.
    """
    if time.time() > deadline:
        return None, "skipped"
    s = session()
    try:
        r = s.head(url, timeout=ASSET_TIMEOUT, allow_redirects=True, verify=False)
        if r.status_code in (400, 403, 405, 429, 501) or r.status_code >= 500:
            r = s.get(url, timeout=ASSET_TIMEOUT, allow_redirects=True,
                      stream=True, verify=False,
                      headers={"Range": "bytes=0-2048"})
            r.close()
        code = r.status_code
        dead = code in (404, 410) or code >= 500
        return (not dead), code
    except (requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout,
            requests.exceptions.Timeout):
        return True, "timeout"        # slow != broken; do not claim it
    except requests.exceptions.RequestException as e:
        return False, type(e).__name__
    except Exception as e:
        return False, type(e).__name__


def normalise_phone(raw):
    d = re.sub(r"\D", "", raw)
    if len(d) < 9 or len(d) > 15:
        return None
    if len(d) > 10:
        d = d[-10:]
    return d


def detect_platform(html, final_url, headers, host):
    low = (html or "").lower()
    hay = low + " " + (final_url or "").lower() + " " + " ".join(
        "%s:%s" % (k, v) for k, v in (headers or {}).items()).lower()
    for name, sigs in PLATFORM_SIGNATURES:
        for sig in sigs:
            if sig in hay:
                if name == "WordPress":
                    m = RE_WP_THEME.search(html or "")
                    if m:
                        return "WordPress (theme: %s)" % m.group(1)
                return name
    gen = RE_GENERATOR.search(html or "")
    if gen:
        g = gen.group(1).strip()
        if g and len(g) < 60:
            return g
    hits = sum(1 for s in SPA_SIGNATURES if s in low)
    if hits >= 1:
        soup_text_len = len(re.sub(r"<[^>]+>", " ", low))
        if "id=\"root\"" in low or "id='root'" in low or "/assets/index-" in low:
            return "Vite/React SPA"
        if "ng-version" in low:
            return "Angular SPA"
        if "vue.js" in low or "__vue__" in low:
            return "Vue SPA"
        if soup_text_len < 4000:
            return "JS SPA (no SSR)"
    if "x-powered-by" in (headers or {}):
        return "custom (%s)" % headers["x-powered-by"][:40]
    return "custom/unknown"


# --------------------------------------------------------------------------
# THE SCAN
# --------------------------------------------------------------------------

def scan_site(url, host):
    """Scan a real website. Returns (faults, meta)."""
    faults = []
    meta = {"final_url": None, "platform": "unknown", "reachable": False}

    def fault(code, sev, evidence):
        faults.append({"code": code, "severity": sev, "evidence": evidence})

    # A bio link pointing at a PDF/image is not a website - scan the root
    # instead, and record the fact that the link is a file.
    bio_path = urlparse(url).path or "/"
    binary_bio = bio_path.lower().rstrip("/").endswith(BINARY_EXT)
    if binary_bio:
        url = "%s://%s/" % (urlparse(url).scheme, host)

    # ---- DNS -------------------------------------------------------------
    base, www = base_and_www(host)
    base_ok, base_err = resolves(base)
    www_ok, www_err = resolves(www)
    host_ok = base_ok if host == base else www_ok

    if not base_ok and not www_ok:
        fault("DNS_FAIL", "critical", "%s does not resolve (%s)" % (host, base_err or "NXDOMAIN"))
        meta["platform"] = "dead domain"
        return faults, meta

    if host.startswith("www.") and not www_ok and base_ok:
        fault("WWW_DNS_FAIL", "critical",
              "%s %s while %s resolves" % (www, www_err or "NXDOMAIN", base))
    elif not www_ok and base_ok and is_registrable(base):
        fault("WWW_DNS_FAIL", "critical",
              "%s %s while %s resolves" % (www, www_err or "NXDOMAIN", base))
    if not base_ok and www_ok and is_registrable(base):
        fault("APEX_DNS_FAIL", "critical",
              "%s %s while %s resolves" % (base, base_err or "NXDOMAIN", www))

    # ---- pick a host that actually resolves ------------------------------
    if not host_ok:
        host = www if www_ok else base
        url = re.sub(r"^(https?://)[^/]+", r"\g<1>" + host, url)

    scheme = urlparse(url).scheme
    https_url = re.sub(r"^http://", "https://", url)
    http_url = re.sub(r"^https://", "http://", url)

    # ---- SSL -------------------------------------------------------------
    si = ssl_info(host)
    meta["ssl"] = si
    if si["valid"]:
        dl = si.get("days_left")
        if dl is not None and dl < 0:
            fault("SSL_EXPIRED", "critical", "expired %s" % si["expires"])
        elif dl is not None and dl <= SSL_EXPIRY_WARN_DAYS:
            fault("SSL_EXPIRING_SOON", "high",
                  "certificate expires %s (%d days)" % (si["expires"], dl))
    else:
        kind = si.get("error_kind")
        if kind == "expired":
            fault("SSL_EXPIRED", "critical", "certificate expired: %s" % si.get("detail", "")[:80])
        elif kind == "hostname_mismatch":
            fault("SSL_HOSTNAME_MISMATCH", "critical",
                  "certificate does not cover %s" % host)
        elif kind == "self_signed":
            fault("SSL_SELF_SIGNED", "critical", "self-signed certificate on %s" % host)
        elif kind == "incomplete_chain":
            fault("SSL_CHAIN_BROKEN", "critical", "incomplete certificate chain on %s" % host)
        elif kind == "no_https_port":
            fault("NO_HTTPS", "critical", "no HTTPS on %s (port 443 refused)" % host)
        elif kind == "timeout":
            fault("SSL_UNREACHABLE", "high", "port 443 timed out on %s" % host)
        else:
            fault("SSL_INVALID", "critical", "invalid certificate on %s (%s)" % (host, kind))

    # ---- HTTP ------------------------------------------------------------
    res, err = None, None
    for candidate, verify in ((https_url, True), (https_url, False), (http_url, True)):
        if candidate == https_url and not verify and res is not None:
            break
        try:
            res = fetch(candidate, verify=verify)
            break
        except requests.exceptions.SSLError as e:
            err = ("ssl", str(e)[:120])
            continue
        except requests.exceptions.TooManyRedirects:
            err = ("redirect_loop", "redirect loop")
            continue
        except (requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout,
                requests.exceptions.Timeout):
            err = ("timeout", "no response in %ds" % READ_TIMEOUT)
            continue
        except requests.exceptions.ConnectionError as e:
            err = ("conn", type(e).__name__)
            continue
        except Exception as e:
            err = ("other", type(e).__name__)
            continue

    # ---- bio link points at a dead deep page? fall back to the homepage ----
    orig_path = urlparse(url).path or "/"
    if orig_path not in ("", "/") and (res is None or res["status"] >= 400):
        bad = "no response" if res is None else "HTTP %d" % res["status"]
        root_res = None
        for candidate, verify in (("https://%s/" % host, True),
                                  ("https://%s/" % host, False),
                                  ("http://%s/" % host, True)):
            try:
                root_res = fetch(candidate, verify=verify)
                break
            except Exception:
                continue
        if root_res is not None and root_res["status"] < 400:
            fault("DEAD_BIO_LINK", "critical",
                  "the Instagram bio link %s returns %s while the homepage still works"
                  % (orig_path[:60], bad))
            res = root_res

    if res is None:
        kind = err[0] if err else "conn"
        if kind == "timeout":
            fault("TIMEOUT", "critical", "site did not respond within %ds" % READ_TIMEOUT)
        elif kind == "redirect_loop":
            fault("REDIRECT_LOOP", "critical", "infinite redirect loop on %s" % host)
        else:
            fault("SITE_UNREACHABLE", "critical",
                  "no HTTP response from %s (%s)" % (host, err[1] if err else "connection failed"))
        meta["platform"] = "unreachable"
        # A failed TLS handshake on a host we could not reach at all is the same
        # event, not a second fault - do not double-count it into the score.
        faults = [f for f in faults
                  if f["code"] not in ("SSL_INVALID", "SSL_UNREACHABLE", "NO_HTTPS")]
        return faults, meta

    if binary_bio:
        fault("BIO_LINK_IS_FILE", "medium",
              "the Instagram bio link opens the file %s rather than a website" % bio_path[:60])

    meta["final_url"] = res["final_url"]
    meta["status"] = res["status"]
    meta["bytes"] = res["bytes"]
    meta["load_seconds"] = round(res["elapsed"], 2)
    meta["redirect_chain"] = [c["status"] for c in res["chain"]]
    final_host = (urlparse(res["final_url"]).hostname or "").lower()

    status = res["status"]
    if status >= 500:
        fault("HTTP_5XX", "critical", "server returns HTTP %d" % status)
    elif status == 404:
        fault("HTTP_404", "critical", "homepage returns HTTP 404")
    elif status == 403:
        fault("HTTP_403", "critical", "homepage returns HTTP 403 Forbidden")
    elif status >= 400:
        fault("HTTP_%d" % status, "high", "homepage returns HTTP %d" % status)
    else:
        meta["reachable"] = True

    if urlparse(res["final_url"]).scheme == "http":
        if not any(f["code"] in ("NO_HTTPS",) for f in faults):
            fault("NO_HTTPS", "critical", "site serves over plain HTTP (%s)" % res["final_url"])
    if len(res["chain"]) >= 3:
        fault("LONG_REDIRECT_CHAIN", "low",
              "%d redirects: %s" % (len(res["chain"]),
                                    " -> ".join(str(c["status"]) for c in res["chain"])))

    parked_markers = ("this domain is for sale", "buy this domain", "domain is parked",
                      "godaddy.com/forsale", "hugedomains", "sedoparking",
                      "future home of something quite cool", "under construction",
                      "coming soon", "site is temporarily unavailable",
                      "default web site page", "index of /", "account suspended")
    html = res["html"] or ""
    low_html = html.lower()
    for marker in parked_markers:
        if marker in low_html[:6000]:
            fault("PARKED_OR_PLACEHOLDER", "critical",
                  "homepage shows placeholder text: '%s'" % marker)
            break

    for hostkey, label in list(SOCIAL_ONLY.items()) + list(AGGREGATORS.items()):
        if final_host == hostkey or final_host.endswith("." + str(hostkey)):
            fault("REDIRECTS_OFFSITE", "critical",
                  "domain redirects to %s (%s)" % (final_host, label if isinstance(label, str) else ""))
            break

    # ---- parse -----------------------------------------------------------
    try:
        soup = BeautifulSoup(html, "html.parser")
    except Exception:
        soup = BeautifulSoup("", "html.parser")

    for tag in soup(["script", "style", "noscript", "template", "svg"]):
        tag.decompose()
    body_text = re.sub(r"\s+", " ", soup.get_text(" ", strip=True))
    meta["body_chars"] = len(body_text)

    platform = detect_platform(html, res["final_url"], res["headers"], final_host)
    meta["platform"] = platform

    # An error page tells us nothing about booking/testimonials/etc - do not
    # invent content faults from a 404 or 500 body.
    if not meta["reachable"]:
        return faults, meta

    if meta["reachable"] and len(body_text) < THIN_BODY_CHARS:
        sev = "medium"
        note = "body %d chars" % len(body_text)
        if "SPA" in platform or "Next" in platform or "Nuxt" in platform:
            note += " (%s renders client-side, nothing for Google to index)" % platform
        fault("NO_SSR_CONTENT", "medium", note)
    if meta["reachable"] and len(body_text) < 120:
        fault("EMPTY_HOMEPAGE", "high", "homepage has %d chars of text" % len(body_text))

    if res["elapsed"] > SLOW_LOAD_SECONDS:
        fault("SLOW_LOAD", "medium",
              "homepage took %.0f seconds to deliver its HTML" % res["elapsed"])

    if not soup.find("meta", attrs={"name": re.compile("^viewport$", re.I)}):
        fault("NO_VIEWPORT_META", "high",
              "no mobile viewport meta tag - page does not scale on phones")

    title = (soup.title.string.strip() if soup.title and soup.title.string else "")
    if not title:
        fault("NO_TITLE", "medium", "page has no <title> tag")
    meta["title"] = title[:120]
    desc = soup.find("meta", attrs={"name": re.compile("^description$", re.I)})
    if not desc or not (desc.get("content") or "").strip():
        fault("NO_META_DESCRIPTION", "low", "no meta description for search results")

    if urlparse(res["final_url"]).scheme == "https":
        mixed = re.findall(r'(?:src|href)=["\']http://[^"\']+["\']', html, re.I)
        mixed = [m for m in mixed if "://localhost" not in m and "w3.org" not in m
                 and "schema.org" not in m and "xmlns" not in m.lower()]
        if len(mixed) >= 3:
            fault("MIXED_CONTENT", "medium",
                  "%d assets loaded over insecure http:// on an https page" % len(mixed))

    # ---- images ----------------------------------------------------------
    deadline = time.time() + ASSET_TIME_BUDGET
    imgs, seen = [], set()
    for tag in BeautifulSoup(html, "html.parser").find_all("img"):
        src = (tag.get("src") or tag.get("data-src") or tag.get("data-lazy-src") or "").strip()
        if not src or src.startswith("data:") or src.startswith("blob:"):
            continue
        full = urljoin(res["final_url"], src)
        if full in seen:
            continue
        seen.add(full)
        imgs.append(full)
    total_imgs = len(imgs)
    dead_imgs = 0
    checked_imgs = 0
    dead_img_example = ""
    for u in imgs[:MAX_IMAGES_CHECKED]:
        alive, st = probe(u, deadline)
        if alive is None:
            break
        checked_imgs += 1
        if not alive:
            dead_imgs += 1
            if not dead_img_example:
                dead_img_example = "%s -> %s" % (u.split("/")[-1][:40], st)
    meta["images_total"] = total_imgs
    if total_imgs == 0 and meta["reachable"] and len(body_text) > 200:
        fault("NO_IMAGES", "medium", "homepage contains zero <img> tags")
    if dead_imgs:
        fault("DEAD_IMAGES", "medium",
              "%d of %d images checked return an error (%s)" % (dead_imgs, checked_imgs, dead_img_example))

    # ---- internal links --------------------------------------------------
    links, lseen = [], set()
    for a in BeautifulSoup(html, "html.parser").find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith(("#", "mailto:", "tel:", "javascript:", "sms:", "data:")):
            continue
        full = urljoin(res["final_url"], href)
        h = (urlparse(full).hostname or "").lower()
        if h != final_host:
            continue
        if "/cdn-cgi/" in full or "/wp-json" in full or "/feed" in full:
            continue          # infrastructure endpoints, not navigation
        full = full.split("#")[0]
        if full in lseen or full.rstrip("/") == res["final_url"].rstrip("/"):
            continue
        lseen.add(full)
        links.append(full)
    dead_links = 0
    checked_links = 0
    dead_link_example = ""
    for u in links[:MAX_LINKS_CHECKED]:
        alive, st = probe(u, deadline)
        if alive is None:
            break
        checked_links += 1
        if not alive:
            dead_links += 1
            if not dead_link_example:
                dead_link_example = "%s -> %s" % (urlparse(u).path[:40] or "/", st)
    meta["links_total"] = len(links)
    if dead_links:
        sev = "high" if dead_links >= 3 else "medium"
        fault("DEAD_LINKS", sev,
              "%d of %d internal links checked are broken (%s)" % (dead_links, checked_links, dead_link_example))
    if meta["reachable"] and len(links) == 0 and len(body_text) > 200:
        fault("NO_INTERNAL_LINKS", "medium", "homepage has no internal navigation links")

    # ---- booking ---------------------------------------------------------
    hay = low_html
    booking_hits = [k for k in BOOKING_KEYWORDS if k in hay]
    strong_hits = [k for k in BOOKING_STRONG if k in hay]
    meta["booking_signals"] = strong_hits[:4] or booking_hits[:4]
    if not booking_hits:
        fault("NO_BOOKING", "high",
              "no booking keyword found anywhere on the homepage")
    elif not strong_hits:
        fault("WEAK_BOOKING", "medium",
              "only passive booking wording (%s), no real online booking system" % ", ".join(booking_hits[:3]))

    # ---- phone -----------------------------------------------------------
    phones, tel_links = {}, []
    for a in BeautifulSoup(html, "html.parser").find_all("a", href=True):
        href = a["href"].strip()
        if href.lower().startswith("tel:"):
            tel_links.append(href[4:])
    candidates = list(tel_links)
    for m in RE_PHONE.finditer(body_text):
        candidates.append(m.group(0))
    for c in candidates:
        digits = re.sub(r"\D", "", c)
        if len(digits) < 9 or len(digits) > 15:
            continue
        if re.match(r"^(19|20)\d{2}$", digits):
            continue
        key = normalise_phone(c)
        if key and key not in phones:
            phones[key] = c.strip()
    meta["phones"] = list(phones.values())[:5]
    if not phones:
        fault("NO_PHONE", "high", "no phone number found in the page HTML")
    elif len(phones) >= 2:
        vals = list(phones.values())[:3]
        fault("PHONE_CONFLICT", "high",
              "%d different numbers on one page: %s" % (len(phones), ", ".join(vals)))
    if not tel_links and phones:
        fault("PHONE_NOT_CLICKABLE", "medium",
              "phone number is text only - not a tap-to-call tel: link")

    # ---- email -----------------------------------------------------------
    emails = set()
    for m in RE_EMAIL.finditer(html):
        e = m.group(0).lower()
        if any(p in e for p in PLACEHOLDER_EMAILS):
            continue
        emails.add(e)
    meta["emails"] = sorted(emails)[:3]
    if not emails:
        fault("NO_EMAIL", "medium", "no contact email address published on the site")

    # ---- social ----------------------------------------------------------
    found_social = set()
    for name, doms in SOCIAL_PLATFORMS.items():
        for d in doms:
            if d in hay:
                found_social.add(name)
                break
    meta["social"] = sorted(found_social)
    if not found_social:
        fault("NO_SOCIAL_LINKS", "low", "no social media links on the site")

    # ---- trust content ---------------------------------------------------
    if not any(k in hay for k in TESTIMONIAL_KEYWORDS):
        fault("NO_TESTIMONIALS", "medium", "no patient testimonials or reviews on the homepage")
    if not any(k in hay for k in BEFORE_AFTER_KEYWORDS):
        fault("NO_BEFORE_AFTER", "low", "no before/after or smile gallery found")

    # ---- copyright -------------------------------------------------------
    this_year = datetime.now().year
    years = []
    for m in RE_COPYRIGHT.finditer(body_text[-4000:] if len(body_text) > 4000 else body_text):
        for g in m.groups():
            if g and 1990 <= int(g) <= this_year + 1:
                years.append(int(g))
    if not years:
        for m in RE_COPYRIGHT.finditer(html):
            for g in m.groups():
                if g and 1990 <= int(g) <= this_year + 1:
                    years.append(int(g))
    if years:
        y = max(years)
        meta["copyright_year"] = y
        if y < this_year - 1:
            fault("STALE_COPYRIGHT", "low",
                  "footer still says (c) %d - %d years out of date" % (y, this_year - y))

    return faults, meta


def scan_lead(row):
    """Full per-lead scan. Never raises."""
    username = (row.get("Username") or "").strip()
    result = {
        "username": username,
        "name": (row.get("Name") or "").strip(),
        "email": (row.get("Email") or "").strip(),
        "country": (row.get("Country") or "").strip(),
        "phone_csv": (row.get("Phone") or "").strip(),
        "followers": _int(row.get("Followers")),
        "website": (row.get("Website") or "").strip(),
        "final_url": None,
        "scanned_at": now_iso(),
        "reachable": False,
        "faults": [],
        "platform": "none",
        "score": 0,
        "pitch_hook": "",
    }
    raw = result["website"]

    try:
        if not raw:
            result["faults"] = [
                {"code": "NO_WEBSITE", "severity": "critical",
                 "evidence": "Instagram bio has no website link at all"},
                {"code": "NO_BOOKING", "severity": "high",
                 "evidence": "no site means no online booking"},
                {"code": "NO_SEO_PRESENCE", "severity": "high",
                 "evidence": "nothing to rank in Google for local dental searches"},
            ]
            result["platform"] = "none"
        else:
            url, host = normalise_url(raw)
            if not url:
                result["faults"] = [{
                    "code": "MALFORMED_URL", "severity": "critical",
                    "evidence": "bio link is not a usable URL: %s" % raw[:80]}]
                result["platform"] = "invalid link"
            else:
                bucket = _link_bucket(host)
                if bucket:
                    label, plat, code = bucket
                    result["faults"] = [
                        {"code": code, "severity": "critical",
                         "evidence": "only online presence is a %s (%s) - no real website"
                                     % (label, url[:70])},
                        {"code": "NO_BOOKING", "severity": "high",
                         "evidence": "no site means no online booking"},
                        {"code": "NO_SEO_PRESENCE", "severity": "high",
                         "evidence": "a %s cannot rank in Google for local searches" % label},
                    ]
                    result["platform"] = plat
                    result["final_url"] = url
                else:
                    faults, meta = scan_site(url, host)
                    result["faults"] = faults
                    result["platform"] = meta.get("platform", "unknown")
                    result["reachable"] = meta.get("reachable", False)
                    result["final_url"] = meta.get("final_url")
                    result["details"] = {k: v for k, v in meta.items()
                                         if k not in ("platform", "reachable", "final_url")}
    except Exception as e:
        result["faults"] = [{"code": "SCAN_ERROR", "severity": "medium",
                             "evidence": "scanner error: %s: %s" % (type(e).__name__, str(e)[:100])}]
        result["platform"] = "unknown"

    result["score"] = score_faults(result["faults"])
    result["pitch_hook"] = build_pitch(result)
    return result


def _int(v):
    try:
        return int(float(str(v).strip()))
    except Exception:
        return 0


def _link_bucket(host):
    """(label, platform, fault_code) if host is not a real website."""
    h = host.lower()
    for d, lab in AGGREGATORS.items():
        if h == d or h.endswith("." + d):
            return ("link-in-bio page", lab, "NO_REAL_WEBSITE")
    for d, lab in SHORTENERS.items():
        if h == d or h.endswith("." + d):
            return ("shortened link", lab, "NO_REAL_WEBSITE")
    for d, lab in MESSENGERS.items():
        if h == d or h.endswith("." + d):
            return (lab, lab, "NO_REAL_WEBSITE")
    for d, lab in SOCIAL_ONLY.items():
        if h == d or h.endswith("." + d):
            return (lab, lab, "NO_REAL_WEBSITE")
    for d, lab in THIRD_PARTY.items():
        if h == d or h.endswith("." + d):
            return (lab, lab, "NO_REAL_WEBSITE")
    return None


def score_faults(faults):
    total = 0
    for f in faults:
        total += SEVERITY_WEIGHT.get(f.get("severity"), 0)
    return min(total, 100)


# --------------------------------------------------------------------------
# PITCH HOOK
# --------------------------------------------------------------------------

PITCH_PRIORITY = [
    "SSL_EXPIRED", "SSL_HOSTNAME_MISMATCH", "SSL_SELF_SIGNED", "SSL_CHAIN_BROKEN",
    "SSL_INVALID", "DNS_FAIL", "WWW_DNS_FAIL", "APEX_DNS_FAIL", "HTTP_5XX",
    "HTTP_404", "HTTP_403", "SITE_UNREACHABLE", "TIMEOUT", "REDIRECT_LOOP",
    "PARKED_OR_PLACEHOLDER", "REDIRECTS_OFFSITE", "DEAD_BIO_LINK", "NO_HTTPS",
    "NO_WEBSITE", "NO_REAL_WEBSITE", "MALFORMED_URL", "EMPTY_HOMEPAGE", "DEAD_LINKS",
    "DEAD_IMAGES", "NO_SSR_CONTENT", "PHONE_CONFLICT", "NO_VIEWPORT_META",
    "SLOW_LOAD", "BIO_LINK_IS_FILE", "NO_BOOKING", "NO_SEO_PRESENCE",
    "NO_PHONE", "STALE_COPYRIGHT", "MIXED_CONTENT",
    "WEAK_BOOKING", "NO_TESTIMONIALS", "PHONE_NOT_CLICKABLE", "NO_IMAGES",
    "NO_EMAIL", "NO_TITLE", "NO_BEFORE_AFTER", "NO_SOCIAL_LINKS",
]


def _article(word):
    return "an" if word[:1].lower() in "aeiou" else "a"


def build_pitch(result):
    faults = result.get("faults") or []
    if not faults:
        return ""
    by_code = {}
    for f in faults:
        by_code.setdefault(f["code"], f)
    chosen = None
    for code in PITCH_PRIORITY:
        if code in by_code:
            chosen = by_code[code]
            break
    if chosen is None:
        chosen = sorted(faults, key=lambda f: -SEVERITY_WEIGHT.get(f["severity"], 0))[0]

    code = chosen["code"]
    ev = chosen.get("evidence", "")
    host = ""
    try:
        fu = result.get("final_url")
        if fu:
            host = (urlparse(fu).hostname or "")
        if not host:
            host = normalise_url(result.get("website") or "")[1] or ""
    except Exception:
        host = ""
    host = host or "your site"
    name = result.get("name") or "your practice"
    plat = result.get("platform") or ""

    T = {
        "SSL_EXPIRED":
            "Your SSL certificate on %s has expired (%s), so Chrome is showing every "
            "visitor a red 'Not secure - attackers may be trying to steal your "
            "information' warning before they can reach your practice." % (host, ev),
        "SSL_HOSTNAME_MISMATCH":
            "The security certificate on %s does not actually cover that address, so "
            "browsers block the page with a full-screen privacy warning." % host,
        "SSL_SELF_SIGNED":
            "%s is using a self-signed certificate, which every modern browser treats "
            "as untrusted and hides behind a warning page." % host,
        "SSL_CHAIN_BROKEN":
            "The certificate chain on %s is incomplete, so a share of your visitors "
            "(especially on Android) get a security warning instead of your site." % host,
        "SSL_INVALID":
            "The SSL certificate on %s is invalid, so browsers warn visitors away "
            "before your homepage loads." % host,
        "DNS_FAIL":
            "Your domain %s does not resolve at all any more - anyone typing it in "
            "gets a 'site can't be reached' error, which means the link in your "
            "Instagram bio is dead." % host,
        "WWW_DNS_FAIL":
            "Anyone who types www in front of your domain never reaches you - %s - "
            "and that is a silent leak of patients who assume you have closed." % ev,
        "APEX_DNS_FAIL":
            "Your bare domain is dead - %s - so every link, business card and "
            "directory listing without 'www' sends patients to an error page." % ev,
        "HTTP_5XX":
            "Your homepage is currently returning a server error (%s), so right now "
            "nobody can see your site at all." % ev,
        "HTTP_404":
            "Your homepage at %s returns a 404 Not Found - the link in your bio "
            "leads to an error page." % host,
        "HTTP_403":
            "Your server is returning 403 Forbidden on the homepage, so visitors and "
            "Google are both locked out of %s." % host,
        "SITE_UNREACHABLE":
            "I could not reach %s at all from the UK (%s) - your bio link is "
            "effectively offline for anyone trying to find you." % (host, ev),
        "TIMEOUT":
            "%s took longer than 10 seconds to respond and then gave up entirely - "
            "most patients leave after three." % host,
        "REDIRECT_LOOP":
            "%s is stuck in an infinite redirect loop, so the browser gives up and "
            "shows an error instead of your practice." % host,
        "PARKED_OR_PLACEHOLDER":
            "The page at %s is still showing a placeholder/parked page rather than "
            "your practice (%s)." % (host, ev),
        "REDIRECTS_OFFSITE":
            "Your domain no longer serves a website - it just bounces visitors "
            "straight to a social page (%s)." % ev,
        "DEAD_BIO_LINK":
            "The link in your Instagram bio is dead - %s - so every follower who taps "
            "it lands on an error page instead of your practice." % ev,
        "NO_SEO_PRESENCE":
            "You have no real website, so when someone in your area googles 'dentist "
            "near me' there is simply nothing of yours for Google to show.",
        "NO_HTTPS":
            "%s still loads over plain http, so Chrome flags it 'Not secure' in the "
            "address bar on every single visit." % host,
        "NO_WEBSITE":
            "%s has no website link in the Instagram bio at all, so every patient who "
            "wants to book has to DM you and wait." % name,
        "NO_REAL_WEBSITE":
            "The only link you have is %s %s rather than a real website, which means "
            "you are invisible in Google when someone searches for a dentist near "
            "them." % (_article(plat or "link-in-bio page"), plat or "link-in-bio page"),
        "MALFORMED_URL":
            "The link in your Instagram bio is broken and does not open a working "
            "page (%s)." % ev,
        "EMPTY_HOMEPAGE":
            "Your homepage delivers almost no readable content to Google (%s), so it "
            "is effectively an empty page as far as search is concerned." % ev,
        "DEAD_LINKS":
            "Several links in your own navigation are broken - %s - so patients "
            "clicking through your site hit error pages." % ev,
        "DEAD_IMAGES":
            "There are broken images on your homepage right now (%s) - visitors see "
            "empty grey boxes where your practice photos should be." % ev,
        "NO_SSR_CONTENT":
            "Your homepage ships almost no HTML to Google (%s), so search engines see "
            "a blank page where your services should be." % ev,
        "PHONE_CONFLICT":
            "Your site shows %s - a patient reading it has no idea which one actually "
            "rings your front desk." % ev,
        "NO_VIEWPORT_META":
            "Your site has no mobile viewport tag, so on a phone it loads zoomed-out "
            "and unreadable - and roughly 70%% of dental searches happen on mobile.",
        "SLOW_LOAD":
            "Your %s, and more than half of mobile visitors give up on a page that "
            "slow before it ever finishes." % ev,
        "NO_BOOKING":
            "There is no way to book an appointment on your site - not one booking "
            "link or form anywhere on the homepage - so every enquiry has to become "
            "a phone call during opening hours.",
        "NO_PHONE":
            "I could not find a phone number anywhere in your homepage HTML, which "
            "means a patient on mobile has nothing to tap.",
        "STALE_COPYRIGHT":
            "Your %s, which quietly tells every visitor the site has been "
            "abandoned." % ev,
        "BIO_LINK_IS_FILE":
            "The link in your Instagram bio opens a file rather than a website - %s - "
            "so nobody who taps it ever lands on a page that can book them in." % ev,
        "MIXED_CONTENT":
            "Your https pages are still loading %s, which breaks the padlock and "
            "makes the browser flag your site as insecure." % ev,
        "WEAK_BOOKING":
            "Your site talks about appointments but has no actual online booking - "
            "%s - so every request still has to go through the phone." % ev,
        "NO_TESTIMONIALS":
            "There is not a single patient review or testimonial on your homepage, "
            "which is the first thing a nervous new patient looks for.",
        "PHONE_NOT_CLICKABLE":
            "Your phone number is plain text rather than a tap-to-call link, so "
            "mobile visitors have to copy it out by hand.",
        "NO_IMAGES":
            "Your homepage has no images at all - no practice, no team, no smiles - "
            "which makes it very hard to trust.",
        "NO_EMAIL":
            "There is no contact email published anywhere on your site, so anyone who "
            "cannot call has no way to reach you.",
        "NO_TITLE":
            "Your homepage has no title tag, so Google shows a bare URL in search "
            "results instead of your practice name.",
        "NO_BEFORE_AFTER":
            "You have no before/after or smile gallery on the site, which is the "
            "single most persuasive thing a cosmetic dental page can show.",
        "NO_SOCIAL_LINKS":
            "Your website does not link to your Instagram at all, so the audience you "
            "have built there never connects to your site.",
    }
    hook = T.get(code)
    if not hook:
        hook = "I spotted a problem on %s: %s." % (host, ev)
    return re.sub(r"\s+", " ", hook).strip()


# --------------------------------------------------------------------------
# IO
# --------------------------------------------------------------------------

def load_cache(path):
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, dict):
            return data
    except Exception as e:
        log("[warn] could not read cache %s (%s) - starting fresh" % (path, e))
    return {}


def save_json(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def read_leads(path, country=None, limit=None, skip_no_website=False):
    wanted = []
    if country:
        wanted = [c.strip().lower() for c in country.split(",") if c.strip()]
    rows = []
    with open(path, "r", encoding="utf-8", errors="replace", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            c = (row.get("Country") or "").strip().lower()
            if wanted and not any(w in c or c in w for w in wanted):
                continue
            if skip_no_website and not (row.get("Website") or "").strip():
                continue
            if not (row.get("Username") or "").strip():
                continue
            rows.append(row)
            if limit and len(rows) >= limit:
                break
    return rows


# --------------------------------------------------------------------------
# MAIN
# --------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(
        description="Scan lead websites for faults and score them.")
    ap.add_argument("--input", default=DEFAULT_INPUT, help="lead CSV")
    ap.add_argument("--output", default=DEFAULT_OUTPUT, help="scan_results.json")
    ap.add_argument("--cache", default=DEFAULT_CACHE, help="scan_cache.json")
    ap.add_argument("--country", default=None,
                    help='filter, substring match, comma-separated (e.g. "United Kingdom")')
    ap.add_argument("--limit", type=int, default=None, help="max leads this run")
    ap.add_argument("--workers", type=int, default=25, help="threads (20-30)")
    ap.add_argument("--with-website-only", action="store_true",
                    help="skip leads whose Website column is empty")
    ap.add_argument("--min-score", type=int, default=0,
                    help="only write leads scoring >= this to the output file")
    ap.add_argument("--refresh", action="store_true",
                    help="ignore the cache and re-scan everything selected")
    ap.add_argument("--no-cache-write", action="store_true",
                    help="do not persist results to the cache file")
    args = ap.parse_args()

    workers = max(1, min(40, args.workers))

    if not os.path.exists(args.input):
        log("[fatal] input not found: %s" % args.input)
        return 2

    t_start = time.time()
    leads = read_leads(args.input, args.country, args.limit, args.with_website_only)
    log("[scanner] %d leads selected from %s" % (len(leads), os.path.basename(args.input)))
    if args.country:
        log("[scanner] country filter: %s" % args.country)

    cache = {} if args.refresh else load_cache(args.cache)
    log("[scanner] cache holds %d previously scanned leads" % len(cache))

    todo = [r for r in leads if (r.get("Username") or "").strip() not in cache]
    cached_hits = len(leads) - len(todo)
    log("[scanner] %d already cached (skipping), %d to scan with %d workers"
        % (cached_hits, len(todo), workers))

    results_by_user = {}
    for r in leads:
        u = (r.get("Username") or "").strip()
        if u in cache:
            results_by_user[u] = cache[u]

    done = 0
    errors = 0
    if todo:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(scan_lead, row): row for row in todo}
            for fut in as_completed(futures):
                row = futures[fut]
                u = (row.get("Username") or "").strip()
                try:
                    res = fut.result()
                except Exception as e:
                    errors += 1
                    res = {"username": u, "name": (row.get("Name") or "").strip(),
                           "email": (row.get("Email") or "").strip(),
                           "country": (row.get("Country") or "").strip(),
                           "website": (row.get("Website") or "").strip(),
                           "final_url": None, "scanned_at": now_iso(),
                           "reachable": False,
                           "faults": [{"code": "SCAN_ERROR", "severity": "medium",
                                       "evidence": "worker crashed: %s" % type(e).__name__}],
                           "platform": "unknown", "score": 8, "pitch_hook": ""}
                results_by_user[u] = res
                cache[u] = res
                done += 1
                if done % 100 == 0:
                    rate = done / max(0.001, time.time() - t_start)
                    log("[scanner] %d/%d scanned  (%.1f/s, %d cached hits, %d errors)"
                        % (done, len(todo), rate, cached_hits, errors))
                    if not args.no_cache_write:
                        save_json(args.cache, cache)

    if not args.no_cache_write:
        save_json(args.cache, cache)

    ordered = [results_by_user[(r.get("Username") or "").strip()]
               for r in leads
               if (r.get("Username") or "").strip() in results_by_user]
    ordered = [r for r in ordered if r.get("score", 0) >= args.min_score]
    ordered.sort(key=lambda r: (-r.get("score", 0), -_int(r.get("followers", 0))))
    save_json(args.output, ordered)

    # ---- summary ---------------------------------------------------------
    elapsed = time.time() - t_start
    n = len(ordered)
    clean = sum(1 for r in ordered if r.get("score", 0) == 0)
    reach = sum(1 for r in ordered if r.get("reachable"))
    avg = (sum(r.get("score", 0) for r in ordered) / n) if n else 0
    log("")
    log("[scanner] DONE  %d leads in %.1fs  (%d newly scanned, %d from cache, %d errors)"
        % (n, elapsed, done, cached_hits, errors))
    log("[scanner] reachable sites: %d | clean (score 0, DO NOT CONTACT): %d | avg score: %.1f"
        % (reach, clean, avg))
    log("[scanner] wrote %s" % args.output)
    log("[scanner] cache  %s (%d entries)" % (args.cache, len(cache)))

    fault_counts = {}
    plat_counts = {}
    for r in ordered:
        for f in r.get("faults", []):
            fault_counts[f["code"]] = fault_counts.get(f["code"], 0) + 1
        p = r.get("platform") or "unknown"
        plat_counts[p] = plat_counts.get(p, 0) + 1
    log("")
    log("[scanner] top faults:")
    for code, c in sorted(fault_counts.items(), key=lambda kv: -kv[1])[:18]:
        log("            %-24s %5d  (%.0f%%)" % (code, c, 100.0 * c / max(1, n)))
    log("[scanner] platforms:")
    for p, c in sorted(plat_counts.items(), key=lambda kv: -kv[1])[:15]:
        log("            %-32s %5d" % (p[:32], c))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        log("\n[scanner] interrupted - cache preserved, re-run to resume")
        sys.exit(130)
