# Segment: `no-booking` — 3-touch sequence

---

## TOUCH 1 — Day 0

**Subject lines** (rendered char count in brackets)
1. `Your site takes calls, not bookings` [35]
2. `Nowhere to book on {{practice}}'s site` [~37 — suppress if practice name > 22 chars, fall back to #1]
3. `I rebuilt your homepage with booking` [36]

**Body** (82 words with a 20-word `{{fault_evidence}}`)

```
Hi {{first_name}} — I ran a scan on {{practice_domain}}. {{fault_evidence}}

So I rebuilt your homepage with booking in it:

{{demo_url}}

Your logo, your colours, your page copy, and a booking button that opens.

It's auto-generated, so it's rough in places. The booking flow is the part worth 30 seconds.

I'm Milin, a developer in Surat, India. Not local to you, not pretending to be.
```

**Single CTA:** open `{{demo_url}}` and click the booking button. No reply asked for. No price. No call booked.

---

## TOUCH 2 — Day 3

**Subject lines**
1. `Most people don't leave voicemails` [34]
2. `What booking costs to install` [29]
3. `Booking install: 48 hours, $449` [31]

**Body** (54 words)

```
{{first_name}} — when someone hits a voicemail, most of them just
call the next practice. They don't ring back later. About a third
of calls during clinic hours go unanswered anyway, because the
front desk is with a patient.

That's the whole reason I sent the demo:

{{demo_url}}

Real booking on your actual site is $449, live in 48 hours.
Nothing else on the site changes.
```

**Single CTA:** open the demo and run the booking flow. Price is context for the click, not a separate ask.

---

## TOUCH 3 — Day 7

**Subject lines**
1. `Last one from me` [16]
2. `Should I delete the demo?` [25]
3. `Closing this out` [16]

**Body** (41 words)

```
{{first_name}} — last one from me.

Your demo stays up until {{demo_expiry_date}}, then it gets deleted:

{{demo_url}}

If booking is a next-year thing rather than a this-month thing,
reply "later" and I'll stop emailing you.

— Milin, Surat, India
```

**Single CTA:** one-word reply (`later` / `yes`). This is the only touch that asks for a reply.

**Only use subject #3 or the expiry line if the demo genuinely auto-deletes on that date.** If demos are permanent, drop `{{demo_expiry_date}}` and use "I'll leave the demo up either way."

---

## Compliance footer (all three touches, does not count toward word limits)

```
You're getting this because {{practice}} is listed publicly at {{practice_domain}}.
Don't want these? {{unsubscribe_url}} — one click, no reply needed.
Milin {{sender_last_name}}, {{sender_street_address}}, Surat, Gujarat {{postcode}}, India
```

Notes for the sending system:
- Unsubscribe must be honoured within 10 days (CAN-SPAM) and must work without a login.
- UK records: PECR consent rules bite for sole traders and unincorporated partnerships. Either suppress UK leads that aren't registered limited companies, or verify company status before sending. Ltd/PLC dental groups are fine under the corporate-subscriber carve-out.
- AU: Spam Act needs the same identity + functional unsubscribe. The footer above covers it.

---

## Merge fields this segment needs

| Field | Source | Fallback |
|---|---|---|
| `{{first_name}}` | enrichment | `there` — never guess a name off the practice name |
| `{{practice}}` | listing | `your practice` |
| `{{practice_domain}}` | scan | required — no send without it |
| `{{fault_evidence}}` | scanner, one sentence | **required — no fallback, drop the lead** |
| `{{demo_url}}` | generator | **required — no fallback, drop the lead** |
| `{{contact_method_found}}` | scan (feeds `fault_evidence`) | required |
| `{{page_count}}` | scan (feeds `fault_evidence`) | required |
| `{{demo_expiry_date}}` | generator | omit line if demos don't expire |
| `{{unsubscribe_url}}`, `{{sender_street_address}}`, `{{postcode}}`, `{{sender_last_name}}` | system | required |

---

## `pitch_hook` template the scanner generates

Emitted into `{{fault_evidence}}`. **Hard cap 20 words** or Touch 1 breaks its word limit.

```
{{page_count}} pages, and no way to book on any of them —
the only route in is {{contact_method_found}}.
```

`{{contact_method_found}}` is chosen from a closed list, never free text:
- `the phone number in your header`
- `the contact form on {{form_path}}`
- `a phone number and a contact form`
- `a phone number on your Contact page`

**Emission rules:**
1. Only fires when the crawler actually reached ≥ 5 pages AND returned zero matches across the full vendor list (Calendly, NexHealth, Zocdoc, LocalMed, Setmore, Acuity, Dentrix Ascend, Denticon, Flex, Yapi, Weave, Solutionreach, Podium, Doctible, plus generic `/book`, `/schedule`, `/appointment` routes and iframe/script-src checks).
2. If the crawl was blocked, partial, or timed out — **drop the lead from the segment.** Do not soften the sentence. A wrong "you have no booking" to a practice that has Zocdoc in a footer widget kills the reply and deserves to.
3. Re-scan at send time, not at list-build time. A lead that installed booking last month must exit the segment.
4. No consequence clause in the hook. The scanner states what's there. Touch 2 carries the "why it matters", and it uses population stats, not claims about their revenue.

---

## Price placement

**Offer:** Booking system install — **$449, live in 48 hours.**

- **Touch 1: no price, no offer name.** The email's only job is the click. A dollar figure in a first cold email turns a curious tap into a filed-under-agency-spam. It also invites a "how much for a whole new site" tangent that Milin doesn't want yet in this segment.
- **Touch 2: name it in full — "$449, live in 48 hours."** This is the right moment. They've either clicked the demo or they haven't; either way the price now does the qualifying. $449 is low enough that a practice owner can approve it without a partners' meeting, so stating it plainly removes the main reason to stall ("I'd have to find out what this costs").
- **Touch 3: do not repeat the price.** Repeating it reads as haggling. The breakup sells nothing — it asks permission to stop.

**Do not** mention the $149/mo care plan, the $1,200–2,500 migration, or the $299 rescue anywhere in this sequence. This segment has a working site and one missing part. Adding a second offer makes the email read like a menu, and menus get deleted. Upsell the care plan after the install ships.