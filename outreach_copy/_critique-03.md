# broken-site — 3-touch cold sequence

**Segment rule that overrides everything else here:** this copy may only send if the scanner has a live, re-verified fault. Re-check the fault within 6 hours of send. If the fault has cleared, the lead drops out of this segment (see branch rules at the end). One false "your site is broken" email to a clinician is unrecoverable.

---

## MERGE FIELDS THIS SEGMENT NEEDS

| Field | What it holds | Fallback / rule |
|---|---|---|
| `{{salutation}}` | `Dr. Reyes` (verified surname + title) or `Marcus` | If no verified name: **omit the greeting line entirely** and open on the finding. Never `Hi there`, never the practice name as a person. |
| `{{practice}}` | Practice name as written on their site | Required. No lead sends without it. |
| `{{domain}}` | Bare domain they'd recognise — `northgatefamilydental.com` | Required. Strip protocol. Keep `www.` only when the www host *is* the fault. |
| `{{fault_type}}` | Routing enum, never printed: `dns_www_nxdomain` \| `ssl_expired` \| `http_5xx` \| `images_404` | Required. Drives the three fields below. |
| `{{fault_label}}` | ≤18 char human name of the fault, for subject lines — `SSL expired`, `www not resolving` | Required. Lowercase after first word. |
| `{{pitch_hook}}` | The one generated sentence. Template below. | Required. Blank = suppress lead. |
| `{{fix_scope}}` | Noun phrase, ≤5 words — `a certificate renewal`, `one DNS record` | Required. Used to prove it's small. |
| `{{fix_instruction}}` | Touch 2 only. Real, correct instruction their own web person could follow. ≤25 words. | Required for touch 2. Blank = skip touch 2, jump to touch 3. |
| `{{scan_date}}` | `14 Aug` — date the evidence was captured | Required. Day + month, no year, no time. |
| `{{recheck_date}}` | Touch 2 only. Date of the day-3 re-scan. | Required for touch 2. |
| `{{demo_url}}` | Live personalised demo | Required. Must return 200 at send time. |
| `{{unsubscribe_url}}` | One-click, working, no login | Required, all three touches. |
| `{{postal_address}}` | Milin's real street address, Surat | Required, all three touches — CAN-SPAM. |

Do **not** add `{{city}}`, `{{specialty}}` or follower counts to this segment. Broken-site converts on evidence, and extra personalisation reads as surveillance.

---

## THE `pitch_hook` TEMPLATE THE SCANNER GENERATES

One sentence. Observation, then plain patient-facing effect. No adjective, no consequence-inflation, no number they can't verify.

```
{{scanned_host}} {{observed_result}} as of {{scan_date}}, so {{visitor_effect}}.
```

Hard constraints on generation: ≤30 words · exactly one sentence · past-or-present tense on a fact the scanner literally observed · no words from this list: *losing, costing, patients are, Google will, ranking, penalty, risk, urgent, immediately*.

Filled per fault type:

| `fault_type` | `pitch_hook` |
|---|---|
| `dns_www_nxdomain` | `www.{{domain}} returned NXDOMAIN as of {{scan_date}}, so anyone who types the www version gets a browser error page instead of your site — the version without www works fine.` |
| `ssl_expired` | `The SSL certificate on {{domain}} expired on {{expiry_date}}, so Chrome and Safari now show a full-page "Not secure" warning before the site loads.` |
| `http_5xx` | `{{domain}} returned a {{status_code}} error on {{fail_count}} of {{check_count}} checks between {{first_seen}} and {{scan_date}}, so the site was unreachable for part of each of those days.` |
| `images_404` | `{{broken_count}} of the {{total_count}} images on your homepage return 404 as of {{scan_date}}, so the hero photo and {{second_area}} load as empty boxes.` |

Matching values:

| `fault_type` | `fault_label` | `fix_scope` | `fix_instruction` (touch 2) |
|---|---|---|---|
| `dns_www_nxdomain` | `www not resolving` | `one DNS record` | `Add a CNAME record for "www" pointing at {{domain}} in your DNS panel, then force HTTPS on it. Ten minutes, propagates within the hour.` |
| `ssl_expired` | `SSL expired` | `a certificate renewal` | `Reissue the certificate in your host's SSL panel — most have a one-click Let's Encrypt renewal — then turn auto-renew on so it doesn't lapse again.` |
| `http_5xx` | `site returning {{status_code}}` | `a server config fix` | `Ask your host to check the error log for {{scan_date}}. A {{status_code}} at this pattern is usually PHP memory or a plugin, not the site itself.` |
| `images_404` | `homepage images 404` | `broken file paths` | `The image files are missing from the server, not just unlinked. Whoever did the last migration needs to re-upload the media folder and re-point the paths.` |

---

## PRICE: WHERE IT GOES

**Offer: emergency site rescue, $299 flat.**

- **Touch 1 — no number.** Say "I can fix it today." A price in the opener makes it a sales email before they've read the finding.
- **Touch 2 — name it, once, in the last line.** By then you've given the fix away free, so $299 lands as convenience, not as a pitch. This is the sentence that converts this segment.
- **Touch 3 — repeat the same $299, once.** Same number, no discount, no "for this week only." Discounting a $299 emergency fix destroys the frame that it's a small job.

Never mention the $1,200–2,500 migration, the $149/mo plan or the booking install anywhere in this sequence. The demo already plants the rebuild; the upsell happens after the fix is paid and delivered, when you're a vendor instead of a stranger.

---

# TOUCH 1 — day 0

### Subject lines (pick by fault type; keep static text ≤20 chars so merges fit)

1. `{{domain}} — {{fault_label}}` → *northgatefamilydental.com — SSL expired*
2. `{{fault_label}} on your site` → *www not resolving on your site*
3. `One broken thing on your site`

Truncate `{{domain}}` over 26 chars to the registrable name only. No question marks — questions read as pitch.

### Body

```
{{salutation}},

{{pitch_hook}}

Fixing that is {{fix_scope}}, not a rebuild. I can do it today.

I also rebuilt your homepage, so you can judge the work instead of
the email:
{{demo_url}}

Reply "fix it" and I'll send the two things I need from you.

Milin Dholiya — web developer, Surat, India
Concept demo, not indexed, unaffiliated with {{practice}}.
{{postal_address}} · Unsubscribe: {{unsubscribe_url}}
```

~69 words rendered, excluding signature block.

### Rendered example (illustrative values, not a real lead)

```
Subject: northgatefamilydental.com — SSL expired

Dr. Reyes,

The SSL certificate on northgatefamilydental.com expired on 14 Aug, so
Chrome and Safari now show a full-page "Not secure" warning before the
site loads.

Fixing that is a certificate renewal, not a rebuild. I can do it today.

I also rebuilt your homepage, so you can judge the work instead of
the email:
https://milin555.github.io/northgate-family-dental/

Reply "fix it" and I'll send the two things I need from you.

Milin Dholiya — web developer, Surat, India
Concept demo, not indexed, unaffiliated with Northgate Family Dental.
[street address], Surat, Gujarat 395007, India · Unsubscribe: [link]
```

### Call to action

**One:** reply with `fix it`.

Deliberate deviation from the house rule that the click is the ask. In the other four segments the demo link *is* the CTA. Here it isn't — a broken-site lead converts on the repair, not the redesign, and routing them through a demo click adds a touch before any money moves. The link stays in because it's the only proof that a stranger from another country can actually do the work; it just isn't the ask.

---

# TOUCH 2 — day 3

**Angle: give the fix away.** Not a bump, not a re-send. You hand them the exact instruction so their own web person can do it for free, and only then mention that you'll do it instead. This is the highest-trust move available and it's what makes the $299 readable.

### Subject lines

1. `The actual fix for {{domain}}`
2. `What to tell your web person`
3. `{{fault_label}} — how to fix it`

Do not reply into the touch-1 thread. Fresh subject, fresh thread — a threaded follow-up reads as chasing.

### Body

```
{{salutation}},

Still showing on {{recheck_date}}. Here's the fix, so whoever manages
your site can just do it:

{{fix_instruction}}

If there's no one to hand that to, I'll do it today — $299 flat,
nothing else attached.

Milin

Unsubscribe: {{unsubscribe_url}} · {{postal_address}}
```

~55 words rendered with a 25-word `{{fix_instruction}}`. If the instruction runs longer, cut the instruction, not the frame.

### Call to action

**One:** reply if they want you to do it. The email is functional even if they never reply — that's the point of it.

---

# TOUCH 3 — day 7

### Subject lines

1. `Closing your file`
2. `Last one from me`
3. `Leaving this here`

### Body

```
{{salutation}},

Last one from me — I won't email again.

The demo stays up two more weeks: {{demo_url}}

If {{fault_label}} is still there next month, this address still works.
Same $299.

Milin

Unsubscribe: {{unsubscribe_url}} · {{postal_address}}
```

~38 words rendered.

### Call to action

**One:** reply later, on their timing. No date, no scarcity beyond the literal truth that the demo comes down — and if you say two weeks, actually take it down in two weeks.

---

## BRANCH RULES (these are what keep rule 1 true)

- **Re-scan before every touch.** Touch 2 and 3 both assert the fault is still live. If it isn't, the assertion is a lie.
- **Fault cleared between touch 1 and 2** → drop the sequence. Send one line instead, no pitch, no link: *"Saw {{domain}} is sorted — ignore my last email. Good luck with the practice. Milin"* Then suppress for 90 days. These become warm inbound surprisingly often.
- **Fault cleared between touch 2 and 3** → send nothing. Mark `resolved_no_sale`.
- **Any reply at all** → sequence halts immediately, including out-of-office and "not interested."
- **Demo URL not returning 200 at send time** → hold the send. An email about their broken site containing a broken link is the worst possible outcome for this segment.

## COMPLIANCE

- Real postal address in all three footers — CAN-SPAM requires it and the current templates omit it.
- Working one-click unsubscribe plus a `List-Unsubscribe` header; honour within 24 hours, not the 10 days the law allows.
- **UK:** PECR permits B2B email to a limited company or LLP without prior consent, but **sole traders and partnerships are treated as individuals and need consent.** A large share of UK dental practices are exactly that. Either check company status per UK lead before sending, or accept the exposure knowingly — don't let the segment default into it.
- **Australia:** the Spam Act needs sender identification, a functional unsubscribe, and at minimum inferred consent from a publicly published business address relevant to that business. A published practice email plus a fault on that practice's own site is a defensible basis; a scraped personal address is not.
- Never write that the fault is a HIPAA/GDPR/compliance issue, never mention liability, never imply anyone could act against them. The finding on its own is enough.

## SENDING NOTES

- Plain text only. No HTML, no tracking pixel, no image. One link in touch 1 and 3, zero in touch 2 besides unsubscribe.
- Don't spin this copy. The evidence line is already unique per lead — that's the variation.
- Cap at 6 sends per inbox per day for this segment; it's the highest-reply and highest-complaint copy of the five, and a complaint spike here poisons every other segment on the same domain.