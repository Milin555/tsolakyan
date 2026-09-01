# Locked-platform — 3-touch cold email sequence

Plain text only. One link per email, on its own line. No tracking pixel, no HTML, no images — clinician spam filters and clinician patience both punish them.

---

## Merge fields this segment needs

| Field | What it holds | Fallback if missing |
|---|---|---|
| `{{greeting_name}}` | `Dr. {{last_name}}` when a named clinician is on record | `{{practice}} team` |
| `{{practice}}` | Practice name exactly as written on their site | required — suppress lead if absent |
| `{{domain}}` | Bare domain, no `https://` (`waimeadental.com`) | required |
| `{{platform}}` | Exact fingerprint: `ProSites`, `PBHS`, `Officite`, `Dentalfone`, `Optimized360` | required — suppress lead if ambiguous |
| `{{platform_evidence}}` | The **literal string** the scan found, quoted verbatim (`"DESIGN AND CONTENT © 2013-2026 BY DENTALFONE"`, `/prosites/assets/` in a stylesheet path, `<meta name="generator" content="Officite">`) | required — no evidence, no send |
| `{{evidence_location}}` | Where it sits: `in the page footer`, `in the homepage source`, `on the DNS record for` | required |
| `{{demo_url}}` | Live personalised rebuild | required |
| `{{price_band}}` | One number where page count allows (`$1,400`), else `$1,200–2,500` | `$1,200–2,500` |
| `{{unsubscribe_url}}` | One-click, no login, no reply needed | required |
| `{{postal_address}}` | Real postal address, CAN-SPAM | required |
| `{{pitch_hook}}` | Scanner-generated, template below | required |

**Hard gate:** `{{platform}} == ProSites` is the only case where the contract quote may be used. Everything else routes to Touch 2 Variant B. Wire this as a branch, not a note to yourself.

---

## The `pitch_hook` template the scanner generates

```
{{platform_evidence}} — {{evidence_location}} {{domain}}. That's {{platform}}: a dental
vendor platform sold as a monthly subscription rather than as a site you hold the files to.
```

Renders as:

> `"DESIGN AND CONTENT © 2013-2026 BY DENTALFONE" — in the page footer of waimeadental.com. That's Dentalfone: a dental vendor platform sold as a monthly subscription rather than as a site you hold the files to.`

Every word is scan-derived or publicly true of all five vendors. No consequence, no threat, no legal claim.

---

## TOUCH 1 — day 0 (80 words)

**Subject options**
1. `Who owns your website files` (27)
2. `{{practice}} — a rebuilt homepage` (requires practice ≤ 24 chars, else use 1 or 3)
3. `The {{platform}} line on your site` (30–38)

**Body**

```
{{greeting_name}},

{{pitch_hook}}

So I rebuilt your homepage as something you'd own outright. Live now,
nothing to install:

{{demo_url}}

Concept only, not indexed, every page marked unaffiliated. If the
direction's right I'll finish it, move it to {{domain}} and hand you
the code. If not, ignore this.

Milin Dholiya
Surat, India
```

**Single CTA:** click the demo link. No price, no meeting ask, no question to answer.

---

## TOUCH 2 — day 3 — *branches on platform*

New angle: ownership and the exit. Not a bump — this email never references Touch 1.

**Subject options**
1. `One line from ProSites' own terms` (33) — **Variant A only** / `Two questions for {{platform}}` (30 max) — **Variant B only**
2. `Who actually owns your website` (30)
3. `Before your next renewal` (24)

### Variant A — ProSites leads only (58 words)

```
{{greeting_name}},

ProSites' own terms:

"The Customer's website (including all graphical content and related HTML
coding provided by ProSites) is the property of ProSites and the Customer
has no rights to the website beyond the terms of its subscription."

Moving off it is {{price_band}}, once. The code ends up yours.

Reply "how" and I'll lay out the steps.

Milin
```

### Variant B — PBHS / Officite / Dentalfone / Optimized360 (49 words)

```
{{greeting_name}},

Two questions worth putting to {{platform}} before your renewal date:

If we leave, do we keep the design and the site files?
Is there a way out mid-term?

However that lands, rebuilding it as yours is {{price_band}}, once.
Reply "how" and I'll lay out the steps.

Milin
```

**Single CTA:** reply with one word. The demo link is deliberately absent here so the ask is unambiguous.

---

## TOUCH 3 — day 7 (42 words)

**Subject options**
1. `Closing this out` (16)
2. `Last one from me` (16)
3. `I'll stop here` (14)

**Body**

```
{{greeting_name}},

Last email from me.

The demo stays up either way: {{demo_url}}

If {{platform}} ever stops working for you, the rebuild is {{price_band}}
and I'm one reply away. Otherwise I'll leave you to it — good luck with
the practice.

Milin
```

**Single CTA:** reply. No deadline on the demo — a fake expiry is manufactured urgency and this audience smells it.

---

## Compliance footer — appended to all three touches

Not counted in the body word limits above.

```
—
Milin Dholiya · independent web developer · Surat, Gujarat, India
{{postal_address}}
Don't want these? {{unsubscribe_url}} — one click, no reply needed.
```

Two operational flags:
- **UK leads (1,681):** under PECR, sole traders and partnerships count as individual subscribers, not corporate. A large share of UK practices are exactly that. Route UK leads through a separate list with tighter consent handling rather than assuming B2B exemption covers them.
- Honour unsubscribes across all three touches instantly — a Touch 1 opt-out must kill Touch 2 and 3 the same day.

---

## Price: which offer, named where

**Offer to name:** full migration off the locked platform — `$1,200–2,500`, or a single computed number.

**Where it goes:**

| Touch | Price | Why |
|---|---|---|
| 1 | Never | The demo is the whole hook. A number in the opener turns a curiosity click into a budget decision before they've seen anything. |
| 2 | **First named here** | By day 3 they've either clicked or not. Naming it filters out the "just curious" and kills the "what does this cost" stall that eats a whole reply cycle. |
| 3 | Restated once, flat | Costs four words and makes the breakup actionable months later when their renewal actually lands. |

Prefer one number over the range wherever the scan gives a page count — `$1,400` gets a yes or a no, `$1,200–2,500` gets a negotiation.

**Do not name in this sequence:** the $149/mo care plan. It is the second conversation, after they've said yes to the migration. Two prices in a cold email reads as a menu, and menus get closed.