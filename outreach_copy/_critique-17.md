# LEGAL & ETHICS AUDIT — locked-platform 3-touch sequence

Verdict: **do not send as written.** Nothing here is fear-selling or fake-local — those rules are respected. The exposure is concentrated in three places: (1) an unsubstantiated commercial claim about five named third parties, (2) the demo site itself, which is a bigger legal object than the email, and (3) two missing statutory disclosures.

---

## BLOCKERS — sequence cannot send until resolved

### B1. `pitch_hook` asserts a fact about the vendor's commercial terms that no scan can produce

**Text:** `That's {{platform}}: a dental vendor platform sold as a monthly subscription rather than as a site you hold the files to.`

**Rule:** FTC Act §5 (deceptive/unsubstantiated advertising claim); UK Business Protection from Misleading Marketing Regs 2008 reg.3–4 (comparative advertising must be verifiable and must not discredit a competitor); Australian Consumer Law s18 (misleading or deceptive conduct). Also your own Hard Rule 1.

The scan produces a *build fingerprint*. A footer string proves who built the site. It does not prove the contract type, the billing model, or who holds the files — those vary by vendor, by reseller, by legacy contract, and some of these practices bought out or self-host. The claim is stated as fact about the recipient's specific arrangement and is not substantiable at send time.

**Corrected `pitch_hook`:**
```
{{platform_evidence}} — {{evidence_location}} {{domain}}. That's a {{platform}}-built
site. On most {{platform}} plans the design and code stay with the vendor, so it's
worth knowing which side of that your contract sits on.
```
Verifiable ("a {{platform}}-built site" = literally what the evidence shows), hedged ("most plans"), and hands the factual question back to them rather than asserting it.

### B2. The quoted ProSites clause is an unverified, undated, unattributed quote from a third party's contract

**Text:** `ProSites' own terms: "The Customer's website ... is the property of ProSites and the Customer has no rights to the website beyond the terms of its subscription."`

**Rule:** ACL s18 / FTC §5 / BPMMR 2008 reg.4(c) (must not discredit a competitor); trade libel if the clause is stale or misquoted. Terms of service change without notice, and enterprise or legacy customers frequently sit on a different paper.

Quoting a competitor's terms in a sales email is legal **only** if the quote is exact, current, attributed, and dated. Right now it is asserted with no source and no retrieval date, and it is being applied to a recipient whose contract you have never seen.

**Corrected:**
```
From ProSites' published terms of service (retrieved {{terms_retrieved_date}} —
{{terms_source_url}}):

"[verbatim clause]"

Your own contract may read differently — worth checking before renewal.
```
Operational gate: re-fetch and diff that clause **monthly**; auto-pause Variant A if the string no longer appears at the source URL. Do not send Variant A from cached copy.

### B3. The personalised demo is the largest legal object in this campaign and the email under-describes it

**Text:** `Concept only, not indexed, every page marked unaffiliated.`

Building a public page with the practice's **real logo, real brand colours, real name** and, presumably, their homepage copy touches four separate regimes:

- **Copyright.** The site text, layout and images are almost certainly owned by the vendor — the ProSites clause you quote in Touch 2 *says so in writing*. Reproducing them in your demo infringes the very party whose terms you're citing. You cannot quote that clause as proof of vendor ownership and simultaneously copy the material it covers.
- **Trademark / passing off.** Real logo + real brand colours on a live public URL is unauthorised mark use. "Marked unaffiliated" is a mitigation, not a defence, and it doesn't survive a screenshot shared out of context.
- **Personal data (UK/EU GDPR, AU Privacy Act).** Staff headshots, named dentists, any patient-facing imagery = personal data you have no lawful basis to republish. Patient before/after imagery would be special-category data. This is the single fastest route to a complaint that costs you real money.
- **Third-party licences.** Stock photography on their current site is licensed to *them* (or to the vendor), not to you, and not sublicensable.

**Required changes to the generator, not the copy:**
- Logo: yes (nominative use, arguably defensible). Photography, staff images, patient images, testimonials: **strip entirely**, substitute neutral placeholders.
- Body copy: paraphrase or use placeholder text. Do not lift the vendor's copy verbatim.
- Enforce `noindex,nofollow` **plus** `X-Robots-Tag` header **plus** `robots.txt` disallow **plus** no sitemap entry. The email states "not indexed" as fact; if one of those is missing that sentence becomes a false statement in a commercial email.
- Persistent visible banner above the fold, not a footer line: `Unofficial concept by Milin Dholiya. Not affiliated with, endorsed by, or connected to {{practice}}.`
- Auto-expire at 60 days; instant takedown endpoint; takedown honoured same-day on any request from the practice **or the vendor**.

**Corrected email line:**
```
Unofficial concept, blocked from search engines, my own placeholder photos,
banner on every page saying it isn't yours. Say the word and it's gone.
```

### B4. No advertisement identifier in any of the three emails

**Rule:** CAN-SPAM 15 U.S.C. §7704(a)(5)(A)(i) — a commercial message must contain clear and conspicuous identification that it *is* an advertisement or solicitation. There is no B2B carve-out. The Australian Spam Act likewise requires the message clearly identify the sender and the commercial nature.

None of the three touches says this. Touch 1 in particular reads as a personal note.

**Fix — add to the compliance footer, all three touches:**
```
This is an advertisement for web development services. You have not
worked with me before.
```
That second sentence also kills any "fake familiarity" reading, which your Hard Rule 6 already bans.

### B5. No Article 14 notice — you obtained these addresses from a third-party source, not from the recipient

**Rule:** UK GDPR Art.14 (data not obtained from the data subject: you must disclose identity, purposes, legal basis, **the source of the data**, retention, and the right to object — within one month or at first communication, whichever is first). Australian Privacy Act APP 5 imposes a materially similar notification duty.

First communication *is* Touch 1. The notice is due then, and it is absent.

**Fix — compliance footer:**
```
I found this address published on {{source_url}}. Legal basis: legitimate
interest in B2B outreach. I hold your practice name, public email and a
technical scan of your public homepage; deleted on request or after 12
months. Object or erase: {{privacy_url}}
```

---

## FIX BEFORE SEND

### F1. `"once"` is a material-omission risk if the migration requires ongoing spend

**Text:** `Moving off it is {{price_band}}, once.` / `rebuilding it as yours is {{price_band}}, once.`

**Rule:** FTC §5 (deceptive omission of a material cost); UK CPUTR 2008 reg.6 (misleading omission); ACL s18.

"Once" is an affirmative representation of total cost. If the rebuilt site *needs* hosting, a domain, or an SSL cert to stay live, the true cost is not once. You've deliberately withheld the $149/mo care plan — that's a fine sales decision **if** the plan is genuinely optional. It is not fine if the site doesn't function without it.

**Corrected:** `Moving off it is {{price_band}}, one time. You'd host it yourself after that — around $X a year, your account not mine.`

If hosting truly is optional and self-serve, that wording is honest and actually strengthens the ownership pitch.

### F2. Touch 2 presumes a renewal date you don't have

**Text:** `Two questions worth putting to {{platform}} before your renewal date:` and subject `Before your next renewal`

Minor Hard Rule 1 violation — you don't know they have one, or when. Also the closest thing in the sequence to manufactured urgency.

**Corrected:** `Two questions worth putting to {{platform}} whenever you next renew:` Subject → `Two questions for your web vendor` (drops the vendor trademark from the subject line, which also helps deliverability).

### F3. Vendor trademarks in subject lines

**Text:** `One line from ProSites' own terms` / `The {{platform}} line on your site`

Not a CAN-SPAM deception issue — they're accurate. But a competitor's mark in a subject line plus a sender they don't recognise is the classic implied-affiliation pattern, and it is the highest-complaint-risk configuration in the set. Prefer `Who owns your website files` and `Your website's build fingerprint`. **Hard rule:** the platform name must never appear in the From name, the display name, or the sending domain.

### F4. `"something you'd own outright"` overstates what you can convey

You cannot convey what you don't hold — stock image licences, any retained vendor content, third-party fonts and plugins.

**Corrected:** `So I rebuilt your homepage as something you'd hold the files and code for.` And ship an actual written IP assignment at contract stage; the claim is only true if paper backs it.

### F5. Australia — inferred consent needs an explicit gate, not an assumption

**Rule:** Spam Act 2003 s16 + Sch.2. Inferred consent exists for a **conspicuously published** work address where the message is **directly relevant** to that person's role — **and** where the publication carries no statement that unsolicited commercial email is unwanted.

That last condition is the one campaigns fail. It requires the scanner to check the actual page where the address was published.

**Add to the merge table as a hard gate for AU leads:**
- `{{source_url}}` — the exact page the address was published on. Required.
- `{{no_spam_notice_found}}` — boolean from scanning that page for "no unsolicited", "no marketing emails", "not for solicitation" and similar. **If true, suppress the lead.**
- Role relevance: address must belong to the practice/admin, not a named clinician's personal address.
- Unsubscribe must be honoured within 5 business days (your "same day" clears this).

### F6. UK — "tighter consent handling" is not a policy

Your operational note correctly spots the PECR sole-trader problem but doesn't resolve it. PECR reg.22 treats sole traders and unincorporated partnerships as **individual subscribers**: unsolicited marketing email requires **prior consent**. Soft opt-in doesn't apply — they've never bought from you.

There is no version of "tighter handling" that makes an unconsented send to a UK sole-trader practice lawful.

**Decision, wire it as a branch:** check Companies House for a registered company matching the practice. Limited company / LLP → send under legitimate interests with a documented LIA. No match, or unresolvable → **suppress**. Expect this to remove a meaningful share of the 1,681.

---

## ADVISORY

**A1 — AHPRA is the sleeper risk on the demo, not the email.** Australian National Law s133 prohibits advertising a regulated health service using testimonials, and prohibits misleading or unreasonable-expectation claims. Liability attaches to *whoever advertises*. A live public page carrying an Australian dental practice's name, testimonials and before/after images is an advertisement — published by you. UK GDC guidance and the CAP Code cover similar ground. Your generator must strip testimonials, before/after imagery, and superlatives ("best", "painless", "leading", "#1") from **every** demo, and the AU/UK demos should sit behind a one-time access token rather than a guessable public URL.

**A2 — The email body makes zero clinical claims.** Correct as written. Do not let future variants reference patient volume, bookings, new-patient numbers, or "more patients" — that converts a web-services pitch into a health-services advertising claim and pulls the whole sequence under AHPRA/GDC.

**A3 — Scan freshness.** Footer strings go stale. A practice that migrated three months ago receives an email confidently describing a platform it no longer uses — an unsubstantiated claim under Hard Rule 1, and an instant credibility loss. Gate: scan must be ≤7 days old at send, re-verified at queue time.

**A4 — Address provenance.** CAN-SPAM §7704(b) treats harvesting and dictionary attacks as aggravated violations with enhanced penalties. Every address must be traceable to a specific published page on the practice's own site, stored in `{{source_url}}`, which F5 and B5 both need anyway. No pattern-guessed addresses (`info@`, `contact@` constructed rather than observed). No purchased or scraped-aggregator lists.

**A5 — Unsubscribe durability.** CAN-SPAM requires the mechanism stay functional for **at least 30 days** after send. Your link is one-click and login-free — good — but it must outlive the campaign infrastructure. Suppression list is permanent and global across all segments, not per-campaign.

**A6 — Touch 2 has no demo link but Touch 3 does.** Intentional and fine. Just confirm the Touch 3 demo URL still resolves at day 7 given the B3 auto-expiry — a dead link in a breakup email is a bad last impression and makes "the demo stays up either way" false.

---

## Already correct — keep

- No legal threat, no compliance guarantee, no "you could be sued", no implied liability. Clean across all three touches.
- No fear-selling. `If not, ignore this` and `Otherwise I'll leave you to it` are genuinely respectful exits and are rarer than they should be in this category.
- Identity is honest: `Milin Dholiya · Surat, Gujarat, India` in every footer, no fabricated local presence, no Anglicised alias. This is both the ethically right call and the legally safe one.
- One-click, no-login, no-reply unsubscribe with same-day cross-touch suppression exceeds CAN-SPAM's 10-business-day floor and clears the Spam Act's 5-day floor.
- Postal address present as a required, send-blocking field. Confirm it's a real deliverable street address or a CMRA-registered box, and that it is **identical** across all three touches.
- No deadline on the demo, no fake expiry. Correct read of the audience.

---

## Revised compliance footer (all three touches)

```
—
This is an advertisement for web development services. We have not worked
together before.

Milin Dholiya · independent web developer · Surat, Gujarat, India
{{postal_address}}

I found this address published at {{source_url}}. Legal basis: legitimate
interest in B2B outreach. I hold your practice name, public email address
and a technical scan of your public homepage — deleted on request, or
after 12 months. Details and erasure: {{privacy_url}}

Don't want these? {{unsubscribe_url}} — one click, no reply needed.
```

Longer than you'd like. B4 and B5 are statutory and cannot be compressed away; footers aren't read anyway, so the cost lands on nothing you were relying on.

---

## New send-blocking merge fields

| Field | Purpose | Blocks |
|---|---|---|
| `{{source_url}}` | Page the address was published on | B5, F5, A4 — all sends |
| `{{privacy_url}}` | Art.14 / APP 5 notice | All sends |
| `{{no_spam_notice_found}}` | Scanned from `source_url` | AU sends if true |
| `{{uk_entity_type}}` | Companies House match | UK sends if not company/LLP |
| `{{terms_retrieved_date}}` + `{{terms_source_url}}` | ProSites quote provenance | Touch 2 Variant A |
| `{{scan_age_days}}` | Freshness | All sends if >7 |