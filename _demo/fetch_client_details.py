"""Pulls each practice's real address, phone and dentist names off their site.

The image scrape got schema.org addresses for only 8 of 20, because most
clinic sites put the address in the footer as plain text rather than in
markup. This looks in all the places a real address actually lives, and also
collects the names of the dentists who actually work there so the team pages
can stop being placeholders.

    python _demo/fetch_client_details.py [--only slug]

Writes _demo/client_assets/<slug>/details.json
"""
import argparse, io, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from demo_config import load, BASE

OUT = os.path.join(BASE, "_demo", "client_assets")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

STREET = (r"\d{1,6}[\w\-]*\s+[A-Z][\w'.\-]*(?:\s+[A-Z][\w'.\-]*){0,4}\s+"
          r"(?:Street|St|Road|Rd|Avenue|Ave|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way|"
          r"Highway|Hwy|Parkway|Pkwy|Place|Pl|Court|Ct|Terrace|Circle|Trail|Plaza|Suite|Ste)\b"
          r"[^|\n<>]{0,60}")
US_TAIL = r"[A-Z][\w .'\-]{2,28},?\s+(?:A[LKZR]|C[AOT]|D[EC]|FL|GA|HI|I[ADLN]|K[SY]|LA|M[ADEINOST]|N[CDEHJMVY]|O[HKR]|P[AR]|RI|S[CD]|T[NX]|UT|V[AT]|W[AIVY])\s+\d{5}(?:-\d{4})?"
UK_PC = r"\b[A-Z]{1,2}\d{1,2}[A-Z]?\s*\d[A-Z]{2}\b"
AU_TAIL = r"[A-Z][\w .'\-]{2,28},?\s+(?:NSW|VIC|QLD|WA|SA|TAS|ACT|NT)\s+\d{4}"

NAME_RE = re.compile(r"\bDr\.?\s+([A-Z][a-z'\-]+(?:\s+[A-Z][a-z'\-]+){0,2})")
NOT_NAME = re.compile(r"^(And|The|Our|Your|Us|Who|What|When|Book|Call|Visit|Now|Today|"
                      r"Team|Staff|Office|Dental|Smile|Care|New|Meet|Welcome|About)$", re.I)


def clean(s):
    return re.sub(r"\s+", " ", (s or "")).strip(" ,|·-")


JUNK_ADDR = re.compile(
    r"(review|whatsapp|access|book now|call us|follow|instagram|facebook|"
    r"rating|star|award|hygienist|welcome|open|hours|am\b|pm\b|\?|!)", re.I)


def pick_address(text, country):
    """The most complete address-looking run that reaches a real locality.

    Requiring the locality is what separates an address from a sentence that
    happens to contain "Dr".
    """
    cands = []
    for m in re.finditer(STREET, text):
        seg = text[m.start():m.start() + 170]
        tail = None
        for pat in (US_TAIL, AU_TAIL, UK_PC):
            t = re.search(pat, seg)
            if t:
                tail = seg[:t.end()]
                break
        if tail:                       # no locality, no address
            cands.append(clean(tail))

    if not cands:                      # locality on its own still beats nothing
        for pat in (US_TAIL, AU_TAIL):
            for m in re.finditer(pat, text):
                cands.append(clean(m.group(0)))

    cands = [c for c in cands if 12 <= len(c) <= 140 and not JUNK_ADDR.search(c)]
    if not cands:
        return None
    cands.sort(key=len, reverse=True)
    return cands[0]


def scrape(pw, cfg):
    site = cfg["website"]
    out = {"slug": cfg["slug"], "address": None, "phone": None,
           "doctors": [], "pages": [], "error": None}
    if not site:
        out["error"] = "no website"
        return out

    b = pw.chromium.launch()
    ctx = b.new_context(user_agent=UA, viewport={"width": 1440, "height": 1000},
                        ignore_https_errors=True)
    try:
        page = ctx.new_page()
        page.goto(site, wait_until="domcontentloaded", timeout=40000)
        page.wait_for_timeout(2200)

        targets = [site]
        links = page.eval_on_selector_all("a[href]", "e => e.map(x => x.href)") or []
        for pat in (r"contact|location|find-us|visit",
                    r"meet|team|about|our-doctors?|staff|dentists?"):
            hit = [l for l in links if re.search(pat, l, re.I) and l.startswith("http")]
            targets += hit[:1]

        text_all, names = "", []
        for t in dict.fromkeys(targets):
            try:
                if t != site:
                    page.goto(t, wait_until="domcontentloaded", timeout=30000)
                    page.wait_for_timeout(1800)
                out["pages"].append(t)
                body = page.evaluate("() => document.body.innerText")
                text_all += "\n" + body
                if out["phone"] is None:
                    tel = page.eval_on_selector_all(
                        'a[href^="tel:"]', "e => e.map(x => x.getAttribute('href'))") or []
                    if tel:
                        out["phone"] = clean(tel[0].replace("tel:", ""))
                # Names from headings and image alts, where team members live.
                heads = page.eval_on_selector_all(
                    "h1,h2,h3,h4,img", "e => e.map(x => x.innerText || x.alt || '')") or []
                names += [h for h in heads if "Dr" in h]
            except Exception:
                pass

        out["address"] = pick_address(text_all, cfg["country"])

        raw = []
        for blob in names + [text_all]:
            for m in NAME_RE.finditer(blob or ""):
                n = clean(m.group(1))
                n = re.sub(r"\s+Dr\.?$", "", n).strip()      # "Chan Dr" -> "Chan"
                first = n.split()[0] if n.split() else ""
                if not first or NOT_NAME.match(first) or len(n) < 3:
                    continue
                raw.append(n)

        # A bare surname is the same person as the full name that contains it,
        # so keep the longest form of each and drop the fragments.
        raw = list(dict.fromkeys(raw))
        raw.sort(key=lambda s: -len(s.split()))
        docs = []
        for n in raw:
            if any(n != k and re.search(r"\b" + re.escape(n) + r"\b", k) for k in docs):
                continue
            docs.append(n)
        # A surname alone is no use on a profile page; keep one only if the
        # site never gave a full name for anyone.
        full = [n for n in docs if len(n.split()) >= 2]
        out["doctors"] = ["Dr. " + n for n in (full or docs)[:6]]
    except Exception as e:
        out["error"] = str(e)[:140]
    finally:
        try:
            ctx.close(); b.close()
        except Exception:
            pass

    d = os.path.join(OUT, cfg["slug"])
    os.makedirs(d, exist_ok=True)
    io.open(os.path.join(d, "details.json"), "w", encoding="utf-8").write(
        json.dumps(out, indent=2, ensure_ascii=False))
    return out


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(); ap.add_argument("--only"); a = ap.parse_args()
    from playwright.sync_api import sync_playwright

    rows = load()
    if a.only:
        rows = [r for r in rows if r["slug"] == a.only]
    na = np = nd = 0
    with sync_playwright() as pw:
        for cfg in rows:
            r = scrape(pw, cfg)
            na += bool(r["address"]); np += bool(r["phone"]); nd += bool(r["doctors"])
            print(f"{cfg['rank']:2} {cfg['slug'][:30]:32} "
                  f"addr {'Y' if r['address'] else 'n'} · tel {'Y' if r['phone'] else 'n'} · "
                  f"drs {len(r['doctors'])}  {clean(r['address'] or '')[:52]}")
    print(f"\n{na}/{len(rows)} address · {np}/{len(rows)} phone · {nd}/{len(rows)} with dentist names")
