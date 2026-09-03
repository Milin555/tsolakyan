# The Gap Pitch — selling a rebuild to a practice whose site already works

`OUTREACH_20.md` sells against a **defect**: "your footer says 2003", "visitors get an SSL
warning". Visceral, undeniable, and it closes fast.

But of 400 sites scanned on 1 Sep, **44 were live with no obvious defect**. Those practices
are often the better prospects — a maintained site means they already believe the website
matters and have paid for it before. You just can't use fear on them.

This is the pitch for that group.

---

## The rule

**Never say "modern", "better", "cleaner", or "more professional".**

They chose that site. They paid for it. Those words attack their judgement and are pure
opinion — they will disagree by reflex, for free.

**Bring one number they can verify themselves in 30 seconds.**

Speed is the best number available because:
- Google PageSpeed Insights is free, public and neutral
- They can check it without trusting you
- It is causally linked to lost patients, and Google publishes that link
- Your static builds genuinely win — 0.1 MB vs 2-3 MB is not a rounding error

You stop being a salesman and become someone who did them a favour.

---

## The four beats

**1. The measured gap** — their number, your number, no adjectives.
**2. The proof** — live link, same content, same brand, side by side.
**3. Their economics** — translate the gap into their own case values.
**4. Independent verification** — tell them to check it without you.

Then get out. No ask, no "would love to hop on a call".

---

## Worked example — Dr. Farzad Shaygan, Irvine Implant & Restorative Dentistry

Measured 1 Sep 2026 on `ocsidentistry.com`:

| Metric | Theirs | A static rebuild |
|---|---|---|
| Page weight | 2.54 MB | ~0.1 MB |
| Requests | 34 | ~8 |
| Render-blocking JS | 20 files | 0 |
| Load (desktop, wifi) | ~4.0 s | <1 s |
| Load (phone, 4G) | ~8-12 s | ~1.5 s |

```
Dr. Shaygan - your homepage loads 2.5 MB across 34 files. On a phone on 4G
that is roughly 8 seconds before a patient sees anything. Google's own field
data puts a large share of visitors as gone before that finishes.

I rebuilt it as a static page - same content, same branding - at 0.1 MB and
under a second:

https://milin555.github.io/demo-.../

Don't take my word for it: run both through PageSpeed Insights. It is free
and it is Google's own tool.

For a practice doing full-arch work, one extra consultation a quarter covers
this several times over. If it is not useful, ignore this and I won't follow up.
```

**Why this works on him specifically:** prosthodontist, 32 years, implants and full-arch.
Case values run $20,000-40,000. He does not need to believe in "modern design" - he needs
to believe one more consultation is worth more than the build. At his case values that is
arithmetic, not persuasion.

---

## What "real-time experience" should actually mean

Not animation. Not parallax. For a dental practice the only interactions that make money:

| Feature | Why it earns |
|---|---|
| **Real booking with live availability** | A "request an appointment" form that emails the office loses the 11pm researcher. They book with whoever answers first. |
| **One-tap call on mobile** | Most dental searches are mobile and urgent. Every extra tap loses people. |
| **Cost range on the treatment page** | Implant patients research price first. No price = they leave to find one. |
| **Before/after slider by case type** | The single strongest conversion asset in cosmetic dentistry. |
| **Sub-second load** | Everything above is worthless if the page hasn't rendered. |

---

## Claims you must not make

Be careful here. Overclaiming loses the deal at the first informed question.

- **Do not promise rankings.** You cannot control Google.
- **Do not promise "X more patients".** You have no baseline and no attribution.
- **Do not say their site is "broken"** when it isn't. Shaygan's site is well maintained -
  valid SSL, mobile viewport, alt text, a page per treatment, current copyright. Say so.
  Acknowledging what is good makes the speed gap credible.

Defensible: *speed affects conversion, here are both numbers, verify them yourself.*
Not defensible: *this will get you more patients.*

---

## When to use which pitch

| Their site | Pitch | Speed |
|---|---|---|
| Broken (SSL, 2003 footer, no mobile) | Defect pitch — `OUTREACH_20.md` | Fast, days |
| Works but slow / heavy | **Gap pitch — this file** | Slower, weeks |
| Fast, modern, well-converting | Don't pitch a rebuild. Offer the $99/mo care plan | Long |
