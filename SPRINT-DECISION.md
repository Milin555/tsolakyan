# SPRINT DECISION — 22 Aug → 15 Sep 2026
**Output of the 4-agent research run. Target: $1,000–2,000 COLLECTED.**

---

## THE HARD CONSTRAINT NOBODY BUILT INTO THE PLAN

**"Collected" means money in a bank account, not a signed deal.**

Verified: on Dodo Payments' **default** cycle, a sale made 1–15 Sep pays out **18 Sep — after your deadline.** Only sales closed by 31 Aug pay out 4 Sep.

**Therefore your real deadline is not 15 Sep. It is ~5 Sep for high-ticket international sales.**
That is **14 days**, not 24.

Two ways to beat it:
1. **Razorpay** — verified to onboard Indian individuals on personal PAN, video KYC ~3–4 min, settles **INR domestically** (no foreign payout leg). Payment Links let you invoice one client with no checkout build.
2. **Sell to Indian customers in INR via UPI** — instant, no payout cycle at all.

**BLOCKED / DO NOT USE:**
- Stripe India self-serve — India is "Preview", contact-sales only. (This also kills ExtensionPay, a Stripe wrapper.)
- AppSumo — Net-60 from month end. An August sale pays in November.
- Lemon Squeezy, Paddle, Polar, Gumroad, PayPal, Wise, Payoneer — **UNVERIFIED**, docs 403/404/login-walled. Do not assume.

⚠️ **Two open questions to close with a human, not a search engine:**
- Razorpay's actual international-card activation timeline for an individual account
- FIRC/FIRA, purpose codes, and RBI treatment of export-of-service receipts. **Entirely unverified.** Get an accountant on this before invoicing abroad.

---

## THE DECISION

**PRIMARY: Dental "broken right now" rescue + Linktree rebuilds.**
**PARALLEL VALIDATION: Indian weight-discrepancy recovery (brother's data, this week).**

Not a hedge — they consume different resources. Dental uses your dev time, templates and list. The India play uses your brother's time, his data and his WhatsApp groups. Running both costs you almost nothing extra and roughly doubles your shots.

### Why dental is primary
- **Zero build.** 4 Webflow templates + `deploy_all.py` + `gh` authed. Ships today.
- **List exists.** 23,388 records with websites. 212 with no website at all.
- **Highest ticket.** ProSites migration $1,200–2,500 — one close nearly ends the sprint.
- **Verified evidence base.** Faults already documented in `dental-prospects.json`.

### Why the India play is validation-gated, not primary
- **Price is unproven.** Sellers anchor at Shiprocket's ₹199–799/mo. Asking ₹15,000–25,000 is a 20× jump. It may work when framed against ₹67,000 blocked — but nobody has tested it.
- **You don't control the outcome.** Shiprocket decides whether to refund. Sell the *audit and filing pack* (labour you control), never the recovery.
- **But its mechanics are better than dental's:** INR/UPI is instant, and WhatsApp distribution carries no spam-law exposure.

If your brother's data shows a ₹20,000+ leak, this becomes primary immediately.

---

## THE FOUR OFFERS (ranked, all ship with what you already own)

| # | Offer | Price | Build | First $ | Source list |
|---|---|---|---|---|---|
| 1 | **Emergency site rescue** — DNS dead, SSL expired, 404s, broken forms | **$299 flat** | 1 day | **2–4 days** | Scanner over 23,388 URLs |
| 2 | **Linktree → real site** | **$495** | **0 days** | 2–5 days | 212 pre-qualified (168 linktr.ee + 44 bit.ly) |
| 3 | **ProSites escape migration** | **$1,200–2,500** | 0 days | 5–10 days | Filter US records for ProSites/PBHS/Officite fingerprints |
| 4 | **Booking-gap install** | **$449** | 2 days | 3–6 days | 16 of 24 audited sites lack booking (67% hit rate) |

**#2 priced at $495, not $349** — market's own beginner floor is $500–1,500. Pricing below it signals amateur. Verified: new signups converted at **16% vs 0.8%** for an existing list at $295–750 price points. Higher prices convert *better* here.

**#3 is the swing.** ProSites' own terms, verbatim:
> *"The Customer's website (including all graphical content and related HTML coding provided by ProSites) **is the property of ProSites** and the Customer has no rights to the website beyond the terms of its subscription."*

That is your subject line. It's their contract, not your claim.

---

## KILLED BY RESEARCH — do not build these

| Idea | Why it died |
|---|---|
| **Standalone paid website audit $49–199** | Free dental audits are saturated lead magnets (GrowthPlug, Dental Revenue, WebsiteLinter). MySiteAuditor sells the *tooling* at $49–79/mo to agencies who give the output away. No vendor found selling a paid audit to dentists. **The audit is the door-opener; the fix is the product.** |
| **HIPAA tracking-pixel audit** | The underlying legal theory was **vacated by a federal court in June 2024 (*AHA v. Becerra*)**; OCR withdrew its appeal. Selling doctors a dead legal theory is wrong and dangerous. **KILLED.** |
| **Marketplace reconciliation SaaS** | TheSellerBuddy (Vanani & Associates, CA firm, Ahmedabad) gives 7 such tools free, funded by GST compliance retainers. |
| **Indian seller SaaS at $49/mo** | Price anchor is Shiprocket ₹199–799/mo. ₹4,300/mo is absurd. Zoho Books India is **free** under ₹25 lakh revenue. Two incumbents just exited: browntape → ginesys, evanik → zobrx. |
| **AI/AEO visibility audit (standalone)** | A dentist can ask ChatGPT for free in 10 seconds. Otterly's $29 tier undercuts any one-time report. Use as a bonus page inside a paid deliverable. |
| **Review-reply tooling** | Real pain, but the cause is Google's platform behaviour. You cannot fix it. Refund magnet. |
| **Any app-store channel** | Slack ~10 weeks (needs 5 workspaces before submission). Zapier 90-day beta, no revenue mechanism. Notion waitlist. Shopify public listing: review gate *is* the billing gate. Chrome is the only viable one (Google killed its own payments in 2021, so your checkout is live regardless of queue) — but budget 3–10 days. |
| **Product Hunt / directory submissions** | PH largely dead for revenue in 2026 — 7th place → ~50 visitors. HN sends >10× PH traffic. Zero evidence "submit to 100 directories" produces customers. |
| **Boilerplates** | Actively declining. ShipFast down to $2.8k/mo from $250k/5mo, and Marc Lou had a 35,000-person audience first. |

---

## THE 24-DAY PLAN

### Days 1–2 (22–23 Aug) — UNBLOCK, BUILD NOTHING
- [ ] **Start Razorpay activation.** Personal PAN + Aadhaar video KYC. This is the critical path.
- [ ] **Send yourself a $1 test payment** end-to-end. Confirm it lands. Do not skip.
- [ ] Call an accountant re: FIRC / purpose codes / export-of-service. One call.
- [ ] **Fix email infrastructure.** Real sending domain, SPF/DKIM/DMARC, warm-up started. **Drop Canada (CASL) and EU from the cold list entirely.**
- [ ] Brother: pull last 6 months of Shiprocket data. Declared weight vs charged weight, line by line.
- [ ] Write the broken-site scanner (DNS, SSL, HTTP status, dead images) over the URL column.

### Days 3–5 (24–26 Aug) — FIRST OFFERS OUT
- [ ] Run scanner across all 23,388 URLs. Sort by severity.
- [ ] **Offer #1 live:** email the top 100 broken sites. Subject = their specific fault.
- [ ] **Offer #2 live:** Instagram DM the 212 link-in-bio practices. Attach a live rebuilt demo.
- [ ] Score brother's leak. **If ₹20,000+ → India play goes primary.**

### Days 6–10 (27–31 Aug) — VOLUME + THE SWING
- [ ] 100+ contacts/day across offers #1 and #2
- [ ] Fingerprint US records for ProSites/PBHS/Officite → **Offer #3** to the top 50
- [ ] Build 3 live demo sites for the highest-value #3 targets *before* emailing them
- [ ] **Close anything you can by 31 Aug** — this is the safe-payout date

### Days 11–17 (1–7 Sep) — CONVERT
- [ ] Follow up 3× on every send. Most replies come on touch 2–4.
- [ ] Phone the UK list (`uk_call_list.csv`, 361 rows) — email + call same week converts far better
- [ ] Deliver fast. Same-day delivery generates referrals inside the deadline.

### Days 18–24 (8–15 Sep) — LAND THE MONEY
- [ ] Chase every unpaid invoice **daily**
- [ ] Offer a small discount for immediate payment — cash today beats more tomorrow
- [ ] Stop selling on 12 Sep. Spend the last 3 days collecting.

---

## THE NUMBERS

| Path | Price | Sales needed |
|---|---|---|
| Emergency rescue | $299 | 4–7 |
| Linktree rebuild | $495 | 2–4 |
| ProSites migration | $1,500 avg | **1–2** |
| Mixed realistic | — | **3–5 total** |

**Daily outreach target: 100–150 contacts.** At 2–5% cold reply → 3–7 conversations/day → 3–5 closes over 24 days.

---

## HONEST ODDS

**P(collect $1,000 by 15 Sep): ~55–65%.**

**What drives it up:**
- Zero build required — templates and list already exist
- 23,388 addressable records is genuinely a lot of shots
- One ProSites close alone nearly ends it
- The India play is a second independent shot at almost no marginal cost

**What drives it down:**
- **Payment activation is the single biggest risk.** If Razorpay takes 10 days or the FIRC question blocks you, nothing else matters.
- Payout timing compresses 24 days to ~14 for international sales
- Cold email at volume from a cold domain will underperform for the first week
- High-ticket (#3) closes on a call, not a card — that takes time you may not have

**Most likely failure mode:** you sell $1,500 by 12 Sep and only $400 has actually *landed* by 15 Sep.

**Leading indicator — check on 1 Sep:** if you have **zero paid invoices** by then, stop chasing high-ticket and push volume on #1 and #2 at whatever price closes today.

---

## THE FIVE RULES

1. **Payment rails before product.** An unbanked sale is not collected money.
2. **Close by 5 Sep, not 15 Sep.** Payout cycles eat the difference.
3. **Sell the fix, never the audit.** The audit is free; it opens the door.
4. **Never promise an outcome you don't control** — not a lawsuit avoided, not a refund recovered, not "compliance." Report what you found, charge for what you do.
5. **Higher price converts better.** $495 beats $349. $1,500 beats $800. Do not discount out of fear.
