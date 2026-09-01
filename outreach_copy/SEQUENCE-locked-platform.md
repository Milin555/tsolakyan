# LOCKED-PLATFORM — FINAL 3-TOUCH SEQUENCE (production)

Plain text, `text/plain; charset=UTF-8`. No manual line wrapping inside paragraphs — one paragraph = one source line (shown wrapped here for reading only). ASCII only in the body: no em dashes, no en dashes, no curly quotes, no `©` outside a quoted evidence string that has been ASCII-folded. One content link plus the unsubscribe, never more.

---

## SEND-DAY SCHEDULE

| Touch | Day | Sent to | Kill conditions |
|---|---|---|---|
| 1 | Day 0 | All validated leads | — |
| 2 | Day 3 | Non-repliers, non-bouncers, non-unsubscribers. Platform fingerprint re-verified at queue time (fail = suppress) | Hard bounce on T1, reply, unsubscribe, fingerprint no longer present |
| 3 | Day 8 | Only leads with recorded engagement (demo page hit from a non-scanner user-agent, or any open on a non-Gmail-hosted recipient). Zero-signal Gmail-hosted recipients exit the sequence after Touch 2. | As above, plus zero engagement |

Touch 3 is threaded onto Touch 2 (same `References`/`In-Reply-To`). Touch 2 is a fresh thread and never references Touch 1. Demo auto-expiry is 90 days so the Touch 3 link is always live.

Volume: 4–6 week warmup from 20/day on a dedicated sending domain. US first. UK and AU held until the gates in the merge table clear.

---

## TOUCH 1 — Day 0

Two variants. **Variant A fires whenever the scan found a live fault** — this is the default and the higher-converting path. Variant B only when the scan is clean.

### Subject lines (pick by availability, in order)
1. `The {{platform}} line in your footer` — 31–38 chars
2. `{{practice}} - {{fault_short}}` — e.g. `Waimea Dental - booking link is 404`, only if ≤ 45 chars
3. `Rebuilt {{practice}}'s homepage` — fallback, only if `{{practice}}` ≤ 22 chars, else use 1

No two recipients share a subject: every option carries `{{platform}}`, `{{practice}}` or `{{fault_short}}`.

### Variant A — a live fault was found (78 words)

```
{{greeting}},

{{fault_line}}

Separately, your footer still credits the design to {{platform}}, which usually means the files aren't yours. So I rebuilt your homepage as a site you'd hold the code for. Your name, your colours, live now:

{{demo_url}}

Unofficial concept, blocked from search, my own placeholder photos, banner on every page saying it isn't yours. If the direction's right I'll finish it and move it to {{domain}}. If not, delete this.

Milin Dholiya
Web developer, Surat, India
```

### Variant B — clean scan, ownership angle only (64 words)

```
{{greeting}},

{{pitch_hook}}

So I rebuilt your homepage as a site you'd hold the code for. Your name, your colours, live now:

{{demo_url}}

Unofficial concept, blocked from search, my own placeholder photos, banner on every page saying it isn't yours. If the direction's right I'll finish it and move it to {{domain}}. If not, delete this.

Milin Dholiya
Web developer, Surat, India
```

**Single CTA:** click the demo. No price, no meeting ask, no question.

---

## TOUCH 2 — Day 3

New angle: ownership and the exit. Never references Touch 1.

### Subject lines
1. `Two questions for your web vendor` (33)
2. `Who holds the files for {{domain}}` (varies)
3. `{{practice}} - one thing worth asking` (only if `{{practice}}` ≤ 20 chars)

Vendor trademarks never appear in the subject, the From name, the display name, or the sending domain.

### Variant A — ProSites-fingerprinted leads only (66 words)

Gated on `{{terms_clause_verified}} == true`. The clause is re-fetched from `{{terms_source_url}}` and diffed monthly; if the string no longer appears at source, Variant A auto-pauses and those leads route to Variant B.

```
{{greeting}},

From ProSites' published terms, retrieved {{terms_retrieved_date}} ({{terms_source_url}}):

"the website ... is the property of ProSites and the Customer has no rights to the website beyond the terms of its subscription"

Your own contract may read differently. Worth checking.

Rebuilding it as yours is {{price_band}}, one time. You'd host it after that, roughly $60 a year on your own account, not mine.

Reply and I'll lay out the steps.

Milin
```

### Variant B — PBHS / Officite / Dentalfone / Optimized360, and any paused ProSites leads (57 words)

```
{{greeting}},

Two questions worth putting to {{platform}} whenever you next renew:

If we leave, do we keep the design and the site files?
Is there a way out mid-term?

However that lands, rebuilding it as something you hold the code for is {{price_band}}, one time. You'd host it after that, roughly $60 a year on your own account, not mine.

Reply and I'll lay out the steps.

Milin
```

**Single CTA:** reply. No demo link here — the ask has to be unambiguous. "Reply and I'll lay out the steps" is one of four rotations (see rotation table below); no sentence in this touch is byte-identical across the campaign.

---

## TOUCH 3 — Day 8 (engagement-gated, 74 words)

### Subject lines
1. `The {{practice}} demo, still up`
2. `{{domain}} - leaving this here`
3. `One more thing about {{domain}}`

No breakup language. No "last chance", no "closing this out", no deadline.

```
{{greeting}},

Not going to keep emailing. Two things before I stop.

{{secondary_finding}}

And the rebuild stays up either way, no expiry, nothing to sign:

{{demo_url}}

If {{platform}} ever stops being worth the invoice, moving off it is {{price_band}} and I'm one reply away. Otherwise good luck with the practice, genuinely.

Milin Dholiya
Web developer, Surat, India
```

**Single CTA:** reply. `{{secondary_finding}}` is a second real, scan-derived observation the earlier touches did not use — it is what keeps this from being a bump, and it is per-lead entropy for the filters.

---

## COMPLIANCE FOOTER — appended to all three touches

Not counted in word limits. Hardcoded at build time, not per-row merged, except `{{source_url}}`.

```
--
This is an advertisement for web development services. We have not worked together before.

Milin Dholiya, independent web developer, Surat, Gujarat, India
[real street address, identical on all three touches]

I found this address published at {{source_url}}. Legal basis: legitimate interest in B2B outreach. I hold your practice name, public email address and a technical scan of your public homepage. Deleted on request or after 12 months: milindholiya.com/privacy

Don't want these? {{unsubscribe_url}} - one click, no reply needed.
```

Headers on every send: `List-Unsubscribe: <https://...>, <mailto:...>`, `List-Unsubscribe-Post: List-Unsubscribe=One-Click`. The body unsubscribe URL lands on a POST-confirm page ("Yes, stop these") so link-scanning security gateways cannot silently unsubscribe the lead. SPF + DKIM + DMARC aligned on the sending domain; unsubscribe host aligned with the From domain. Suppression is permanent, global across all segments, honoured same day.

---

## THE `pitch_hook` TEMPLATE THE SCANNER GENERATES

Three templates, one per evidence type. Never interpolate raw markup. `{{platform_evidence}}` is stripped of newlines and stray quote characters, ASCII-folded, capped at 60 chars, and downcased if its caps ratio exceeds 0.6 — except the leading word, which is sentence-cased.

**Type 1 — footer or copyright string:**
```
Your footer reads "{{platform_evidence}}".
```
Renders: `Your footer reads "Design and content (c) 2013-2026 by Dentalfone".`

**Type 2 — asset path in the page source:**
```
Your homepage still loads its stylesheets from {{platform_evidence}}, which is {{platform}}'s.
```
Renders: `Your homepage still loads its stylesheets from /prosites/assets/, which is ProSites'.`

**Type 3 — generator meta tag:**
```
Your homepage source names {{platform}} as the site generator.
```
Renders: `Your homepage source names Officite as the site generator.`

No consequence, no threat, no claim about their contract, no explanation of what the platform is. The quote does the work; the dentist draws his own conclusion.

**`fault_line` templates** (Variant A, highest priority when present, in this order): booking/appointment link returning 4xx or 5xx; SSL cert expired or expiring in under 30 days; phone number mismatch across pages; no mobile viewport meta; contact form POST failing; homepage LCP over 4s on mobile. Each has its own prose template, e.g.:
```
Your "Book Appointment" button on {{domain}} returns a 404 on mobile.
```

---

## REQUIRED MERGE FIELDS + FALLBACKS

Every field has a fail-closed validator. "Suppress" means the row is killed and logged, never sent with an empty string.

| Field | Holds | Fallback if empty / invalid |
|---|---|---|
| `{{greeting}}` | `Dr. {{last_name}}` only when the scan found exactly ONE clinician and `last_name` matches `^[A-Z][a-zA-Z'-]{1,20}$` after stripping honorifics and credentials (Dr., DDS, DMD, PC) | `Hello,` — never `{{practice}} team`. Multi-dentist practices and all role addresses (info@, office@, frontdesk@) get `Hello,` |
| `{{practice}}` | Normalised name: cut at `\|`, `-`, `:`; strip LLC/Inc/PC/PLLC/DDS; strip leading "Home"/"Welcome to"; title-case if all-caps; reject if >32 chars, contains a digit, or matches a comma-city pattern | Subject options 2 and 3 disabled, subject 1 used. Body never contains `{{practice}}`, so no body fallback needed |
| `{{domain}}` | Bare domain, no scheme | Suppress lead |
| `{{platform}}` | One of the five. Requires TWO independent fingerprints (footer string AND asset path, or either AND DNS/hosting). Re-verified at Touch 2 queue time | Suppress lead. Single-signal matches are suppressed, not guessed |
| `{{platform_evidence}}` | Literal scan string, ASCII-folded, newline-stripped, 60-char cap | Suppress lead — no evidence, no send |
| `{{pitch_hook}}` | Rendered from evidence type | Suppress lead |
| `{{fault_line}}` | One real live fault, prose template | Empty → route to Touch 1 Variant B. Never prints blank |
| `{{fault_short}}` | ≤ 22-char subject form of the fault | Empty → subject option 2 disabled |
| `{{secondary_finding}}` | A second real observation, unused in T1/T2 | Empty → the line and its blank line are removed entirely; Touch 3 renders at 62 words and still reads clean |
| `{{demo_url}}` | `{{practice_slug}}.demo.milindholiya.com` — path/param-free, human-legible, no shortener, no redirect hop, no token | Suppress lead |
| `{{price_band}}` | Single number only when the crawl completed AND page count is under the validated threshold; otherwise the range | `$1,200-2,500` |
| `{{source_url}}` | Exact page the address was published on | Suppress lead (CAN-SPAM harvesting exposure, GDPR Art.14, AU inferred consent all need it) |
| `{{unsubscribe_url}}` | Per-recipient POST-confirm URL, aligned domain, live 30+ days | Suppress send at build time — never renders empty |
| `{{terms_retrieved_date}}` / `{{terms_source_url}}` / `{{terms_clause_verified}}` | ProSites quote provenance | Any missing or false → lead routes to Touch 2 Variant B |
| `{{no_spam_notice_found}}` | Boolean from scanning `source_url` | True → suppress lead (AU-critical) |
| `{{uk_entity_type}}` | Companies House match | No match / unresolvable → suppress UK lead |
| `{{scan_age_days}}` | Freshness | >7 → requeue for rescan, do not send |

**Rotation:** every fixed sentence in every touch has four stored phrasings, assigned per-lead by hash and held stable across all three touches. That covers "So I rebuilt your homepage...", the disclaimer clause, "Reply and I'll lay out the steps", and the Touch 3 sign-off.

---

## WHY THIS WORKS

The email leads with a thing the dentist can verify on his own site in four seconds and never explains his own business back to him, so nothing in it reads as an agency talking. The demo link carries his practice name in the subdomain, which kills the phishing reflex that otherwise ends the sequence at that line, and the fault-first variant converts an ownership argument he can defer into a problem he has today. Price appears once, on day 3, after the demo has already done the selling.

---

## DELIBERATELY NOT FIXED

**1. The demo sits on a subdomain of my own personal brand domain, not an unrelated host.** Deliverability is right that one URI blocklisting on `milindholiya.com` takes out Touch 1 and Touch 3 across the entire list, and that a rebuilt-site host attracts abuse complaints. The dentist is also right that `demo-a7f92.vercel.app` gets zero clicks, ever. A recognisable human domain with his practice name on the front of it is the single largest conversion lever in the sequence, and a link nobody clicks has a deliverability score of zero regardless of its reputation. Mitigation instead of separation: sending domain is a different registration from the demo domain, DBL/SURBL monitored daily, takedowns honoured in hours, per-page noindex enforced at header, meta, and robots.txt level.

**2. The evidence quote still opens the email.** Deliverability wants it moved inline and mid-sentence because a caps-heavy quoted string on line one hits caps-ratio heuristics. The dentist explicitly named that line as the reason he keeps reading. Compromise taken: the string is ASCII-folded, newline-stripped, 60-char capped, and downcased when caps ratio exceeds 0.6, but it stays in the first content line. If seed testing shows placement damage, the fix is to shorten the quote further, not to bury it.

**3. Touch 2 Variant A still quotes ProSites' terms rather than being dropped.** Both critiques flagged it: 78% byte-identical content across thousands of sends, and an adversarial quote about a named company aimed at its own paying customers, which will reach ProSites within 48 hours. It survives because it is the only sentence in the campaign that does the whole argument by itself. It is now shortened to the ~25-word operative fragment, dated and source-linked, surrounded by four rotating phrasings, re-verified monthly against the live terms page, and fail-closed to Variant B. That reduces the fingerprint and the trade-libel exposure; it does not eliminate either, and if a vendor complaint lands at the registrar or ESP, Variant A goes off permanently rather than being defended.