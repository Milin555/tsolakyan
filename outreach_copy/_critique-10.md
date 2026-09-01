# LEGAL & ETHICS AUDIT — `no-booking` 3-touch sequence

Jurisdictions: CAN-SPAM (US), PECR + UK GDPR (UK), Spam Act 2003 + ACL + AHPRA (AU).

---

## BLOCKERS — do not send until fixed

### B1. The core factual claim is false as written
**Text:** `{{page_count}} pages, and no way to book on any of them — the only route in is the phone number in your header`
Also subject: `Nowhere to book on {{practice}}'s site`

**Rule:** FTC Act §5 (deceptive commercial claim), UK CAP Code 3.1/3.7 (substantiation), Australian Consumer Law s18 (misleading conduct — applies to B2B). Also violates Milin's own Rule 1.

A phone number **is** a way to book. The sentence contradicts itself inside one clause — it asserts "no way to book" and then names the way to book. A dentist reads that in two seconds and files it as agency spam. Separately, `{{page_count}}` is *pages the crawler reached*, not pages the site has; asserting "18 pages" for a 40-page site is a false statement about their business.

**Corrected hook (18 words):**
```
I checked {{page_count}} pages and found no online booking — the only route in is {{contact_method_found}}.
```
**Corrected subject 2:** `No online booking on {{practice}}'s site`
**Corrected subject 1:** `Your site takes calls, but not online bookings`

### B2. Touch 2 asserts two unsubstantiated statistics as fact
**Text:** `when someone hits a voicemail, most of them just call the next practice. They don't ring back later.` and `About a third of calls during clinic hours go unanswered anyway`

**Rule:** FTC §5 substantiation; CAP 3.7 (holding evidence *before* sending); ACL s18. "Most" and "about a third" are objective quantified claims. These numbers circulate in booking-vendor marketing decks and are not independently sourced. If Milin cannot produce the study on request, both are deceptive — and both are also fear-selling (Rule 3): the payload is "you are losing patients right now."

**Fix — either cite or drop.** Safest rewrite, no statistics, no fear, same job (43 words):
```
{{first_name}} — a call that lands on voicemail during clinic hours
depends on someone ringing back. An online booking doesn't.

That's the whole reason I sent the demo:

{{demo_url}}

Real booking on your actual site is $449, usually live within
48 hours of getting access. Nothing else on the site changes.
```
**Corrected subject 1:** `Voicemail vs. a booking button`

### B3. "live in 48 hours" is an unqualified performance promise
**Text:** `$449, live in 48 hours` / `Booking install: 48 hours, $449`

**Rule:** ACL s29(1)(m) (false representation about services), FTC §5, CAP 3.1. Delivery depends on the practice supplying DNS/CMS access and a booking-vendor account. If it slips because *they* were slow, Milin still made an unconditional promise.

**Fix:** `$449, usually live within 48 hours of getting site access.` Subject: `Booking install: $449, live in ~48h`

### B4. No advertisement disclosure (Touch 1 especially)
**Rule:** CAN-SPAM 16 CFR 316.3(a)(1) — a commercial email sent without prior affirmative consent must carry **clear and conspicuous notice that the message is an advertisement or solicitation**. Touch 1 deliberately carries no price and no offer name, which makes it *more* exposed on this point, not less: nothing on the face of it identifies it as a solicitation.

**Fix — add as the first footer line, all three touches:**
```
This is a sales email from an independent web developer.
```

### B5. The demo site itself is the largest unmanaged legal risk, and the doc doesn't address it at all
The generator publishes a live page containing **their logo, their brand colours and their page copy**, and Touch 1 says so out loud.

- **Copyright / trademark:** reproducing a practice's logo and copy on a public URL is prima facie infringement and, if the URL or page title carries their name, passing off (UK) / s18 ACL (AU).
- **AHPRA (AU) s133:** advertising a regulated health service must not use **testimonials**, must not offer gifts/discounts, must not create unreasonable expectation of benefit. If any of the four templates auto-populates a reviews/testimonials slider or ships filler like "painless dentistry" or "best in town", the demo is a non-compliant health advertisement carrying the dentist's identity. Same exposure under GDC *Advertising Guidance* (UK) and state dental board rules (US).
- **Indexing:** a public duplicate of their homepage can be crawled and can compete with or be mistaken for the real site.

**Required before any send:**
1. `X-Robots-Tag: noindex, nofollow` + `robots.txt` disallow on every demo URL.
2. Demo URLs must be **unguessable and brand-free** — `demo.<milins-domain>/d/a7f3k9`, never `/smilebright-dental`.
3. Persistent on-page banner: *"Unofficial mock-up built by Milin {{sender_last_name}}, an independent developer. Not affiliated with or endorsed by {{practice}}. Removed on request: <email>."*
4. **Audit all four templates and strip every clinical claim, testimonial block, review widget, before/after image and "guarantee" from the demo layer.** Milin must not add a single word of clinical copy. Only the prospect's own text may appear.
5. One-email takedown, honoured same day.

### B6. UK GDPR Article 14 notice is missing entirely
`{{first_name}}` is enriched personal data obtained from a third party, not from the data subject. Article 14 requires a privacy notice **at the first communication**, identifying the controller, the legitimate-interests basis, **the source of the data**, retention period, and the right to object (Art 21). The footer has none of it. The PECR corporate-subscriber carve-out does **not** cover this — it's a separate obligation, and "the practice is a Ltd" doesn't stop `john@` being personal data about John.

**Fix — footer line for all UK/EU records:**
```
How I got your details and how to have them deleted: {{privacy_notice_url}}
```
The linked page must state the enrichment source by name, the LIA outcome, retention, and the Art 21/17 routes. Also run and file the Legitimate Interests Assessment before the first send — the ICO expects it to pre-exist, not to be written after a complaint.

---

## SHOULD-FIX

### S1. AU unsubscribe deadline is wrong in the sending notes
**Text:** `Unsubscribe must be honoured within 10 days (CAN-SPAM)`
Spam Act 2003 s18 requires AU unsubscribes honoured within **5 business days** — half the CAN-SPAM window. Set the system-wide SLA to 5 business days globally; UK/EU objections should be actioned immediately in practice.

### S2. AU inferred consent has an unchecked precondition
Inferred consent under Spam Act Sch.2 cl.4 requires the address to be **conspicuously published in connection with that person's role** *and* **not accompanied by a statement that they don't want unsolicited commercial email**. Many practice contact pages carry exactly such a notice. Nothing in the scanner checks for it.

**Fix:** add a scanner pass over the contact/privacy/legal pages for "no unsolicited", "no marketing", "do not contact", "no cold call/email". Any hit → drop the lead, all jurisdictions. Also prefer role addresses published on the site over enriched personal addresses for AU.

### S3. `"Last one from me"` must be enforceable, or it's a deceptive subject line
CAN-SPAM 16 CFR 316.3(a)(2) / s.16 Spam Act: the subject must not materially mislead. If a non-responder is later rotated into a different Milin campaign, "Last one from me" was false when sent.

**Fix:** either enforce permanent global suppression on Touch 3 send, or change to `Last one about booking` and keep the promise scoped.

### S4. The `reply "later"` mechanic is a suppression trap
**Text:** `If booking is a next-year thing rather than a this-month thing, reply "later" and I'll stop emailing you.`
The word "later" invites the system to treat it as *defer and re-add in 6 months*. The sentence promises "I'll stop." Under CAN-SPAM this is an opt-out request the moment it's received; under UK GDPR it's an Art 21 objection; under the Spam Act it's an unsubscribe. Re-adding them breaches all three.

**Fix:** map `later` → the same permanent global suppression as the unsubscribe link, no exceptions, and say so: `reply "later" and I'll take you off my list for good.` Note also that a reply-based opt-out never substitutes for the one-click link — keep both.

### S5. `demo_expiry_date` must be a real automated job
The doc already conditions this correctly; hardening it: if the deletion is manual, aspirational, or quietly reversible, both `Should I delete the demo?` and the expiry line are deceptive subject/body content (CAN-SPAM 316.3(a)(2)) and manufactured urgency (Rule 6). The date must be set at generation time by the same cron that deletes, and the URL must actually 404 on that date. If not: drop the line, drop subject #3, use `I'll leave the demo up either way` as specified.

### S6. Re-scan is only gated at segment entry, not per touch
Rule 3 covers list-build vs. send. But if the practice installs Calendly on day 2, Touch 2's `That's the whole reason I sent the demo` and Touch 3 both assert a fault that no longer exists.

**Fix:** re-run the booking scan before **every** touch. Any vendor match, blocked crawl, partial crawl or timeout → exit the sequence silently. Same standard as entry: no softening.

### S7. Header/from-line integrity is unspecified
CAN-SPAM 316.3(a)(1)/§7704(a)(1), Spam Act s17: From name, From domain and Reply-To must accurately identify the sender. Given Rule 8, add explicit constraints: no US/UK-implying brand in the sending domain or display name, no `.co.uk`/`.us` sending domain, no "Dental Web Partners"-style entity that doesn't exist. Display name = `Milin {{sender_last_name}}`. Reply-To must be a monitored mailbox — an unmonitored one undercuts the Touch 3 reply-based opt-out.

### S8. Footer address must be genuinely postal
`{{sender_street_address}}, Surat, Gujarat {{postcode}}, India` satisfies CAN-SPAM §7704(a)(5) only if mail actually reaches Milin there. Add a send-time validation that the field is populated and non-placeholder — a template that ships with an empty or dummy address is a per-email violation. A residential Surat address is fine; an unregistered PO box is not.

---

## PASSES — keep exactly as written

- `I'm Milin, a developer in Surat, India. Not local to you, not pretending to be.` — the single strongest line in the sequence, and it directly discharges Rule 8. Do not soften it or move it to the footer.
- `It's auto-generated, so it's rough in places.` — pre-empts the credibility failure and is honest.
- No clinical or medical claims anywhere in the email copy. **The email body is clean on dental-advertising rules — the exposure is entirely in the demo page (B5).**
- No legal threat, no compliance guarantee, no ADA/GDPR/WCAG-lawsuit framing anywhere. Clean.
- Price placement logic (none in T1, full in T2, none in T3) is sound and creates no legal issue.
- Single-offer discipline — omitting the care plan, migration and rescue offers is correct and also reduces claim surface.
- `{{fault_evidence}}` and `{{demo_url}}` having **no fallback, drop the lead** — this is the control that keeps Rule 1 enforceable. Never add a fallback.
- Drop-on-blocked-crawl rule. Correct and non-negotiable.
- `{{first_name}}` → `there`, never derived from the practice name. Extend: never guess `Dr {{last_name}}` from a domain either.

---

## Summary

| # | Severity | Issue |
|---|---|---|
| B1 | Blocker | "no way to book" is self-contradicting and false; page_count overstates |
| B2 | Blocker | Two unsubstantiated statistics + fear-sell in Touch 2 |
| B3 | Blocker | Unqualified "live in 48 hours" performance promise |
| B4 | Blocker | No advertisement disclosure (CAN-SPAM 316.3) |
| B5 | Blocker | Demo page: IP, noindex, AHPRA/GDC testimonial + clinical-claim exposure |
| B6 | Blocker | No UK GDPR Art 14 privacy notice or LIA |
| S1 | High | AU unsubscribe SLA is 5 business days, not 10 |
| S2 | High | AU inferred consent — unchecked "no unsolicited email" notices |
| S3 | High | "Last one from me" unenforced |
| S4 | High | `reply "later"` not mapped to permanent suppression |
| S5 | Med | Expiry claim must be a real automated deletion |
| S6 | Med | Re-scan only at entry, not per touch |
| S7 | Med | From/Reply-To integrity rules unspecified |
| S8 | Med | Postal address field needs send-time validation |

Nothing here requires abandoning the sequence. The structure, the honesty about being in India, and the drop-the-lead rules are better than most compliant agency email. The failures are concentrated in one false sentence (B1), one over-claiming statistic block (B2), and an entirely unmanaged demo-hosting surface (B5).