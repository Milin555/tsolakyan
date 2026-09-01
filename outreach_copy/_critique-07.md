# Legal & Ethics Audit — link-in-bio 3-touch sequence

Not legal advice. Jurisdiction-specific items (esp. UK PECR corporate-subscriber status and AU inferred consent) should be confirmed with a solicitor before scaled sending.

**Verdict: do not send as written.** Four blockers. The legal exposure is real but manageable; the bigger problem is that three claims in the copy are not supported by what the scanner actually checks, which violates your own hard rule 1 and is the thing that will get you reported rather than ignored.

---

## BLOCKERS — fix before a single send

### B1. "no page that takes a booking" is fabricated relative to the scan

> Touch 1: *"so {{practice}} has nothing for Google to show and **no page that takes a booking**."*
> Touch 2: *"A rented link page can't rank, can't hold your reviews, **can't take a Tuesday-night booking**."*

**Rule:** Your hard rule 1. Also FTC Act §5 (unsubstantiated claim), Australian Consumer Law s18 (misleading or deceptive conduct in trade or commerce — applies B2B, strict liability, no honest-mistake defence), UK Business Protection from Misleading Marketing Regs 2008 (B2B misleading advertising).

**Why it's false:** the scanner's condition (b) only checks that the sole bio link *resolves to* linktr.ee / bit.ly / wa.me / etc. It never crawls what's inside. Linktree pages very commonly contain a Dentally / Zocdoc / Calendly / NHS / Cliniko booking link. You are telling a dentist who has a booking link that they don't have one. That is the single most likely email in this sequence to get a furious reply.

**Fix — pick one:**
- Crawl the link platform page, extract outbound links, and **suppress the lead if any known booking host appears**. Then the claim is true and it's your strongest line.
- Or drop the claim entirely: *"and nothing behind it that you own."*

Same for "can't hold your reviews" — a website doesn't hold reviews either; reviews live on Google and Facebook regardless. Delete that clause, it's a false benefit.

---

### B2. `pitch_hook` asserts a domain-registry fact you cannot obtain

> *"and no website domain was found registered to {{practice}}."*

**Rule:** hard rule 1; ACL s18; BPMMR 2008.

WHOIS registrant fields have been redacted by default since GDPR. You cannot determine what domains are "registered to" a named business, and reverse-WHOIS by organisation name is unreliable-to-useless for small practices. Separately, name-based domain lookup misses the common real cases: `drsmith.com` instead of `willowlanedental.com`, a page inside a group/DSO site, `.co.uk` vs `.com`, a Wix/Squarespace subdomain, a website listed only on the Google Business Profile.

**There is also a direct logical contradiction in your own spec.** Your UK suppression rule keeps leads whose contact is a *practice-domain* address. So a surviving UK lead is `sarah@willowlanedental.co.uk` — which proves a domain **is** registered to the practice, while the email tells them none was found. That email is self-refuting on arrival.

**Fix — all three:**
1. Rewrite the hook to what you actually observed:
   `The only link on {{instagram_handle}} goes to {{link_platform}}, and I couldn't find a website of your own anywhere for {{practice}}.`
2. Add scan checks before the lead qualifies: Google Business Profile "website" field is empty; a SERP query for `"{{practice}}" {{city}}` returns no practice-owned domain in the top 10; **the contact email's domain does not resolve to a live site** (if `@willowlanedental.co.uk` serves a homepage, this lead is not in this segment).
3. Suppress on any hit.

---

### B3. Publishing a live page carrying their real name and logo, with no disclaimer and no noindex

> Touch 1: *"So I built one and put it up: {{demo_url}} / Your name, your logo, your colours, real pages."*

**Rules:** trade mark infringement / passing off (UK TMA 1994 s10, US Lanham Act §32/43(a), AU TMA 1995 s120); copyright in the logo and any scraped images/copy; UK GDPR / AU Privacy Act if staff names or photos are reproduced.

The defence available to you is that it's a non-confusing, non-trading, private preview. **Every one of those qualifiers has to be actually true**, and right now none of them are enforced. A publicly indexable page with a practice's logo, name and a "Book" button is a page a real patient can find and try to book urgent care through. That is the scenario that turns a marketing email into an actual harm — and into a demand letter.

**Fix — generator-level, non-negotiable:**
- `X-Robots-Tag: noindex, nofollow` + `robots.txt` disallow on the whole demo host.
- Unguessable slug (`/d/willow-lane-7fq2x`), not a predictable one.
- Persistent visible banner, top of every demo page: **"Unofficial demo built by Milin Web, Surat. Not affiliated with {{practice}}. Not a real booking page."**
- No working booking form, no form that accepts patient data, no phone number that isn't verifiably theirs (or no `tel:` link at all).
- Logo used at rendered size only, pulled from their public IG/GBP; no scraped patient photos, no scraped review text, no staff headshots.
- Auto-expire and hard-delete on a timer. Instant takedown on any request, no questions.
- Say it in the email so it reads as courtesy rather than cover: *"It's unlisted and not indexed."*

---

### B4. Demo pages will fail health-advertising law in the UK and Australia if the templates carry standard marketing furniture

Nothing in the *email copy* makes a clinical claim — that part is clean. The exposure is the demo page you attach to it, branded with a regulated practitioner's practice name.

- **Australia:** Health Practitioner National Law s133 **bans testimonials in advertising a regulated health service outright** — a "What our patients say" carousel, even with placeholder text, on a page bearing an AHPRA-registered practice's name is a live problem, and s133 can bite the advertiser, not just the practitioner. Also bans claims creating unreasonable expectations of benefit.
- **UK:** naming a prescription-only medicine to the public is prohibited under the Human Medicines Regs 2012 reg 279 — **the word "Botox" on a med-spa template is a criminal-offence risk, not an ASA slap.** CAP Code s12 bars "painless", "safe", superiority claims. GDC standards require registration details, complaints procedure and prices on a practice site.
- **US:** FTC Endorsement Guides + the 2024 Rule on Consumer Reviews and Testimonials — fabricated reviews or placeholder star ratings carry direct civil penalties.

**Fix:** the generator ships with **zero** testimonials, **zero** star ratings, **zero** before/after images, **zero** treatment outcome claims, **zero** prescription drug names (Botox, Juvéderm, Dysport, semaglutide). Service names as plain nouns only. Placeholder text must be obviously placeholder, never fake praise.

And per your hard rule 2: **never** describe the result as "compliant" in the email or on the demo. Building safe templates is a quality decision; saying so is a promise you can't make.

---

## HIGH — legally exposed or plainly dishonest

### H1. "$495 to own it outright" — materially incomplete price

> Touch 2: *"$495 to own it outright, about a week to finish."*

**Rule:** ACL s18 & s29 (misleading representations about price); FTC deceptive-pricing; UK BPMMR (misleading omission of material information).

"Own it outright" tells a clinician the total cost of ownership is $495. If the site sits on your hosting, or they need a domain, or it degrades without the $149/mo plan, that's a material omission — and the complaint writes itself when the first renewal invoice lands. It also poisons the exact quality this sequence trades on.

**Fix:** `$495 and the site is yours — code and content, no monthly fee to me. Domain and hosting you buy yourself; I'll point you at both.`

That sentence names no second price (respecting your own rule) while removing the deception. It also pre-answers the objection.

### H2. "about a week to finish" — unsubstantiated delivery claim

Your clock depends entirely on how fast *they* send logo, copy, hours and domain access. As written it's a promise you don't control.

**Fix:** `about a week from the day you send me your details.`

### H3. Subject line "{{practice}} — I built you a website"

**Rule:** CAN-SPAM §7704(a)(2) (materially misleading subject); ACL s18.

You built a *demo*, on *your* domain, that isn't theirs. Touch 1 never corrects it — Touch 2 does, three days later, which is too late for a recipient who only ever opens the first. Low-cost fix, meaningful risk reduction.

**Fix:** `{{practice}} — I built you a demo site`. And in the body, `So I built a demo of one:` rather than `So I built one and put it up`.

### H4. "Taking the demo down Friday" — deadline that will frequently be false

Your own note flags the timer condition, correctly. Two gaps remain even if timers exist:
- Subject says **Friday**, body says **end of the week**. Touch 3 fires on day 7, which can be any weekday, so those two will routinely disagree and neither will match the real expiry timestamp.
- **Fix:** drive both from the real value: subject `Demo comes down {{demo_expiry_date}}`, body `deletes itself on {{demo_expiry_date}}`. If `demo_expiry_date` is null, the variant is not eligible — enforce that in the template, don't leave it to judgement.

Recommendation: **set real expiry regardless.** It makes the deadline honest, and auto-deletion is also the mitigation for B3. One change closes two findings.

### H5. "Last email from me" / "I'll leave you alone" must be enforced as permanent

**Rule:** CAN-SPAM §7704(a)(1) (false or misleading transmission/content); ACL s18.

If a non-replier who received Touch 3 ever re-enters another Milin campaign — a different segment, a different offer, a new domain next quarter — the statement was false when made.

**Fix:** completing Touch 3 writes a permanent do-not-recontact entry keyed on hashed email, enforced across **every** list and sending domain, not just this sequence. If you're not prepared to enforce that, change the wording to `last email from me about this` — but the permanent version is better copy and better ethics.

---

## CAN-SPAM (US)

| Requirement | Status |
|---|---|
| Physical postal address | **Present** via `{{sender_address}}` — but see C1 |
| Functional opt-out, 30 days live, honoured ≤10 business days | Present in copy; see C2 |
| Accurate From / Reply-To / routing | See C3 |
| Non-deceptive subject | See H3, H4 |
| **Clear & conspicuous identification as an advertisement** | **MISSING — C4** |

**C1 — no suppression rule on the footer merge fields.** Your suppression list covers `demo_url` and `first_name` but not `sender_address` or `unsubscribe_url`. A blank-render of either is a per-message statutory violation (up to $53,088 per email under current FTC adjustment). Add a hard render-time gate: **abort the send if any `{{` survives into the final message body, subject or footer.** That also protects the subject lines — `Your Instagram link goes to ` with an empty `{{link_platform}}` is both deceptive and an obvious blast tell.

**C2 — "I won't contact you again" is a global promise.** Unsubscribe must therefore suppress across every list and sending domain you operate, not just this sequence. Also: the unsubscribe page must not require a login, a reason, or re-entry of their address (§7704(a)(4) permits requiring nothing beyond the email address and a single-page visit). Standardise on **honouring within 48 hours** — that clears CAN-SPAM's 10 business days *and* Australia's stricter 5 working days in one policy. Add `List-Unsubscribe` and `List-Unsubscribe-Post` headers (RFC 8058); not law, but required by Gmail/Yahoo bulk-sender policy and it's how "one click" actually becomes one click.

**C3 — sender identity.** From must be your real name, on a domain you own, that does not imply a US/UK presence. No `dentalwebstudio.co.uk`, no "Dental Web Group of London", no lookalike domain. Reply-to must be monitored by a human — Touch 2 and 3 both ask for replies, so an unmonitored reply-to is itself a misleading representation.

**C4 — advertisement identification is absent.** §7704(a)(5)(A)(i) requires clear and conspicuous notice that the message is an advertisement or solicitation, and the statute provides no "obviously an ad" exception (only affirmative consent or transactional/relationship messages are exempt). Touch 1 is the weakest — it names no price and reads as a favour. Add one line to the footer, first position:

`This is a sales email — I build websites for dental practices.`

That satisfies the requirement without the tonal damage of "ADVERTISEMENT".

---

## UK — PECR & UK GDPR

**U1 — your corporate-subscriber test is the wrong test. This is a genuine compliance gap, not a technicality.**

> *"suppress UK leads whose contact is a personal gmail/hotmail rather than a practice domain"*

PECR reg 22's consent requirement doesn't apply to **corporate subscribers** (limited companies, LLPs, plcs, public bodies). Sole traders and unincorporated partnerships are treated as **individual subscribers and need prior consent** — and a huge share of UK dental practices are exactly that. `sarah@smilecarebrighton.co.uk` tells you nothing about incorporation status; a sole-trader dentist has a practice-domain email like everyone else.

**Fix:** qualify UK leads against **Companies House** — send only where the practice resolves to an active limited company or LLP. Suppress sole traders and partnerships regardless of email domain. Store the company number on the lead record as your evidence.

**U2 — Article 14 notice is missing.** `sarah@willowlanedental.co.uk` is personal data whether or not PECR applies. You collected it from Instagram, not from her, so Art 14 requires you to tell her at first contact: the source, what you hold, the purpose, that your basis is legitimate interests, retention, and her rights — including the **absolute right to object to direct marketing** (Art 21(2)). "Listed publicly as a dental practice" is a start; it is not an Art 14 notice.

**Fix — one footer line:** `Where I got your details, and how to have them deleted: milin.dev/privacy`

Behind it: a short page covering source (public Instagram business profile), data held (name, practice, handle, business email), purpose, legitimate-interests basis, retention, objection/erasure route. Also **write and keep a Legitimate Interests Assessment** — the ICO expects a documented one, and it's the first thing asked for in a complaint. It should cover the scanning too, not just the sending.

**U3 — UK representative (Art 27).** You're a controller outside the UK with no UK establishment, processing UK personal data to offer services to UK-based people, so UK GDPR applies extraterritorially under Art 3(2) and Art 27 requires a designated UK representative, published. Same for any EU/Ireland leads under EU GDPR Art 27. Enforcement risk is low in practice; the obligation is real and cheap to satisfy via a representative service. Flagging so it's a decision, not an oversight.

**U4 — erasure vs suppression.** On an objection, delete the prospect record but **retain a hashed email on the suppression list indefinitely** — that retention is permitted and in fact necessary to honour the opt-out. Don't delete the suppression entry.

---

## Australia — Spam Act 2003

Practically your highest-enforcement-risk jurisdiction. ACMA is active, penalties are per-message, and dentists complain.

**A1 — "conspicuously published" is a much narrower gate than "publicly listed."** Inferred consent under Sch 2 cl 4 requires the address to have been conspicuously published **by the practice, in a business capacity, in connection with that role**, without an accompanying no-unsolicited-messages statement, and the message must be **directly relevant** to that role.

That means, hard rules for AU leads:
- Only send to an address the practice itself published (IG bio, own website contact page). A guessed pattern address (`info@`, `firstname@`) or one bought from a directory **fails** — it isn't published by them, and inferred consent does not exist.
- **Record the source URL and the date you observed it** on every AU lead. This is the exact evidence ACMA asks for, and without it you cannot defend a complaint.
- **Scan for a disclaimer** near the published address ("we do not accept unsolicited commercial email") and suppress on any hit. Currently nothing in your spec does this.
- Suppress non-principal named addresses (hygienist, receptionist) — relevance to *that individual's* role is weak.

**A2 — s17 sender identification is thin.** "Milin" with no surname, no trading name, does not "clearly and accurately identify" the sender. Contact details must remain reasonably likely to be valid for 30 days.

**Fix:** signature reads `Milin [Surname] — [trading name], Surat, India`, plus a reachable email in the footer. Also, sign Touch 2 and Touch 3 with the country, not just "Milin". A recipient whose Touch 1 went to spam may only ever see Touch 2 — country disclosure shouldn't depend on which email lands.

**A3 — unsubscribe: 5 working days, 30 days live.** Stricter than CAN-SPAM. Covered by the 48-hour policy in C2.

**A4 — ACL s18** applies B2B with no materiality threshold and no honest-mistake defence. It is the operative rule for B1, B2, H1, H2, H3 and H4 above. Australia is where the fabrication findings hurt most.

---

## MEDIUM — ethics and internal consistency

**M1 — Touch 2 contradicts your own stated rule.**

> Doc: *"What this sequence deliberately does not say: nothing about losing patients..."*
> Touch 2: *"someone hears about {{practice}}, types the name into Google, and lands on {{link_platform}} or nothing at all."*

That's a lost-patient vignette. It's hedged and it's mild, and it isn't unethical — but it's an imagined scene, not an observed finding, which puts it on the wrong side of "the finding is the pitch."

**Fix:** `someone types {{practice}} into Google and there's no site of yours for them to land on.` Same point, observable, one clause shorter.

**M2 — subject "What Google shows for {{practice}}" promises a SERP check you didn't run.** The scan does a domain lookup, not a search-results check. Either actually run the SERP query (recommended anyway — see B2 fix) and cite it, or change the subject to `{{practice}} has no site of its own`.

**M3 — "nothing for Google to show" is overstated.** They almost certainly have a Google Business Profile, which Google shows prominently and which carries reviews. Saying otherwise to someone who can see their own map pack listing reads as ignorance.

**Fix:** `so nothing you control comes up when someone searches the name.`

**M4 — "say so and I'll stop" is ambiguous.** Reads as "stop emailing" when you mean "take the demo down." Given B3, make the takedown offer explicit and unconditional: `Say the word and I'll delete it.`

**M5 — India / DPDP Act 2023.** Your processing happens in India, so the DPDP Act plausibly applies to you as a Data Fiduciary. Its consent-first model has no legitimate-interests equivalent, which fits cold outreach badly. Enforcement posture and rule commencement have been moving; verify current status rather than relying on this note. Flagging only so you don't treat India as a safe harbour by default.

---

## What passes clean

- No implied legal threat, no compliance guarantee, no promised legal outcome anywhere. Hard rule 2 is fully met.
- No clinical or medical claims in the email copy. Nothing that touches GDC/AHPRA/state-board advertising rules **in the emails** — the exposure is entirely in the demo pages (B4).
- No fake local identity, no American alias, no claimed local office. Surat disclosed in Touch 1 signature. Correct call, and putting it in the signature rather than the body is the right instinct — just extend it to all three touches (A2).
- Reply-stops-sequence, and "not interested" gets acknowledgement plus suppression rather than a rebuttal. That's a higher standard than the law requires and it's the right one.
- No manufactured urgency in Touches 1 and 2. Touch 3's deadline is conditioned correctly in principle — just needs to be enforced in the template rather than by judgement (H4).
- Single CTA per touch, no price in Touch 1, no second offer anywhere. Structurally sound.
- Footer already carries a relationship statement and a genuine one-click promise — most cold sequences don't have either.

---

## Rewritten copy — ready to paste

**pitch_hook**
```
The only link on {{instagram_handle}} goes to {{link_platform}},
and I couldn't find a website of your own anywhere for {{practice}}.
```

**Touch 1** (55 words — shorter than the original)
```
{{first_name}} — the only link on {{instagram_handle}} goes to
{{link_platform}}, and I couldn't find a website of your own
anywhere for {{practice}}.

So I built a demo of one: {{demo_url}}

Your name, your logo, your colours, real pages. It's unlisted and
not indexed. Say the word and I'll delete it.

Milin {{surname}}, web developer, Surat, India
```
Subjects: `Your Instagram link goes to {{link_platform}}` / `{{practice}} — I built you a demo site` / `A real site behind your bio link`

**Touch 2** (62 words)
```
{{first_name}} — someone types {{practice}} into Google and there's
no site of yours for them to land on. A link page you rent can't
rank, and it isn't yours to keep.

The demo is still up: {{demo_url}}. $495 and the site is yours,
code and content, no monthly fee to me. Domain and hosting you buy
yourself; I'll point you at both. About a week from the day you
send me your details.

Want it? Reply with one word.

Milin, Surat, India
```
Subjects: `{{practice}} has no site of its own` / `Still up if you want it` / `Your demo site, and the price`

**Touch 3 — timer version** (only if `demo_expiry_date` is non-null)
```
{{first_name}} — last one from me. The demo at {{demo_url}} deletes
itself on {{demo_expiry_date}}. If you want it, reply "keep it" and
it's yours for $495. If not, I'll leave you alone. Either way, good
luck with the practice.

Milin, Surat, India
```
Subject: `Demo comes down {{demo_expiry_date}}` / `Last email from me` / `Closing this out`

**Touch 3 — no-timer version**
```
{{first_name}} — last one from me. The demo at {{demo_url}} stays
up either way. If you want it, reply "keep it" and it's yours for
$495. If not, this is the last you'll hear from me. Good luck with
the practice.

Milin, Surat, India
```
Subject: `Last email from me` / `Closing this out` only.

**Footer, all three touches**
```
This is a sales email — I build websites for dental practices.

You're getting this because {{practice}} is listed publicly as a
dental practice and this address is published as its business
contact. Don't want these? {{unsubscribe_url}} — one click, no
reply needed, and I won't email you again from any address of mine.

Where I got your details and how to have them deleted:
{{privacy_url}}

{{sender_legal_name}} — {{sender_email}}
{{sender_address}}
```

---

## Additions to the suppression / send-gate spec

Hard-fail the send if any of these are true:

1. `demo_url`, `first_name`, `sender_address`, `unsubscribe_url`, `privacy_url` or any subject-line merge field is blank.
2. Any literal `{{` survives into the rendered subject, body or footer.
3. The link-platform page contains an outbound booking link (Dentally, Zocdoc, Calendly, Cliniko, NHS, Doctolib, etc.).
4. The contact email's domain serves a live homepage.
5. The Google Business Profile has a website URL populated, or a SERP for `"{{practice}}" {{city}}` returns a practice-owned domain in the top 10.
6. **UK:** no active limited company or LLP for the practice on Companies House.
7. **AU:** no recorded source URL + observation date proving the practice conspicuously published that address; or a no-unsolicited-email statement appears near it; or the address belongs to a non-principal named individual.
8. Email is on the global permanent do-not-contact list (which now includes every lead that completed Touch 3).

Ranked by expected damage: **B1 and B2 are what will get you reported** — they're wrong to the recipient's face, about their own business, and no legal defence helps because they're simply untrue. **B3 and B4 are what could get you a demand letter.** Everything under CAN-SPAM/PECR/Spam Act is real but routine, and fixable with a footer rewrite plus three suppression rules.