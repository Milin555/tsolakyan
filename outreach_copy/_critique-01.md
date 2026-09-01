# no-website (6,543) — 3-touch sequence

**Segment logic:** nothing to criticise, so the finding is an *absence* that the scanner can actually prove. The email's whole job is the click on {{demo_url}}. No consequence framing ("you're losing patients"), no urgency that isn't literally true.

---

## TOUCH 1 — day 0 (78 words incl. hook)

**Subjects**
1. `no website for {{practice}}`
2. `I built you a website`
3. `your Instagram, as a website`

**Body**

```
{{first_name}} — {{pitch_hook}}

So I built one. Your photos, your name, your logo, live right
now: {{demo_url}}

It's not a mockup or a template screenshot — it's a real site
on the internet. Open it on your phone, it takes a minute.

If it's no use to you, say so and I'll delete it.

Milin — web developer, Surat, India

{{unsubscribe_url}}
{{sender_postal_address}}
```

**CTA:** click {{demo_url}}. Nothing else. No price, no call booking, no "let me know a good time".

---

## TOUCH 2 — day 3 (47 words)

Angle: answer the two questions they had on day 0 and didn't ask — *is this real, and what's the catch?* This is where the price lands.

**Subjects**
1. `what the demo would cost`
2. `before you ask: the price`
3. `the boring part`

**Body**

```
{{first_name}} — the demo site is still up: {{demo_url}}

Here's the boring part. To make it properly yours — your own
domain, your hours, a contact form that emails you — is $495
once. No monthly fee, no contract, and you own the files.

Yes or no is both fine.

Milin

{{unsubscribe_url}}
{{sender_postal_address}}
```

**CTA:** reply yes or no.

---

## TOUCH 3 — day 7 (39 words)

**Subjects**
1. `last one from me`
2. `taking the demo down`
3. `I'll stop emailing`

**Body**

```
{{first_name}} — last email from me.

The demo comes down {{takedown_date}}; I pay for the hosting so
I don't keep dead ones up. If you want it, reply "yes" and it's
yours for $495: {{demo_url}}

Either way, good luck.

Milin

{{unsubscribe_url}}
{{sender_postal_address}}
```

**CTA:** reply "yes".

⚠️ Only ship the takedown line if the demos genuinely get deleted on {{takedown_date}}. If they don't, cut it to "This is the last one from me" — a fake deadline is exactly the agency behaviour this list is immune to.

---

## Merge fields for this segment

| Field | Notes |
|---|---|
| `{{first_name}}` | Fallback ladder: first name → `Dr {{last_name}}` → **drop the greeting entirely** and open on the hook. Never "Hi there", never "Hi {{practice}}". |
| `{{practice}}` | Subject line 1 + hook. Suppress if it's over ~28 chars or the subject blows past 45. |
| `{{city}}` | Used inside the hook to prove a real search happened. |
| `{{pitch_hook}}` | The one scan-derived sentence. Hard cap 25 words. |
| `{{demo_url}}` | All three touches. Same URL throughout. |
| `{{takedown_date}}` | Touch 3 only. Must be a real date. |
| `{{unsubscribe_url}}` | One-click, working, all three. |
| `{{sender_postal_address}}` | Milin's real Surat postal address — CAN-SPAM requires it on every send. |

Optional, only if the scanner is confident: `{{instagram_handle}}`, `{{follower_count}}`.

---

## pitch_hook — exact template the scanner generates

```
I looked up {{practice}} in {{city}} — {{found_surface}} comes up, but {{absence_evidence}}.
```

**`{{found_surface}}`** (pick the strongest confirmed one):
- `your Instagram and your Google listing`
- `your Instagram`
- `your Google listing`

**`{{absence_evidence}}`** (pick the one the scan actually proved):
- `there's no website behind either` — no owned domain found on any surface
- `the website field on the listing is empty` — GBP present, website slot null
- `your bio has no link in it at all` — IG bio link field empty
- `the only link is {{bio_link_host}}, which isn't a site you own` — bio link resolves to linktr.ee / facebook.com / a booking vendor

**Rendered examples:**
> I looked up Riverbend Family Dental in Boise — your Instagram and your Google listing come up, but there's no website behind either.

> I looked up Kensington Smile Studio in London — your Instagram comes up, but your bio has no link in it at all.

**Emit rules (all must pass, or suppress the lead — do not send a guess):**
1. No domain in the Google Business Profile website field.
2. IG bio link is empty, or resolves to a host on the not-owned list.
3. No registered domain matching the practice name.
4. Name + city search returns no owned site in the top 10.

If any check is inconclusive, drop the lead out of the send. A wrong "you have no website" to someone who has one burns the sender domain and proves every cynical thing they believe about agencies.

---

## Offer and price placement

- **Offer:** $495 site build. That is the only thing named in this sequence.
- **Touch 1: no price.** The demo has to be judged on its own before money enters the frame. Price on touch 1 turns a "huh, that's my clinic" into a "here comes the pitch".
- **Touch 2: name $495 in full**, with what's included (domain, hours, contact form) and what isn't (no monthly, no contract, files are theirs). Day 3 is right — they've either clicked or they haven't, and the ones who clicked are silently pricing it in their head. Answer them before they invent a number.
- **Touch 3: repeat $495 once**, as the close. No discount, no "for this week only". Discounting at the breakup tells them the first number was made up.
- **Do not mention the $149/mo care plan anywhere in the cold sequence.** A monthly fee next to a one-off price makes the one-off look like bait. Raise it after they reply yes, at handoff.
- Emergency rescue / migration offers are irrelevant here — there's no site to rescue or migrate. Keep them out.

---

## Compliance notes

- Real postal address + working one-click unsubscribe on all three; honour opt-outs within 10 business days (CAN-SPAM) and immediately in practice.
- UK: PECR's B2B exemption covers corporate subscribers, but a sole-trader dentist counts as an individual. For UK leads, send only to practice/role addresses (info@, reception@, the practice domain), not to a personal-looking address at a free provider.
- AU Spam Act: same rules, plus the sender identification must be accurate — "Milin, web developer, Surat, India" satisfies it and matches Rule 8.
- Nothing in the copy claims a legal, ranking, or patient-volume outcome. Keep it that way in any variant.