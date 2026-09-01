# LINK-IN-BIO — FINAL PRODUCTION SEQUENCE (v2)

**Offer:** link-in-bio → owned website, **495 USD one payment**
**Format:** `text/plain` only. No HTML alternative, no images, no pixel, no click-tracking rewrite. Max 2 links per message.
**Price:** named in Touch 1 subject variant C only (A/B test), in body from Touch 2.

---

## SEND SCHEDULE

| Touch | Day | Window | Notes |
|---|---|---|---|
| 1 | Day 0 | Tue/Wed/Thu, 07:30–09:30 **recipient local time** | Never Mon (inbox triage) or Fri (dead) |
| 2 | Day 3 | same window, different weekday than Touch 1 | |
| 3 | Day 8 | same window | |

Hard rules: 200–400 sends/day total across all mailboxes. 20–40/mailbox/day. First 500 leads run as a monitored pilot; do not scale until complaints are under 0.1%. Any reply of any kind stops the sequence immediately. Touch 1 bounce auto-suppresses Touches 2 and 3. Re-verify the list before each touch. No `Re:`/`Fwd:` prefix on Touches 2 and 3 — ever. Demo URL gets a live HTTP 200 check *inside the send job*, per message; non-200 → skip the lead.

---

## TOUCH 1 — Day 0

**Subject lines** (rotate; C is the price-forward test cell)

- A. `{{practice}}, as a website` (~30)
- B. `I built the site behind your bio link` (37)
- C. `A real website for {{practice}} — 495 USD` (~42)

**Body — 71 words**

```
{{first_name}} — {{instagram_handle}} links to {{link_platform_phrase}},
and that's the only link on it.

I took your logo and your colours off the profile and built the site that
should be behind it: {{demo_url}}

Private link, not indexed by Google, and it comes down the moment you say
so. The booking button works — press it and a real confirmation lands in
your inbox.

It's yours to look at, nothing attached. If it's not for you, reply "no"
and I'm gone.

Milin {{surname}} — web developer, Surat, India
```

**Single CTA:** open the demo. Nothing else asked.

---

## TOUCH 2 — Day 3

**Subject lines**

- A. `{{practice}} — the demo, and what it costs` (~44)
- B. `Your demo site is still live, {{first_name}}` (~42)
- C. `{{practice}} in {{city}} — the demo site` (~40) — fires only if `city` is non-empty and ≤12 chars

**Body — 84 words**

```
{{first_name}}, someone hears your practice name, searches it, and the best
they land on is {{link_platform_phrase}}. That page isn't yours. It won't
rank for your name the way your own site would, it can't hold your reviews,
and it can't take a booking at nine on a Tuesday night.

The demo is still up: {{demo_url}}

495 USD, one payment. The site, the code and the domain registered in your
name, yours to move anywhere. Nothing ongoing to me. Usually about a week
to finish.

If you already have a site I didn't find, say so and I'll delete the demo
today.

Milin {{surname}} — Surat, India
```

**Single CTA:** reply. Demo link is support, not the ask.

---

## TOUCH 3 — Day 8

**Subject lines**

- A. `The demo site for {{practice}}` (~34)
- B. `{{first_name}}, what happens to the demo` (~40)
- C. `{{practice}} — deleting the demo in 30 days` (~45)

**Body — 79 words**

```
{{first_name}} — last one from me, then I stop either way.

The demo at {{demo_url}} deletes itself 30 days from the day I built it. I
don't keep pages carrying someone else's name and logo longer than that,
so it goes whether you reply or not.

Three ways this ends. Want it: tell me and it's yours, 495 USD, domain in
your name. Want it gone today: tell me and it's deleted within the hour.
Want me gone: the link below does that permanently.

Milin {{surname}} — Surat, India
```

The 30-day expiry must be a **real timer wired to the generator**. If demos do not actually expire, delete subject C and replace paragraph two with: `The demo at {{demo_url}} stays up either way.`

---

## FOOTER — all three touches (below signature, excluded from word counts)

```
This is an advertisement for website design services.

I found {{practice}} through your public Instagram profile
{{instagram_handle}} and used the business contact address published
there. I'm Milin {{surname}}, a web developer in Surat, India, writing to
you in your professional capacity. I keep your name, practice name and
business email only for as long as this outreach runs.

Don't want these? {{unsubscribe_url}} — one click, no reply needed, no
form. You go on a permanent do-not-contact list and I won't email you
from any of my lists again.

{{sender_address}}
```

**UK/EU recipients only — one extra line above the unsubscribe paragraph:**

```
You can object to this use of your details or ask me to delete them at any
time. Full notice, legal basis and your rights: {{privacy_url}}
```

**Headers, mandatory:** `List-Unsubscribe` + `List-Unsubscribe-Post: List-Unsubscribe=One-Click` (RFC 8058). SPF + DKIM aligned, DMARC `p=none` with `rua=` actually read. `From: Milin {{surname}} <milin@sendingdomain>`, `Reply-To` on the same domain, monitored by a human. Sending domain ≠ demo domain ≠ portfolio domain. UTF-8 verified end to end through every ESP.

---

## PITCH_HOOK — exact template the scanner generates

```
The only link on {{instagram_handle}} goes to {{link_platform_phrase}}, and a domain search on {{practice}} returned nothing live.
```

Fires only when all three hold: (a) active Instagram business profile, (b) sole outbound bio link resolves to linktr.ee / beacons.ai / campsite.bio / facebook.com / wa.me / bit.ly, (c) domain lookup on the practice name returns nothing live. Any failure → lead is not in this segment.

**`pitch_hook` is scanner-internal only.** It is a qualification record and a QA string. It is never rendered into an email body. Touch 1 sentence one is hand-written and stays hand-written. No `{{link_url}}` appears anywhere — not in the hook, not in the body, not in a subject. Nothing in the sent copy asserts that no website exists; the copy only states what the bio link points to, which is directly observed.

---

## REQUIRED MERGE FIELDS + FALLBACKS

Standing rule: **no cosmetic fallback ever prints in place of a fact.** Where the field carries the personalisation, the fallback is suppression — a rendered "Doctor" or "your practice" is worse than an unsent email.

| Field | Example | If empty / fails gate | Validation gate |
|---|---|---|---|
| `{{first_name}}` | Sarah | **SUPPRESS LEAD** | 2–15 chars, alphabetic only, not a title (`Dr`, `Dr.`, `Doctor`, `Prof`), not a token that also appears in `practice`, passes name dictionary |
| `{{practice}}` | Willow Lane Dental | **SUPPRESS LEAD** | Strip emoji/pictographs, strip leading/trailing punctuation and pipes. Reject if it contains `\|`, `http`, `@`, a 7+ digit run, or `book`/`dm`/`link below`/`⬇`. Reject if >45 chars. Title-case if fully uppercase. Reject if equal to `first_name` |
| `{{instagram_handle}}` | @willowlanedental | **SUPPRESS LEAD** | Strip any leading `@` and any `instagram.com/` prefix on ingest, prepend exactly one `@` at render. Reject if result contains `/` or `.` |
| `{{link_platform_phrase}}` | Linktree | **SUPPRESS LEAD** | Stored as a rendered phrase, not a label (table below). Never appears in a subject line |
| `{{demo_url}}` | `https://dentaldemo.site/d/willow-lane-7f3a91` | **SUPPRESS LEAD** | Full `https://` written out (bare `domain.tld/path` does not autolink in Outlook). Transliterated slug + random suffix. Live HTTP 200 check at send time, per message |
| `{{surname}}` | Shah | Renders as nothing; signature becomes `Milin — web developer, Surat, India` | Static value, not per-lead. Only degrades gracefully because it is not a personalisation claim |
| `{{city}}` | Leeds | Subject C of Touch 2 is **not offered**; rotation falls to A or B. Never appears in a body | Non-empty, ≤12 chars, alphabetic + spaces. Never paired with "near you" or "in your area" |
| `{{unsubscribe_url}}` | — | **BLOCK SEND** (hard error, alert) | Must resolve, must be genuinely one-click, no interstitial, live 30+ days |
| `{{sender_address}}` | Milin's real Surat postal address | **BLOCK SEND** (hard error, alert) | Static, must be a real address that receives mail |
| `{{privacy_url}}` | `https://milinweb.co/privacy` | **BLOCK SEND for UK/EU leads**; omit the line for US/AU | Page must be live before first send |

**`link_platform_phrase` table** (store the phrase, not the label):

| resolved domain | phrase |
|---|---|
| linktr.ee | `Linktree` |
| beacons.ai | `Beacons` |
| campsite.bio | `Campsite` |
| facebook.com | `your Facebook page` |
| wa.me | `a WhatsApp link` |
| bit.ly | `a shortened link` |

**Pre-send linter — reject the fully rendered subject and body if any of these appear:** `{{` or `}}` · `undefined` / `null` / `None` / `nan` / `N/A` · a double space · ` ,` or ` .` or `, ,` · a leading `—`, `-` or comma · an empty `()` · any emoji · any URL in the subject · subject over 60 chars. Reject = suppress the lead and alert. Never auto-repair, never substitute a default.

**Demo page requirements (gate the whole segment):** persistent non-dismissible banner — *"Unofficial demo built by Milin {{surname}}, independent web developer, Surat, India. Not affiliated with or authorised by {{practice}}. Shown for demonstration only. Remove this page: [one click]"* — plus `noindex,nofollow` meta **and** `X-Robots-Tag` header, robots.txt disallow, unguessable slug, one-click takedown honoured within the hour and logged, and 30-day auto-delete. Demo templates ship with no testimonials, no reviews widget, no before/after imagery, no prices or offers, and none of "best" / "leading" / "painless" / "#1" / "specialist" — those are the practice's regulatory exposure, not yours to create.

**Suppression:** one global, permanent, cross-segment list keyed on email hash *and* registrable domain, consulted by every segment forever. Any reply containing stop / unsubscribe / remove / not interested / take me off writes to it automatically. Suppress the whole domain after one complaint. Suppress `abuse@`, `postmaster@`, `webmaster@`, `security@`, `privacy@`, and all `.gov`, `.edu`, `nhs.uk` and hospital-system domains. UK leads send only if verified as a live Ltd or LLP at Companies House. AU leads send only where the address is conspicuously published on the practice's own site in a business capacity, with source URL and date logged per lead, and no "no unsolicited email" notice present. Kill switch: complaints above 0.2% over a rolling 1,000 sends stops the campaign.

---

## WHY THIS WORKS (3 sentences)

Sentence one states a fact the reader can verify in two seconds from their own phone, and then stops — the diagnosis clause that made the old draft sound like every agency email is gone, because a dentist can work out what a Linktree can't do without being told. The demo is described as something a person did ("I took your logo and colours off the profile") rather than as a feature list, and the three lines that actually unblock the click — private, not indexed, comes down when you say; booking button works; nothing attached — answer the suspicion that free work from a stranger always triggers, before the click rather than after. Everything past that is subtraction: no deficiency verdict, no compliance talk, no manufactured deadline, no one-word-reply tic, and a real 30-day expiry that exists for an honest reason the reader can respect.

---

## DELIBERATELY NOT FIXED

**1. No screenshot image in the email — the dentist explicitly asked for one and I overrode him.** He is right that seeing three seconds of the site would push him past the "don't tap unknown foreign links" reflex. But an `<img>` in an unsolicited message from a zero-reputation domain is blocked by default in Outlook and Gmail, so the specific reader he describes — a UK/US practice on managed IT — would see a broken placeholder icon, which is *worse* than no image, while the whole list eats the spam-score hit. The compensating moves are in the copy instead: the practice name inside the demo slug, "I took your logo and colours off the profile" as a description of what he'll see, and "private, not indexed, comes down when you say."

**2. No hand-written body variants rotated per lead.** Deliverability is correct that three fixed bodies across ~27k sends is a fingerprint, and the honest fix is 3–4 genuinely different hand-written versions per touch. I shipped one per touch because a solo sender maintaining twelve bodies will let ten of them rot, and the diluted versions would be worse copy than the best version — the volume cap (200–400/day, domain rotation, pilot-first) buys down the same volumetric risk without degrading the thing that actually earns the reply. Revisit this only after the pilot proves the copy converts.

**3. No named local reference case ("I did this for [practice] in your city — here's theirs").** The dentist says this is what would beat the email, and he's right that it's the strongest possible proof. It cannot be written until it's true, and naming a practice that isn't a client, or one that never agreed to be cited, is exactly the fabrication Rule 1 exists to prevent. The correct sequencing is: land the first three builds in any market, ask permission to cite them, then add a fourth line to Touch 2 — not invent it now.