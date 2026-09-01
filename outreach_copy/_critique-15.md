# LEGAL & ETHICS AUDIT — `broken-site` 3-touch sequence

Jurisdictions audited: CAN-SPAM Act + FTC Act §5 (US), PECR reg. 22 + UK GDPR + CAP/ASA + GDC (UK), Spam Act 2003 + Australian Consumer Law + AHPRA/National Law s133 (AU). Severity: **BLOCKER** = do not send until fixed · **HIGH** = fix this week · **MEDIUM** · **NOTE**.

---

## BLOCKERS

### B1 — No advertisement disclosure in any of the three touches
**Rule:** CAN-SPAM 15 U.S.C. §7704(a)(5)(A)(i) — a commercial message sent without the recipient's affirmative consent must contain "clear and conspicuous identification that the message is an advertisement or solicitation." Cold prospecting = no consent, so this applies to all three touches. Australian Spam Act s17 separately requires sender identification in every message. Presence of a postal address and unsubscribe does *not* satisfy the ad-disclosure element; it is a distinct requirement and the most commonly missed one.

**Text:** all three footers. Touch 1 has `Milin Dholiya — web developer, Surat, India`, touches 2 and 3 have only `Milin`.

**Corrected footer, identical in all three touches:**
```
Milin Dholiya — web developer, Surat, India.
This is a cold sales email. I found {{domain}} on a public listing
and scanned it; you never gave me your address.
{{postal_address}} · Unsubscribe (one click, honoured in 24h): {{unsubscribe_url}}
How I got your address & what I store: {{privacy_url}}
```
The plain-English admission also does the ethical work Rule 8 is reaching for.

---

### B2 — The demo site itself is the largest unaddressed legal exposure, and the doc never mentions it
The sequence is audited to death; the artefact it links to is not audited at all. `{{demo_url}}` is described as carrying "real logo, real brand colours, real business name," publicly reachable, on the sender's domain.

**Exposures:**
- **Copyright** — reproducing their logo, photography and body copy on a third-party server is infringement in all three jurisdictions. A footer disclaimer is not a licence and does not cure it.
- **Trademark / passing off** (UK) / **s18 misleading conduct** (AU ACL) — a live public page presenting itself as the practice's homepage under the practice's marks.
- **Health advertising law** — if the generator scrapes their existing homepage, it may reproduce patient testimonials, reviews or before/after imagery onto a page *the practice did not authorise and cannot control*. Testimonials in health-service advertising are prohibited outright by National Law s133 (AU); UK GDC/CAP rules restrict before/after and outcome claims. You would be publishing an unlawful health advertisement in the practice's name. This is worse for them than the broken site.

**Required before any send:**
1. Demo pages use **placeholder/neutral copy only** — no testimonials, no reviews, no before/after images, no clinical or outcome claims, no pricing, no practitioner names/credentials.
2. Logo used at most once, small, or replaced with a wordmark in their brand colours. Photography must be your own stock, never theirs.
3. Enforce "not indexed" for real: `X-Robots-Tag: noindex, nofollow` header **and** meta noindex **and** `robots.txt` disallow **and** excluded from sitemap. Claiming "not indexed" while relying on meta alone is a claim you may not be able to stand behind.
4. Persistent visible on-page banner, not a footer: *"Unofficial concept demo built by Milin Dholiya (Surat, India). Not affiliated with, endorsed by, or operated by {{practice}}. Contact: [address] — say the word and this comes down."*
5. One-click takedown honoured same day, and takedown on any reply including "not interested."

---

### B3 — `www.{{domain}}` renders as `www.www.example.com`
**Text:** merge table — *"Keep `www.` only when the www host is the fault"* — combined with the `dns_www_nxdomain` hook, *"`www.{{domain}} returned NXDOMAIN`"*. For exactly the fault type where the rule says to keep the `www.`, the hook prepends a second one.

A malformed hostname in an email whose entire credibility rests on evidence accuracy destroys the segment. **Fix:** `{{domain}}` is always the bare registrable host, no exceptions; the hook supplies the `www.` prefix itself. Delete the conditional from the merge table.

---

### B4 — Nested merge field breaks touch 3 grammar for `http_5xx`
**Text:** touch 3 — *"If {{fault_label}} is still there next month"* with `fault_label = site returning {{status_code}}` renders: *"If site returning 503 is still there next month, this address still works."*

Two defects: a merge field inside a merge field (many ESPs will not resolve the inner one and will ship the literal `{{status_code}}`), and broken English in the final impression email.

**Fix:** add a dedicated `{{fault_noun}}` field — `the www record`, `the certificate`, `the 503s`, `the missing images` — and reword: *"If {{fault_noun}} is still an issue next month, this address still works."*

---

### B5 — Blank `{{salutation}}` renders a naked comma
**Text:** `{{salutation}},` — the fallback rule says "omit the greeting line entirely," but the comma is static text outside the field. Blank renders a line containing only `,`.

**Fix:** the comma lives inside the merge field (`Dr. Reyes,`), and the fallback is empty string with the blank line suppressed.

---

## HIGH

### H1 — "nothing else attached" is contradicted by the documented plan
**Text:** touch 2 — *"I'll do it today — $299 flat, nothing else attached."*
Against: *"the upsell happens after the fix is paid and delivered."*

The reader parses "nothing else attached" as "no follow-on sales." The plan is a follow-on sale. That is a misleading representation about the service (FTC Act §5; CPUTR 2008 reg. 5, UK; ACL s18/s29(1)(m), AU) and it is plainly dishonest even where legal.

**Corrected:** *"I'll do it today — $299 flat, one-off, no subscription, no contract."* True, keeps the convenience frame, and leaves the post-delivery conversation honest.

---

### H2 — "I can do it today" is an unqualified capability claim you cannot honour for `http_5xx`
**Text:** touch 1 — *"Fixing that is {{fix_scope}}, not a rebuild. I can do it today."* For `fault_type = http_5xx`, `fix_scope = a server config fix` — and your own touch-2 instruction concedes it may be host-side PHP memory or a plugin, i.e. something you may have no access to. Same problem for `images_404` where the media is genuinely gone and unrecoverable.

Unsubstantiated performance claim: FTC substantiation doctrine; ACL s29(1)(b)/(m); CPUTR reg. 5.

**Corrected, `http_5xx` and `images_404` variant of the line:**
*"That's usually {{fix_scope}}, not a rebuild. I'll look today — and if it turns out to be something only your host can change, I'll tell you that and you pay nothing."*

Add a stated scope boundary to the offer: *emergency site rescue, $299 flat, refunded in full if the fault is outside what I can reach.*

---

### H3 — Four substantiation overreaches inside `pitch_hook`
Rule 1 says every claim must come from a real scan finding. Each of these asserts more than the scan observed.

| # | Quoted text | Problem | Corrected |
|---|---|---|---|
| a | `ssl_expired` — *"Chrome and Safari now show a full-page \"Not secure\" warning before the site loads"* | Factually wrong. "Not secure" is the omnibox label for plain HTTP. An expired cert produces `NET::ERR_CERT_DATE_INVALID` — *"Your connection is not private."* Also untrue for visitors if the site never redirects to HTTPS. | *"The SSL certificate on {{domain}} expired on {{expiry_date}}, so anyone arriving on the https version gets a full-page \"Your connection is not private\" warning before the site loads."* Gate the send on an observed HTTP→HTTPS redirect or HSTS. |
| b | `http_5xx` — *"so the site was unreachable for part of each of those days"* | N failures across M checks over a date range does not establish failure on *each* day. Scanner cannot know this. | *"so the site failed to load on {{fail_count}} of those checks."* Drop "each of those days" entirely. |
| c | `images_404` — *"so the hero photo and {{second_area}} load as empty boxes"* | Rendering claim the HTTP scan never made. Lazy-loading, CSS background fallbacks and placeholders mean "empty boxes" may be false. | *"so those images don't load for visitors."* Or capture an actual screenshot and then the claim is substantiated. |
| d | `dns_www_nxdomain` — *"the version without www works fine"* | A separate positive assertion about their site. Requires its own verified 200 on the apex in the same scan. | Keep the wording, but make apex-200 a hard gate: no apex 200, no send. |

Also required for (d): NXDOMAIN must be confirmed on **two independent resolvers from two geographies** before it is stated as fact. A single resolver failure, DNSSEC hiccup or your own network path is not their outage — and that is precisely the "unrecoverable" false email the doc opens by warning against.

---

### H4 — "I won't email again" conflicts with a five-segment machine
**Text:** touch 3 — *"Last one from me — I won't email again."*

If the lead can be re-enrolled into any of the other four segments, or re-scanned into `broken-site` in 90 days, this becomes a false statement to someone who did not opt out. Under CAN-SPAM an unsubscribe was not requested here, so continued mail is legal — but the sentence makes it a lie, and it is exactly the kind of lie a cynical clinician screenshots.

**Fix — pick one and enforce it in the CRM:**
- Honour it: touch 3 writes the address to a **global** suppression list across all five segments, permanently. Keep the sentence.
- Or reword: *"Last one from me on this."*

---

### H5 — No UK GDPR Article 14 notice; PECR analysis is incomplete
**Text:** the COMPLIANCE section addresses PECR consent for sole traders and stops there.

Two gaps:
1. PECR reg. 22's corporate-subscriber position governs *consent to send*. It does not displace **UK GDPR**, which applies whenever the address or the record is personal data — `dr.reyes@practice.com`, a named surname in `{{salutation}}`, a scan tied to a named individual. You need a documented lawful basis (legitimate interests + a completed LIA), and **Article 14** requires you to tell the data subject, at first contact, that you obtained their data from a third-party source, what you hold, why, and their right to object. Nothing in the copy does this.
2. Same obligation, in substance, under Australian Privacy Act APP 5 for the AU list.

**Fix:** the `{{privacy_url}}` line in B1's footer, pointing at a real page that states the source ("public practice listings and your own website"), the lawful basis, retention, and a working objection/erasure address. Complete and file an LIA before the first UK send.

---

### H6 — AU inferred consent requires a check the scanner does not perform
**Text:** *"A published practice email plus a fault on that practice's own site is a defensible basis."*

Broadly right, but Spam Act Sch. 2 cl. 4 removes inferred consent where the address is published **with a conspicuous statement that unsolicited commercial email is not wanted**. Many clinic contact pages carry exactly that line.

**Fix:** the scraper must scan the page the address was published on for that statement and hard-suppress on a hit. Also record, per AU lead, the **URL the address was published at and the capture date** — that record is your entire defence and it is not in the merge-field list.

---

## MEDIUM

### M1 — "Closing your file" is a deceptive subject line
**Text:** touch 3, subject option 1. **Rule:** CAN-SPAM §7704(a)(2) — subject must not be likely to mislead about the contents. There is no file, no account, no prior relationship; it borrows the register of an existing supplier. Options 2 and 3 are honest.

**Fix:** delete option 1. Use *"Last one from me"* or *"Leaving this here."*

---

### M2 — "Still showing on {{recheck_date}}" can ship as a false statement
**Text:** touch 2. `{{recheck_date}}` is defined as "date of the day-3 re-scan," which is not necessarily the send date. Any queue delay, throttle (you cap at 6/inbox/day), or timezone rollover makes the sentence assert a fault status you did not verify that day.

**Fix:** `{{recheck_date}}` is stamped at send time by the pre-send verification, not by the day-3 job; the same 6-hour re-verification window mandated for touch 1 applies to touches 2 and 3. Hold the send if the check is stale.

---

### M3 — Touches 2 and 3 drop the "unaffiliated" disclaimer, and touch 3 still carries the demo link
**Text:** touch 1 footer carries *"Concept demo, not indexed, unaffiliated with {{practice}}"*; touch 3 contains `{{demo_url}}` with no such line.

**Fix:** wherever `{{demo_url}}` appears, the disclaimer appears with it. Touch 3 becomes:
```
The demo stays up two more weeks: {{demo_url}}
(Concept demo — not indexed, not affiliated with {{practice}}.)
```

---

### M4 — Unsubscribe mechanics under-specified for the "one-click" claim
**Text:** *"Working one-click unsubscribe plus a `List-Unsubscribe` header."*

**Fix:** specify RFC 8058 — `List-Unsubscribe: <https://…>, <mailto:…>` **plus** `List-Unsubscribe-Post: List-Unsubscribe=One-Click`, with the endpoint accepting POST. A GET-only link will be fired by security scanners and mail-client prefetchers, silently unsubscribing engaged leads. The landing page must complete the opt-out with no login, no preference centre, no "are you sure," and no re-entry of the address.

---

### M5 — "the two things I need from you" invites credential sharing
**Text:** touch 1 CTA. Fixing DNS or SSL means the reply will often contain registrar or host **passwords**, sent in plaintext by a clinician, to a stranger overseas — a security and (given what else sits on a practice's infrastructure) a data-protection problem for both parties.

**Fix:** pre-empt it in the reply template, and consider naming it in touch 1: *"Reply \"fix it\" and I'll send the two things I need — read-only details or a delegated invite. Please don't email me passwords."*

---

## NOTES

- **N1 — Scanning conduct.** Rate-limit the scanner, set an identifying User-Agent with a contact URL, and honour `robots.txt`. Repeatedly polling a host that is already returning 5xx is both bad manners and the fact pattern you would least want to explain.
- **N2 — Two-week demo takedown** is asserted in touch 3. Automate the expiry job; do not leave it to intent. Same for takedown-on-request and takedown-on-any-reply.
- **N3 — Sender identity.** The From display name should be `Milin Dholiya` on all three touches, on one sending domain, with a real Indian-registered footer. Do not vary the from-name or use an initials-only alias — CAN-SPAM §7704(a)(1) covers materially misleading header information, and consistency also protects the "honesty converts" premise the brief is built on.
- **N4 — Clinical claims:** the email copy itself is clean. Zero clinical or health-outcome language, no fear-selling, blocklist is well constructed and the "give the fix away in touch 2" structure is genuinely ethical. All medical-advertising exposure in this sequence lives on the demo page, not in the email — see B2.
- **N5 — Fear-selling check:** passes. The one residual pressure word is the internal offer name "emergency site rescue" — it never appears in recipient-facing copy, and should stay that way.

---

## SEND GATE — do not release until all true

1. B1 ad-disclosure footer live on all three touches · 2. B2 demo pages stripped of testimonials/before-after/clinical claims, banner live, noindex enforced four ways, takedown automated · 3. B3/B4/B5 merge bugs fixed and rendered against all four `fault_type` values with a blank `{{salutation}}` · 4. H1 and H2 wording replaced · 5. H3 hooks regenerated, apex-200 and two-resolver gates live · 6. H4 decided and enforced in the CRM · 7. `{{privacy_url}}` page published, LIA filed, UK company-status check running per lead · 8. H6 no-unsolicited-email scan + published-source URL recorded per AU lead · 9. M4 RFC 8058 one-click verified end to end · 10. Pre-send fault re-verification within 6 hours applied to **all three** touches, with `{{demo_url}}` 200-check.