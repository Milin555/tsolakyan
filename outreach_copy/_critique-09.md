# DELIVERABILITY & SPAM AUDIT — "no-website" 3-touch sequence

**Verdict: this sequence is well-written as copy and dangerous as infrastructure.** The prose is clean and low-trigger. The kill risk is almost entirely in (a) what `{{demo_url}}` actually *is*, (b) content fingerprinting across 19,629 near-identical sends, and (c) merge-field breakage. Assume cold domain, no reputation.

**The number that governs everything:** 6,543 × 3 = **19,629 sends**. Gmail's spam-complaint ceiling is 0.30%, target <0.10%. That is **20 complaints before you're in trouble, 59 before Gmail starts junking you wholesale.** Twenty people out of 6,543 hitting "Report spam" ends the domain. Every finding below is priced against that budget.

---

## A. CRITICAL — the demo link is a brand-impersonation classifier magnet

### A1. You are hosting a page with the prospect's real name and real logo on a domain you own
> "Your photos, your name, your logo, live right now: {{demo_url}}"

**Risk:** This is the single largest threat in the whole program, and it isn't mentioned anywhere in the doc. Microsoft Defender (Safe Links detonation) and Google Safe Browsing both run **brand-impersonation classifiers**. A brand-new, low-reputation page displaying "Riverbend Family Dental" + their scraped logo, on a domain that is demonstrably *not* theirs, linked from an unsolicited bulk email, is a textbook match for the phishing pattern those models were trained on. Dental practices skew heavily to Microsoft 365 with ATP — Safe Links will detonate your URL on *every* recipient before a human ever sees it. One classifier hit and the demo host lands on Safe Browsing / SmartScreen, which nukes the link in Gmail *and* Chrome *and* Outlook simultaneously.

**Fix (all of these, non-negotiable):**
- Persistent visible banner on every demo, above the fold, not dismissible: *"Unofficial demo built by [full name], an independent web developer. Not affiliated with or authorised by [practice]. Built from publicly available photos. [Remove this demo]"* — with a working one-click removal link.
- `<meta name="robots" content="noindex,nofollow">` + `X-Robots-Tag` header. A demo that gets indexed becomes a duplicate-brand page and invites a trademark complaint, which is a faster domain death than any spam filter.
- **No live contact form, no email capture, no login field, no phone-number capture** on the demo. A form on an impersonating page is what flips a "suspicious" score to "phishing". This directly conflicts with Touch 2's promise — sell the form, don't ship it in the demo. Render it as a visually disabled/greyed element labelled "contact form — enabled on the real build".
- Valid, dedicated TLS cert. Not a wildcard on a shared free host.

### A2. Per-prospect subdomains = fast-flux infrastructure signature
**Risk:** If the generator emits `riverbend-family-dental.demos.yourdomain.com`, you are creating **6,543 brand-new hostnames on one zone in a matter of weeks**. Every one has zero reputation and never accumulates any, because each is seen exactly once. Passive-DNS-based reputation systems (Spamhaus DBL, Cisco Talos, Defender) read high-volume ephemeral subdomain creation as fast-flux/phishing infrastructure. It also means URL-reputation caching never helps you — you get judged cold, 19,629 times.

**Fix:** **Path-based, single host.** `demos.yourdomain.com/riverbend-family-dental`. One hostname accumulates one reputation. This is a one-line generator change and it is probably worth more than every copy edit in this audit combined.

### A3. The demo host, the sending domain, and the money domain must be three different things
**Risk:** As designed, every email in the sequence links to the same root. When (not if) complaint volume gets that root URIBL-listed, you lose the emails *and* the demos *and* your actual business site in one event.

**Fix:** Sending domains (plural, see H2) ≠ demo host domain ≠ primary business domain. The demo host should be a boring, non-keyword domain. **Never** a free host — `*.vercel.app`, `*.netlify.app`, `*.pages.dev`, `*.github.io`, `*.web.app` are all heavily abused shared namespaces carrying inherited reputation you cannot control.

### A4. Unspecified: tracking
**Risk:** The doc is silent on open/click tracking. If you use a shared tracking domain from an outreach tool (`t.instantly.ai`, `link.smartlead.ai`, etc.) or any shortener (`bit.ly`, `tinyurl`), you inherit thousands of other senders' reputation and add a redirect hop. Redirect chains from unknown senders are a direct phishing signal. An open-tracking pixel is a 1×1 image that forces HTML and adds a well-known bulk fingerprint.

**Fix:** **Zero tracking.** No pixel, no click wrapper, no shortener, no UTM soup. Measure by server logs on the demo host (path is unique per prospect — you already have per-prospect attribution for free) and by replies. Send **plain text only, no HTML part at all.** Bare URLs, autolinked by the client. Never anchor text — an `<a>` whose text differs from its `href` is the highest-confidence phishing heuristic in existence.

---

## B. CRITICAL — content fingerprinting across 19,629 near-identical sends

### B1. Every email in the segment opens with the same four words
> "{{first_name}} — I looked up {{practice}} in {{city}} — ..."

**Risk:** Strip the merge fields and Touch 1 is **~60 bytes-identical words across 6,543 messages**. Gmail clusters by content shingle, not by sender; SpamAssassin/Rspamd run fuzzy hashing (Razor/Pyzor/`FUZZY_DENIED`). A handful of early complaints teaches the cluster, and then *every subsequent copy of that cluster is junked at delivery* — including messages to recipients who would have loved it. This is how a good sequence dies at send 400 despite a perfect first 399.

**Fix:** Build **4–6 genuinely distinct openers per touch** (not spintax word-swaps — spintax produces detectably synthetic text and doesn't break the shingle). Rotate deterministically by lead hash. Also rotate: greeting punctuation (`—` / `,` / `.` / no greeting), sign-off, and sentence order. Target: no two sends in a rolling 500 share more than ~40% shingle overlap.

### B2. The em-dash opener is the fingerprint inside the fingerprint
> "{{first_name}} — "

**Risk:** Three separate problems in one character. (1) It appears at byte offset ~0 in all three touches for all 6,543 leads — the most stable hashable position in the message. (2) U+2014 in a plain-text part forces quoted-printable or base64 encoding; get the charset header wrong and 6,543 clinicians see `Sarah â€" I looked up...`, which is instantly a scam. (3) In August 2026, an em dash in the first line of an unsolicited email reads as machine-generated to a human, which costs you the very "this is a real person" impression the whole sequence is built on.

**Fix:** Rotate the separator. Default to `{{first_name}},` with a line break. Force UTF-8 with an explicit `Content-Type: text/plain; charset=UTF-8` and verify round-trip through your actual sending path before volume.

### B3. Straight vs. curly quote inconsistency
> `reply "yes" and it's yours`

**Risk:** If the generator emits typographic quotes here but ASCII apostrophes in `it's` / `don't` elsewhere, you get mixed encoding within one message — a small but real "assembled by a script" tell, and another encoding-mangle vector.

**Fix:** Normalise every outbound message to a single quote convention. Recommend: ASCII throughout, no curly quotes, no em dashes anywhere.

---

## C. Spam-trigger words and phrases — exact quotes

Individually most of these are survivable. On a **cold domain** they stack, and this list stacks hard in Touch 2.

| Severity | Exact quote | Why it fires | Fix |
|---|---|---|---|
| **HIGH** | `No monthly fee, no contract` | The classic offer triad. `no contract` is a long-standing SpamAssassin body-rule target (telemarketing / free-trial lineage) and `no monthly fee` sits right beside `no fees`, `no obligation`. Both in one clause is the highest-density trigger in the sequence. | Rewrite as fact, not offer: *"You pay once. There's nothing recurring, and the files are yours."* Kills both phrases, keeps 100% of the meaning. |
| **HIGH** | `it's yours for $495` | `yours for $` is a direct-response purchase construction. Combined with a deadline and a link in the same 39-word email (Touch 3), this is the three-part spam shape: **price + deadline + link**. | *"If you want it, reply yes. It's $495 and I'll get started."* Separate the price from the link by at least one sentence. |
| **HIGH** | `web developer` (signature, all 3) | Not a filter rule — a *category* signal. Dental inboxes receive this pitch ~20×/week and have trained their own filters and their own reflexes on it. M365 tenants with even mild custom rules will have keyword blocks on `web design` / `website design` / `SEO`. | Unavoidable and honesty requires it, but move it out of the position of prominence: `Milin [Surname], Surat, India` in the sign-off, `I build websites for dental practices` inside the body of Touch 2 only. |
| **MEDIUM** | `live right now` | `right now` is a mild urgency token, and paired with an unfamiliar URL it reads as pressure. | *"...is at {{demo_url}}."* You lose nothing. |
| **MEDIUM** | `It's not a mockup or a template screenshot` | Two problems. Denying a doubt plants it. And you have voluntarily put the word **`template`** in a cold email from a web developer — the exact word your recipient uses when dismissing you. | Delete the sentence. Replace with a demonstration, not a denial: *"Open it on your phone and it works — the buttons do things."* |
| **MEDIUM** | `Open it on your phone, it takes a minute.` | Functionally identical to the banned `quick question` / `just a minute of your time` move — a time-cost reassurance. Your own Rule 6 rejects this family. | *"Takes about ten seconds to look at."* or cut entirely. |
| **MEDIUM** | `taking the demo down` + `{{takedown_date}}` | Subject 3.2 plus the Touch 3 body. "X will be removed on [date], click here" from an unknown sender is structurally a **credential-phish shape**. This is one of the most-trained-on patterns in email security. | If the takedown is real, state it *without* a date in the subject and *after* the link in the body. Never put a removal deadline in a subject line. |
| **LOW** | `$495` (×3 across sequence) | Currency + figure in body. Trivial alone; contributes to score density in a 47-word email where it's ~2% of the total text. | Keep. Named price is a trust asset; just don't crowd it. |
| **LOW** | `Either way, good luck.` / `say so and I'll delete it` | Clean. No action. | — |

---

## D. Subject line audit

### D1. `no website for {{practice}}` — **CRITICAL, do not ship**
Three independent failure modes:
- **Empty merge → `no website for `** with a trailing space. A subject that ends mid-sentence is the single most recognisable broken-mail-merge artifact in existence, and it goes in the one place the recipient cannot avoid seeing it.
- **Uppercase practice names.** IG and GBP are full of `SMILE DENTAL CARE`, `BRIGHT SMILES FAMILY DENTISTRY`. Renders as `no website for SMILE DENTAL CARE` — **all-caps in subject is a classic scored trigger** and looks like shouting.
- **The assertion is the risk.** A subject line that flatly tells a business owner they don't have something they might actually have is the highest-complaint-probability subject in the set. A single scan false positive here produces an angry reply *and* a spam report.

**Fix:** Kill it, or gate it behind: non-empty AND ≤28 chars AND title-cased AND ASCII-only AND scan confidence at maximum. Even then, prefer the softer `{{practice}} — no site behind the Instagram?` (question, not verdict).

### D2. `I built you a website` — **HIGH**
Unsolicited-gift framing is the oldest scam grammar there is (`I have something for you`, `a gift for you`). From a stranger on a cold domain, this is the least trustworthy of the three. It's also byte-identical across 6,543 sends — a perfect subject-hash cluster, and subject clustering is faster and cheaper for a provider than body clustering.

**Fix:** Demote to a small-volume A/B cell only, never the primary. Better: `built a site for {{practice}} — have a look`.

### D3. `your Instagram, as a website` — **best of the set, KEEP as primary.** Specific, verifiable, no claim, no offer, no urgency, degrades gracefully (no merge field to break).

### D4. `before you ask: the price` — **MEDIUM**
The `word: word` colon-prefix construction is a sales-automation house style (`quick one: ...`, `re: your website`). Filters and humans both recognise it.
**Fix:** `the price, since you didn't ask` or just `$495`.

### D5. `what the demo would cost` — **MEDIUM.** `cost` in a subject from a new domain is a mild trigger and signals "sales email" before the open. `the boring part` (3rd option) is the strongest of the three — keep it as primary.

### D6. `last one from me` — **HIGH**
One of the five most over-used breakup subjects in cold outreach history. Gmail has classified millions of these. Near-guaranteed cluster membership with mail that is *already* junked.
**Fix:** `closing the file on this one` / `no reply, so — done` / `{{practice}} — wrapping up`. Anything not in the canonical breakup vocabulary.

### D7. `I'll stop emailing` — **MEDIUM.** Implies they asked you to. Mildly gaslighting, and it *invites* the reader to consider that you emailed them repeatedly without permission — the exact thought that precedes clicking "Report spam".

### D8. All-lowercase across all nine subjects — **MEDIUM (systemic)**
The lowercase-subject trick worked because it read as human. It is now the default output of every outreach tool on the market, and it's a consistent, machine-detectable style across **all three touches for all 6,543 leads**. Consistency is the fingerprint.
**Fix:** Mix. Roughly a third sentence-case. Never title case, never all caps.

### D9. Length — **LOW.** `no website for Riverbend Family Dental` = 38 chars, truncates on iPhone at ~35. Cap at 32 for mobile.

---

## E. Merge-field breakage — the highest-probability real-world failure

### E1. `{{first_name}}` fallback ladder doesn't cover the punctuation — **CRITICAL**
> Doc: "first name → `Dr {{last_name}}` → **drop the greeting entirely** and open on the hook."
> Template: `{{first_name}} — {{pitch_hook}}`

**Risk:** Field-level fallback cannot delete the ` — ` that follows it. The rendered output is `" — I looked up..."` — leading space, orphaned dash. Broken on the first line of the first email.
**Fix:** This must be a **conditional block**, not a fallback value: `{{#if greeting}}{{greeting}}, {{/if}}{{pitch_hook}}`. Test the empty path explicitly.

### E2. Nested merge inside a merge — **CRITICAL**
> `the only link is {{bio_link_host}}, which isn't a site you own`
> ...lives inside `{{absence_evidence}}`, which lives inside `{{pitch_hook}}`.

**Risk:** Two-level nesting is where mail merges reliably fail. If the inner field is null you ship: `"the only link is , which isn't a site you own"` — comma orphan, mid-sentence. Worse, many merge engines render an unresolved *nested* token literally, so a clinician receives `the only link is {{bio_link_host}}`. That message single-handedly proves every cynical thing they believe.
**Fix:** Resolve `{{pitch_hook}}` to a **flat, fully-rendered string in the database** before it ever touches the sending tool. The email template must contain zero conditional logic and zero nesting. Then add a pre-send regex gate on the final rendered body: reject any message matching `\{\{|\}\}|  |\s,|\s\.|—\s*$|:\s*$`.

### E3. `{{practice}}` has a length cap for the subject and none for the hook — **HIGH**
> "Suppress if it's over ~28 chars" — subject only.
> Hook: `I looked up {{practice}} in {{city}}`

**Risk:** GBP legal names are monsters. Renders as: *"I looked up Dr. John A. Smith, DDS, PC Family & Cosmetic Dentistry of Greater Boise LLC in Boise — your Instagram..."* Reads as a database dump, because it is one.
**Fix:** Store a separate normalised `{{practice_display}}`: strip `LLC / PC / PLLC / DDS / DMD / Inc / Ltd`, strip trailing `Dentistry|Dental` if >4 words, title-case, ASCII-fold, strip emoji, ≤30 chars. Use it everywhere. If normalisation can't get under 30 chars, drop the lead.

### E4. `{{practice}}` will contain emoji — **HIGH**
IG display names routinely carry `✨ 🦷 💎`. `no website for Smile Dental ✨` from a cold domain: emoji in subject is a scored trigger, and emoji in a *name* position looks like a compromised-account send.
**Fix:** Hard strip all non-ASCII from `{{practice}}` and `{{first_name}}`. If stripping changes the string, drop the lead.

### E5. `{{city}}` from Instagram is garbage — **HIGH**
IG location fields contain `🌎 Worldwide`, `DM for appt`, `Boise | Meridian | Nampa`, `Book below ⬇️`, and empty strings. This field's entire job is *"prove a real search happened"*, so a wrong value inverts its purpose exactly.
**Fix:** Source `{{city}}` **only** from the Google Business Profile address, never from IG. Validate against a geo table. No match → drop the lead. This field is load-bearing for credibility; a guess is worse than nothing.

### E6. `{{first_name}}` from IG handles — **HIGH**
Scrapes yield `smilesbyjen`, `Dr Smile`, `Bright`, `DrJenDDS`, `The`. `smilesbyjen — I looked up...` is dead on arrival.
**Fix:** Accept a first name only if it's alphabetic, 2–15 chars, and matches a name dictionary. Otherwise fall to `Dr {{last_name}}`, otherwise **no greeting**. Never derive a name from a handle or an email local-part.

### E7. `{{takedown_date}}` locale ambiguity — **MEDIUM**
`26/08/2026` means August to a UK reader and nothing to a US one. `08/26/2026` reverses.
**Fix:** Unambiguous long form always: `Wednesday 26 August`. Also: **it must be ≥14 days out**, or you hit E8.

### E8. The takedown date creates a self-inflicted trap — **MEDIUM**
Touch 3 goes out day 7 with a takedown date. A prospect who replies "yes" on day 12 finds a dead link, and the sale evaporates because your own automation deleted the product.
**Fix:** Takedown ≥14 days after Touch 3, and any inbound reply must auto-extend the demo by 30 days.

### E9. `{{demo_url}}` empty — **CRITICAL**
> "live right now: {{demo_url}}"

Renders as a sentence that ends in a colon. The email has literally no purpose without it.
**Fix:** Hard pre-send assertion: `demo_url` non-null, HTTPS, returns 200, and the response body contains `{{practice_display}}`. Any failure → block the send, not just the field.

---

## F. Opt-out and compliance — where the copy is *worse* than the doc thinks

### F1. Missing `List-Unsubscribe` and `List-Unsubscribe-Post` headers — **CRITICAL**
The doc specifies `{{unsubscribe_url}}` as a **body link only**. Since February 2024, Gmail and Yahoo **require RFC 8058 one-click unsubscribe headers** for bulk senders, and it's now a de facto expectation at any volume. Without them, Gmail's own UI won't show the native unsubscribe button — which means an annoyed recipient's *only* available exit is the "Report spam" button. **You are converting unsubscribes into complaints by omission.** Against a 20-complaint budget, this alone can end the program.
**Fix:**
```
List-Unsubscribe: <https://…/u/{{token}}>, <mailto:unsub@…?subject=unsubscribe>
List-Unsubscribe-Post: List-Unsubscribe=One-Click
```
The URL must action on a bare `POST` with no confirmation page, no login, no "are you sure". Verify the endpoint responds 200 to POST before volume.

### F2. No "why you're getting this" line — **HIGH**
The footer is `{{unsubscribe_url}}` + address, unlabelled. Recipients who can't reconstruct why they received something complain instead of unsubscribing.
**Fix:** One plain line, all three touches:
`You're getting this because {{practice}} is listed publicly in {{city}} and I couldn't find a website for it. Unsubscribe: {{unsubscribe_url}}` — this is the cheapest complaint-rate reduction available to you.

### F3. Reply-based opt-out is promised but not wired to suppression — **CRITICAL**
> Touch 1: "If it's no use to you, say so and I'll delete it."

**Risk:** You explicitly invited a reply-to-decline, then scheduled two more emails. A prospect who replies *"no thanks"* on day 1 and receives the price on day 3 will not unsubscribe — they will report spam, because you broke a promise you made in writing. This is the highest-intent complaint source in the sequence.
**Fix:** **Any inbound reply halts the sequence immediately**, before classification. Then classify. Negative-intent patterns (`no`, `not interested`, `remove`, `stop`, `unsubscribe`, `take me off`, `do not contact`) → permanent suppression across all domains and all future campaigns, plus delete the demo and reply once confirming both. Manual review of the ambiguous bucket, daily.

### F4. UK role-address guidance is correct for PECR and costly for deliverability — **MEDIUM**
> "send only to practice/role addresses (info@, reception@, the practice domain)"

**Risk:** Legally sound, deliverability-hostile. Role accounts are (a) disproportionately represented among **recycled spam traps** — abandoned practice domains whose `info@` gets repurposed, and a single Spamhaus trap hit lists the sending IP/domain; (b) shared inboxes with higher complaint rates (several staff, any one can report); (c) subject to more aggressive gateway filtering. This tension isn't acknowledged in the doc.
**Fix:** Keep the PECR-compliant targeting, but **isolate UK role-address sending onto its own domain and its own IP pool**, verify every address with real-time SMTP validation plus a trap-risk/domain-age check, and drop any address on a domain with no MX activity or no live website. Treat that pool as your highest-risk cohort and cap daily volume there.

### F5. Mononym sender identity — **MEDIUM**
> "Milin — web developer, Surat, India" / "Milin"

CAN-SPAM needs accurate header info + postal address (satisfied). AU's Spam Act §17 requires clear sender identification. A single name, no surname, no business name, no sender website, plus an overseas address, is a low-trust identity to both a human clinician and to M365, which finds no corroborating domain to score.
**Fix:** Full name in the signature. Put a real one-page site for yourself at the root of the **sending** domain (name, photo, what you do, portfolio, contact) — a sending domain that resolves to a real human page scores materially better than one that 404s. This costs an afternoon.

---

## G. List hygiene and complaint math

### G1. Bounce rate will kill you before content ever does — **CRITICAL**
Scraped GBP/IG email addresses bounce at **8–15%** unverified. The tolerance on a cold domain is **<2%**, and >3% on a fresh domain triggers throttling within a day or two.
**Fix:** Real-time SMTP verification on 100% of 6,543 addresses immediately pre-send (not at scrape time — dental staff turnover is high and these lists rot fast). Drop all `unknown` results. Route catch-all domains into a **separate, later, low-volume pool** — never mix them into the main send. Auto-suppress on first hard bounce across the whole program.

### G2. No engagement gate between touches — **HIGH**
Touch 2 and Touch 3 fire on day 3 and day 7 regardless of behaviour. Sending twice more to people who never opened is how you convert indifference into complaints, and it's the phase where complaint rate spikes on cold domains.
**Fix:** With no open tracking (per A4), gate on the proxies you do have: demo-page hit in your server logs, or any reply. **No demo hit and no reply after Touch 2 → drop before Touch 3.** You will lose a few sales and save the domain. On a 20-complaint budget that trade is not close.

### G3. Scan false positives are the complaint engine — **CRITICAL**
> "there's no website behind either"

The emit rules are genuinely good, but at even a **1% false-positive rate you are telling 65 practice owners they don't have a website they in fact have**. Those 65 are the most likely people in the entire list to report spam — they're offended, and you've handed them proof you didn't check. 65 > 59 (the 0.3% Gmail ceiling). **One percent of error is the entire program.**
**Fix:** Add a fifth emit rule the doc is missing — **`{{practice}} + "dentist" + {{city}}` must return no owned site in Bing top 10 either**, not just Google. Add a sixth: MX lookup on any domain in the practice's email address — `sarah@riverbenddental.com` proves an owned domain exists even when no website is indexed, and that is a *very* common scan miss. Then manually spot-check 200 leads by hand before the first send. If the manual FP rate is above 0.5%, do not ship.

### G4. Sequence density on a cold domain — **MEDIUM.** Day 0 / 3 / 7 is tight for a first-ever campaign from a zero-reputation domain. Widen to day 0 / 5 / 12 for the first 2,000 leads, tighten only once complaint rate is confirmed <0.05%.

---

## H. Infrastructure the doc never mentions

### H1. Authentication — **CRITICAL.** SPF (single lookup chain, ≤10 DNS lookups), DKIM 2048-bit, DMARC published at minimum `p=none; rua=` with monitoring from day one. `p=quarantine` within 30 days. Missing DMARC = rejected outright by Gmail/Yahoo at bulk volume.

### H2. Volume and warmup — **CRITICAL.** 19,629 sends at a safe cold-domain rate of 30–40/day/mailbox means you need roughly **10–14 mailboxes across 3–5 sending domains**, running 8–10 weeks, after a 3–4 week warmup during which you send *nothing* cold. Attempting this from one mailbox on one new domain will burn it inside a week. Never send from the primary business domain.

### H3. Sending domain naming — **MEDIUM.** If the sending domain is a keyword domain (`dentalwebsitepros.com`, `getdentalsites.com`), the From header advertises the category before the subject is read, and keyword domains registered recently are independently scored. Use a neutral personal-brand domain — your own name.

### H4. Threading not specified — **LOW/MEDIUM.** The doc never says whether touches 2 and 3 are same-thread replies. Same-thread lowers per-message reputation cost, but if Touch 1 landed in spam the whole thread is buried. Recommend: Touch 2 as an in-thread reply (`In-Reply-To`), Touch 3 as a **new thread with a new subject** — it gets a fresh placement decision at the point where you most need one.

### H5. No seed list / no placement testing — **HIGH.** You are flying blind with zero tracking. Seed 15–20 addresses across Gmail, Outlook.com, M365 tenants, Yahoo, and a couple of dental-practice-typical hosts. Check placement before every batch of 500. This is the only instrument you have.

---

## I. Rewrites — Touch 2 is the one that needs it

**Touch 2 as written** carries `no monthly fee`, `no contract`, and `$495` inside 47 words, on a cold domain. That's the highest trigger density in the sequence, in the shortest message, where boilerplate (unsubscribe + postal address + why-line) will outweigh the actual content — a genuinely bad content-to-boilerplate ratio that filters do score.

```
{{first_name}}, the demo's still up: {{demo_url}}

The boring part, since you're probably wondering. To make it
properly yours — your own domain, your hours, a contact form
that reaches you — is $495. You pay once, there's nothing
recurring, and the files are yours to keep or move.

Yes or no, either's fine.

Milin [Surname]
Surat, India

You're getting this because {{practice_display}} is listed
publicly in {{city}} and I couldn't find a website for it.
Unsubscribe: {{unsubscribe_url}}
{{sender_postal_address}}
```
Removes `no monthly fee` and `no contract`, adds the why-line, lifts word count enough to fix the boilerplate ratio.

**Touch 3 body**, minimum change — separate price from link, drop the deadline out of the subject:
```
{{first_name}}, last email from me.

I take the demos down after a couple of weeks — I pay for the
hosting and don't like keeping dead ones around. This one goes
on {{takedown_date}}.

If you want it, it's $495 and you just reply yes. Here it is
one more time: {{demo_url}}

Either way, good luck.
```

---

## Ranked: fix these before a single send

1. **A1** — impersonation banner, noindex, no live form on demos *(will get you Safe-Browsing-listed)*
2. **F1** — `List-Unsubscribe` / `List-Unsubscribe-Post` headers *(you are manufacturing complaints without them)*
3. **G3** — the fifth and sixth emit rules + 200-lead manual FP audit *(1% error = program over)*
4. **E2 / E1 / E9** — flatten nested merges, conditional greeting block, pre-send regex + demo-URL assertion gate
5. **G1** — 100% real-time email verification, catch-alls in a separate pool
6. **A2** — path-based demo URLs on one host, not 6,543 subdomains
7. **H1 / H2** — SPF/DKIM/DMARC, 3–5 domains, 10–14 mailboxes, 3–4 week warmup
8. **B1 / B2** — 4–6 rotating openers per touch, kill the em dash
9. **D1** — retire `no website for {{practice}}` as a subject
10. **C** — strip `no contract` / `no monthly fee` / `it's yours for $495` / `template`
11. **F3** — any reply halts the sequence, before classification
12. **G2** — no demo hit and no reply after Touch 2 → drop before Touch 3

**What's already right, so you don't break it:** no fear-selling, no legal claims, no fake urgency, no fake local identity, named price with no discount ladder, no `$149/mo` in the cold sequence, real postal address, and a reply-driven CTA (inbound replies are a genuine positive reputation signal). The copy discipline here is better than 95% of cold outreach. The infrastructure around it is what will kill it.