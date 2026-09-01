# DELIVERABILITY & SPAM AUDIT — locked-platform 3-touch sequence

Assumption applied throughout: **cold domain, zero reputation, ~9k+ recipients across US/UK/AU, list assembled by scraping.** That is the worst starting position that exists. Nothing below is theoretical.

---

## TIER 0 — WILL BURN THE DOMAIN. FIX BEFORE A SINGLE SEND.

### 0.1 No `List-Unsubscribe` header. This is a hard fail, not a nice-to-have.

The spec's only opt-out is body copy:

> `Don't want these? {{unsubscribe_url}} — one click, no reply needed.`

Excellent copy. Irrelevant to the filter. Gmail and Yahoo's bulk-sender rules require, for anyone sending over 5,000/day to their users — and you have 9,073 in one sub-segment alone:

- `List-Unsubscribe: <https://…>, <mailto:…>`
- `List-Unsubscribe-Post: List-Unsubscribe=One-Click` (RFC 8058)
- Unsubscribe processed within **2 days**
- Spam complaint rate held **under 0.10%** (0.30% = enforcement)
- SPF **and** DKIM, plus DMARC with at least `p=none` on the From domain, with alignment

The document mentions none of these. Not SPF, not DKIM, not DMARC, not rDNS, not a warmup ramp, not bounce thresholds, not Google Postmaster Tools. A sequence document that specifies merge-field fallbacks in this much detail and omits authentication entirely is a sequence that gets its domain nuked in week two.

**Fix:** headers above on all three touches; dedicated sending subdomain or a separate outreach domain (never the domain the demos are hosted on, never the main brand domain); 4–6 week warmup starting at 20/day; hard-stop volume rules per recipient ESP.

### 0.2 The unsubscribe link will be auto-clicked by security scanners, and it will silently destroy your list.

`one click, no reply needed` + a bare GET URL means Proofpoint, Mimecast, Barracuda, Defender ATP and Cisco link-rewriting will **fetch every URL in the email on delivery**. Dental practices with any managed IT have one of these. Result: leads unsubscribe themselves without ever seeing the email, and your `{{demo_url}}` click data becomes noise you'll misread as interest.

**Fix:** the emailed link goes to a confirmation page with a POST button ("Yes, stop these"). RFC 8058 one-click stays in the *header* — that path is only invoked by real mail clients, not scanners. Never expose the destructive GET in the body.

### 0.3 Unique-per-recipient `{{demo_url}}` reads as a tracking token, and one blocklisting kills all 9,000 sends.

Two separate failures on the same line:

**(a) URL shape.** Every recipient gets a different URL. If those are `demo.milin.dev/d/7f3a9c21` or carry `?ref=`/`?id=` params, that is structurally identical to a tracking/redirect link — the exact pattern SpamAssassin, URIBL and the Gmail classifier weight against. On a cold domain with no history it is close to disqualifying.

**Fix:** human-legible, param-free, path-only: `https://demo.<yourdomain>.com/waimea-dental`. No query string. No redirect hop. No shortener — bit.ly, tinyurl, rebrand.ly and friends are blocklisted wholesale and their presence alone can route you to spam.

**(b) Single point of failure.** All demos on one host = one URI blocklist entry (SURBL/URIBL/Spamhaus DBL) takes out Touch 1 and Touch 3 for the entire list simultaneously, on every ESP that consults those lists. And the demo host is the thing most likely to get reported: you are hosting a rebuilt copy of someone's site with **their real logo and brand colours**, unrequested. That is a DMCA/abuse complaint waiting to happen, and abuse complaints against a host feed straight into domain reputation.

**Fix:** demo host on a domain with **no relationship to the sending domain**; monitor it against DBL/SURBL daily; `noindex` plus `X-Robots-Tag` (spec says not indexed — enforce it at header level, not meta only); a visible "not affiliated, remove this on request" line with a working takedown address on every demo page; honour takedowns in hours.

### 0.4 Touch 2 Variant A is a 45-word identical block sent to thousands of people. It is a bulk-content fingerprint and a legal complaint magnet.

> `"The Customer's website (including all graphical content and related HTML coding provided by ProSites) is the property of ProSites and the Customer has no rights to the website beyond the terms of its subscription."`

The email is 58 words. **78% of it is byte-identical across every ProSites recipient.** Cloudmark, Razor/Pyzor and DCC fingerprint on exactly this: high-volume repetition of a distinctive text block from a new sender. The merge fields do not save you — checksum-based systems are designed to ignore small variable regions.

Second problem: you are quoting a named company's contract terms, adversarially, at thousands of that company's paying customers. ProSites will receive forwards of this within 48 hours. Vendor abuse complaints to your registrar, host and ESP are fast and effective, and if those terms have been revised since your scrape you are publishing a false statement of fact about a named business. Rule 1 of the brief ("never fabricate an observation") is not satisfied by a quote you captured once and never re-verified.

**Fix:** re-verify the clause against the live terms page on the send date, automated, fail-closed. Attribute and date it inline ("ProSites' terms of service, retrieved 12 Aug 2026"). Cut the quote to the shortest fragment that carries the meaning (~15 words) and vary the surrounding 40 words across at least four rotations. Or — the safer call on a cold domain — drop Variant A entirely and run everyone through Variant B, which asks questions instead of asserting facts about a third party.

### 0.5 The list itself is the biggest reputation risk and the document never addresses it.

Instagram-bio-scraped dental contacts means: high invalid rate, heavy role-account concentration (`info@`, `office@`, `frontdesk@`, `smile@`, `hello@`), and recycled spam traps from stale directory data. Bounce over ~2% on a cold domain and you are throttled before the copy ever gets judged.

Also note the direct collision: `Dr. {{last_name}}` addressed to `info@practice.com` is read by a front-desk coordinator, who is the person most likely to mark it spam and least likely to be flattered.

**Fix:** real-time verification pass (not just syntax) with catch-all domains suppressed or heavily throttled; drop any address unverified in 12+ months; segment role accounts to their own list with a non-personal greeting and lower volume; complaint feedback loops registered where available; seed accounts across Gmail/Outlook/Yahoo/GoDaddy-hosted (huge among US dental) monitored per batch.

---

## TIER 1 — CONTENT-LEVEL SPAM SIGNALS

### 1.1 Your emails open with a line of ALL CAPS and a copyright symbol.

Rendered Touch 1, first content line:

> `"DESIGN AND CONTENT © 2013-2026 BY DENTALFONE" — in the page footer of waimeadental.com.`

A shouted all-caps string, a `©`, and a year range, as the opening line, in an unsolicited email from an unknown domain. That hits caps-ratio heuristics, and on a phone it reads as a scam header before a single word is processed. The strategic reasoning for verbatim quoting is sound; leading with it in caps is not.

**Fix:** never let raw evidence open the email. Move it inline, mid-sentence, sentence-cased with the original preserved in a short quote:

> `Your homepage footer credits the design to Dentalfone — "design and content © 2013-2026 by Dentalfone".`

Cap `{{platform_evidence}}` at ~60 chars, strip newlines, strip stray quote characters, and if the caps ratio of the captured string exceeds ~0.6, downcase it in the render.

### 1.2 `{{platform_evidence}}` renders inconsistently and sometimes as raw code.

The table permits three shapes: a quoted footer string, `/prosites/assets/`, and `<meta name="generator" content="Officite">`. That third one puts a **raw HTML tag with angle brackets and nested double quotes** into the first line of a plain-text email. It will look broken, it may be mangled by the templating layer, and an unsolicited email containing raw markup is a genuine content signal.

The path variant renders as `/prosites/assets/ — in the homepage source of x.com.` — a naked filesystem path with no quotes, breaking the pattern the example sets.

**Fix:** three separate hook templates, one per evidence type, each written as prose. Never interpolate raw markup. Escape and length-cap everything before render.

### 1.3 Subject lines: three of nine pattern-match known spam or phishing.

| Subject | Verdict |
|---|---|
| `Before your next renewal` | **Kill it.** "renewal" is core vocabulary for subscription-billing phishing ("your renewal is due", "renewal failed"). From an unrecognised domain to a business inbox, this is the single highest-risk subject in the set. |
| `Last one from me` / `Closing this out` / `I'll stop here` | **Rewrite.** The breakup email is the most recognisable cold-outreach shape in existence. Filters have seen it several billion times; so has every recipient. `Last one` also sits adjacent to "last chance". |
| `One line from ProSites' own terms` | **High risk.** Third-party brand in the subject, framed adversarially. Compounds 0.4. |
| `Who owns your website files` / `Who actually owns your website` | Weak, and **near-duplicates of each other** across Touch 1 and Touch 2 — which confirms to any filter (and any recipient) that this is a sequence, not correspondence. |
| `{{practice}} — a rebuilt homepage` | Best of the set, and the only one carrying real personalisation. See 2.1 for how it breaks. |

**Fix:** every subject must carry a recipient-unique token — practice name, or `{{domain}}`. Zero identical subjects across the send. Kill "renewal". Replace the Touch 3 breakup subject with something concrete: `The <practice> demo — still up`. Keep subjects under ~45 chars for mobile; you already do.

### 1.4 Phrases that read as template, not as a person typing.

- `Live now, nothing to install:` — "nothing to install" is software-promo vocabulary and adds nothing. Cut.
- `Concept only, not indexed, every page marked unaffiliated.` — comma-spliced fragment; no human writes this. It is a disclaimer, and stacked disclaimers correlate with spam. Rewrite as a sentence: `It's a concept, not indexed, and marked as unaffiliated on every page.`
- `If not, ignore this.` — appears in a very large share of cold templates. Gmail's unwanted-mail classifier is trained on this corpus.
- `Reply "how" and I'll lay out the steps.` — appears **byte-identical in both Variant A and Variant B**, i.e. in every Touch 2 you will ever send. It is a constant across the entire campaign and a clean fingerprint. Also: curly vs straight quotes will vary by pipeline and mojibake if charset is wrong.
- `Two questions worth putting to {{platform}} before your renewal date` — you don't know their renewal date. This is implied knowledge you don't have and manufactured timing pressure, breaking the brief's own rules 1 and 6. Cut `before your renewal date`.

### 1.5 The body is hard-wrapped. It will look broken on the phone every recipient reads it on.

> `So I rebuilt your homepage as something you'd own outright. Live now,`
> `nothing to install:`

Manual wrapping at ~70 chars, then re-wrapped by a narrow mobile viewport, produces ragged half-lines. It also looks machine-generated, because it is.

**Fix:** no manual line breaks inside paragraphs. One paragraph = one line in the source. Let the client wrap. Send `text/plain; charset=UTF-8` with `Content-Transfer-Encoding: quoted-printable`, or ASCII-fold: your em dashes, en dash in `$1,200–2,500`, curly quotes and `©` are all non-ASCII and all mojibake to `â€"` / `Â©` the moment one hop in the chain gets the charset wrong. That single failure mode makes the email unreadable and looks exactly like spam obfuscation.

### 1.6 Touch 3 has the worst link-to-text ratio in the sequence.

42 words, two URLs (demo + unsubscribe), a breakup subject, from a cold domain, as the third unengaged contact. Roughly one link per 21 words. Short + link-dense + terminal-sounding is a textbook shape.

**Fix:** either take Touch 3 to ~75 words with one more specific, scan-derived sentence about their site, or drop the demo URL and leave the unsubscribe as the only link. Do not ship it at 42 words with two links.

### 1.7 "One link per email" is not what the spec actually produces.

Touches 1 and 3 carry two links. That's fine and normal — but the document states a rule it violates, which means whoever implements it won't be counting. State it accurately: one *content* link plus the unsubscribe, and never more.

Also ensure the unsubscribe URL is on a domain **aligned with the From domain**. An ESP-branded unsubscribe host on a cold sending domain is a mismatch that costs you.

---

## TIER 2 — MERGE-FIELD FAILURES (highest-probability real-world break)

The table marks fields "required" but specifies **no fail-closed runtime assertion**. "Required" in a spec is a wish. Every one of these needs a pre-send validator that kills the row, logs it, and never substitutes an empty string.

### 2.1 `{{practice}}` — you are interpolating a scraped `<title>` tag into a subject line.

Real-world values from dental sites: `Home | Smile Dental Care - Best Dentist in Austin, TX`, `Smile Dental Care, LLC`, `Dr. Marcus Webb DDS & Associates`, `SMILE DENTAL CARE`.

- Subject 2 becomes an SEO title tag with a hyphen and a city in it. Instantly recognisable as scraped.
- `{{practice}} team,` becomes `Home | Smile Dental Care - Best Dentist in Austin, TX team,`
- Ampersands and apostrophes break naive templating and can HTML-escape into `&amp;` in a plain-text email.

**Fix:** normalise at scan time — strip everything after `|`, `-`, `–`, `:`; strip `LLC/Inc/PC/DDS/DMD/PLLC`; strip leading `Home`/`Welcome to`; title-case if all-caps; reject if >32 chars, contains a comma-city pattern, or contains a digit. Enforce the stated ≤24-char subject gate in code. If normalisation fails, suppress the lead — do not send with a mangled name.

### 2.2 `{{greeting_name}}` — the `Dr.` prefix will double, and the wrong-doctor problem is worse than the blank-field problem.

- Scraped `last_name` is frequently `Dr. Smith`, `Smith, DDS`, `Smith DDS` → renders `Dr. Dr. Smith DDS,`. Fatal on line one.
- If `last_name` is empty but the branch still builds `Dr. {{last_name}}` you get `Dr. ,` — worse than any fallback.
- Multi-dentist practices: naming the wrong partner, or the associate who left in 2023, is an instant spam-report and it is common in this vertical.
- The fallback `{{practice}} team,` is a known mass-send tell in its own right.

**Fix:** validate `last_name` against `^[A-Z][a-zA-Z'’-]{1,20}$` after stripping credentials and honorifics; reject anything else. Only use the named greeting when the scan found **one** clinician; multi-dentist practices go to the practice fallback. Consider replacing `{{practice}} team,` with a plain `Hello,` — less personalised reads better than falsely personalised, and this audience is calibrated for exactly that tell.

### 2.3 `{{platform}}` — "suppress if ambiguous" is correct and will be ignored under volume pressure.

Sites migrated *off* these vendors routinely retain stale footer credits and orphaned asset paths. You will pitch "move off ProSites" to a practice that left ProSites two years ago. That is the single most credibility-destroying outcome available, and Touch 2 Variant A doubles down on it with a contract quote for a contract they no longer hold.

**Fix:** require **two independent** fingerprints (e.g. footer string *and* asset path *or* DNS/hosting evidence) before classifying. Single-signal matches get suppressed, not guessed. Re-verify at Touch 2 send time, not just at scan time — a 3-day-old finding is cheap to re-check and the whole sequence rests on it.

### 2.4 `{{price_band}}` — the fallback is fine; the computed number is a trap.

`Prefer one number over the range wherever the scan gives a page count.` Page count from an automated crawl is unreliable (JS-rendered nav, blog archives, orphaned pages). `$1,400` on a 60-page site anchors you into a loss you then have to walk back, which is a worse outcome than the negotiation you were avoiding.

**Fix:** only emit a single number when the crawl is complete and the count is under a threshold you've validated against past jobs. Otherwise the range. Never a number derived from a partial crawl.

### 2.5 `{{postal_address}}` and `{{unsubscribe_url}}` as merge fields is a category error.

These are constants for the whole campaign. Making them per-row merge fields creates a path where one renders empty and you ship a footer reading `Don't want these?  — one click, no reply needed.` — non-compliant under CAN-SPAM *and* it looks broken. Hardcode them into the footer template. Assert non-empty at build time, once.

Your Surat address is legally fine for CAN-SPAM (a valid physical postal address is the requirement; it need not be US). It must be real and consistent.

---

## TIER 3 — JURISDICTION AND SEQUENCE MECHANICS

**UK (1,681).** The PECR note is right and incomplete. Sole traders and partnerships are individual subscribers, so the corporate-B2B soft-opt-in lane doesn't cover them — and a large fraction of UK dental practices are exactly that. Also: PECR requires the sender be identifiable and an opt-out be present in *every* message, which you satisfy. Recommend a stricter posture than the doc implies: for UK, single touch, no sequence, or drop the segment until you have a defensible consent basis.

**Australia (622).** The Spam Act 2003 is materially stricter than CAN-SPAM and the document doesn't mention it. It requires consent — and the only available lane is *inferred* consent from a conspicuously published business address where the message is **relevant to that person's role**. Whether an unsolicited web-development pitch is "relevant to the role" of a practising dentist is arguable at best. Unsubscribe must function for 30 days and be honoured within 5 business days. ACMA issues real penalties. Treat AU as the highest-legal-risk, lowest-priority segment.

**Sequence mechanics not specified anywhere:**
- No engagement gating. Three touches to an address with zero opens is pure negative signal to Gmail. Gate Touch 3 on any engagement, or on non-Gmail-hosted recipients.
- No hard-bounce kill switch between touches. A Touch 1 bounce must remove the row from Touch 2 and 3 automatically.
- Three separate threads (Touch 2 explicitly never references Touch 1). Consider threading Touch 3 onto Touch 2 — reply-chain continuity is a mild positive signal and reads more like correspondence.
- Touch 2 and 3 both CTA "reply". The From address must be a monitored, mail-receiving mailbox on the aligned domain. If it's a send-only relay address, the CTA is a lie and the replies vanish.
- No per-ESP throttling, no seed-list placement testing, no Postmaster Tools monitoring. Without inbox-placement visibility you will not know the domain is burned until conversions hit zero.

---

## THE STRUCTURAL PROBLEM, STATED PLAINLY

Across thousands of sends you have, functionally, **five emails per touch** — one per platform — with a name and a domain swapped in. Every constant sentence (`So I rebuilt your homepage as something you'd own outright.`, `Reply "how" and I'll lay out the steps.`, `Concept only, not indexed, every page marked unaffiliated.`, the entire footer, the entire ProSites quote) is a shared fingerprint. Checksum-based filtering exists specifically to catch this shape, and merge fields do not defeat it.

**Fix:** minimum four rotating phrasings for every fixed sentence in every touch, assigned per-lead and held stable across the sequence. Better: let the scanner contribute one genuinely lead-specific sentence to each body — page count, load time, an expiring cert, a broken form, a mobile-viewport failure. That serves deliverability (real per-message entropy) and the brief's own strategy (real observations) with one change. It is the highest-leverage fix in this document after the authentication headers.

---

## SHIP ORDER

1. SPF/DKIM/DMARC + `List-Unsubscribe` / `List-Unsubscribe-Post`; dedicated sending domain; 4–6 week warmup.
2. Fail-closed merge-field validator; `{{practice}}` and `last_name` normalisation; two-signal `{{platform}}` gate.
3. Kill the raw ALL-CAPS opening line; kill `Before your next renewal`; kill or date-and-shorten the ProSites quote.
4. Demo URLs param-free and human-legible on an unrelated domain; unsubscribe behind POST confirm.
5. Per-lead sentence variation from the scan; four rotations of every constant sentence.
6. List verification, role-account segmentation, bounce kill-switch; UK and AU segments held back pending consent review.
7. Remove manual line wrapping; ASCII-fold or set charset correctly.
8. Seed-list placement testing before volume; Postmaster Tools from day one.