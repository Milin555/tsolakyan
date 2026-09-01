# broken-site — FINAL 3-touch sequence (production)

**Pre-send law (unchanged, non-negotiable):** fault re-verified within 6h of every send; scanner error or timeout = treat as CLEARED and hold (fail closed). No lead sends without a live, re-verified fault.

**Character set:** pure ASCII. No em dashes, no middots, no curly quotes anywhere in subject or body. Store paragraphs as single unwrapped lines; let the client wrap.

---

## SEND-DAY SCHEDULE

| Touch | Day | Thread | Links in body | Re-scan required |
|---|---|---|---|---|
| 1 | Day 0 | New | 1 (unsubscribe only) | Yes, <6h |
| 2 | Day 3 | New thread, new subject | 2 (demo + unsubscribe) | Yes, <6h |
| 3 | Day 8 | New thread, new subject | 2 (demo + unsubscribe) | Yes, <6h |

Send window: Tue-Thu, 08:00-11:00 **recipient local time**, jittered +/-40 min. Never send if `scan_date` > recipient's current local date. Warm-up ramp: 2 sends/inbox/day week 1, 4 week 2, 6 week 3+. Kill switch: >0.10% complaint or >2% hard bounce over rolling 500 sends halts the whole domain.

---

## TOUCH 1 - Day 0

### Subject lines (choose by `len(domain)`; assign variant by hash of lead ID)

1. `{{fault_headline}} on {{domain}}` -> *Certificate expired 14 Aug on northgatefamilydental.com*
2. `{{domain}}: something you'll want to see` — **only** if `len(domain) > 24`
3. `Found this on {{domain}} this morning`

No question marks. No bare `domain - label` construction. `{{fault_headline}}` values: `Certificate expired {{expiry_date}}` | `The www version isn't loading` | `{{status_code}} errors on {{fail_count}} checks` | `{{broken_count}} homepage images not loading`.

### Body

```
{{salutation}},

{{pitch_hook}}

{{verify_step}}

It's {{fix_scope}}, not a rebuild. Whoever manages your site can do it in about ten minutes, free. If there's nobody to hand it to, I'll do it for $299 flat, nothing else bundled in.

Just reply. I'll tell you exactly what access I need before you give me anything.

Milin Dholiya, web developer, Surat, India.
I scan dental practice sites for faults like this one. That's how I found yours, on {{source_domain}}.

{{postal_address}}
Unsubscribe: {{unsubscribe_url}}
```

UK/EU leads only, one extra footer line above the address:
```
How I handle contact data and how to have it deleted: {{privacy_url}}
```

**Rendered example (illustrative, not a real lead):**

```
Subject: Certificate expired 14 Aug on northgatefamilydental.com

Dr. Reyes,

The SSL certificate on northgatefamilydental.com expired on 14 Aug, so Chrome and Safari show a full-page security warning that a visitor has to click through before the site loads.

Open your site in a private tab on your phone and you'll see it. Private tab matters - your normal browser has the site cached and will look fine.

It's a certificate renewal, not a rebuild. Whoever manages your site can do it in about ten minutes, free. If there's nobody to hand it to, I'll do it for $299 flat, nothing else bundled in.

Just reply. I'll tell you exactly what access I need before you give me anything.

Milin Dholiya, web developer, Surat, India.
I scan dental practice sites for faults like this one. That's how I found yours, on northgatefamilydental.com.

[street address], Surat, Gujarat 395007, India
Unsubscribe: [link]
```

**CTA: one.** Reply normally. No keyword, no link, no demo.

---

## TOUCH 2 - Day 3

### Subject lines

1. `The actual fix for {{domain}}`
2. `What to tell your web person about {{domain}}`
3. `{{domain}}: the fix, and the thing I built`

### Body

```
{{salutation}},

I wrote to you on {{scan_date}} about {{fault_noun}} on {{domain}}. I checked again on {{recheck_date}} and it's still there.

Here's the fix, so whoever manages your site can just do it:

{{fix_instruction}}

That's the whole job. If there's nobody to hand it to, I'll do it for $299 flat.

Separate thing, and the reason I bothered emailing at all: I rebuilt your homepage on one of my templates before I wrote to you, so you can look at actual work instead of a sales email. It's a concept, it isn't connected to your practice, and it's blocked from search:

{{demo_url}}

Milin Dholiya, web developer, Surat, India.

{{postal_address}}
Unsubscribe: {{unsubscribe_url}}
```

~120 words. It earns the length: the fix is free, the demo is free, and the recipient has had three days to confirm touch 1 was true.

**CTA: one.** Reply if they want it done. The email is useful to them even if they never reply.

---

## TOUCH 3 - Day 8

### Subject lines

1. `Last note about {{domain}}`
2. `Taking the {{domain}} demo down {{teardown_date}}`
3. `Leaving this here for {{domain}}`

### Body

```
{{salutation}},

Last one from me about this.

{{fault_noun}} was still showing on {{domain}} when I checked on {{recheck_date}}. The fix is in the email I sent on {{prev_touch_date}} if you want to pass it to someone, and it costs you nothing to use it.

If you'd rather I just did it, it's $299 and this address works whenever, including next month.

I'm taking the demo down on {{teardown_date}}:
{{demo_url}}

Milin Dholiya, web developer, Surat, India.

{{postal_address}}
Unsubscribe: {{unsubscribe_url}}
```

~85 words, 2 links. Wording is `Last one from me about this` - not `I won't email again`, because the system can break that promise. Teardown is automated, not intentional.

**CTA: one.** Reply on their timing.

---

## PITCH_HOOK - what the scanner generates

```
{{scanned_host}} {{observed_result}} {{observation_time_clause}}, so {{visitor_effect}}.
```

Constraints: <=32 words, exactly one sentence (plus one optional gated second sentence for `dns_www_nxdomain`), stated only as what the scanner literally observed, no inference about days/causes/counts it did not measure. Banned tokens: *losing, costing, patients are, Google will, ranking, penalty, risk, urgent, immediately, HIPAA, GDPR, liability, compliance*.

| fault_type | pitch_hook |
|---|---|
| `ssl_expired` | `The SSL certificate on {{domain}} expired on {{expiry_date}}, so Chrome and Safari show a full-page security warning that a visitor has to click through before the site loads.` |
| `dns_www_nxdomain` | `www.{{domain}} returned NXDOMAIN when I checked on {{scan_date}}, so anyone who types the www version gets a browser error instead of your site.` + gated 2nd sentence `The version without www loads normally.` **only** if the scanner independently fetched the apex and got 2xx with a non-empty body. |
| `http_5xx` | `{{domain}} returned {{status_code}} on {{fail_count}} of {{check_count}} checks between {{first_seen}} and {{scan_date}}, so some visitors in that window got an error page instead of the site.` |
| `images_404` | `{{broken_count}} of the {{total_count}} images on your homepage return 404 as of {{scan_date}}, so {{second_area}} doesn't load.` Emit **only** when `broken_count >= 2` and `second_area` is non-null. |

Scanner gates: `ssl_expired` requires https reachable/redirected-to (HTTP-only sites are a different fault). `images_404` requires a re-fetch with a real browser user-agent before flagging. `http_5xx` `fix_instruction` PHP variant requires a detected PHP/WordPress fingerprint.

### `verify_step` (the highest-value field in the sequence)

| fault_type | verify_step |
|---|---|
| `ssl_expired` | `Open your site in a private tab on your phone and you'll see it. Private tab matters - your normal browser has the site cached and will look fine.` |
| `dns_www_nxdomain` | `Type www.{{domain}} into your phone browser, exactly like that with the www. You'll get an error page. Leave the www off and it loads normally.` |
| `http_5xx` | `It's intermittent, so it may well load fine for you right now. Your host's error log for {{first_seen}} to {{scan_date}} will show them - ask for it, you don't need me for that.` |
| `images_404` | `Open your homepage in a private tab on your phone and scroll. The gaps are visible without any tools.` |

### `fault_noun` / `fix_scope` / `fix_instruction`

| fault_type | fault_noun (prose) | fault_label (subject only) | fix_scope | fix_instruction |
|---|---|---|---|---|
| `ssl_expired` | `the expired certificate` | `SSL expired` | `a certificate renewal` | `Reissue the certificate in your host's SSL panel - most have a one-click Let's Encrypt renewal - then switch auto-renew on so it doesn't lapse again.` |
| `dns_www_nxdomain` | `the www problem` | `www not resolving` | `one DNS record` | `Add a CNAME record for "www" pointing at {{domain}} in your DNS panel, then force HTTPS on it. Ten minutes of work; usually live within the hour, sometimes longer depending on your TTL.` |
| `http_5xx` | `the {{status_code}} errors` | `{{status_code}} errors` | `a server-side setting` | `Ask your host to pull the error log for {{scan_date}}. A {{status_code}} on this pattern is almost always a server-side setting, not your site content.` |
| `images_404` | `the missing images` | `homepage images 404` | `broken image paths` | `Those image URLs return 404 from the server. Whoever handled the last site change needs to check whether the files moved or the paths did, and re-point them.` |

---

## REQUIRED MERGE FIELDS + FALLBACKS

Rule: **no field ever prints a token, a blank, or a lone punctuation mark.** Anything marked SUPPRESS means the lead does not send at all.

| Field | Fallback if empty |
|---|---|
| `{{salutation}}` | Conditional block, not a default: `{% if salutation %}{{salutation}},\n\n{% endif %}`. Empty = the entire line and its comma are removed and the body opens on `{{pitch_hook}}`. Never `Hi there`. Verify empty-field rendering in the ESP on all three touches before launch. Title only used when the source page states it adjacent to the name. |
| `{{practice}}` | Only used on the demo page now, not in the email. Gate anyway: reject if it contains `\|`, `:`, `Home`, `Welcome`, `Best`, a state abbreviation, or >40 chars. Bad value = demo renders with domain text instead. |
| `{{domain}}` | SUPPRESS. |
| `{{fault_type}}` | SUPPRESS. Never printed. |
| `{{fault_headline}}` | Falls back to subject variant 3 (`Found this on {{domain}} this morning`). |
| `{{fault_label}}` | Subject lines only. Empty = use subject variant 3. Never used in prose. |
| `{{fault_noun}}` | `the problem I wrote about` |
| `{{pitch_hook}}` | SUPPRESS. |
| `{{verify_step}}` | Prints nothing, line removed. Touch 1 still sends (the hook stands alone), but log it - a missing verify_step is a scanner defect. |
| `{{fix_scope}}` | `a small fix` |
| `{{fix_instruction}}` | Empty = skip Touch 2 entirely, move Touch 3 to day 5. |
| `{{scan_date}}` | `earlier this month` (rendered in recipient's timezone; never later than recipient's local date) |
| `{{recheck_date}}` | `this morning` |
| `{{prev_touch_date}}` | `in my last email` (sentence reads `The fix is in the email I sent in my last email` -> use alternate clause `The fix is in my previous email`) |
| `{{teardown_date}}` | `at the end of the month` - and actually delete it then, automated. |
| `{{demo_url}}` | Empty or non-200 = the entire demo paragraph is removed from Touch 2 and Touch 3. Sequence still sends. |
| `{{source_domain}}` | `your own site` |
| `{{unsubscribe_url}}` | SUPPRESS. |
| `{{postal_address}}` | SUPPRESS. |
| `{{privacy_url}}` | SUPPRESS for UK/EU leads. Non-UK/EU: line omitted. |
| `{{second_area}}`, `{{expiry_date}}`, `{{status_code}}`, `{{fail_count}}`, `{{check_count}}`, `{{first_seen}}`, `{{broken_count}}`, `{{total_count}}` | Nested inside hooks. SUPPRESS if null - never print a default. |

**Pre-send regex gate on the fully rendered subject + body:** reject on `{{`, `}}`, `undefined`, `null`, `NaN`, `0 of 0`, `1 images`, `1 of the`, double space, leading/trailing comma, or a line consisting only of punctuation.

---

## INFRASTRUCTURE (floor, not optional)

Dedicated sending subdomain, never root. SPF + DKIM + DMARC aligned. `List-Unsubscribe` **and** `List-Unsubscribe-Post: List-Unsubscribe=One-Click`; unsubscribe live 60 days minimum, suppresses across all five segments permanently, honoured within 24h. Open tracking off, click tracking off, no link wrapping, no shorteners, no HTML part. SMTP-verify every mailbox within 24h of send; drop catch-all-unverifiable; segment out `info@`/`office@`/`frontdesk@`. Drop any address whose source page hasn't changed in 24+ months.

Demos: registered domain you own (`demos.<neutral-brand>.com`), three-domain isolation from sending and portfolio domains, unguessable slug (`/demo-concept-8f3a2c/`), `X-Robots-Tag: noindex, nofollow` verified in the same call as the 200, persistent top-of-viewport disclaimer plus same-day takedown address. Demo contains **no** logo file, no scraped photography, no staff or patient images, no testimonials, no before/after, no superlatives, no specialty/registration placeholders. Brand colours only.

UK: send only on a positive Companies House match to Ltd or LLP, recorded in `uk_entity_status`. No match, no send. AU: fetch the source page and suppress on any no-unsolicited-email statement; `email_source` must be `business_published`, not an Instagram bio.

---

## BRANCH RULES

- Fault cleared between touch 1 and 2 -> drop sequence, send the courtesy note **with full footer**, suppress 90 days:
```
Saw {{domain}} is sorted. Ignore my last email, and good luck with the practice.

Milin Dholiya, web developer, Surat, India.
{{postal_address}}
Unsubscribe: {{unsubscribe_url}}
```
- Cleared between 2 and 3 -> send nothing, mark `resolved_no_sale`.
- Any reply halts immediately, including out-of-office. Replies containing *not interested, remove, stop, unsubscribe* write to the **global cross-segment** suppression list.
- Touch 3 completion writes `promised_no_contact` -> permanent suppression across all five segments.
- Demo non-200 at send time -> strip the demo paragraph, do not hold the whole send.

---

## WHY THIS WORKS

Touch 1 hands the clinician a fact they can confirm on their own phone in ten seconds without trusting the sender, which is the one thing no other agency email has ever given them. The demo moves to touch 2, where it arrives *after* the fix has been handed over free, so it reads as generosity rather than as the real motive - and it stops touch 1 looking structurally identical to a domain-scam phish. Naming $299 in touch 1, immediately after telling them their own web person can do it free, closes the "what will this cost me" loop before it becomes a reason to defer.

---

## WHAT I DELIBERATELY DID NOT FIX

**1. No screenshot, no image, still plain text only.** The dentist is right that an attached screenshot of the browser warning would win outright. I didn't do it: an image or attachment from a cold unknown foreign sender asserting a security fault on the recipient's domain is a much larger deliverability and phishing-shape penalty than the conversion gain, and an unread email converts at zero. The `verify_step` clause is the substitute - it makes them generate the screenshot themselves, in their own browser, which is more convincing anyway.

**2. The distance objection is not answered.** No "I'll call your office manager at 2pm," no timezone reassurance, no attempt to compete with a local developer on availability. Any line I could write there would either be a promise about response time I can't hold across a 10-13 hour offset, or the kind of reassurance that draws attention to the thing it's reassuring about. Nationality is stated plainly once and then left alone; the $299 price point makes it a low-stakes decision where distance matters less than it would at $2,500.

**3. I did not build 16 hand-authored skeleton variants.** The deliverability audit is correct that four canned bodies per day is a near-duplicate cluster. I raised the unique fraction instead - domain and fault-specific content now appear in every touch, touch 2 opens with the domain and two dates, touch 3 carries three merged fields - and specified hash-assigned subject rotation. Genuinely rewriting each frame four times is the right next step, but it's an authoring job rather than a copy decision, and shipping the sequence with three real skeletons per touch and honest per-lead evidence beats delaying to write twelve more.