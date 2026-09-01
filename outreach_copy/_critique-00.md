# Segment: link-in-bio — 3-touch cold sequence

**Offer:** Link-in-bio → real website build, **$495**
**Price named:** first time in **Touch 2**, repeated in **Touch 3**. Never in Touch 1.

---

## Merge fields this segment needs

| Field | Example | Notes |
|---|---|---|
| `{{first_name}}` | Sarah | Suppress lead if missing — do NOT fall back to "Doctor" or "there". |
| `{{practice}}` | Willow Lane Dental | Legal/trading name as shown on their IG bio. |
| `{{instagram_handle}}` | @willowlanedental | Used as proof the scan was real, not a blast. |
| `{{link_platform}}` | Linktree / Facebook page / WhatsApp link / bit.ly | Human-readable label, not the raw domain. |
| `{{link_url}}` | linktr.ee/willowlane | Held in reserve — only used in `pitch_hook`, not in the body. |
| `{{demo_url}}` | milin.dev/d/willow-lane | Hard requirement. **No demo, no send.** |
| `{{city}}` | Leeds | Optional; used in Touch 2 variant subject only. |
| `{{unsubscribe_url}}` | — | Footer, every touch. |
| `{{sender_address}}` | Milin's Surat postal address | Footer, every touch. CAN-SPAM. |

**Suppression rules:** drop the lead if `demo_url` failed to build, if `first_name` is blank, or if the record is a personal/consumer address rather than the practice's business address (UK PECR — corporate subscribers only; individuals and sole traders need opt-in, so suppress UK leads whose contact is a personal gmail/hotmail rather than a practice domain).

---

## pitch_hook — exact template the scanner generates

```
The only link on {{instagram_handle}} goes to {{link_platform}} ({{link_url}}), and no website domain was found registered to {{practice}}.
```

Fires only when: (a) an active Instagram business profile exists, (b) the sole outbound bio link resolves to linktr.ee / bit.ly / wa.me / facebook.com / beacons / campsite, and (c) a domain lookup on the practice name returns nothing live. If any of the three fail, the lead is not in this segment.

Touch 1 body below is written so `{{pitch_hook}}` can be dropped straight into sentence one.

---

# TOUCH 1 — day 0

**Subject lines**
1. `Your Instagram link goes to {{link_platform}}` (~36 chars rendered)
2. `{{practice}} — I built you a website` (~36)
3. `A real site behind your bio link` (32)

**Body** (67 words)

```
{{first_name}} — the only link on {{instagram_handle}} goes to
{{link_platform}}. There's no website of your own behind it, so
{{practice}} has nothing for Google to show and no page that takes
a booking.

So I built one and put it up: {{demo_url}}

Your name, your logo, your colours, real pages. Have a look — if
it's wrong for you, say so and I'll stop.

Milin, web developer, Surat, India
```

**Single CTA:** open the demo link. Nothing else is asked for. No call, no meeting, no "let me know your thoughts."

---

# TOUCH 2 — day 3

Different angle: Touch 1 was *you don't have one*. Touch 2 is *here's the specific moment it costs you* — the patient who already knows the name and still can't find them. Price lands here.

**Subject lines**
1. `What Google shows for {{practice}}` (~40)
2. `Still up if you want it` (23)
3. `Your demo site, and the price` (29)

**Body** (56 words)

```
{{first_name}} — someone hears about {{practice}}, types the name
into Google, and lands on {{link_platform}} or nothing at all. A
rented link page can't rank, can't hold your reviews, can't take a
Tuesday-night booking.

The site is still live: {{demo_url}}. $495 to own it outright,
about a week to finish.

Want it? Reply with one word.

Milin
```

**Single CTA:** reply. The demo link is support, not the ask.

---

# TOUCH 3 — day 7

**Subject lines**
1. `Taking the demo down Friday` (27) — only use if the demo genuinely expires
2. `Last email from me` (18)
3. `Closing this out` (16)

**Body** (43 words)

```
{{first_name}} — last one from me. The demo at {{demo_url}} comes
down at the end of the week. If you want it, reply "keep it" and
it's yours for $495. If not, I'll leave you alone. Either way, good
luck with the practice.

Milin
```

**Single CTA:** two-word reply.

**Important:** the takedown line is only usable if demos actually expire on a timer. If they don't, either set them to, or swap the first two sentences for: `last one from me. The demo at {{demo_url}} stays up either way.` — a deadline that isn't real is manufactured urgency and they will smell it.

---

## Footer (all three touches, below the signature, excluded from word counts)

```
You're getting this because {{practice}} is listed publicly as a
dental practice. Don't want these? {{unsubscribe_url}} — one click,
no reply needed, and I won't contact you again.

{{sender_address}}
```

---

## Notes on the sequence

**Why no price in Touch 1.** Touch 1 has one job: get the click onto a page with their own logo on it. A number in that email turns it into a quote before they've seen anything, and the whole advantage of the demo is that it argues for itself.

**Why $495 and nothing else.** Do not mention the $149/mo care plan or the $449 booking install anywhere in the cold sequence — a second number halves reply rate. The build includes a booking button; the standalone booking install is only relevant to leads who already have a site, which this segment by definition does not. Care plan comes up after they say yes, never before.

**On the Surat line in Touch 1.** It stays. It goes in the signature, not the body, so it reads as a fact rather than a disclaimer. Clinicians assume offshore anyway; volunteering it before they wonder is the thing that buys credibility for the rest.

**Reply handling.** Any reply — including "no thanks" — stops the sequence immediately. "Not interested" gets a one-line acknowledgement and a suppression-list entry, not a rebuttal.

**What this sequence deliberately does not say:** nothing about losing patients to competitors, nothing about what happens if Linktree changes its terms, nothing about ADA/GDC/AHPRA rules, no compliance language of any kind. The finding is the pitch.