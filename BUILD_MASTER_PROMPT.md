# BUILD MASTER PROMPT — OUTREACH MACHINE
**Target: turn 29,931 leads into personalised live demos + sent emails, automatically.**
**Owner: Milin · Machine: Windows, Python 3.12.10, Node 24.11.1, gh authed as Milin555**

---

## §0 SHARED CONTEXT — PASTE INTO EVERY BUILD AGENT

```
=== PROJECT: OUTREACH MACHINE (internal tool, single user) ===

This is NOT a product to sell. It is an internal tool for one operator.
No auth, no billing, no multi-user, no dashboard UI unless explicitly asked.
Optimise for: works today > elegant. CLI scripts > web app.

ROOT: C:\Users\Promise\Desktop\outreach

ENVIRONMENT (verified):
- Python 3.12.10 at C:\Users\Promise\AppData\Local\Programs\Python\Python312\python
- Node v24.11.1, npm available
- git (mingw64), curl, GitHub CLI `gh` authenticated as **Milin555**
- Windows. Console is cp1252 — ALWAYS write files with encoding="utf-8",
  and never print raw emoji/unicode to stdout or the script crashes.

THE LEAD FILE: data/dental_leads_targeted.csv  (29,931 rows, 8.4 MB)
Columns (exact, in order):
  Username, Name, Category, Email, Phone, Website, Country, Followers, Following, Bio
Notes:
- This is INSTAGRAM-SCRAPED data. Username/Followers/Following/Bio are IG fields.
- The Website column is EMPTY for many rows. ~23,388 have a website.
- Some "websites" are linktr.ee / bit.ly links — those are leads WITHOUT a real site.
- Country values include "United Kingdom", "Australia", "United States", etc.
- csv.field_size_limit must be raised (Bio fields are long): csv.field_size_limit(10**7)

EXISTING CODE (read before writing — do not duplicate):
- campaign_manager.py (336 ln) — SMTP sequencer. Spintax, 5-step follow-ups,
  DAILY_LIMIT_PER_ACCOUNT=25, reads email_accounts.txt, CRM at data/campaign_crm.csv.
  ** KNOWN BUG: line ~84 DEMO_LINK = "https://your-portfolio.vercel.app" is a
     PLACEHOLDER. Emails currently link nowhere. Must become per-lead. **
- deploy_all.py (209 ln) — deploys static sites to GitHub Pages via `gh`. OWNER="Milin555".
  Read its run() helper and PROJECTS list for the deploy pattern.
- check_replies.py (317 ln), check_bounces.py, check_account_health.py, dashboard.py
- add_and_update_crm.py — CRM helpers

TEMPLATES (each is a git repo with index.html + assets/):
- "Gary Solnit Dentist"  (also has variant-blue/)
- "Lura Dentist"         (also has variant-blue/)
- "Modern Smile Center Dentist" (also has variant-blue/)
- "Ritter Ramsey Dentist"(also has variant-blue/)

HARD RULES:
1. NEVER send email to a real person. Build the machinery; the operator fires it.
   Any sending function must default to DRY RUN and require an explicit --send flag.
2. NEVER commit or push to a repo you did not create. Deploy only to NEW repos.
3. Every script: `--dry-run` default, `--go` to act. Print what it WOULD do first.
4. Write UTF-8 always. Never print emoji to console.
5. Rate-limit every network loop. Timeouts on every request. Never hang.
6. Idempotent: re-running must not duplicate work. Cache results to disk.
7. No new heavy dependencies without checking they install on Windows first.
   Prefer stdlib + requests + beautifulsoup4. Avoid Playwright unless necessary.
8. If a lead has no website, that is DATA not an error. Handle it.
```

---

## §1 LEADER PROMPT

```
[PASTE §0]

=== ROLE ===
You are the BUILD LEAD for the Outreach Machine. You plan, assign, integrate and
verify. You do not write feature code yourself unless integrating.

=== THE PIPELINE YOU ARE BUILDING ===

  leads.csv
     |
     v
  [1] SCANNER  ---------> scan_results.json   (faults + score per lead)
     |
     v
  [2] RANKER   ---------> queue.csv           (best targets first)
     |
     v
  [3] DEMO GENERATOR ---> live URL per lead   (scrape brand -> reskin -> deploy)
     |
     v
  [4] CAMPAIGN ---------> personalised email with THAT lead's demo link
     |
     v
  [5] TRACKER  ---------> replies, opens, status in CRM

=== BUILD ORDER (non-negotiable — operator must be able to sell by Day 3) ===
Day 1: [1] Scanner + [2] Ranker.  Deliver a ranked queue of real targets.
Day 2-3: [3] Demo generator. This kills the 20-min-per-demo bottleneck.
Day 3: [4] Wire per-lead demo link into campaign_manager. Fix DEMO_LINK bug.
Day 4+: [5] Tracking improvements. Only what is needed.

=== YOUR OUTPUT ===
1. A task breakdown, one task per agent, with exact file paths and interfaces
2. The data contract between each stage (exact JSON/CSV schema)
3. Acceptance test for each stage ("run X, expect Y")
4. Integration plan + how you will verify end-to-end on 20 sample leads

=== RULES ===
- Define the DATA CONTRACT between stages FIRST. Agents build to the contract.
- Every stage must run standalone from CLI and be independently testable.
- Prefer 3 small scripts that work over 1 framework that half-works.
- Test on 20 leads before anything touches 29,931.
```

---

## §2 AGENT A — SCANNER

```
[PASTE §0]

=== ROLE ===
Build `scanner.py`. It reads the lead CSV, checks each website, and writes a
fault report per lead.

=== WHAT IT MUST DETECT (per website) ===
TECHNICAL (hard failures — highest value, most urgent to the prospect):
- DNS: does the domain resolve? does the www variant resolve? (both matter)
- HTTP status (follow redirects, note 3xx chains and final status)
- SSL: valid? expired? expiring within 30 days?
- Page load: total bytes, server-rendered body length (a near-empty body = SPA
  with no SSR = real SEO problem worth flagging)
- Dead images: count <img> whose src returns 404
- Dead internal links (sample up to 15)

CONTENT / CONVERSION:
- Online booking present? (look for: book, appointment, schedule, calendly,
  nexhealth, zocdoc, localmed, setmore, acuity, dentrix, opendental)
- Phone number present in HTML? more than one DIFFERENT number? (conflict = fault)
- Email present?
- Social links present? which platforms?
- Testimonials/reviews present?
- Before/after gallery present?
- Copyright year in footer (stale = >1 year old)

PLATFORM FINGERPRINT (this drives the pitch — very important):
Detect from HTML/asset URLs: ProSites, PBHS, Officite, Dentalfone, Optimized360,
Wix, Squarespace, WordPress (+ theme if visible), Webflow, GoDaddy, Shopify,
linktr.ee, bit.ly, Vite/React/Next (SPA), Google Sites

=== OUTPUT CONTRACT — scan_results.json (one object per lead) ===
{
 "username": "...", "name": "...", "email": "...", "country": "...",
 "website": "...", "final_url": "...", "scanned_at": "ISO8601",
 "reachable": true,
 "faults": [
   {"code":"WWW_DNS_FAIL","severity":"critical","evidence":"www.x.com NXDOMAIN"},
   {"code":"NO_BOOKING","severity":"high","evidence":"no booking keyword found"},
   {"code":"SSL_EXPIRED","severity":"critical","evidence":"expired 2026-07-02"},
   {"code":"DEAD_IMAGES","severity":"medium","evidence":"4 of 12 images 404"},
   {"code":"STALE_COPYRIGHT","severity":"low","evidence":"(c) 2020"},
   {"code":"PHONE_CONFLICT","severity":"high","evidence":"2 numbers: x, y"},
   {"code":"NO_SSR_CONTENT","severity":"medium","evidence":"body 180 chars"}
 ],
 "platform": "ProSites",
 "score": 78,
 "pitch_hook": "one sentence quoting the single most embarrassing fault"
}

=== SCORING ===
score = severity-weighted fault total, capped 100.
critical=30, high=15, medium=8, low=3.
A site with NOTHING wrong scores 0 and should NOT be contacted.

=== REQUIREMENTS ===
- Concurrent (ThreadPoolExecutor, 20-30 workers), 10s timeout per request
- Resume-safe: cache to scan_cache.json, skip already-scanned on re-run
- Progress to stderr every 100 leads
- CLI: --limit N, --country "United Kingdom", --input, --output, --workers
- MUST handle: empty Website, linktr.ee, bit.ly, malformed URLs, timeouts
- Test on --limit 20 first and SHOW the output before running full

=== ACCEPTANCE ===
`python scanner.py --limit 20 --country "United Kingdom"` produces valid JSON
with at least one real fault found and no crash.
```

---

## §3 AGENT B — DEMO GENERATOR

```
[PASTE §0]

=== ROLE ===
Build `demo_generator.py`. Input: one lead. Output: a live, personalised demo
site URL. This is THE bottleneck-killer — currently 20 minutes manual per demo.

=== PIPELINE ===
1. SCRAPE their brand:
   - logo (look for: <img> with 'logo' in src/alt/class, og:image, favicon,
     apple-touch-icon; prefer SVG > PNG > JPG; largest available)
   - brand colours (parse CSS for most-used non-neutral colours; also check
     theme-color meta; return primary + accent as hex)
   - business name, tagline, phone, email, address, services list
   - hero image if one exists and is >800px wide
   - Instagram photos from the lead's IG username if site assets are poor
2. PICK a template from the 4 dental templates (match by tone/colour if possible)
3. RESKIN: replace logo, colour variables, business name, phone, services, images
4. QUALITY GATE (see below) — REJECT bad output rather than ship it
5. DEPLOY to a NEW GitHub repo via `gh`, enable Pages, return the live URL
6. Record: lead username -> demo URL in demos.json

=== THE QUALITY GATE — THIS IS THE MOST IMPORTANT PART ===
A bad demo is WORSE than no demo. It proves you cannot do better than what they
have. Auto-generation is ~60% good by default; your job is to catch the other 40%.

REJECT and flag for manual review if ANY of:
- logo failed to download, is <100px, or is a generic placeholder/favicon only
- extracted colours have contrast ratio < 4.5:1 against the template background
- business name is missing, or is a URL, or >60 chars
- fewer than 2 usable images found
- any template token left unreplaced (grep the output for {{ }} or TOKEN)
- the extracted colour is pure white/black only (means extraction failed)

Rejected leads go to demos_needs_review.json — NOT to the deploy step.
Print a REJECT REASON for each. Aim to auto-ship only what genuinely looks good.

=== REQUIREMENTS ===
- Deploy to NEW repos only, named: demo-{slug}. NEVER touch existing repos.
- Follow the `gh` pattern already in deploy_all.py (read it first)
- Idempotent: if demo-{slug} exists, skip or update, never duplicate
- CLI: --lead-username X (single), --from-queue queue.csv --limit N (batch)
- --dry-run default: show what it WOULD scrape/build/deploy without deploying
- Cache scraped assets to assets_cache/{slug}/ so re-runs are fast
- Rate-limit deploys (gh API limits). 1 deploy per 3s minimum.

=== ACCEPTANCE ===
`python demo_generator.py --lead-username <real one> --go` produces a live
GitHub Pages URL that loads, shows THEIR logo, THEIR colours, THEIR name,
and has zero unreplaced tokens. Screenshot or fetch it to prove it.
```

---

## §4 AGENT C — PIPELINE INTEGRATION

```
[PASTE §0]

=== ROLE ===
Wire the stages together and fix the campaign bug. Build `pipeline.py`.

=== TASK 1 — FIX THE DEMO_LINK BUG (do this first, it is live) ===
campaign_manager.py line ~84 has:
    DEMO_LINK = "https://your-portfolio.vercel.app"
This is a placeholder. Every email sent links to nothing.
Change it so the demo link is PER LEAD, read from demos.json
({username: url}). If a lead has no demo URL, that lead must be SKIPPED, not
sent with a broken link. Make the skip loud (log it).

=== TASK 2 — BUILD ranker.py ===
Read scan_results.json, output queue.csv sorted best-first.
Rank by: score DESC, then prefer (a) has email, (b) country in
[United Kingdom, Australia, United States], (c) Followers > 500 (they care about
their image), (d) critical faults present.
Add a `pitch_hook` column: the one-sentence observation to open the email with.
CLI: --min-score N --country X --limit N --output queue.csv

=== TASK 3 — BUILD pipeline.py (the orchestrator) ===
    python pipeline.py --country "United Kingdom" --limit 50
Runs: scanner -> ranker -> demo_generator -> stages emails as DRAFTS in CRM.
It must NOT send. It stages. Print a summary table at the end:
    scanned N | faults found N | demos built N | rejected N | staged N
Then print the exact command the operator would run to actually send.

=== TASK 4 — SAFETY RAILS in campaign_manager.py ===
- Add a hard --send flag. Without it, DRY RUN prints emails to console only.
- Add a global MAX_SENDS_PER_RUN cap (default 50).
- Refuse to run if the sending domain is a consumer Gmail AND count > 20;
  print a warning about deliverability and require --i-know-the-risk.
- Add every recipient to a sent_log.csv with timestamp so nobody is ever
  emailed twice by accident.
- Read SUPPRESSION_LIST.txt and bounced_addresses.txt and skip those. If those
  files do not exist, create them empty.
- EXCLUDE any lead whose Country is Canada or an EU country by default
  (CASL / GDPR risk) unless --include-restricted is passed.

=== ACCEPTANCE ===
`python pipeline.py --country "United Kingdom" --limit 20` runs end to end,
deploys real demos, stages 20 emails, sends ZERO, and prints the summary.
```

---

## §5 RUN ORDER

1. Leader defines the data contract
2. Agent A + Agent B build **in parallel** (no file collisions — different files)
3. Agent C integrates once A and B produce output
4. Test end-to-end on 20 UK leads
5. **Operator reviews the 20 demos by eye** before anything is sent
6. Operator fires the send

## §6 WHAT THIS SYSTEM MUST NEVER DO

- Send email without an explicit `--send` flag from the operator
- Push to any repo it did not create
- Email anyone on the suppression or bounce list
- Ship a demo that failed the quality gate
- Email Canada or the EU without an explicit override flag
