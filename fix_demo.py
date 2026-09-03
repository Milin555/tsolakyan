"""
fix_demo.py - strip the Foundation Dental Retreats coaching template's own
content out of a built/deployed demo.

The four source templates were reskins of a dental COACHING business
(Dr. Jim Arnold's Foundation Dental Retreats). The homepage reskins cleanly,
but About, Booking, Retreats and the doctor pages still carry that business's
real staff and its services - "Buy/Sell Advisory", "Transitions Program",
"CEO & Mastermind Coach". A prospect who clicks "Book an appointment" on their
own "rebuilt site" sees four strangers and a practice-brokerage service.

Verified live on all 21 deployed demos, 2 Sep 2026.

Usage:
    python3 fix_demo.py <dir> [--dry-run]
"""
import os, re, sys, glob

DROP_PAGES = ["apply.html", "retreats.html",
              "doctor-daniel-ahmed.html", "doctor-emilie-drumm.html",
              "doctor-emman-collins.html", "doctor-marcus-rishi.html"]

STRAY = ["Dr. Jim Arnold, DDS", "Dr. Jim Arnold", "Jim Arnold",
         "Dr. Gary Solnit, DDS", "Dr. Gary Solnit", "Gary Solnit",
         "Debra Englehardt-Nash", "Englehardt-Nash",
         "Dr. Kathryn Alderman", "Kathryn Alderman",
         "Dr. Emilie Drumm", "Emilie Drumm", "Dr. Emman Collins",
         "Emman Collins", "Dr. Marcus Rishi", "Marcus Rishi",
         "Dr. Daniel Ahmed", "Daniel Ahmed"]

COACHING = ["Buy/Sell Advisory", "Transitions Program",
            "Accountability &amp; Board Peers", "Accountability & Board Peers",
            "CEO &amp; Mastermind Coach", "CEO & Mastermind Coach",
            "Founder &amp; Mastermind Host", "Founder & Mastermind Host",
            "Mastermind Host", "Mastermind Coach", "Mastermind"]


def match_block(src, start):
    """From an opening '<div' at start, return end index past its </div>."""
    i, depth = start, 0
    while i < len(src):
        if src.startswith("<div", i):
            depth += 1
            i += 4
        elif src.startswith("</div>", i):
            depth -= 1
            i += 6
            if depth == 0:
                return i
        else:
            i += 1
    return -1


def match_tag(src, start, tag):
    """From an opening <tag at start, return index past its matching </tag>."""
    i, depth = start, 0
    op, cl = "<" + tag, "</" + tag + ">"
    while i < len(src):
        if src.startswith(op, i) and (i + len(op) >= len(src) or src[i+len(op)] in " >\t\n"):
            depth += 1; i += len(op)
        elif src.startswith(cl, i):
            depth -= 1; i += len(cl)
            if depth == 0:
                return i
        else:
            i += 1
    return -1


def drop_section_containing(src, needle, tag="section"):
    """Remove the whole <section> that contains needle - heading, intro and all.

    Removing only the team cards leaves an orphaned 'Our Team / Superheroes
    Behind the Dental Care' header with nothing under it, which reads as a
    broken page. We do not know the practice's real dentists, so the honest
    result is no team section at all.
    """
    out, guard = src, 0
    while guard < 20:
        guard += 1
        hit = out.find(needle)
        if hit < 0:
            break
        seg = out[:hit]
        best = -1
        for m in re.finditer(r'<' + tag + r'[\s>]', seg):
            best = m.start()
        if best < 0:
            break
        end = match_tag(out, best, tag)
        if end < 0:
            break
        out = out[:best] + out[end:]
    return out


def drop_enclosing(src, needle, cls):
    """Remove every <div class=cls ...> block that contains needle."""
    out, guard = src, 0
    while guard < 40:
        guard += 1
        hit = out.find(needle)
        if hit < 0:
            break
        # walk back to the nearest opening div carrying cls
        seg = out[:hit]
        best = -1
        for m in re.finditer(r'<div[^>]*class="[^"]*' + re.escape(cls) + r'[^"]*"', seg):
            best = m.start()
        if best < 0:
            break
        end = match_block(out, best)
        if end < 0:
            break
        out = out[:best] + out[end:]
    return out


def fix_file(path, dry=False):
    src = open(path, encoding="utf-8", errors="replace").read()
    orig = src
    notes = []

    # 1. the whole team SECTION - heading, intro and cards together.
    #    Removing only the cards leaves an orphaned "Our Team / Superheroes
    #    Behind the Dental Care" header sitting above nothing.
    if "team_list" in src or "team_item" in src:
        before = src
        src = drop_section_containing(src, "team_list")
        src = drop_section_containing(src, "team_item")
        if src != before:
            notes.append("removed entire team section (heading + cards)")
    for n in ("Jim Arnold", "Gary Solnit", "Englehardt-Nash", "Kathryn Alderman"):
        before = src
        src = drop_enclosing(src, n, "w-dyn-item")
        if src != before:
            notes.append(f"removed leftover team card containing {n}")

    # 2. booking option-cards for coaching services and named dentists
    for n in ["Transitions Program"] + STRAY:
        before = src
        src = drop_enclosing(src, n, "option-card")
        if src != before:
            notes.append(f"removed booking option-card: {n}")

    # 3. the entire "Select Dentist" step - no real names to put in it
    m = re.search(r'<!--\s*Step 2: Dentist\s*-->\s*<div class="booking-step"', src)
    if m:
        b = src.find('<div class="booking-step"', m.start())
        e = match_block(src, b)
        if e > 0:
            src = src[:m.start()] + src[e:]
            notes.append("removed 'Select Dentist' booking step")

    # 3b. the careers section. The template advertises "Dental Assistant" and
    #     "Receptionist / Front Desk Officer" vacancies, all linking to
    #     apply.html. A demo must not advertise jobs the practice has not
    #     opened.
    if "job-item" in src or "job-images_list" in src:
        before = src
        src = drop_section_containing(src, "job-item")
        src = drop_section_containing(src, "job-images_list")
        if src != before:
            notes.append("removed careers/vacancies section")

    # 4. links to pages we delete. Hrefs carry query strings
    #    (apply.html?role=dentist), so match the page name then anything up to
    #    the closing quote.
    for p in DROP_PAGES:
        before = src
        href = r'href="' + re.escape(p) + r'[^"]*"'
        src = drop_enclosing(src, f'href="{p}', "w-dyn-item")
        src = re.sub(r'<li[^>]*>\s*<a[^>]+' + href + r'[^>]*>.*?</a>\s*</li>',
                     '', src, flags=re.S)
        src = re.sub(r'<a[^>]+' + href + r'[^>]*>.*?</a>', '', src, flags=re.S)
        if src != before:
            notes.append(f"removed links to {p}")

    # 5. any surviving stray strings anywhere (alt=, content=, onclick=, text)
    for n in sorted(STRAY, key=len, reverse=True):
        if n in src:
            src = src.replace(n, "Our clinical team")
            notes.append(f"scrubbed leftover '{n}'")
    for n in sorted(COACHING, key=len, reverse=True):
        if n in src:
            src = src.replace(n, "General Dentistry")
            notes.append(f"scrubbed coaching term '{n}'")

    if src != orig and not dry:
        open(path, "w", encoding="utf-8").write(src)
    return notes


def retitle(d, dry=False):
    """Every page shipped with the homepage's <title>. Give each its own."""
    idx = os.path.join(d, "index.html")
    if not os.path.exists(idx):
        return []
    home = open(idx, encoding="utf-8", errors="replace").read()
    m = re.search(r'<title[^>]*>(.*?)</title>', home, re.S | re.I)
    if not m:
        return []
    brand = m.group(1).split("|")[0].strip()
    LABEL = {"about": "About the practice", "booking": "Book an appointment",
             "blog": "News", "service": "Treatments",
             "service-cosmetic": "Cosmetic dentistry",
             "service-preventive": "Preventive dentistry",
             "service-restorative": "Restorative dentistry",
             "service-orthodontics": "Orthodontics",
             "privacy": "Privacy policy", "terms": "Terms",
             "cookies": "Cookie policy", "licenses": "Licenses",
             "404": "Page not found"}
    done = []
    for f in glob.glob(os.path.join(d, "*.html")):
        base = os.path.basename(f)[:-5]
        if base == "index" or base not in LABEL:
            continue
        s = open(f, encoding="utf-8", errors="replace").read()
        new = f"{brand} | {LABEL[base]}"
        s2 = re.sub(r'(<title[^>]*>).*?(</title>)', lambda mm: mm.group(1) + new + mm.group(2),
                    s, count=1, flags=re.S | re.I)
        if s2 != s:
            if not dry:
                open(f, "w", encoding="utf-8").write(s2)
            done.append(f"{base}.html -> '{new}'")
    return done


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    d = sys.argv[1]
    dry = "--dry-run" in sys.argv
    print(f"{'DRY RUN: ' if dry else ''}fixing {d}")
    for p in DROP_PAGES:
        f = os.path.join(d, p)
        if os.path.exists(f):
            print(f"  delete  {p}")
            if not dry:
                os.remove(f)
    total = 0
    for f in sorted(glob.glob(os.path.join(d, "*.html"))):
        notes = fix_file(f, dry)
        if notes:
            print(f"  {os.path.basename(f)}")
            for n in notes:
                print(f"      - {n}")
            total += len(notes)
    for t in retitle(d, dry):
        print(f"  title   {t}")
    print(f"  {total} content fix(es)")


if __name__ == "__main__":
    main()
