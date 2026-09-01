# THE PLAYBOOK — $5,000 by 15 September 2026

**Written 17 Aug 2026 · 29 days · target $5,000 · minimum manual work**

---

# PART 0 — HOW TO USE THIS

Read Part 1 and Part 4 today. Everything else is reference — open it when you reach that day.

**The one rule:** if you only ever do one thing from this document, run the automation in Part 6 and answer replies. Everything else is optimisation.

## 0.1 — The honest probability model

You asked me to never hide numbers. Here they are.

| Outcome by 15 Sep | Probability | What it needs |
|---|---|---|
| $0 | 12% | You stop after week 1 |
| $500–1,500 | 28% | One or two channels run, some replies |
| $1,500–3,000 | 25% | Automation runs, 3–5 small deals |
| $3,000–5,000 | 20% | Above + one high-ticket close |
| **$5,000+** | **15%** | Everything runs + 1–2 high-ticket + luck |

**Realistic centre of gravity: $1,500–3,000.**

$5,000 is a genuine stretch, not a sure thing. I'm telling you that because a plan built on a lie fails silently — you'd blame yourself in September instead of blaming the estimate.

**But:** $5,000 by 15 October is roughly 55%. Nothing here is wasted if it lands late.

## 0.2 — Why the number is what it is

$5,000 in 29 days means roughly **8–10 closed deals**, or **3–4 if high-ticket**.

Working backwards from a realistic funnel:

```
8 deals
÷ 12% close rate (cold, no calls, no testimonials)
= 67 genuinely interested people
÷ 25% of repliers being interested
= 268 replies
÷ 3.5% reply rate
= 7,650 outbound touches
```

**7,650 touches in 29 days = 264/day.** That is only possible with automation. It is not possible by hand. This is why Part 6 exists.

## 0.3 — What automation can and cannot do

This is the most important table in the document. Be honest with yourself about it.

| Task | Automatable? | Reality |
|---|---|---|
| Lead cleaning, dedup, scoring | ✅ 100% | Already half-built |
| Generating personalised demo sites | ✅ 100% | `rebrand_automation.py` exists |
| Deploying to live URLs | ✅ 100% | GitHub Pages API |
| Sending email + follow-ups | ✅ 100% | `campaign_manager.py` exists |
| Detecting replies, updating CRM | ✅ 100% | `check_replies.py` built today |
| Submitting contact forms | ⚠️ ~70% | Form structures vary; rest is manual |
| Drafting proposals | ✅ 100% | AI drafts, you paste |
| Instagram DMs | ❌ **0%** | **Automation = permanent ban** |
| LinkedIn outreach | ⚠️ 30% | Automation risks restriction |
| **Sales conversations** | ❌ **0%** | Human. Always. |
| Delivery + revisions | ⚠️ 50% | Rebrand automated, comms are not |
| Getting paid | ❌ 0% | Human |

**The honest summary:** you can automate everything up to the reply. After a reply, it's you.

That's fine — reply volume is low. **Realistic manual load: 45–75 minutes/day.** Mostly answering messages.

Anyone selling you "fully automated client acquisition" is selling you a ban or a refund.

## 0.4 — The strategy in five lines

1. **Fix email** — it's the only channel that scales to thousands with zero daily effort. 29 days now fits the 14-day warmup that 7 days didn't.
2. **Put a live, personalised demo in message one.** Never ask "can I send you the link?"
3. **Run 5 channels in parallel** so no single failure kills the month.
4. **Sell the expensive products too**, not only $397 dental sites.
5. **Follow up 5 times.** Your single biggest historical failure.

---

# PART 1 — WHY YOUR EMAIL GOT NO REPLIES

You said you think they landed in spam. **Partly right, but spam is not the main reason** — and getting this wrong would make you fix the wrong thing.

## 1.1 — What was actually wrong, ranked by impact

### Cause #1 — You never included a link 🔴 **Biggest cause**

Your email said:

> *"I actually spent the last 10 hours building a custom, modernized version of your entire site from scratch... **can I send over the live link** and a quick video?"*

Look at what you asked a stranger to do: **reply to an unknown sender, then wait**, to see something they can't verify exists.

That is a high-effort ask for zero immediate value. Even with perfect inbox delivery, that email converts at roughly **0.3–0.8%**.

And here's the part that stings: **there was no link to send.** All 7 demos have zero live URLs. Even someone who replied "yes, send it" would have waited while you scrambled.

**Fix:** the live link goes in message one. No permission needed. They click, they see their own practice, done.

### Cause #2 — Follow-ups never sent 🔴 **Code bug**

`campaign_manager.py:249` set `target_step = 1` instead of `2`. Result: **1,750 leads stuck at step 1, exactly 1 ever reached step 2.**

Industry-wide, **60–80% of cold email replies come from touches 2–5.** You sent touch 1 to 1,751 people and touch 2 to one person.

Fixed today — now a real 5-touch sequence over 18 days.

### Cause #3 — 18 lookalike free Gmail accounts 🟠 **Real, but third**

`milindholiya01/02/03/…`, `dholiyamilin4/5/6/…`

Free Gmail *does* pass SPF and DKIM — that part was fine. The problems are different:

- **Google's own outbound filtering.** 18 near-identical accounts sending near-identical mail to strangers gets throttled at the source. Some of your mail likely never left Google.
- **No domain reputation to build.** On `gmail.com` you inherit a shared reputation you cannot influence.
- **Recipient-side filtering.** Business mail servers score unknown `@gmail.com` senders harshly for commercial content.
- **No DMARC control, no tracking domain, no way to diagnose.**

### Cause #4 — Instagram-scraped addresses are low quality 🟡

Many of those addresses are `info@`, `contact@`, `hello@` — shared inboxes checked by a receptionist who has no authority to buy a website and every incentive to delete unsolicited mail.

### Cause #5 — You never checked for replies 🔴

**Zero leads marked `Replied`. Zero marked `Bounced`.**

You may have had replies. You never looked. That's what's running in the background right now.

## 1.2 — MEASURED RESULTS (not theory)

I scanned all 18 inboxes on 17 Aug. All 18 logged in — **your accounts are not banned.** Here is exactly what came back:

```
Total inbound messages:        301
  Your own test emails:        215   ← test_all_accounts.py talking to itself
  Real external senders:        86
    SaaS marketing to you:      79   ← instantly.ai (40), apify (11), gmail (19)
    Actual leads from CRM:       7
```

**The 7 messages from real leads, in full:**

| From | Type | Reality |
|---|---|---|
| jlevesque@acdq.qc.ca | `Réponse automatique` | out-of-office |
| jdupuis@acdq.qc.ca | `Réponse automatique` | out-of-office |
| bertrand@emrn.ca | `Réponse automatique` | out-of-office |
| ctetreault@galenova.com | `Réponse automatique` | out-of-office |
| patricia@impactortho.com | `Re: your site` | **"Please remove my email from your list"** |
| eg@gdawny.com | unsubscribe | removal request |
| joanne.blazey@envistaco.com | unsubscribe | removal request |

### The actual numbers

| Metric | Value |
|---|---|
| Emails sent | 1,751 |
| Total responses | 7 → **0.40%** |
| Auto-replies (not human) | 4 |
| Removal requests | 3 |
| **Genuinely interested humans** | **0 → 0.00%** |

**A normal cold email campaign gets 1–3% replies. You got zero interest and three people asking to be removed.**

That is not a marginal underperformance. It's a complete failure, and it's worth sitting with for a second rather than explaining away — because the fix depends on naming the cause correctly.

### What this proves

**Your accounts work.** All 18 logged in fine. Not banned.

**Mail was being delivered — at least partly.** Four French auto-responders fired. An out-of-office only triggers on a message that reached a live mailbox. So at minimum, some mail arrived.

**Therefore spam filtering was not the whole story.** You assumed spam. The data says the bigger problem was the email itself:

- no link to click
- an ask that required a reply before any value
- exactly one follow-up across 1,751 people

**This is genuinely good news.** Deliverability is expensive and slow to fix. An offer is free to fix, and you can fix it today.

If the cause had been spam filtering, the fix would be $79 and 14 days of warmup with no guarantee. Instead the cause is: **you asked strangers for permission to show them something that didn't exist, once.** Put a live link in message one and follow up five times, and you are testing a genuinely different offer — not the same one louder.

> ⛔ **Do not contact these three again — ever:**
> `patricia@impactortho.com` · `eg@gdawny.com` · `joanne.blazey@envistaco.com`
>
> They asked to be removed. Emailing them again is illegal under CAN-SPAM and GDPR, and it's the fastest way to get a spam complaint filed against your domains. They are now marked `Unsubscribed` in the CRM so the sequence can never reach them.

## 1.3 — The corrected email

| Old | New |
|---|---|
| "can I send the link?" | **link in message 1** |
| 2 touches (1 real) | **5 touches over 18 days** |
| free Gmail ×18 | **3 real domains, 6 inboxes, SPF/DKIM/DMARC** |
| no tracking | **reply detection + CRM sync** |
| generic template | **their practice name, their live site** |

---

# PART 2 — WHAT YOU ACTUALLY OWN

You have far more than you've been selling. Full inventory:

## 2.1 — Product assets

| Asset | What it is | Sells as | Price |
|---|---|---|---|
| `Gary Solnit Dentist` | 430 files, multi-page dental | Practice site | $497 |
| `Lura Dentist` | 432 files + blue variant | Practice site | $497 |
| `Modern Smile Center` | 432 files | Practice site | $497 |
| `Ritter Ramsey Dentist` | 435 files | Practice site | $497 |
| **`dr-ritter-academy`** | **Course platform + real testimonial videos, masterclass video** | **Academy** | **$2,497** |
| **`dr-jim-arnold-hub`** | **113KB coaching authority hub** | **Authority Hub** | **$1,497** |
| `the-protocol-prototype` | React 19 + Vite + Tailwind 4, built | Premium funnel | $1,497 |
| `d2c-template` | Full store: index, product, cart, WebP | E-com store | $997 |
| `saidharanx-demo` | Catalogue + PDF generation | Catalogue site | $797 |
| `foundation-dental-retreats` | Event/retreat lander | Landing page | $397 |
| `ritter-metz-static` | Video-led lander | Landing page | $397 |

**Total distinct sellable products: 11.** You have been pitching 4 of them, at your lowest price.

## 2.2 — Data assets

| File | Rows | Use |
|---|---|---|
| `clean_verified_leads.csv` | **30,745 — all verified valid** | **Email engine fuel** |
| ...of which **never contacted** | **30,688** | Fresh pool |
| `dm_call_list.csv` | 7,248 paying-market dental | DM + forms |
| `A_LIST_dm.csv` | 107 no-website + 5k followers | Highest priority |
| `form_list.csv` | 6,283 with websites | Contact forms |
| `USA.csv` | 18,911 | US volume |
| `campaign_crm.csv` | 1,751 already-touched | Re-engage |
| `prospects.md` | 6 named coaching prospects | **Highest value** |

## 2.3 — Infrastructure

- `gh` authenticated as `Milin555` — free instant deploys
- Python + Node + git installed
- `campaign_manager.py` — 5-touch engine (fixed today)
- `rebrand_automation.py` — template personalisation
- `check_replies.py` — reply detection (built today)
- `deploy_all.py` — mass deployment (built today)
- **Claude 20x** — effectively unlimited drafting, coding, research capacity

## 2.4 — Structural advantages

- **India-based:** ₹ cost base, $ revenue. A $497 site is a strong day's work locally. You can profitably undercut every Western freelancer.
- **UPI:** instant payment from local clients. No 3-day clearing.
- **You can build fast:** template swap, not custom build. Real 48-hour delivery.

## 2.5 — What you're missing

| Gap | Impact | Fix | Time |
|---|---|---|---|
| **No live URLs** | 🔴 Blocks everything | `deploy_all.py` | 15 min |
| **No payment account** | 🔴 Can't get paid | Wise/Payoneer | 20 min + 2 days |
| No testimonials | 🟠 Halves close rate | First client | week 1 |
| No sending domains | 🟠 Blocks email | Buy 3 | $36 |
| No portfolio page | 🟠 No single link | Build | 1 hr |
| No brand/identity | 🟡 Looks amateur | Name + logo | 2 hrs |

---

# PART 3 — EVERY WAY TO MAKE MONEY, SCORED

You asked for all possible ways, not just selling websites. Here are **41**, each scored on what it can realistically produce in 29 days.

Scoring: **Speed** (cash velocity) · **Effort** (manual load — lower is better) · **Ceiling** (realistic $ by 15 Sep)

## 3.1 — Service offers (selling work)

| # | Offer | Price | Speed | Effort | Ceiling | Verdict |
|---|---|---|---|---|---|---|
| 1 | Dental practice site | $497 | 🟢 | 🟡 | $2,500 | ✅ **Core** |
| 2 | Course/Academy platform | $2,497 | 🟡 | 🟡 | $2,500 | ✅ **Core** |
| 3 | Authority hub (coaches) | $1,497 | 🟡 | 🟡 | $3,000 | ✅ **Core** |
| 4 | E-commerce store | $997 | 🟡 | 🟠 | $1,000 | ✅ Run |
| 5 | Landing page / funnel | $397 | 🟢 | 🟢 | $1,200 | ✅ Run |
| 6 | **Speed optimisation** | $197 | 🟢🟢 | 🟢 | $1,000 | ✅ **Underrated** |
| 7 | **Mobile fix** | $147 | 🟢🟢 | 🟢 | $700 | ✅ **Underrated** |
| 8 | SEO audit + fixes | $297 | 🟡 | 🟡 | $600 | ⚠️ Optional |
| 9 | Google Business Profile setup | $147 | 🟢 | 🟢 | $500 | ✅ Easy add-on |
| 10 | **AI chatbot install** | $297 | 🟢 | 🟢 | $900 | ✅ **High margin** |
| 11 | **Missed-call-text-back** | $197+$47/mo | 🟢 | 🟢 | $600 | ✅ **Dentists love this** |
| 12 | Review generation setup | $197 | 🟢 | 🟢 | $400 | ⚠️ Optional |
| 13 | Booking system integration | $197 | 🟢 | 🟡 | $400 | ⚠️ Add-on |
| 14 | AI blog/content pack | $147 | 🟢 | 🟢 | $600 | ✅ Pure margin |
| 15 | Logo / brand kit | $97 | 🟢 | 🟢 | $300 | ✅ Add-on |

**Why #6 and #7 are underrated:** they're **provable**. You run PageSpeed Insights on their site, screenshot a score of 34/100, and say *"I'll get this to 90+ for $197, or you pay nothing."* No trust required — the number is public and verifiable. Delivery is 2 hours. It's the fastest yes available to you, and it turns into a website sale later.

## 3.2 — Recurring revenue

| # | Offer | Price | Ceiling by 15 Sep | Verdict |
|---|---|---|---|---|
| 16 | Care plan (hosting + edits) | $97/mo | $500 | ✅ Offer to all |
| 17 | Hosting resale | $29/mo | $150 | ✅ Bundle |
| 18 | Monthly content | $197/mo | $400 | ⚠️ Later |
| 19 | Chatbot subscription | $47/mo | $200 | ✅ Bundle |

**Reality:** recurring won't move the 29-day number much (one month of $97 is $97). But 6 care plans = **$582/month forever**, which is October's floor already covered. Always offer it. Never count on it for September.

## 3.3 — Leverage: other people sell for you

| # | Channel | Speed | Effort | Ceiling | Verdict |
|---|---|---|---|---|---|
| 20 | **White-label for marketing agencies** | 🟡 | 🟢 | **$2,000** | ✅ **Highest leverage** |
| 21 | Subcontract for busy freelancers | 🟢 | 🟢 | $1,200 | ✅ **Run this** |
| 22 | Partner with dental consultants | 🟠 | 🟡 | $1,500 | ⚠️ Slow |
| 23 | Referral commission to coaches | 🟠 | 🟢 | $800 | ⚠️ Optional |
| 24 | Partner with local web agencies | 🟢 | 🟢 | $1,000 | ✅ Run |

**#20 is the single most underrated play in this document.**

Marketing agencies that serve dentists sell websites but often don't build them. They have the clients; they need a builder. **One agency relationship can send 3–10 builds a month at $300–400 each.**

Why it beats end-client outreach:
- Agencies **reply** — it's their business, not an interruption
- **No sales conversation** — they already sold it
- **Repeat volume** from one yes
- They don't care that you're in India; they care that you're fast and cheap
- No testimonials needed — your demos are the proof

**One agency partnership can be worth more than 100 dentist DMs.**

## 3.4 — Marketplaces (buyers come to you)

| # | Platform | Speed | Effort | Ceiling | Payment delay | Verdict |
|---|---|---|---|---|---|---|
| 25 | **Upwork** | 🟡 | 🟢 | $1,500 | 5d + withdrawal | ✅ **Run daily** |
| 26 | Fiverr | 🟠 | 🟢 | $800 | **14d new seller** | ✅ Set up, don't rely |
| 27 | Freelancer.com | 🟡 | 🟢 | $500 | ~7d | ⚠️ Optional |
| 28 | PeoplePerHour | 🟡 | 🟢 | $500 | ~7d | ⚠️ Optional |
| 29 | Contra | 🟡 | 🟢 | $400 | fast | ⚠️ Optional |
| 30 | Facebook job groups | 🟢 | 🟡 | $600 | direct | ✅ Run |
| 31 | r/forhire | 🟢 | 🟢 | $400 | direct | ✅ Free, run it |

**Critical:** Fiverr holds new-seller funds **14 days** after delivery. A Fiverr sale on 5 Sep pays out around 19 Sep — *after* your deadline. Set it up because it compounds, but do not count it in the $5,000.

## 3.5 — Digital products (passive)

| # | Channel | Price | Ceiling | Verdict |
|---|---|---|---|---|
| 32 | Gumroad — template pack | $79 | $400 | ⚠️ Needs traffic |
| 33 | **Etsy — website templates** | $39 | $600 | ✅ **Has organic traffic** |
| 34 | Creative Market | $49 | $300 | ⚠️ Approval delay |
| 35 | ThemeForest | $24 | $200 | ❌ 2–4 wk approval |
| 36 | Sell your automation scripts | $49 | $200 | ⚠️ Niche |

**Honest math:** $5,000 from $79 products = 63 sales. You have no audience and no traffic. **Digital products will not hit your number.** Etsy is the only one worth 2 hours because it has native search traffic — treat any sales as a bonus, not a plan.

## 3.6 — Local market (India)

| # | Channel | Speed | Effort | Ceiling | Verdict |
|---|---|---|---|---|---|
| 37 | **Local clinics/salons — UPI** | 🟢🟢🟢 | 🟠 | **$1,500** | ✅ **Fallback** |
| 38 | Local gyms, cafés, boutiques | 🟢🟢 | 🟠 | $800 | ✅ Fallback |
| 39 | Local agencies (white-label) | 🟢 | 🟢 | $1,000 | ✅ Run |

**Why this is your insurance policy:** UPI is **instant**. No Wise, no clearing, no 14-day hold. A local clinic can see your demo and pay in the same afternoon. ₹20,000 ≈ $230; four of them ≈ $920.

Higher effort (you leave the house), lower ticket, but **the highest close rate of anything here** — because you're a real person standing there, not an unknown email.

## 3.7 — Inbound / content

| # | Channel | Speed | Effort | Ceiling | Verdict |
|---|---|---|---|---|---|
| 40 | Public teardown videos | 🟠 | 🟡 | $400 | ⚠️ Compounds later |
| 41 | SEO on generated demo sites | 🟠 | 🟢 | $200 | ✅ Free side effect |

**#41 is free:** when you auto-generate 500 demos titled *"Dr. Smith Dental — Website Concept"* and deploy them publicly, some dentists Google themselves and find it. Zero extra effort, small but real.

## 3.8 — Things I considered and rejected

Told plainly so you don't waste days on them:

| Idea | Why not |
|---|---|
| Selling the 30k lead database | Low value, hurts your reputation, likely GDPR issues |
| Flippa / site flipping | Needs traffic history; 29 days is nowhere near enough |
| Dropshipping / affiliate | Different business, starts at zero, no leverage from your assets |
| Crypto/trading | Not a business plan |
| Buying leads | You have 30,745 unused verified ones |
| Paid ads | $5k target with ad spend you don't have; CAC unknown |
| Building a SaaS | 29 days, solo — not viable |
| Cold calling | You've ruled it out |

## 3.9 — The verdict: what actually runs

Ranked by **(ceiling × probability) ÷ effort**:

| Rank | Channel | Ceiling | Manual/day | Automatable |
|---|---|---|---|---|
| 🥇 | **Email at scale, personalised demos** | $3,000 | **5 min** | ✅ 100% |
| 🥈 | **Agency white-label** | $2,000 | **10 min** | ✅ 90% |
| 🥉 | **Coaching high-ticket (6 named)** | $3,000 | 30 min (wk1) | ❌ manual |
| 4 | Contact forms | $1,200 | 20 min | ⚠️ 70% |
| 5 | Upwork proposals | $1,500 | 15 min | ⚠️ AI-drafted |
| 6 | Instagram DM | $1,400 | 25 min | ❌ manual |
| 7 | Speed/mobile quick wins | $1,000 | 10 min | ✅ 80% |
| 8 | Local (fallback) | $1,500 | 2 hrs (burst) | ❌ manual |

**Run 1, 2, 3, 4, 5, 7 from day one.** Add 6 if your Instagram account is aged. Hold 8 in reserve for the Day 21 gate.

Total daily manual load: **60–90 minutes.**

---

# PART 4 — THE OFFER ARCHITECTURE

## 4.1 — The full price list

| Product | Price | Asset used | Delivery |
|---|---|---|---|
| Mobile fix | $147 | — | 2 hrs |
| GBP setup | $147 | — | 2 hrs |
| AI content pack (10 posts) | $147 | AI | 1 hr |
| **Speed optimisation** | **$197** | — | 2 hrs |
| Missed-call-text-back | $197 + $47/mo | Twilio | 3 hrs |
| **Express site** | **$247** | dental template | 1 day |
| AI chatbot install | $297 | — | 3 hrs |
| Landing page | $397 | retreat/metz lander | 1 day |
| **Practice site** ⭐ | **$497** | dental template | 2 days |
| Practice Pro | $797 | dental + SEO | 3 days |
| Catalogue site | $797 | `saidharanx-demo` | 3 days |
| **E-com store** | **$997** | `d2c-template` | 4 days |
| **Authority Hub** ⭐ | **$1,497** | `dr-jim-arnold-hub` | 5 days |
| Premium funnel | $1,497 | `the-protocol-prototype` | 5 days |
| **Academy platform** ⭐ | **$2,497** | `dr-ritter-academy` | 7 days |
| Care plan | $97/mo | — | ongoing |

## 4.2 — The three-tier rule

Never quote one price. Always three. People choose between options far more readily than they decide yes/no on a single number.

> **Express $247** — 3 pages, live in 48 hrs
> **Practice $497** — 6 pages, gallery, booking, SEO ⭐ *most popular*
> **Pro $797** — 10 pages, service pages, blog, 2 revision rounds

The $247 exists to make $497 look reasonable. The $797 exists to make $497 look safe. **Most people pick the middle** — that's the entire point of the structure.

## 4.3 — The wedge strategy

$497 from a stranger is a real decision. **$197 is not.**

```
$197 speed fix  →  they now trust you  →  $497 website  →  $97/mo care plan
    day 1                day 3                day 10           day 14
```

**Why the speed fix is your best wedge offer:**

1. **Provable.** Run their site through PageSpeed Insights. Screenshot the score. If it says 34/100, that's Google's number, not yours. Nothing to argue with.
2. **Guaranteeable.** "90+ or you pay nothing." Zero risk to them.
3. **Fast to deliver.** Image compression, lazy loading, minification — 2 hours.
4. **It opens the website conversation naturally.** "Your site is fast now, but the booking flow is still costing you patients."

**A $197 client is worth more than a $497 prospect**, because the first sale is the hard one.

## 4.4 — Pricing psychology for text-only selling

You have no calls, no testimonials (yet), and no brand. That means:

| Rule | Why |
|---|---|
| **Full payment up front** | Deposits mean 2× the deals for the same cash |
| **Discount for speed, never for pressure** | "$497, or $397 if we start today" |
| **Downsell the scope, never the price** | Dropping $497→$300 for identical work says your price was invented |
| **Name a number in message one when asked** | "Let's discuss pricing" loses busy buyers instantly |
| **Guarantee everything** | "Don't like it, don't pay" costs you nothing and removes the only real objection |

## 4.5 — Bundles

| Bundle | Contents | Value | Price |
|---|---|---|---|
| **Launch** | Site + GBP + 10 posts | $791 | **$597** |
| **Growth** | Site + speed + chatbot + care plan | $1,088 | **$797** |
| **Authority** | Hub + funnel + content + care | $2,238 | **$1,797** |

Bundles raise average order value without new sales conversations. Offer the bundle *after* they say yes to the base product, never before.

---

# PART 5 — THE AUTOMATION STACK

Twelve scripts. Four exist, two I built today, six to build. Ordered by value per hour of build time.

## 5.1 — Build order

| # | Script | Status | Does | Saves |
|---|---|---|---|---|
| 1 | `check_replies.py` | ✅ **built** | Scan inboxes, flag replies, sync CRM | 1 hr/day |
| 2 | `check_bounces.py` | ✅ **built** | Measure bounce rate + reasons | diagnostic |
| 3 | `deploy_all.py` | ✅ **built** | 7 demos → live URLs | unblocks all |
| 4 | `campaign_manager.py` | ✅ **fixed** | 5-touch email sequence | 3 hrs/day |
| 5 | **`batch_rebrand.py`** | 🔨 build | CSV → N personalised sites | **10 hrs/day** |
| 6 | **`deploy_demo.py`** | 🔨 build | Each site → live GitHub Pages URL | **5 hrs/day** |
| 7 | **`build_campaign.py`** | 🔨 build | Merge demo URLs into CRM, arm sequence | 2 hrs |
| 8 | **`form_submit.py`** | 🔨 build | Semi-auto contact form filling | 2 hrs/day |
| 9 | **`daily_report.py`** | 🔨 build | One morning digest: replies, sends, pipeline | 30 min/day |
| 10 | **`site_audit.py`** | 🔨 build | PageSpeed score → wedge-offer ammo | 1 hr/day |
| 11 | `warmup.py` | 🔨 build | Inter-inbox warmup traffic | passive |
| 12 | `agency_finder.py` | 🔨 build | Scrape dental marketing agencies | 3 hrs |

**Scripts 5 + 6 are the core of the whole system.** Together they turn one template into hundreds of personalised, live, individually-addressed websites. That is the thing nobody else does, because by hand it's impossible.

## 5.2 — The engine, end to end

```
clean_verified_leads.csv  (30,688 fresh)
        │
        ▼
  build_campaign.py ──── score, dedupe, segment by country/category
        │
        ▼
  batch_rebrand.py  ──── 500 personalised site folders
        │                (their name, phone, address, category)
        ▼
  deploy_demo.py    ──── 500 live URLs on GitHub Pages
        │
        ▼
  campaign_manager.py ── 5-touch sequence, each email carrying
        │                THAT practice's own live link
        ▼
  check_replies.py  ──── detect replies → mark CRM → stop sequence
        │
        ▼
  daily_report.py   ──── one digest each morning
        │
        ▼
      YOU  ─────────────  answer replies. 45 min/day.
```

## 5.3 — What `batch_rebrand.py` must do

`rebrand_automation.py` today asks 8 questions and makes 1 site. Batch version:

```python
# Input:  a CSV with Name, Phone, Email, Website, Category, City
# Output: one folder per lead, fully personalised

for lead in leads:
    template = pick_template(lead.Category)   # cosmetic → Gary Solnit
                                              # general  → Lura
                                              # ortho    → Modern Smile
    copy_template(template, f"demos/{slug(lead.Name)}")
    replace_text(practice_name, doctor_name, phone, email, address, city)
    swap_hero_image(lead.Category)
    write_meta_title(f"{lead.Name} | Website Concept")
```

**Non-obvious details that matter:**

- **Rotate templates by category.** If 500 dentists get the identical layout and two of them talk, you look like a spammer. Four templates × colour variants = enough variety.
- **Put their city in the copy.** "Serving families in Leeds" reads as built-for-them.
- **Set the page title to their practice name.** Free SEO — some will Google themselves and find it.
- **Never fabricate content.** Do not invent doctor bios, fake reviews, or credentials. Use their real public details or neutral placeholder text. This is both an ethics line and a legal one — inventing testimonials for a real medical practice is not a grey area.
- **Add one honest banner:** *"Concept design — not affiliated with this practice."* It protects you, and it costs nothing in conversion because the personalisation still lands.

## 5.4 — What `deploy_demo.py` must do

```
for each demo folder:
    create repo Milin555/demo-<slug>   (public)
    push files
    enable GitHub Pages
    wait for build
    record URL → demo_urls.csv
```

**Limits you will hit and how to handle them:**

| Limit | Reality | Handling |
|---|---|---|
| GitHub repo creation rate | ~unofficial throttling above a few hundred/hr | 2–3 s sleep between repos |
| Pages builds | 10 builds/hr per repo | one build each, fine |
| Free repo count | unlimited public | fine |
| Pages bandwidth | 100 GB/mo soft | far beyond your traffic |

**Alternative if GitHub throttles:** one repo, many folders. `milin555.github.io/demos/dr-smith/`. Single Pages build, unlimited subfolders, no rate limit at all. **This is actually the better design — build it this way from the start.**

## 5.5 — The daily report

The only thing you should have to read each morning:

```
=== 18 Aug ===
NEW REPLIES: 3
  🔥 Dr. Sarah Chen  — "how much for this?"
  🔥 Bright Smile    — "can you do our logo too?"
  ⚪ Dr. Patel       — "not right now"

SENT YESTERDAY: 287 emails · 30 forms · 25 DMs
SEQUENCE: 1,240 active · 340 at touch 3
PIPELINE: 7 warm · 2 quoted · 1 awaiting payment
REVENUE: $497 collected · $994 quoted
DAYS LEFT: 28 · TARGET GAP: $4,503
```

Everything else runs without you.

---

# PART 6 — THE DAILY AUTOMODE ROUTINE

## 6.1 — What actually happens each day

**Automated, no involvement (runs on a schedule):**
- 200–400 emails sent across the sequence
- Replies detected, CRM updated, sequence stopped for responders
- New demos generated and deployed
- Bounces marked, unsubscribes honoured
- Report written

**Your part — 45 to 75 minutes:**

| Minutes | Task |
|---|---|
| 5 | Read `daily_report.py` output |
| 25 | **Answer every reply** ← the only task that makes money |
| 15 | 25 Instagram DMs (manual — automation = ban) |
| 10 | 5 Upwork proposals (AI-drafted, you paste and send) |
| 10 | Move deals forward: quotes, payment links, chasing |

**That's it.** Delivery work is on top, but only once you have clients — and by then you're being paid for it.

## 6.2 — The rule that decides the month

> **Outreach runs before delivery. Every single day. Even 15 minutes.**

The classic failure: you land two clients in week 2, disappear into delivery for 8 days, and close nothing in week 3. Then week 4 is empty because the pipeline died while you were heads-down.

The automation protects you from this — it keeps sending while you build. But **replies still need answering the same day.** A reply left for 48 hours is usually dead.

## 6.3 — Reply speed

| Response time | Close rate |
|---|---|
| Under 1 hour | ~35% |
| Same day | ~22% |
| Next day | ~12% |
| 3+ days | ~4% |

Check replies **three times a day** — morning, afternoon, evening. Ten minutes each. This single habit is worth more than any other optimisation in this document.

---

# PART 7 — CHANNEL PLAYBOOKS

## 7.1 — EMAIL (the backbone)

**Why it's back:** 29 days now accommodates a 14-day warmup. That's why this works for 15 Sep when it couldn't for 24 Aug.

### Setup — day 1, $79

| Item | Cost |
|---|---|
| 3 sending domains | $36/yr |
| Google Workspace, 6 inboxes @ $7.20 | $43/mo |

**Buy lookalike domains, never your main brand.** If your brand is `milinstudio.com`, send from `milinstudio.co`, `getmilinstudio.com`, `milinstudio.io`. A burned sending domain then costs you $12, not your identity.

**Per domain, before a single send:**
- [ ] SPF record
- [ ] DKIM enabled
- [ ] DMARC (`p=none`)
- [ ] Custom tracking domain
- [ ] mail-tester.com → **9/10 minimum**

### Warmup — 14 days, no exceptions

| Days | Per inbox | Total/day |
|---|---|---|
| 1–3 | 5 | 30 |
| 4–7 | 10 | 60 |
| 8–11 | 20 | 120 |
| 12–14 | 30 | 180 |
| **15+** | **35 cap** | **210** |

Days 1–14 send only to your own inboxes and any real contacts who'll reply. Then live sending from day 15.

**Never exceed 35/inbox/day.** That ceiling is what separates this from your last attempt.

### Volume available

```
Days 15–29 = 15 days × 210/day = 3,150 emails
Plus follow-up touches on earlier sends ≈ 4,500 total touches
```

At a realistic 3% reply rate → **135 replies** → ~34 interested → **~4 deals**.

### The corrected sequence

| # | Day | Subject | Contains |
|---|---|---|---|
| 1 | 0 | `[Practice] — I built you something` | **live link** |
| 2 | 3 | `Re: [Practice]` | short bump |
| 3 | 7 | `the booking problem` | one specific issue + link |
| 4 | 12 | `one thing worth fixing` | free value, no ask |
| 5 | 18 | `closing your file` | breakup |

## 7.2 — AGENCY WHITE-LABEL (highest leverage)

**The play:** marketing agencies serving dentists sell websites but frequently don't build them. You become their build team.

**Why it works better than end-client outreach:**

| End client | Agency |
|---|---|
| Interruption | Business opportunity |
| Needs convincing | Already sold it |
| One-off | 3–10/month |
| Wants testimonials | Wants speed and price |
| Slow to reply | Replies fast |

### Finding them

Search: `"dental marketing agency"`, `"dentist website design"`, `"medical marketing agency"` + city. Also Clutch.co, Google Maps, LinkedIn.

**Target the small ones** — 2–10 people. Big agencies have in-house teams; solo consultants have no volume.

### The pitch

> Subject: white-label builds for your dental clients
>
> Hi [Name],
>
> I build dental practice websites — here are 4: [portfolio]
>
> I white-label for agencies. You keep the client relationship and your margin, I build. $300 flat per site, 5-day turnaround, unlimited revisions within scope.
>
> If you've ever turned down a website because the build wasn't worth the hassle, that's the gap I fill.
>
> Want a free sample build on one of your clients so you can judge the quality?
>
> Milin

**The free sample build is the closer.** It costs you 30 automated minutes and removes all their risk.

**Math:** one agency sending 3 builds/month × $300 = **$900/month recurring**, from a single yes. Two agencies = $1,800/month with zero further selling.

## 7.3 — THE SIX COACHING PROSPECTS (highest ticket)

From your own `prospects.md`, researched 24 July, **never contacted**:

| Prospect | Business | Template match | Price |
|---|---|---|---|
| Dr. Mark Costes | Dental Success Institute | `dr-jim-arnold-hub` | $1,497 |
| Dr. Paul Etchison | Legendary Mastermind | `dr-jim-arnold-hub` | $1,497 |
| Dr. Tarun Agarwal | 3D Dentists | `dr-ritter-academy` | $2,497 |
| Dr. Anissa Holmes | Dentalflix | `dr-ritter-academy` | $2,497 |
| Dr. Nate Jeal | Fast Growth Practice | `dr-jim-arnold-hub` | $1,497 |
| Dr. Justin Bhullar | High Performance | `dr-jim-arnold-hub` | $1,497 |

**These six are worth more than the other 30,000 leads combined.** One close = $1,497–2,497 = 30–50% of your target.

**Do not automate these.** Research each for 20 minutes. Watch a podcast episode. Reference something real. Send by hand. Six messages, hand-written, in week 1.

**Follow up on day 4 and day 9.** High-ticket buyers almost never answer message one — they're busy, not uninterested.

## 7.4 — CONTACT FORMS (spam-filter-proof)

6,283 targets in `form_list.csv`.

**The mechanism:** you submit their form → **their** website emails **their** inbox from **their** domain. It arrives alongside patient enquiries. A spam filter cannot catch mail a server sends to itself.

**Highest delivery rate of any channel you have.** ~70% automatable; the rest need a human because form structures differ.

> Hi — not a patient enquiry, sorry for using this form.
>
> I build websites for dental practices and rebuilt yours as a free sample: [link]
>
> Have a look. If it's not for you, ignore this — it's yours either way.

The apology up front is why it gets read rather than deleted.

## 7.5 — INSTAGRAM DM (manual only)

**107 A-list targets** — no website + 5k+ followers + paying market.

**Automation = permanent ban. There is no safe tool. Do not try.**

| Rule | |
|---|---|
| Account age | 6+ months, real posts, real followers |
| Volume | 10/day → 15 → **25 hard cap** |
| Warm-up | follow + like 2 posts **the day before** |
| "Action Blocked" | **stop 48 hours immediately** |

The day-before warm-up pass takes reply rates from ~5% to 15–20%. It is the difference between this channel working and not.

## 7.6 — UPWORK

AI drafts, you paste. 15 minutes/day, 5 proposals.

> I build websites specifically for dental practices — 4 examples: [portfolio]
>
> For your project I'd focus on [specific detail from their post]. Live in 7 days at $[their budget].
>
> One question: do you want online booking connected, or a simple enquiry form?

**Open with proof, close with a question.** Most competitors open with "I am interested in your project." Ending on a question makes replying easy.

**Payment warning:** 5-day security period + 3–5 day withdrawal. An Upwork sale on 8 Sep may not bank before 15 Sep. Run it — but treat it as October money.

## 7.7 — LOCAL (the insurance policy)

**Hold in reserve. Activate at the Day 21 gate if you're behind.**

| | International | Local |
|---|---|---|
| Payment | Wise, 1–3 days | **UPI, instant** |
| Close rate | ~12% | **~30%** |
| Cycle | 1–2 weeks | **hours** |
| Ticket | $497 | ₹20,000 (~$230) |

**4 local clients ≈ ₹85,000 ≈ $1,000.**

Walk in with demos open on your phone. Don't pitch — show. "This is what I build. Want one?"

Highest close rate of anything in this playbook, because you're a real person standing in front of them instead of an unknown email.

---

# PART 8 — MESSAGE LIBRARY

## 8.1 — Email touch 1

> **Subject:** [Practice Name] — I built you something
>
> Hi [Name],
>
> I build websites for dental practices. I rebuilt yours as a sample this week — it's live here:
>
> **[link]**
>
> Open it on your phone. The main change is booking: one tap instead of a contact form.
>
> Free either way, I just wanted your honest opinion on it.
>
> Milin

**Why this beats your old email:** link in message one, no permission asked, no reply required to get value, one concrete change named.

## 8.2 — Email touch 3 (the workhorse)

> **Subject:** the booking problem
>
> Hi [Name],
>
> Quick specific thing about [Practice]'s current site.
>
> On mobile, a patient scrolls past four screens before finding how to book. Most give up before they get there — that's not a design opinion, it's just how phone traffic behaves.
>
> The version I built puts booking at the top: **[link]**
>
> Worth 30 seconds of your time.
>
> Milin

## 8.3 — Email touch 5 (breakup — highest reply rate)

> **Subject:** closing your file
>
> Hi [Name],
>
> I'll assume the timing isn't right and close your file so I stop cluttering your inbox.
>
> The site is here if you ever want it: **[link]** — it stays live another two weeks.
>
> All the best with the practice.
>
> Milin

**The breakup consistently outperforms every other message in a sequence.** People respond to something ending.

## 8.4 — The wedge (speed offer)

> **Subject:** [Practice] loads in 8.2 seconds
>
> Hi [Name],
>
> Ran your site through Google PageSpeed — it scores **[X]/100** on mobile and takes [Y] seconds to load. Google's own number, screenshot attached.
>
> Anything over 3 seconds loses about half of mobile visitors before the page appears.
>
> I can get it to 90+ for $197. Two-day turnaround, and if I don't hit 90 you pay nothing.
>
> Want me to?
>
> Milin

**The strongest message in this document.** Provable problem, guaranteed outcome, low price, zero risk. Use it on anyone who doesn't bite on the website offer.

## 8.5 — Instagram DM

> Hi [Name] — saw your [real specific thing]. Genuinely good work.
>
> Noticed you don't have a website, so I built you one: **[link]**
>
> Live now, open it on your phone. Free either way — just want your honest opinion.

## 8.6 — Agency white-label

*(Full version in 7.2)* — lead with the portfolio, name the flat price, offer the free sample build.

## 8.7 — Coaching high-ticket

> Hi Dr. [Name],
>
> I've been following [their specific show/program] — [genuine specific observation].
>
> I build course and membership platforms for dental educators. I put together a version of what [their program] enrollment could look like: **[link]**
>
> It's live, have a look on your phone. Free either way — I built it because I wanted to see if I could.
>
> If [specific 2026 thing they're launching] is still being built out, I can have a custom version running in a week.
>
> Milin

## 8.8 — Follow-up that isn't annoying

> Hi [Name] — floating this back up in case it got buried.
>
> No pitch, just the link again: [link]
>
> If it's a no, say the word and I'll stop.

**"Say the word and I'll stop" raises reply rates.** It hands them control, which makes replying feel safe.

---

# PART 9 — SALES & CLOSING (TEXT ONLY)

## 9.1 — When they reply positively

```
Glad you like it! It's yours.

$497 for the full build — your domain, live in 48 hours.
Or $397 if we start today.

Payment link: [link]
Then I need your logo, photos and opening hours. That's it.

Want me to start?
```

**Always end with a question.** A message ending in a full stop invites nothing.

## 9.2 — Objection handling

**"How much?"**
> $497 for the full build, live in 48 hours. $397 if we start today.

*Never say "let's discuss pricing." Busy buyers read that as expensive and stop replying.*

**"Too expensive"**
> No problem — the 3-page Express version is $247 and covers the essentials. Want to see it?

*Downsell scope, never price.*

**"Let me think about it"**
> Of course. What's the part you want to think about — the price, or whether the site's right?

*The single highest-leverage question here. "Let me think" is a polite exit, not an objection. This forces the real reason out, and a real reason can be answered.*

**"We already have a website"**
> I know — that's how I rebuilt it. The problem isn't that it exists. On mobile, booking is four screens down. Have a look at the version I made: [link]

**"Can I pay after?"**
> For bigger builds I do half now, half at launch. At $397 it's up front — that's how the price stays this low. I guarantee it: if you don't like what goes live, you get a full refund.

**"Are you an agency?"**
> No — one person, which is why I'm $397 and not $4,000, and why it's done in 48 hours instead of six weeks.

*Never pretend to be a team. It collapses the moment they ask a second question.*

**Silence after a quote**
> Day 2: "Still interested? Happy to answer anything."
> Day 5: "Want me to hold the $397 price through Friday?"
> Day 9: "Closing your file — say the word if you want it later."

## 9.3 — What loses deals

| Mistake | Instead |
|---|---|
| Long paragraphs | 3 lines max per message |
| No price until they push | Name it immediately |
| "Let me know if interested" | "Want me to start?" |
| Replying next day | Reply within the hour |
| Discounting when pushed | Reduce scope, hold price |
| Overpromising features | Under-promise, over-deliver |

---

# PART 10 — PAYMENT & DELIVERY

## 10.1 — Get paid — set up TODAY

Verification takes 1–2 days. **If you start this on day 20, you cannot be paid by 15 Sep even if you sell.**

| Method | Speed to bank | Use for |
|---|---|---|
| **Wise** | 1–2 days | International ⭐ |
| **Payoneer** | 2–3 days | International backup |
| PayPal | 1–2 days | Clients who insist |
| **UPI** | **instant** | Local ⭐ |
| Razorpay / Instamojo | 1–2 days | Local card payments |

**Set up Wise + UPI minimum. Both today.**

## 10.2 — Money rules

1. **Full payment up front** under $500
2. **50/50** above $500
3. **Never start work before money clears**
4. **Payment link in the message** — no invoicing friction
5. **Written scope** before starting — this is how $497 avoids becoming six weeks of free revisions
6. **Revision cap in writing** — "2 rounds" means two

## 10.3 — Delivery

| Product | Realistic time |
|---|---|
| Speed fix | 2 hrs |
| Express site | 4 hrs |
| Practice site | 6 hrs |
| E-com store | 10 hrs |
| Authority Hub | 12 hrs |
| Academy | 18 hrs |

**Always quote double what it takes.** Deliver in 2 days what you promised in 4. Early delivery generates referrals; late delivery generates refunds.

## 10.4 — What you need from the client

Send this exact list the moment they pay:

```
1. Logo (PNG or SVG)
2. 5-10 photos (clinic, team, treatments)
3. Opening hours
4. Phone, email, full address
5. Services list
6. 2-3 sentences about the practice
7. Domain login (or I'll guide you)
```

**Chase this immediately.** The #1 cause of a late project is a client who paid and then went quiet for six days.

---

# PART 11 — THE 29-DAY CALENDAR

## Week 1 (17–23 Aug) — Build the machine

**Day 1 (today)**
- [ ] `deploy_all.py --go` → 7 live URLs
- [ ] Buy 3 domains, 6 inboxes, SPF/DKIM/DMARC
- [ ] Wise + UPI setup
- [ ] Read bounce + reply results
- [ ] Portfolio page

**Day 2**
- [ ] Build `batch_rebrand.py` + `deploy_demo.py`
- [ ] Generate + deploy first 50 demos
- [ ] Warmup begins (5/inbox)
- [ ] **Contact all 6 coaching prospects, by hand**

**Day 3–5**
- [ ] 200 more demos
- [ ] Contact forms 30/day
- [ ] Upwork/Fiverr live, 5 proposals/day
- [ ] Agency list built, 20 agencies/day
- [ ] Instagram 10/day *(if account is aged)*

**Day 6–7**
- [ ] Coaching follow-up #1
- [ ] `site_audit.py` → wedge offers to 100 worst-scoring sites
- [ ] Warmup at 10/inbox

**Week 1 target: $300–800** (wedge offers + first Upwork)

## Week 2 (24–30 Aug) — Volume

- [ ] Warmup → 20/inbox → 30/inbox
- [ ] 500 demos deployed total
- [ ] Agency outreach continues
- [ ] Coaching follow-up #2
- [ ] **Deliver everything sold, get testimonial #1**

**Week 2 target: cumulative $1,200–2,000**

## Week 3 (31 Aug – 6 Sep) — Email at full scale

- [ ] **Day 15: live sending begins, 210/day**
- [ ] Testimonials go into every message
- [ ] Push Authority/Academy tiers
- [ ] Referral ask to every delivered client

**Week 3 target: cumulative $2,500–3,500**

## Week 4 (7–15 Sep) — Close out

- [ ] Sequence follow-ups doing the work
- [ ] Every warm lead gets a final push
- [ ] Care plan upsell to all clients
- [ ] **11 Sep: last day an international sale banks by the 15th**
- [ ] 12–15 Sep: local/UPI only

**Week 4 target: $5,000** ✅

---

# PART 12 — METRICS & DECISION GATES

## 12.1 — Track five numbers only

| Metric | Weekly target |
|---|---|
| Outbound touches | 1,500 |
| Replies | 45 |
| Positive replies | 11 |
| Quotes sent | 6 |
| **Closed** | **2** |

## 12.2 — Diagnosis

| Symptom | Cause | Fix |
|---|---|---|
| Low touches | Automation not running | Fix scripts first |
| Touches OK, no replies | Deliverability or offer | mail-tester, rewrite subject |
| Replies, none positive | Wrong targets | Re-segment |
| Positive, no quotes | Too slow replying | 3× daily checks |
| Quotes, no closes | Price or trust | Add guarantee, drop to wedge |

## 12.3 — Hard gates

**🚩 GATE 1 — Day 7 (23 Aug)**
Expected: $300+, 10+ replies.
If **$0 and under 5 replies** → deliverability is broken. Stop. Test with mail-tester. Switch weight to contact forms + Upwork + local.

**🚩 GATE 2 — Day 14 (30 Aug)**
Expected: $1,200+.
If under $500 → **activate the local track now.** Do not wait.

**🚩 GATE 3 — Day 21 (6 Sep)**
Expected: $2,500+.
If under $1,500 → $5,000 is out of reach. Switch entirely to fastest-cash mode: local + wedge offers + anything that pays instantly. **Bank $2,000–3,000 rather than chase $5,000 and land $800.**

**🚩 GATE 4 — Day 25 (11 Sep)**
Last day international payment clears. After this, local/UPI only.

---

# PART 13 — WORST-CASE PLAYBOOK

Every realistic failure, with the actual response.

## 13.1 — Email still lands in spam

**Likelihood: 30%**

*Symptoms:* under 0.5% reply rate after day 15.

**Response:**
1. mail-tester.com — score under 9 means fix DNS before anything else
2. Send to your own Gmail/Outlook/Yahoo — check which folder
3. Cut volume to 15/inbox/day for 5 days
4. Strip all links from touch 1 (links hurt cold deliverability), put them in touch 2
5. Shorten subject lines to 2–3 words
6. **If still failing by day 20: abandon email.** Shift everything to contact forms, Upwork, agencies, local.

**Never send more to fix low replies. Volume amplifies a deliverability problem.**

## 13.2 — Instagram account banned

**Likelihood: 40% if you push limits**

**Response:**
1. Do not appeal repeatedly — it rarely works and can harden the block
2. Do not create a new account on the same device/IP
3. Contact forms absorb this channel's volume
4. **Prevention is the only real fix:** 25/day cap, manual only, stop on first "Action Blocked"

## 13.3 — GitHub throttles mass repo creation

**Likelihood: 50% above ~200 repos**

**Response:** switch to the single-repo design — `milin555.github.io/demos/<slug>/`. One repo, unlimited subfolders, no per-repo rate limit. **Build it this way from the start and this never happens.**

Backup hosts: Netlify Drop, Cloudflare Pages, Surge.sh.

## 13.4 — Zero replies across all channels by day 14

**Likelihood: 20%**

This means the *offer* is wrong, not the channel.

**Response:**
1. Switch the lead offer to the **$197 speed fix** — provable and guaranteed
2. Change target: dentists → **agencies** (they reply because it's their business)
3. **Activate local immediately**
4. Drop price to $247 to buy the first testimonial — the first sale is worth more as proof than as cash

## 13.5 — Client says yes then disappears

**Likelihood: 70% that it happens at least once**

**Response:** day 1 "still want me to start?" · day 3 "holding your slot until Friday" · day 7 "releasing your slot, here if you change your mind." Then stop.

**Prevention:** payment link *in the same message* as the yes. Every hour between agreement and payment loses deals.

## 13.6 — Client refuses to pay after delivery

**Likelihood: 15%**

**Prevention is everything:**
- Payment before launch, always
- Deliver on **your** hosting first; transfer only after final payment
- Never hand over source files before payment clears

**If it happens:** keep the site on your hosting, offer a 7-day window, then take it down. Do not fight over $497 — it costs more in time than it returns.

## 13.7 — Wise/Payoneer rejected or delayed

**Likelihood: 25%**

**Response:** apply to **both on day 1**, plus PayPal, plus a local gateway (Razorpay/Instamojo). Redundancy costs nothing. A single payment rail is a single point of failure for the entire month.

## 13.8 — Refund demanded

**Likelihood: 10%**

**Give it immediately, no argument.** A refund costs $397. A public complaint from a dentist in a dental Facebook group costs you the niche. Refund, stay polite, move on.

## 13.9 — Too many clients, can't deliver

**Likelihood: 15%** *(a good problem)*

**Response:** raise the price rather than the hours. Quote longer timelines. Deliver the template swap and charge separately for customisation. **Never miss a deadline to take another client** — one late delivery kills the testimonial you need more than the money.

## 13.10 — A practice complains about their demo site ⚠️

**Likelihood: 10% — and this one has real legal weight**

You're generating sites using real practice names. That's normal spec work, but there are lines:

**Rules that keep this clean:**
- ✅ Their public name, phone, address, services
- ✅ A banner: *"Concept design — not affiliated with this practice"*
- ❌ **Never fabricate testimonials, reviews, doctor bios or credentials**
- ❌ Never copy their photography without permission — use stock or generic imagery
- ❌ Never imply endorsement or that you built their real site
- ✅ Take it down **immediately and politely** on request, no argument

**Fabricating patient reviews or clinical credentials for a real medical practice isn't a grey area — it's the kind of thing that ends a business.** Neutral placeholder text converts nearly as well and carries none of the risk.

**If someone complains:** take it down within the hour, apologise once, don't defend it. Then offer the site free if they want it.

## 13.11 — Google Workspace suspends you for bulk sending

**Likelihood: 20%**

**Response:** stay under 35/inbox/day (Workspace allows 2,000/day, so you're at 2% of the limit — suspension at this volume means content flagging, not volume). Keep 6 inboxes across 3 domains so one suspension costs you 1/6 of capacity, not everything.

## 13.12 — High bounce rate on the list

**MEASURED 17 Aug — this risk did not materialise.**

```
Emails sent:        1,751
Bounces found:         59
BOUNCE RATE:        3.37%   ← healthy for scraped data
Unique bad addresses:  47
```

**Why they bounced:**

| Reason | Count | Share |
|---|---|---|
| No such user (dead address) | 37 | 63% |
| Other / unknown | 10 | 17% |
| **Spam / blocked** | **6** | **10%** |
| Mailbox full | 6 | 10% |

### This is the proof

**Only 6 messages out of 1,751 were explicitly spam-blocked — 0.34%.**

Combined with the four auto-replies that fired, this settles the question you asked:

> **Your mail was being delivered. It reached real inboxes. And it produced zero interest.**

3.37% is a *normal* bounce rate for Instagram-scraped addresses. Anything under 5% means the list is healthy and reusable. **Your 30,745-address list is fine.**

**So the failure was 100% the offer, not the plumbing:**
- no link in the email
- one follow-up across 1,751 people
- an ask that required a reply before delivering any value

That is a much better problem to have. Deliverability takes $79 and 14 days to fix with no guarantee. **An offer takes an afternoon.**

**Action taken:** all 47 dead addresses + 3 unsubscribes are now in `SUPPRESSION_LIST.txt` (49 total) and marked in the CRM. Every future script must check this file before sending.

## 13.13 — You get sick / life happens

**Likelihood: 25%**

This is exactly why automation matters. The sequence keeps sending. **Even 15 minutes answering replies keeps the month alive.** Missing a day of outreach costs little; missing a week of replies kills the pipeline.

## 13.14 — Nothing works and it's 10 Sep with $400

**Response — in this order:**
1. Local, in person, UPI. Every clinic and salon you can reach.
2. Drop to $147–197 wedge offers — fast yes, instant cash
3. Message every single person who ever replied, with a final offer
4. Post in local Facebook groups
5. **Bank what you can and treat the machine as October's asset**

**$800 in September with a working system beats $0 and a perfect plan.**

---

# PART 14 — THE FALLBACK LADDER

If plan A stalls, drop one rung. Don't freeze.

| Rung | Plan | Target | Trigger |
|---|---|---|---|
| **A** | Email + demos at scale + high-ticket | $5,000 | default |
| **B** | Drop email, push forms + Upwork + agencies | $3,500 | Gate 1 fails |
| **C** | Wedge offers ($197 speed fixes) at volume | $2,500 | Gate 2 fails |
| **D** | Local + UPI, in person | $1,500 | Gate 3 fails |
| **E** | Anything that pays this week, any price | $800 | Day 25, still low |
| **F** | Bank what exists, roll machine into October | — | 15 Sep |

**Every rung down is faster cash at a lower ticket. None of them are failure.** The machine you build in week 1 keeps working in October regardless of what September totals.

---

# PART 15 — THE FIVE THINGS THAT DECIDE THIS

Everything above collapses into these:

1. **Deploy the 7 demos today.** Six weeks of finished work is currently invisible to every human on earth. Nothing else functions until this is done.

2. **Set up Wise + UPI today.** 1–2 day verification. Start it late and a sale cannot reach you.

3. **Put a live personalised link in message one.** Never "can I send you the link?" That single change is worth more than every other optimisation combined.

4. **Follow up five times.** You sent 1,751 emails and one follow-up. 60–80% of replies live in touches 2–5. This is your largest, most fixable historical failure.

5. **Answer replies within the hour.** Under 1 hr ≈ 35% close. After 3 days ≈ 4%. Ten minutes, three times a day.

**Do these five and the rest is optimisation. Skip any one of them and nothing else matters.**

---

# PART 16 — APPENDIX A: SCRIPT BUILD SPECS

Exact specifications for the six scripts still to build, in priority order. Hand any of these to Claude and it can be written in one pass.

## A1 — `batch_rebrand.py` 🔴 highest value

```
INPUT   leads.csv  (Name, Phone, Email, Website, Category, City, Country)
        --limit N          how many to generate
        --out demos/       output directory

LOGIC
  for each lead:
    template = route_by_category(lead.Category)
        Cosmetic Dentist   -> Gary Solnit Dentist
        General Dentist    -> Lura Dentist
        Orthodontist       -> Modern Smile Center Dentist
        Pediatric Dentist  -> Ritter Ramsey Dentist
        (rotate variants so no two neighbours match)

    slug = slugify(lead.Name)
    copy template -> demos/<slug>/   (skip .git, __pycache__)

    replace across all .html:
        practice name, doctor name, phone, email, address, city
        page <title> -> "<Practice> | Website Concept"
        meta description -> include city + category

    inject disclaimer banner (see A1.1)

OUTPUT  demos/<slug>/  +  demo_manifest.csv (slug, practice, email, path)

GUARDS
  - never fabricate reviews, bios, credentials, or awards
  - never download their photos; keep template stock imagery
  - skip leads with empty/garbage names
  - skip anything on SUPPRESSION_LIST.txt
```

### A1.1 — The disclaimer banner (non-negotiable)

Inject into every generated page:

```html
<div style="background:#111;color:#fff;padding:8px 16px;
            font:14px/1.4 system-ui;text-align:center">
  Concept design — not affiliated with or endorsed by this practice.
  <a href="mailto:you@domain.com" style="color:#7dd3fc">Request removal</a>
</div>
```

This costs nothing in conversion and it is what keeps section 13.10 from becoming a real problem.

## A2 — `deploy_demo.py` 🔴

**Use the single-repo design.** It avoids GitHub rate limits entirely.

```
SETUP (once)
  create public repo: Milin555/demos
  enable Pages on main /

LOGIC
  copy demos/<slug>/  ->  demos-repo/<slug>/
  git add, commit, push  (batch 50 per commit — not one commit each)
  url = https://milin555.github.io/demos/<slug>/

OUTPUT  demo_urls.csv (slug, practice, email, url)

WHY ONE REPO
  - one Pages build for all sites
  - no repo-creation throttling
  - unlimited subfolders
  - takedown = delete one folder
```

## A3 — `build_campaign.py`

```
INPUT   demo_urls.csv + clean_verified_leads.csv
LOGIC   join on email
        drop anything in SUPPRESSION_LIST.txt
        drop anything already in campaign_crm.csv
        score: has_website, category, country
        write Demo_URL column into CRM
        set Step=0, Status=Active
OUTPUT  data/campaign_crm.csv  armed and ready
```

Then `campaign_manager.py` substitutes `{DemoLink}` per lead — each person receives their own site.

## A4 — `site_audit.py` (the wedge engine)

```
INPUT   form_list.csv (leads with websites)
LOGIC   for each: Google PageSpeed Insights API (free, 25k/day)
        record mobile score, LCP, total bytes
        flag score < 50  -> wedge target
        screenshot the score
OUTPUT  wedge_targets.csv (practice, url, score, lcp, email)
```

Feeds message 8.4. **The most convincing message you can send**, because the number comes from Google, not from you.

## A5 — `form_submit.py`

```
INPUT   form_list.csv + demo_urls.csv
LOGIC   fetch page, locate <form>
        classify fields (name, email, phone, message)
        if all four found  -> auto-submit  (~70% of sites)
        else               -> write to manual_queue.csv
        rate limit: 1 per 20-30s, randomised
OUTPUT  form_log.csv + manual_queue.csv
```

Respect `robots.txt`. Never submit twice to the same site.

## A6 — `daily_report.py`

```
READS   campaign_crm.csv, REPLIES_FOUND.csv, form_log.csv, revenue.csv
PRINTS  new replies (hot first, with preview)
        sends yesterday by channel
        sequence position counts
        pipeline: warm / quoted / awaiting payment
        revenue vs target, days remaining
RUNS    every morning via Task Scheduler
```

The only thing you read each day.

---

# PART 17 — APPENDIX B: QUICK REFERENCE

## Daily checklist — pin this

```
[ ] Read daily report                          5 min
[ ] Answer every reply (3× per day)           25 min
[ ] 25 Instagram DMs (manual, aged acct)      15 min
[ ] 5 Upwork proposals                        10 min
[ ] Move deals: quotes, payment links         10 min
                                        ────────────
                                        65 minutes
```

## Prices at a glance

```
$147  mobile fix / GBP setup / content pack
$197  speed optimisation          ← best wedge
$247  Express site
$297  AI chatbot
$397  landing page
$497  Practice site               ← core offer
$797  Practice Pro / catalogue
$997  e-commerce store
$1,497 Authority Hub              ← high ticket
$2,497 Academy platform           ← high ticket
$97/mo care plan                  ← offer to everyone
```

## The gates

```
Day  7 (23 Aug) — need $300+   else deliverability broken
Day 14 (30 Aug) — need $1,200  else activate local NOW
Day 21 ( 6 Sep) — need $2,500  else switch to fastest-cash
Day 25 (11 Sep) — last day international payment clears
Day 29 (15 Sep) — target $5,000
```

## Never do these

```
✗ Automate Instagram DMs           → permanent ban
✗ Email the 3 unsubscribes         → illegal
✗ Fabricate reviews or bios        → ends the business
✗ Exceed 35 emails/inbox/day       → domain burned
✗ Start work before payment        → you eat the loss
✗ Discount when pushed             → cut scope instead
✗ Skip outreach for delivery       → empty pipeline in 10 days
✗ Send more mail to fix low replies → amplifies the problem
```

## Files in this workspace

```
PLAYBOOK.md            ← this document
SPRINT_7DAY.md         7-day cash sprint
PLAN_5K.md             high-ticket strategy
PLAN_FINAL.md          no-call channel plan

A_LIST_dm.csv          107 best DM targets
dm_call_list.csv       7,248 paying-market practices
form_list.csv          6,283 contact-form targets
SUPPRESSION_LIST.txt   never contact these
REPLIES_FOUND.csv      inbox scan results

check_replies.py       ✅ scan inboxes for replies
check_bounces.py       ✅ measure bounce rate
deploy_all.py          ✅ demos → live URLs
campaign_manager.py    ✅ 5-touch sequence (fixed)
rebrand_automation.py  ⚠️ interactive — needs batch mode
```

---

*End of playbook. Part 15 is the part that matters. Start with `deploy_all.py`.*
