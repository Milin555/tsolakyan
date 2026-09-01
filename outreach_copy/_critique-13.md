# DELIVERABILITY / SPAM AUDIT — `no-booking` 3-touch

Assumption applied throughout: **cold domain, zero reputation, scraped list, sender in IN → recipients in US/UK/AU.** Under those conditions the margin for error is roughly zero, so several things that would be survivable on a warmed domain are rated as fatal here.

---

## TIER 1 — WILL BURN THE DOMAIN

### 1. The demo itself is a brand-clone on a third-party URL. This is the single biggest risk in the sequence and it is not on your list.

Quote: `Your logo, your colours, your page copy` → served at `{{demo_url}}`.

Risk: You are publishing a page that reproduces a business's logo, brand colours and copy on a domain that business does not control, and emailing a link to it. That is a byte-for-byte description of the phishing-clone pattern. Google Safe Browsing and Microsoft SmartScreen both classify "page replicating another entity's branding on an unaffiliated domain" heuristically, and both accept user reports. One cynical dentist clicking "Report phishing" in Gmail, or one submission to Safe Browsing, and the demo host gets an interstitial red warning page. Because every demo lives on that host, **one report poisons every link in every email you have ever sent**. Secondary risk: trademark/copyright complaint → host-level takedown of the whole account.

Fix (all of these, not some):
- Persistent, non-dismissable banner at the top of every demo: `Unofficial demo built by Milin <surname>. Not affiliated with, endorsed by, or operated by {{practice}}.` Include a "remove this demo" link that actually works.
- `X-Robots-Tag: noindex, nofollow` + `robots.txt` disallow. An indexed clone is what gets found and reported.
- Random token in the URL path so it is unguessable and not crawlable.
- Auto-expire (which also makes Touch 3 honest — see #14).
- Do not reproduce their logo at full fidelity if you can avoid it; brand colours + practice name carries 90% of the "this is mine" jolt with a fraction of the legal surface.

### 2. Per-prospect URLs on a fresh host = textbook snowshoe

Risk: A brand-new domain that begins emitting thousands of messages, each containing a **unique, never-before-seen URL**, is the exact fingerprint of snowshoe spam and disposable phishing infrastructure. URL reputation systems have nothing to go on except "new host, high URL entropy, low click history."

Fix:
- One stable host for all demos. `demos.<sending-root>.com/d/<token>` — **a subdomain of the sending domain**, so link domain and From domain are organizationally aligned. Never `demo-8837.vercel.app`, never a per-prospect subdomain, never a per-prospect domain.
- Put a real, indexed homepage on the demo root explaining what the service is, with Milin's real name, real address, and a contact route. A link domain with no root content is a flag by itself.
- Age and warm that host for 3-4 weeks before it appears in cold mail.

### 3. "I ran a scan on your domain" is the opening line of a mass-market scam

Quote: `I ran a scan on {{practice_domain}}.`

Risk: "We scanned your website and found problems" is one of the highest-volume scam templates in existence (fake SEO audits, fake security alerts, fake GDPR notices). Recipients have been trained on it. Filters have been trained on it. Pairing it with an unfamiliar link in the same message pushes the content classifier toward phishing, not just promo. It also triggers the alarm response — *did this person touch my site?* — and alarm converts to "Report spam," which is the metric that actually kills you.

Fix: `I went through {{practice_domain}} this morning.` or `I clicked through {{practice_domain}}.` Human verb, no security connotation, same factual basis. Keep the evidence sentence exactly as-is — the evidence is fine, the word "scan" is not.

### 4. No `List-Unsubscribe` / `List-Unsubscribe-Post` headers

Quote: `Don't want these? {{unsubscribe_url}} — one click, no reply needed.`

Risk: The visible link is good copy and legally sufficient. It is **not** technically sufficient. Since the Gmail/Yahoo bulk sender rules, mail sent at this volume without RFC 8058 one-click headers is treated as non-compliant bulk. The body link does not substitute. You will also fail the "keep complaint rate under 0.3%" threshold much faster without the header, because the header unsubscribe is what people click *instead of* the spam button.

Fix: Set both headers on every send:
```
List-Unsubscribe: <https://.../u/{{token}}>, <mailto:unsub@...>
List-Unsubscribe-Post: List-Unsubscribe=One-Click
```
Honour within seconds, not the 10-day CAN-SPAM ceiling. Keep the visible link too.

### 5. Hard bounces and spam traps from scraped listing data

Not in your doc at all. Scraped dental directories are full of dead practices, sold practices, and recycled-trap domains. A cold domain that hard-bounces above ~2% is finished in one batch.

Fix: SMTP-verify every address immediately before send. Cap hard bounce at 2%, pause the whole send if exceeded. De-prioritise catch-all domains. Refuse any record older than 90 days without re-verification. Credit where due: your emission rule 3 (re-scan at send time) incidentally kills dead domains, which helps — make that the explicit bounce-prevention gate, not a side effect.

### 6. Role accounts — `info@`, `office@`, `frontdesk@`, `hello@`

Dental listings are overwhelmingly role addresses. They have the highest complaint rates of any address class, are disproportionately spam traps, and — directly relevant to your merge-field question — **`{{first_name}}` is always empty for them**, so every one of them gets the degraded fallback template.

Fix: Suppress role prefixes from this segment entirely. If you will not suppress them, they need their own template with no name token and no "Hi there."

---

## TIER 2 — HIGH: merge-field failures that render broken

### 7. `{{first_name}}` fallback breaks Touch 2 and Touch 3 grammatically

Quotes:
- Touch 2: `{{first_name}} — when someone hits a voicemail…` → renders **`there — when someone hits a voicemail`**
- Touch 3: `{{first_name}} — last one from me.` → renders **`there — last one from me.`**

Risk: Touch 1 survives the fallback because "Hi there —" is idiomatic. Touches 2 and 3 do not. Bare `there —` at the top of the message is unambiguous broken automation, and it lands in the **preview pane** on mobile, before the message is even opened. That is the highest-visibility position in the entire email.

Fix: Do not use a string fallback. Use a conditional block that removes the token and re-opens the sentence:
- T2 no-name: `When someone hits a voicemail, most of them just call the next practice.`
- T3 no-name: `Last one from me.`
Test both variants by rendering them, not by trusting the fallback string.

### 8. `{{practice}}` fallback poisons subject #2 and the footer

Quotes:
- Subject 2: `Nowhere to book on {{practice}}'s site` → `Nowhere to book on your practice's site`
- Footer: `You're getting this because {{practice}} is listed publicly at {{practice_domain}}` → `because your practice is listed publicly at…`

Risk: The subject variant exists *only* to be personalised. With the fallback it becomes a generic mass-mail subject that also announces a problem — worst of both. In the footer, the fallback degrades your CAN-SPAM/PECR identification statement into mush.

Fix: If `practice` is a fallback, subject #2 must be **suppressed, not degraded** — fall back to #1, same rule you already apply for length. Footer should read from `{{practice_domain}}` only: `You're getting this because {{practice_domain}} is publicly listed.` The domain is always present (it is a required field), so the footer can never break.

### 9. `{{practice}}` will render garbage even when it is populated

Real listing values you will hit: `SMILE DENTAL CARE, LLC`, `Dr. Ross & Associates`, `THE DENTAL STUDIO`, `Bright Smiles Dental — Main St`, `Wells Dental Group Ltd`.

Renders:
- `Nowhere to book on SMILE DENTAL CARE, LLC's site` — ALL CAPS in a subject is a live spam signal, and the possessive after a legal suffix is illiterate.
- `Nowhere to book on Dr. Ross & Associates's site` — double-s possessive.
- Non-ASCII in the name (accents, emoji in listing data) forces RFC 2047 encoded-word subject headers (`=?UTF-8?B?…`), a minor but real signal on a cold domain.

Fix: Normalise before merge — title-case if the string is >70% uppercase, strip trailing legal suffixes (`LLC`, `Ltd`, `PLLC`, `PC`, `Inc`, `DDS`, `DMD`), strip everything after an em dash or pipe, strip `Dr.` prefixes. Then **hard-suppress subject #2** if the result contains `&`, an apostrophe, ends in `s`, or contains any non-ASCII character. Only clean names get the personalised subject.

### 10. Your 22-character suppression rule for subject #2 is measured against the wrong number

`Nowhere to book on X's site` is 27 characters of chrome. At the 22-char cap the rendered subject is 49 characters. Mobile Gmail truncates around 35-40. `Nowhere to book on Riverside Family Denti…` — truncated mid-word, which reads as broken automation.

Fix: Cap on the **rendered length**, not the field length. Target ≤ 42 rendered characters, which means `{{practice}}` ≤ 15 chars. Most practice names will fail that, so accept that subject #2 fires on a minority of leads and subject #1 carries the volume.

### 11. `{{fault_evidence}}` blows its own 20-word cap, and Touch 1 blows its word limit with it

Your template with the longest legal `contact_method_found`:
> `12 pages, and no way to book on any of them — the only route in is the contact form on /contact-us.html`

That is 21-22 words before `{{form_path}}` gets long. Touch 1's 82-word budget assumed 20. And `{{form_path}}` renders raw scraped paths: `/contact-us.html?id=3`, `/en/contact/`, `/index.php?page=contact`. A raw query-string path in the second sentence of a cold email is a scraper artefact in plain sight — it is the tell that no human wrote this.

Fix: Drop `{{form_path}}` from the closed list entirely. Replace that option with `the contact form on your Contact page`. Then enforce the cap programmatically at emission and drop the lead if it exceeds — same discipline as your other required fields.

### 12. `{{page_count}}` pluralisation and floor

`1 pages, and no way to book on any of them` — the classic. Also: your emission rule requires ≥5 pages crawled, so `5 pages, and no way to book` is your floor, and it makes a 40-page practice site sound like a brochure, which the recipient will notice and hold against you.

Fix: Pluralisation guard. And if crawl depth was capped rather than exhausted, say `at least {{n}} pages` or drop the count and open with `No way to book anywhere on the site —`.

### 13. Footer merge fields are the CAN-SPAM physical address — they must not be merge fields

Quote: `Milin {{sender_last_name}}, {{sender_street_address}}, Surat, Gujarat {{postcode}}, India`

Empty renders: `Milin , , Surat, Gujarat , India`. That is simultaneously a credibility disaster and an **actual CAN-SPAM violation** (no valid physical postal address) and an AU Spam Act violation (no accurate sender identification).

Fix: These four values never vary. Hardcode them as literal text in the template. A constant that lives in a merge-field slot is a defect waiting for a config load to fail.

### 14. Touch 3's expiry claim is a compliance risk if the pipeline lies

Quote: `Your demo stays up until {{demo_expiry_date}}, then it gets deleted`

You already flagged this as conditional, which is good. Two things you did not: `{{demo_expiry_date}}` rendered as `2026-09-01` reads machine-generated, and rendered as `09/01/2026` means 1 September to your UK/AU recipients and 9 January to your US ones.

Fix: Format spelled-out and locale-aware — `1 September` for UK/AU, `September 1` for US. And treat a false expiry claim as a deceptive-content violation, not a copy choice: if the deletion job is not wired up and verified, the line does not ship.

---

## TIER 3 — SUBJECT LINES AND SPAM LEXICON

### 15. `Booking install: 48 hours, $449` — drop this one entirely

Quote it exactly. Currency symbol + numeral + colon-delimited offer format is promotional-tab bait at best and spam-scored at worst. `48 hours` is a delivery-urgency claim. On a cold domain this subject alone can decide the placement of the whole message.

Fix: Cut. Keep the price in the body where it does useful qualifying work. `What booking costs to install` [29] is the correct Touch 2 subject and it is genuinely good — no currency, no numerals, curiosity without a gimmick.

### 16. Touch 3's subjects are the most fingerprinted lines in cold email

Quotes: `Should I delete the demo?`, `Last one from me`, `Closing this out`

Risk: The breakup email is in every SDR playbook on earth. `Should I delete the demo?` is a direct structural descendant of "Permission to close your file?" and "Should I stay or should I go?" — both of which have been sent hundreds of millions of times. Content classifiers cluster on these. So do humans, and humans hitting the spam button is what actually costs you. `Last one from me` [16] and `Closing this out` [16] are additionally so short and so generic that they carry zero personalisation signal.

Fix: `Should I delete the demo?` is the only survivable one because "the demo" is specific to *this* sequence rather than to cold email in general — keep it, drop the other two. Better: make it concrete and non-templatey — `Deleting the {{practice}} demo on {{date}}` when practice is clean, `Deleting the demo` when it is not.

### 17. `I rebuilt your homepage with booking` — alarming, not intriguing

Risk: A stranger claiming to have rebuilt something you own reads, on a phone, between patients, as "someone has done something to my website." That is the same reflex as #3. Alarm → report.

Fix: `A version of your homepage that takes bookings`. Same information, no implication of access.

### 18. Lexicon check — what is actually present

Present and scoring against you: `$449` (×3 including a subject), `48 hours` (×2), `Last one from me`, `Closing this out`, `I ran a scan`, `Should I delete`.

Notably absent, and this is real credit: no `free`, no `guarantee`, no `risk-free`, no `act now`, no `limited time`, no `click here`, no `100%`, no exclamation marks, no ALL CAPS body text, no dollar signs in Touch 1. Nobody's first cold-email draft looks this clean lexically. The problems here are structural and infrastructural, not word-choice.

---

## TIER 4 — TEMPLATE-FINGERPRINT AND STRUCTURE

### 19. Every body in the sequence has the same skeleton, and you will send thousands

All three: `{{name}} — <sentence>` … blank line … **bare URL alone on its own line** … short closer. Six em dashes across three short emails, in identical syntactic positions.

Risk: Gmail clusters near-duplicate bodies across a sending domain via content shingles. Structural identity plus a bare-URL line plus one merge token of variance is a tight cluster. It also reads as AI-written to a human — the naked-URL-on-its-own-line and the em-dash-after-first-name are both now recognised tells.

Fix:
- Write 3 genuinely different hand-authored variants of each touch, rotate them per-lead. Not spun synonyms — different sentence structures.
- Vary the em dash: some variants use a comma, some a full stop, some no name token at all.
- Anchor at least one URL inside a sentence rather than orphaned on its own line.
- Inject `{{contact_method_found}}` or `{{practice_domain}}` into Touch 2's first line — right now Touch 2 is 100% identical across every recipient except the name, which is your worst-clustering message.

### 20. Touch 3 has a bad link-to-text ratio

41 words, and depending on rendering, three links: `{{demo_url}}`, `{{unsubscribe_url}}`, and `{{practice_domain}}` if autolinked. Roughly one link per 14 words in a message with almost no text mass.

Fix: Raise Touch 3 to ~65-70 words, and never autolink `{{practice_domain}}` in the footer — render it as plain text. It is an identification statement, not a destination.

### 21. Send plain text. No pixel, no images, no HTML scaffolding.

Nothing in this sequence needs HTML. If you send HTML anyway:
- **No open-tracking pixel.** A 1×1 remote image in a 41-word email is a poor image-to-text ratio and a known signal; Apple MPP has made the resulting data worthless anyway. You are paying a deliverability cost for a number you cannot trust.
- **No click-tracking wrapper on a shared ESP tracking domain.** Shared tracking domains carry other senders' reputation and are functionally shorteners. If you must track clicks, use a CNAME'd tracking subdomain on your own root — and accept that this puts an extra new hostname in every link.
- **Anchor text must equal the URL.** Anchor text that says one thing over an href that points somewhere else is a first-order phishing heuristic. Given #1, you cannot afford to look one millimetre more like phishing.
- Never attach a screenshot of the demo. Attachments on cold mail from a new domain are a hard flag.

### 22. No URL shorteners — keep it that way

Currently clean. Stating it explicitly because it is the most common regression when someone later complains the raw demo URL is ugly. bit.ly, tinyurl, rebrand.ly and any shared-domain shortener in cold mail on a cold domain is an instant placement penalty. The demo URL being long and ugly is fine.

---

## TIER 5 — REPUTATION MECHANICS

### 23. The sequence is engineered to produce zero replies for two of three touches

Quote: `No reply asked for.` (T1) / `Price is context for the click, not a separate ask.` (T2)

Risk: Replies are one of the strongest positive engagement signals a mailbox provider has. A domain with high send volume, high open-uncertainty, zero replies until day 7, and a growing unsubscribe stream has no positive signal to offset the negative ones. This is a defensible *conversion* choice and a bad *reputation* choice, and on a cold domain the reputation cost comes first.

Fix: Either (a) let Touch 1 accept a reply without asking for one — `if it's useless, tell me and I'll stop` costs nothing and converts a would-be spam-complaint into a reply, or (b) accept it and run a separate genuine reply-generating warmup stream on the same domain for 6 weeks before this sequence goes near it. Do not skip both.

### 24. Touch 3's opt-out-by-reply conflicts with your own footer and creates a manual compliance liability

Quotes: `reply "later" and I'll stop emailing you` versus footer `one click, no reply needed`.

Risk: You are running two opt-out channels, one of which is a human parsing inbound free text. Every `later`, `no thanks`, `remove me`, `stop`, `not interested` arriving as a reply is now a legal obligation with a clock on it. Miss one, send a fourth email, and that recipient reports you.

Fix: Auto-parse inbound replies against a suppression keyword list and suppress on match, immediately, before any human reads it. Better: point `later` at the same one-click link so there is one mechanism and one audit trail.

### 25. Infrastructure baseline — none of this is in the doc

- SPF, DKIM (2048-bit), DMARC. Start `p=none` with rua reporting, move to `p=quarantine` once aligned.
- Custom return-path aligned to the sending domain. Valid MX and A record on the sending domain. Reverse DNS on the sending IP.
- **Do not send from the primary business domain.** Register a secondary (`milinweb.co` to the primary's `.com`), age it 4+ weeks with a live site, send from there. When it burns — and on cold outreach at this volume something eventually will — the primary survives.
- 20-30 sends per inbox per day, hard ceiling. Warm 4-6 weeks. With 9,073 leads at 3 touches, that is ~27,000 sends — plan the mailbox count accordingly and do not compress it.
- Register for Microsoft SNDS and JMRP, and Google Postmaster Tools. Without feedback loops you will find out you are in spam from the reply rate, three weeks late.
- Seed-list inbox placement testing before each batch, not after.

### 26. UK/EU: the PECR carve-out does not cover GDPR

Your note is right about PECR corporate subscribers. It stops short. `{{first_name}}` at a named individual at a dental practice is personal data obtained without their knowledge, which triggers UKGDPR Article 14 — a privacy notice at first contact, within one month. `You're getting this because {{practice}} is listed publicly` is not that notice.

Fix: Add one line to the footer for UK/EU-routed sends: `How I got your details and how to have them removed: <link>` pointing to a real page with the Art. 14 disclosures. It costs eight words and it is the difference between a defensible programme and an ICO complaint.

### 27. Unsourced statistic in a commercial message

Quote: `About a third of calls during clinic hours go unanswered anyway`

Risk: Not a spam-filter issue — a truthfulness issue, and it violates your own Hard Rule 1 in spirit. Unsubstantiated statistical claims in marketing email are actionable under CAN-SPAM's misleading-content provision and under CAP/ASA in the UK. Also: a dentist who thinks that number is wrong for their practice discounts the entire message.

Fix: Cite it inline with a source name, or cut the sentence. The preceding sentence — `most of them just call the next practice` — carries the argument without the number.

---

## FIX CHECKLIST, ORDERED

1. Add the affiliation banner, noindex, tokenised URL and takedown path to every demo. Nothing ships before this.
2. Move demos onto a single aged subdomain of the sending domain.
3. Add `List-Unsubscribe` + `List-Unsubscribe-Post`.
4. Replace `I ran a scan` with a human verb.
5. Replace all string fallbacks with conditional blocks; render-test every empty-field permutation.
6. Hardcode the footer address and surname.
7. Suppress role addresses. SMTP-verify everything. Bounce ceiling 2%, auto-pause.
8. Kill subject `Booking install: 48 hours, $449` and two of three Touch 3 subjects.
9. Normalise `{{practice}}`; suppress subject #2 on any unclean value or >42 rendered chars.
10. Drop `{{form_path}}`; enforce the 20-word cap at emission; fix pluralisation.
11. Write 3 hand-authored variants per touch; add lexical variance to Touch 2.
12. Plain text, no pixel, no shared tracking domain.
13. Secondary sending domain, full auth stack, 4-6 week warmup, postmaster tools registered.
14. Auto-suppress on inbound opt-out keywords.
15. Cite or cut the one-third statistic.
16. Art. 14 line in the UK/EU footer.

The copy discipline here is better than most agency sequences — no fear-selling, no fake urgency, honest about being auto-generated and about being in Surat, one CTA per touch, price placement is correct. What will sink it is infrastructure and merge-field rendering, not tone. And the cloned-brand demo is a bigger exposure than everything else combined.