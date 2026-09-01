# LEGAL & ETHICS AUDIT — `no-website` 3-touch sequence

**Verdict: DO NOT SHIP AS WRITTEN.** The copy itself is unusually clean — no fear-selling, no legal threats, no clinical claims, honest sender identity. But three things make it non-compliant at send time, and one of them (the substantiation gap) is the exact failure mode the brief was written to prevent.

Severity: **BLOCKER** = illegal or provably false. **HIGH** = real enforcement/liability exposure. **MED** = dishonest-but-legal, or jurisdiction-specific.

---

## BLOCKERS

### B1. The core factual claim is not actually substantiated by the scanner — Hard Rule 1 violated in code

The sequence specifies four emit rules (GBP website field null, IG bio link empty/not-owned, no registered domain, no owned site in top 10). **None of them are implemented.** In `C:\Users\Promise\Desktop\outreach\scanner.py` line 916:

```python
if not raw:                      # raw = row["Website"], the CRM column
    result["faults"] = [
        {"code": "NO_WEBSITE", "severity": "critical",
         "evidence": "Instagram bio has no website link at all"},
```

`NO_WEBSITE` fires on **one** signal: an empty CSV column. That is emit rule #2 only, and only half of it. Rules #1, #3 and #4 do not exist anywhere in the file. The scanner then generates the line *"You have no real website, so when someone in your area googles 'dentist near me' there is simply nothing of yours for Google to show"* (line 1100) — a categorical claim about a business, derived from a blank spreadsheet cell.

- **Rule:** CAN-SPAM 15 U.S.C. §7704(a)(2) (deceptive subject headings) and FTC Act §5; AU Spam Act 2003 s17 + ACL s18 (misleading or deceptive conduct); UK CPUTR 2008 reg 5. Plus the brief's own Hard Rule 1.
- **Real-world failure:** a practice with a perfectly good site that simply never put it in their IG bio receives the subject line `no website for Riverbend Family Dental`. That is a false statement about their business, in the subject line, at scale.
- **Fix:** implement rules 1, 3 and 4 as hard gates before this segment can send, *or* change the claim to what the scan actually proves. The narrow, defensible version:

  > `I looked up {{practice}} in {{city}} — your Instagram comes up, but there's no link in the bio, so I couldn't find a site from there.`

  That is true from the one signal you have. `there's no website behind either` and the subject `no website for {{practice}}` must not ship until rules 1/3/4 exist.

### B2. `{{unsubscribe_url}}` is a merge field with nothing behind it

There is no unsubscribe endpoint, no `List-Unsubscribe` header, and no suppression write-path anywhere in the send pipeline. `send_smtp_email()` in `C:\Users\Promise\Desktop\outreach\campaign_manager.py:260` builds the entire message as:

```python
msg['From'] = account['email']
msg['To'] = to_email
msg['Subject'] = subject
msg.attach(MIMEText(body, 'plain'))
```

No headers, no footer injection. The only opt-out handling that exists is `check_replies.py:55`, which keyword-scans replies for "unsubscribe"/"remove me"/"stop" — reactive, manual, and only if someone runs the script.

- **Rule:** CAN-SPAM §7704(a)(3) — a functioning opt-out mechanism that works for **at least 30 days** after send. AU Spam Act s18 — functional unsubscribe honoured within **5 business days** (the compliance notes say 10 days; that is the CAN-SPAM number and is wrong for Australia). PECR reg 22(3). Plus RFC 8058 one-click (`List-Unsubscribe-Post: List-Unsubscribe=One-Click`) for Gmail/Yahoo bulk-sender rules.
- **Fix:** a static endpoint (`/u/<token>`) that appends to `SUPPRESSION_LIST.txt` on GET, plus both headers set in `send_smtp_email`. `campaign_manager.py` already reads `SUPPRESSION_FILE` — wire the endpoint to that file and the loop closes. Until that exists, the footer line is a lie.

### B3. `{{sender_postal_address}}` likewise does not exist in the pipeline

No template in `campaign_manager.py` contains a postal address, and there is no config value for one.

- **Rule:** CAN-SPAM §7704(a)(5)(A)(iii) — valid physical postal address of the sender, on **every** commercial message. Non-US senders are not exempt; the address may be Indian, it must be real and current.
- **Fix:** hardcode the real Surat street address (or a genuine PO box) into the footer builder, not into a merge field that can render empty.

### B4. Missing advertisement identification

None of the three touches state that the message is a solicitation. Touch 1 in particular reads as a gift.

- **Rule:** CAN-SPAM §7704(a)(5)(A)(i) — clear and conspicuous identification that the message is an advertisement or solicitation, required for every message sent without prior affirmative consent. Cold email has no consent, so this is always required. It is the single most commonly missed CAN-SPAM element.
- **Current text:** `So I built one. Your photos, your name, your logo, live right now: {{demo_url}}`
- **Fix:** one clause, and it also reads as honest rather than legalistic:

  > `I'm a web developer and yes, this is a sales email.`

### B5. Touch 3's takedown line — no takedown mechanism exists

`The demo comes down {{takedown_date}}; I pay for the hosting so I don't keep dead ones up.`

The brief already flags this conditionally. Resolving the condition: there is **no** expiry, cron, or deletion job in the repo. The only reference is `PLAYBOOK.md:1438` — "takedown = delete one folder" — a manual note.

- **Rule:** UK CPUTR 2008 **Schedule 1 paragraph 7** — "falsely stating that a product will only be available for a very limited time... in order to elicit an immediate decision" is a **banned practice per se**, no consumer-detriment test required. AU ACL s18. CAN-SPAM deceptive-content.
- **Fix:** cut the line entirely unless a scheduled job actually deletes the folder on `{{takedown_date}}`. Replacement: `This is the last one from me.`

---

## HIGH — the demo site itself is the bigger liability than the email

The audit brief asked about the copy; the copy points at a live URL that republishes a third party's brand. That URL carries more exposure than anything in the email body.

### H1. `Your photos, your name, your logo` — unlicensed republication

Building a public site from a practice's Instagram photos and logo, under their trading name, without permission:

- **Copyright:** photos are theirs (or their photographer's). Public hosting is reproduction + communication to the public. DMCA takedown and statutory damages exposure in the US.
- **Trademark / passing off:** a live site using their name and logo that they did not authorise can constitute passing off (UK/AU) and false designation of origin (US Lanham Act §43(a)) if a patient could land on it.
- **Instagram Platform Terms:** scraping and republishing media is a straight breach.

**Fix — all three required:**
1. `<meta name="robots" content="noindex,nofollow">` plus `X-Robots-Tag` on every demo, and a `Disallow: /` robots.txt. It must be unreachable by search.
2. A persistent, non-dismissible banner: *"Unofficial demo built by Milin Dholiya. Not affiliated with or authorised by {{practice}}."*
3. Honour deletion on request immediately — Touch 1 already promises this (`say so and I'll delete it`); it must be true, and it must also register as an opt-out, not just a file deletion.

### H2. Patient images — special-category data, and possibly the practice's regulatory problem

If the image scraper pulls **any** photo containing a patient — and dental Instagram is roughly half before/after shots — then:

- **UK GDPR Art. 9 / Aus Privacy Act APP 3:** clinical before/after images are health data about an identifiable person. Milin has no lawful basis and no Art. 9 condition. This is not a grey area.
- **AHPRA (Australia), National Law s133:** advertising a regulated health service must not use **testimonials**, and before/after images are heavily restricted. If the demo scrapes their Google reviews or IG testimonial posts into a "what patients say" section, the *dentist* is the one exposed if it ever goes live in their name.
- **GDC (UK) advertising guidance / ASA CAP:** "painless", "best", "guaranteed" and unmoderated before/after imagery all breach it.

**Fix:** image allowlist — logo, exterior, interior, and staff-with-consent only. Any photo the classifier is not confident is patient-free gets dropped. For AU and UK leads, strip reviews/testimonials from the generated template entirely. This is also a sales argument, not just a compliance one.

### H3. 19 rotating consumer Gmail accounts — the highest-severity item in the whole system

`C:\Users\Promise\Desktop\outreach\email_accounts.txt` lists 19+ accounts (`milindholiya01@…` through `dholiyamilin10@…`) sending one identical commercial campaign to a 29,931-address list.

- **18 U.S.C. §1037(a)(4)** makes it a federal criminal offence to falsely represent oneself as the registrant of **five or more** email accounts and intentionally initiate transmission of multiple commercial emails from them. Whether Milin crosses that line depends on whether the registration details are accurate — but the pattern (numbered accounts, rotated to spread volume) is textbook snowshoeing and is exactly what §1037 was written for.
- **CAN-SPAM §7704(b)** treats account-multiplication as an aggravated violation.
- Practically: Gmail ToS prohibits this outright. Terminated accounts cannot receive opt-outs — which converts a ToS problem into a §7704(a)(3) violation, because the opt-out mechanism must remain functional for 30 days.
- Consumer Gmail also cannot properly serve RFC 8058 one-click unsubscribe.

**Fix:** one owned sending domain (or two or three, openly registered to him), SPF/DKIM/DMARC aligned, real business identity. Fewer sends, deliverable, legal.

### H4. `"you own the files"` and `"No monthly fee"` — substantiation gaps in the offer

Touch 2: `is $495 once. No monthly fee, no contract, and you own the files.`

- `your own domain` sits inside a "no monthly fee" sentence. A domain has an annual renewal. If the buyer discovers a recurring cost they were told didn't exist, that is a **misleading omission** — FTC Act §5, UK CPUTR reg 6, ACL s18. Also hosting: who pays for it in month two?
- `you own the files` is only true if every asset in the template is licensable to a client — fonts, stock imagery, theme licence. Worth noting that this project's own prospect research (`dental-prospects.md:89`) found a target running an **expired unlicensed theme banner**. If the 4 templates carry any asset Milin can't sublicense, this sentence is false.
- **No currency stated.** `$495` to an Australian reader defaults to AUD. **ACL s48** requires the single total price, inclusive of GST where applicable, stated prominently.

**Fix:**

> `US$495 one time — your own domain, your hours, a contact form to your inbox. No monthly fee to me. Domain renewal runs about $15/year, paid to the registrar, in your name. All files are yours.`

Use a per-country `{{price}}` field: `US$495` / `£395` / `A$749 inc GST`.

### H5. US contact form + HIPAA

`a contact form that emails you` — for a US practice (a HIPAA covered entity), if the form routes through Milin's server or a third-party form service he controls, and a patient types anything clinical into it, he is a **business associate** handling PHI without a BAA.

**Fix:** form posts directly to their mailbox via a service *they* contract; no free-text symptom field; a line on the form saying "please don't include medical details". Or sign a BAA — but at $495 that is not the right trade.

---

## MEDIUM — corrections to the compliance notes as written

### M1. The UK guidance is under-inclusive

> *"For UK leads, send only to practice/role addresses (info@, reception@, the practice domain), not to a personal-looking address at a free provider."*

The free-provider distinction is not the operative test. **PECR reg 22 turns on whether the subscriber is an individual** — and a sole-trader dentist or a partnership **is** an individual subscriber even at `info@thepractice.co.uk`. Meanwhile **UK GDPR applies independently** to any address that identifies a person, including `drsmith@practice.co.uk` at a corporate domain.

**Fix:** gate UK sends on *entity type* (Companies House / LLP = corporate subscriber, PECR B2B exemption available; sole trader or partnership = suppress), not on mailbox prefix.

### M2. Missing UK GDPR Article 14 notice

Data was scraped, not given by the data subject. **Art. 14** therefore requires telling them what you hold, where it came from, the lawful basis, and how to object — within one month of obtaining it. Nothing in the sequence does this, and it is a routine ICO complaint trigger.

**Fix:** one footer line, which doubles as a trust signal:

> `Where I got your details and how to remove them: {{privacy_url}}`

### M3. Australian inferred consent is weaker than the notes assume

The notes cover s17 sender identification but not **consent**, which is the operative test. Inferred consent under Schedule 2 requires the address to be **conspicuously published** in a business capacity, **not** accompanied by a "no unsolicited commercial email" statement, **and** the message must be relevant to the role of the address holder. A website pitch into a `bookings@` mailbox published for patient enquiries is a thin case; ACMA has issued penalties on precisely this fact pattern.

**Fix:** for AU leads, require the address to come from a page where it is published for general business contact, check for a no-unsolicited statement, and record the source URL per lead. If you can't record where you got it, drop the lead.

### M4. Touch 3 `reply "yes" and it's yours for $495`

This invites contract formation by a one-word reply, before scope, timeline, or revisions are agreed. Any later addition reads as bait.

**Fix:** `reply "yes" and I'll send the scope and an invoice.`

### M5. Subject line 2, `I built you a website`

Marginal. It implies commissioned work for an existing client. Not deceptive enough to be a §7704(a)(2) violation, but it is the one subject in the set that manufactures a relationship — the thing Rule 6 prohibits.

**Fix:** `I built a demo of {{practice}}'s site` or use subject 3, `your Instagram, as a website`, which is accurate and the strongest of the three anyway.

---

## Passes clean

- **No implied legal threat, no compliance guarantee, no promised legal outcome.** Correct throughout.
- **No clinical claims.** The email copy makes none. (The generated *site* is where dental advertising rules bite — see H2.)
- **No fear-selling.** Genuinely absent. No "you're losing patients", no invented urgency (except B5, which is flagged conditionally in the brief itself). This is the ethically strongest part of the sequence.
- **Sender identity is honest.** `Milin — web developer, Surat, India` satisfies AU Spam Act s17 and Rule 8. No fake locality, no fake name, no claimed local office. Recommend adding the surname — `Milin Dholiya` — since s17 wants accurate identification of the individual.
- **Price discipline** — no discount at breakup, care plan held back — is commercially and ethically sound.
- **Suppression architecture exists**: `DEAD_STATUSES`, `SUPPRESSION_FILE`, `BOUNCED_FILE`, and EU/Canada exclusion via `RESTRICTED_COUNTRIES` in `campaign_manager.py`. Good foundations; the unsubscribe endpoint is the missing piece.

---

## Separate finding: the currently-live templates are worse than the sequence under audit

The sequence audited here is a clear improvement on what is in `campaign_manager.py` right now. Those templates should not send again either way:

| Line | File | Issue |
|---|---|---|
| `"Subject": "Re: Website Complete: {Name}"` | `campaign_manager.py:113` | Fake `Re:` on a thread that never existed, plus "Complete" for work not done. **CAN-SPAM §7704(a)(2), deceptive subject heading.** Squarely actionable. |
| `"I actually spent the last 10 hours building a custom, modernized version"` (×3 variants) | `campaign_manager.py:97-107` | False. The generator produces a demo in ~20 seconds. Deceptive commercial content; also the precise dishonesty this list is trained to detect. |
| `"Subject": "quick question"` | `campaign_manager.py:105` | Explicitly banned by Rule 6, and not a question. |
| `"noticed your website layout makes it really easy for patients to scroll past the important info"` | `campaign_manager.py:97` | Sent to every lead regardless of scan. **Fabricated observation — Hard Rule 1.** |
| `"It'll stay live for another two weeks."` | `campaign_manager.py:130` | Same unenforced-deadline problem as B5. |
| `name = "there"` fallback | `campaign_manager.py:180` | Produces "Hey there" — explicitly banned by the merge-field spec. |

---

## Corrected copy — shippable once B1–B4 are actually built

**Touch 1** (subject: `your Instagram, as a website`)

```
{{first_name}} — I looked up {{practice}} in {{city}}. Your
Instagram comes up, but there's no link in the bio, so I
couldn't find a site from there.

So I built one, using your logo and photos from your public
Instagram. It's live now: {{demo_url}}

Real site, not a screenshot. Opens fine on a phone.

I'm a web developer and yes, this is a sales email. If it's no
use, click below — I'll delete the demo and stop emailing.

Milin Dholiya — web developer, Surat, India
Unsubscribe / where I got your details: {{unsubscribe_url}}
{{sender_postal_address}}
```

**Touch 2** (subject: `before you ask: the price`)

```
{{first_name}} — the demo is still up: {{demo_url}}

The price, since you'd ask: {{price}} one time to make it yours
— your own domain, your hours, a contact form to your inbox.
No monthly fee to me. Domain renewal is about $15/year, paid to
the registrar, in your name. All the files are yours.

Yes or no, both fine.

Milin Dholiya — web developer, Surat, India
Unsubscribe: {{unsubscribe_url}}
{{sender_postal_address}}
```

**Touch 3** (subject: `last one from me`) — no-takedown version, use this one unless deletion is genuinely automated

```
{{first_name}} — last email from me.

If you want the site it's {{price}} and I'll send the scope and
an invoice: {{demo_url}}

Either way, good luck with the practice.

Milin Dholiya — web developer, Surat, India
Unsubscribe: {{unsubscribe_url}}
{{sender_postal_address}}
```

---

## Ship gate

1. Unsubscribe endpoint live, writing to `SUPPRESSION_LIST.txt`, plus `List-Unsubscribe` and `List-Unsubscribe-Post` headers in `send_smtp_email()`. *(B2)*
2. Real postal address hardcoded into the footer builder. *(B3)*
3. Ad-identification line in all three touches. *(B4)*
4. Emit rules 1, 3 and 4 implemented in `scanner.py`, or the claim narrowed to the one signal that exists. *(B1)*
5. Takedown line cut, or a deletion job scheduled. *(B5)*
6. Demos `noindex` + "unofficial demo, not affiliated" banner. *(H1)*
7. Patient-image filter; testimonials stripped from AU and UK demos. *(H2)*
8. Move off rotating consumer Gmail before volume sending. *(H3)*

Items 1–5 are legal blockers. Item 6–7 are what stops a single angry dentist with a lawyer from being an expensive afternoon. Item 8 is the one with a criminal statute attached.