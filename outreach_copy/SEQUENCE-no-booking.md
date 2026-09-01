# `no-booking` — FINAL 3-TOUCH SEQUENCE (production)

---

## TOUCH 1 — Day 0

**Subjects** (rotate evenly, log actual per-variant counts)
1. `Put your logo on a site with booking` [36]
2. `What your homepage looks like with booking` [42]
3. `I rebuilt your homepage as a demo` [33]

**Body**

```
{{greeting}}{{practice_domain}} has no way to book online that I could find.
Phone number{{and_form_clause}}, and that's it. You know that already.

So I put your logo, your colours and your own copy onto a homepage
that does have booking, to show you what it'd look like:

{{demo_url}}

Ten seconds. Click the booking button — that's the only part that matters.

Built by a script, so some of it's crooked. If the idea's right I put
booking on your real site and nothing else changes.

Milin, web developer, Surat, India.
```

No price. No reply asked for. One clickable link.

---

## TOUCH 2 — Day 4

**Subjects**
1. `Two days, not six weeks` [23]
2. `What booking costs to install` [29]
3. `the demo for {{practice_short}}` [~30]

**Body**

```
{{greeting_short}}the reason I sent that demo: right now a voicemail is the
only thing your site offers someone at 9pm, or while your front desk is
with a patient.

{{demo_url}}

Usually two days from getting access, not a six-week project. No kickoff
call, no content questionnaire. 449 USD, and nothing else on your site moves.

Milin, web developer, Surat, India.
```

---

## TOUCH 3 — Day 10

**Subjects**
1. `{{practice_domain}} — done either way` [~35]
2. `Nothing further from me` [23]
3. `the demo, then I'm out of your inbox` [36]

**Body**

```
{{greeting_short}}nothing further from me after this one.

The demo stays up either way, in case it's useful later:

{{demo_url}}

If it's a next-year thing, reply "later" and you'll hear nothing again.
Same if you'd rather I took the demo down.

Milin, web developer, Surat, India.
```

Sending Touch 3 writes a **permanent, global** suppression across every current and future sequence. If that can't be guaranteed, do not send Touch 3.

---

## FOOTER (all three touches, identical, plain text)

```
This is an advertisement from an independent web developer. Your address is
published at {{source_url}}. Unsubscribe: {{unsubscribe_url}} (one click, no reply).
How I got your details and your right to object: {{privacy_notice_url}}
Milin {{sender_last_name}}, {{sender_street_address}}, Surat, Gujarat {{postcode}}, India
```

Plus `List-Unsubscribe` and `List-Unsubscribe-Post: List-Unsubscribe=One-Click` headers on every send. Unsubscribe endpoint must outlive any demo teardown by ≥30 days. Suppression is immediate and automated, hard cap 48 hours, no jurisdiction branching.

---

## SEND SCHEDULE

| Touch | Day | Window | Hard stops |
|---|---|---|---|
| 1 | 0 | recipient-local Tue–Thu, 07:00–09:00 | — |
| 2 | +4 | same window, different weekday than T1 | bounce, complaint, any reply, unsub, demo-delete request |
| 3 | +10 | same | same, plus any demo click that produced a reply |

Re-scan at send time, not list-build time: a practice that installed booking between touches exits the segment mid-sequence. Cap 40/mailbox/day. Auto-pause the whole segment at bounce >2% or complaint >0.10%. No fourth touch, ever.

---

## MERGE FIELDS + FALLBACKS

Every field is trimmed at render; `""`, `" "`, `"N/A"`, `"null"`, `"-"`, `"undefined"` are all treated as missing.

| Field | Source | Fallback (what actually prints) |
|---|---|---|
| `{{greeting}}` | composed: `Dr. {{last_name}} — ` | **prints nothing.** Sentence starts at `{{practice_domain}}`, capitalised. No-name is the primary path, not the exception. |
| `{{greeting_short}}` | composed: `Dr. {{last_name}}, ` | **prints nothing.** Next word capitalised (`The reason…` / `Nothing further…`). |
| `{{last_name}}` | enrichment, verified human surname only | none — never inferred from the practice name, never from a role address |
| `{{practice_domain}}` | scan | **required — drop lead.** Render bare (`brightsmilesdental.com`), no `https://`, not anchored |
| `{{practice_short}}` | listing, ≤30 chars, no possessive, `&`→`and` | `your site` (subject 3, T2) |
| `{{and_form_clause}}` | closed list | **prints nothing** → renders `Phone number, and that's it.` Variants: ` and a contact form`, ` on your contact page` |
| `{{contact_method_found}}` | scanner, closed list, fully resolved literal | `the phone number on your site` |
| `{{demo_url}}` | generator, path-based on warmed `.com` apex | **required — drop lead** |
| `{{source_url}}` | per-lead true provenance | **required — drop lead.** Never state the practice site if the address came from elsewhere |
| `{{unsubscribe_url}}` `{{privacy_notice_url}}` | system, same apex as demo | required |
| `{{sender_last_name}}` `{{sender_street_address}}` `{{postcode}}` | static, real mail-receiving address | required |

**Render-time hard block (block, don't warn):** any rendered subject or body containing `{{`, `}}`, `undefined`, `null`, ` 's`, a double space, or a leading lowercase letter after an empty greeting is not sent.

`{{form_path}}` is gone — resolved inside the scanner. No merge field nests inside another.

---

## `pitch_hook` — what the scanner emits

The scanner no longer writes a sentence. It emits two resolved literals only:

```
contact_method_found ∈ {
  "the phone number in your header",
  "the phone number on your contact page",
  "a phone number and a contact form",
  "the phone number on your site"        ← default
}
and_form_clause ∈ { "", " and a contact form", " on your contact page" }
```

**Emission rules (all must pass, else drop the lead):**
1. Crawl completed with **JavaScript executed**, frontier exhausted, ≥5 pages reached.
2. Zero matches across the full vendor list — Calendly, NexHealth, Zocdoc, LocalMed, Setmore, Acuity, Dentrix Ascend, Denticon, Flex, Yapi, Weave, Solutionreach, Podium, Doctible, Dental Intelligence, RevenueWell, Lighthouse 360, CareStack, Curve, tab32, Simplifeye, Adit — plus `/book`, `/schedule`, `/appointment` routes, iframe and script-src checks.
3. **Google Business Profile "Book online" link checked and absent.** Facebook "Book Now" checked and absent.
4. Blocked, partial, timed out, or robots.txt disallow → drop. Never soften the sentence.
5. Page count is never printed. Neither is any consequence clause.
6. Demo QA gate before the email queues: real logo fetched (non-placeholder), ≥2 brand colours extracted, business name in the H1, booking widget renders. Any failure → drop.
7. Demo pages: `X-Robots-Tag: noindex, nofollow`; visible top banner — *"Unofficial demo by Milin {{sender_last_name}}, independent developer, Surat, India. Not affiliated with or endorsed by {{practice_short}}. Delete this demo: [one click]"*; **their own copy only** — no injected superlatives, clinical claims, ratings, testimonials or before/after imagery, even as placeholder.
8. AU only: address must be published on the practice's own site, and the scanner must find no "no unsolicited / no marketing / no vendors" notice. Otherwise suppress.

---

## WHY THIS WORKS

The click is bought by vanity, not by the fault — the dentist already knows he has no booking, so "you know that already" clears the air in four words and the real offer becomes *see your logo on a better site*. Every claim is hedged to what the crawler actually proved ("no way to book that I could find"), which is both the legal floor and the thing that makes it read as a person who looked rather than a batch that fired. "Nothing else changes" and "two days, not six weeks" move to the front because the objection was never the $449 — it was the six-week agency project.

---

## WHAT I DELIBERATELY DID NOT FIX

**1. No screenshot of the demo in the email.** The dentist is right that an inline image of his own homepage would do the work the link asks him to do himself, and it would probably lift conversion. I kept the email zero-image anyway. On a cold domain with no reputation, an embedded image is a remote fetch, a tracking-pixel-shaped object and a link/text ratio problem all at once, and the whole sequence dies at the filter before anyone gets to be delighted. This is the one place I let deliverability overrule the buyer, because a beautiful email in spam converts at zero. Revisit at 90 days of clean sending history.

**2. No proximity proof — no naming a practice down the road running the same setup.** He's right that "the practice on the next high street" beats any testimonial. I can't write it without either inventing a reference or naming a client without permission, and Hard Rule 1 forbids the first. Once there are three real installs with permission to name them, this becomes the strongest line in Touch 2 and should replace the pricing sentence's first clause.

**3. Five hash-assigned body variants per touch — specified, not written.** The deliverability audit is correct that near-duplicate clustering, not any single word, is what burns the domain, and three subjects over one body does not solve it. I shipped one body per touch because five variants of copy this tight tend to degrade into four worse versions of the good one. The correct build step is to write four genuine alternates per touch by hand — different opener, different length (roughly 45/60/80 words), different line breaks — assign by `hash(email) % 5`, hold a recipient on the same variant across all three touches, and keep each variant under 500 sends a week. Do not generate them mechanically.