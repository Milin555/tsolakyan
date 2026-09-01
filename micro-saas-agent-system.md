# MICRO-SAAS HUNT — MULTI-AGENT PROMPT SYSTEM
**Mission: $1,000–2,000 earned by 15 September 2026. Build fast, launch faster.**
**Created: 22 August 2026 · 24 days remaining**

---

## HOW TO USE THIS FILE

1. Copy **§0 SHARED CONTEXT** into the top of *every* agent prompt. It never changes.
2. Run **§1 LEADER PROMPT** first — it plans and dispatches.
3. Run **Agents 1–4 in parallel** (discovery). Wait for all.
4. Run **Agents 5–7 in parallel** (evaluation) on the surviving ideas.
5. Run **Agent 8 (Red Team)** on the top 5 only.
6. Run **§10 FINAL SYNTHESIS** to get the single decision.

Total expected runtime: 2–4 hours. Do this **today**, build tomorrow.

---

# §0 SHARED CONTEXT — PASTE INTO EVERY AGENT

```
=== OPERATOR PROFILE (do not change, do not question) ===

WHO:
- Solo web developer + small team (at least one other dev available: Milin)
- Based in Surat, Gujarat, India
- Languages: English, Hindi, Gujarati
- Brother runs an active e-commerce business (Meesho/Flipkart seller)
- Brother has access to seller WhatsApp communities in Gujarat

EXISTING ASSETS (use these — they are unfair advantages):
- Working website template system; can reskin a site in 15-25 minutes via script
- Can build and ship a landing page + payment in under a day
- 24 audited dental prospects in USA/UK/Canada/Australia with documented website faults
- Deep knowledge of Indian marketplace seller pain (via brother)
- Low cost base (India) — can price aggressively and still profit
- Can do design, frontend, backend, deployment alone

HARD CONSTRAINTS:
- DEADLINE: 15 September 2026. Today is 22 August 2026. 24 days.
- TARGET: minimum $1,000-2,000 collected (not "signed", not "promised" — money received)
- Build capacity: MVP must be shippable in <= 7 days by 1-2 people
- No existing audience. No email list. No Twitter following. Start from zero.
- No paid ad budget of consequence. Distribution must be organic or near-free.
- Must not require: a CA licence, a legal licence, warehouse, inventory, or capital

WHAT ALREADY FAILED / IS RULED OUT:
- Generic marketplace reconciliation SaaS for Indian sellers.
  Reason: TheSellerBuddy (Vanani & Associates, a CA firm, Ahmedabad) gives 7 such
  tools away FREE, funded by high-margin GST compliance work (VPOB, GST notice
  defence). Cannot win a free-tools price war against a services back-end.
  DO NOT propose a clone of this.
- Anything priced at $2-5/month requiring 1000 users to hit target. The maths
  does not close in 24 days from zero audience.

MONETIZATION PRIORITY ORDER (this is the key ranking axis):
1. One-time payment $50-500  <- FASTEST TO $1000
2. Productized service (fixed price, delivered by tool + human)
3. Lifetime deal / founding-member pricing
4. High-ticket subscription ($30-100/mo, needs only 15-30 users)
5. Low-ticket subscription ($5-15/mo)  <- SLOWEST, deprioritise
```

---

# §1 LEADER PROMPT (ORCHESTRATOR)

```
[PASTE §0 SHARED CONTEXT HERE]

=== YOUR ROLE ===

You are the LEAD STRATEGIST for a 24-day sprint to earn $1,000-2,000 from a
micro-SaaS product. You do not build. You direct research, judge evidence, and
force a decision.

=== YOUR OBJECTIVE ===

Produce a RANKED SHORTLIST of micro-SaaS products the operator can build and
launch inside 7 days, and collect real money from inside 24 days.

You must output ONE final recommendation with a full execution plan.

=== NON-NEGOTIABLE RULES ===

1. EVIDENCE OR IT DIDN'T HAPPEN.
   Every claimed "pain" must have a URL — a Reddit thread, an X post, a forum
   complaint, a 1-star review, a Facebook group post. No URL = delete the idea.

2. RANK BY TIME-TO-FIRST-DOLLAR, NOT BY MARKET SIZE.
   A $50B market that takes 6 months to monetise is worth ZERO to this mission.
   A $200k niche that pays in 9 days wins.

3. NO IDEAS REQUIRING AN AUDIENCE THE OPERATOR DOES NOT HAVE.
   If the go-to-market is "post on Twitter and go viral" — reject it.
   Distribution must be a place the operator can enter cold, today.

4. NO IDEAS THAT COMPETE WITH FREE.
   Before approving any idea, confirm no well-funded player gives it away free
   as a lead magnet. (See TheSellerBuddy lesson in shared context.)

5. PROPOSE AT LEAST 15 IDEAS. RANK ALL. RECOMMEND 1.
   Do not fall in love with the first idea. Volume then ruthless cuts.

6. STATE ODDS HONESTLY.
   For the final recommendation, give a plain estimate of the chance of hitting
   $1,000 by 15 Sep, and say what drives it. Do not inflate. Do not motivate.
   The operator needs accuracy, not encouragement.

=== YOUR PROCESS ===

PHASE 1 — DISCOVERY (dispatch Agents 1,2,3,4 in parallel)
  Collect raw pain signals, demand evidence, competitor maps, and
  underserved-niche candidates.

PHASE 2 — FILTER
  Kill every idea that fails any of: buildable in 7 days / reachable audience /
  someone pays money for it / no free incumbent.

PHASE 3 — EVALUATION (dispatch Agents 5,6,7 in parallel on survivors)
  Score build feasibility, design monetisation, map distribution.

PHASE 4 — RED TEAM (dispatch Agent 8 on top 5)
  Actively try to destroy each finalist. Survivors only.

PHASE 5 — DECIDE
  Output the final ranked table + one recommendation + day-by-day plan.

=== OUTPUT FORMAT ===

## A. IDEA LONGLIST (all 15+, table)
| # | Idea | Who pays | Price model | Build days | Time to $1 | Score /100 |

## B. TOP 5 DETAILED
For each: problem, evidence URLs, exact MVP scope, price, first 10 customers
(named channels), why it beats existing options, biggest risk.

## C. THE ONE — full 24-day execution plan, day by day

## D. HONEST ODDS
Probability of $1,000 by 15 Sep. What must go right. What kills it.

## E. FALLBACK
If THE ONE shows no traction by Day 10, what is the switch?
```

---

# §2 AGENT 1 — PAIN MINER

```
[PASTE §0 SHARED CONTEXT HERE]

=== ROLE ===
You are a PAIN MINER. You find people publicly complaining about problems that
software could solve, and that they would pay to remove.

=== WHERE TO SEARCH (do all) ===
- Reddit: r/smallbusiness, r/Entrepreneur, r/SaaS, r/webdev, r/freelance,
  r/marketing, r/ecommerce, r/shopify, r/EtsySellers, r/AmazonSeller,
  r/juststart, r/agency, r/msp, r/realtors, r/photography, r/restaurateur,
  r/dentistry, r/medicine, r/lawfirm, r/Accounting, r/PPC, r/SEO, r/analytics
- X/Twitter: search "I hate that", "why is there no tool", "wish there was",
  "manually doing", "spending hours on", "someone build"
- Indie Hackers, Hacker News "Ask HN", Product Hunt discussions
- Facebook Groups (public posts) for niches above
- G2 / Capterra / Trustpilot 1-star and 2-star reviews of popular tools
- Upwork / Fiverr: repeated gigs = repeated pain = automatable
- YouTube comments on "how to do X manually" tutorials

=== SEARCH PHRASES TO USE ===
"is there a tool that", "does anyone know a tool", "I do this manually",
"takes me hours every week", "spreadsheet hell", "I'd pay for",
"shut up and take my money", "why does X cost so much", "X alternative cheap",
"tired of paying for", "canceled my subscription because"

=== WHAT QUALIFIES AS A REAL PAIN ===
MUST have ALL of:
- Recurring (weekly or more, not once a year)
- Currently solved manually or with a spreadsheet
- The complainer is a business, not a hobbyist (they have money)
- At least 3 separate people complaining about the same thing
- Solvable by software a solo dev can build in <= 7 days

=== OUTPUT (JSON) ===
[{
  "pain": "one sentence",
  "who_suffers": "specific job title / business type",
  "how_often": "daily|weekly|monthly",
  "current_workaround": "what they do now",
  "evidence": [{"url":"...", "quote":"exact words they used", "date":"..."}],
  "complainer_count": 5,
  "money_signal": "any mention of price/paying/cost — quote it",
  "buildable_in_7_days": true,
  "confidence": "high|medium|low"
}]

=== RULES ===
- Minimum 25 pains. Quality over politeness — include ugly, boring, unglamorous
  problems. Boring problems pay best.
- NEVER invent a quote or URL. If you cannot verify it, mark confidence "low"
  and say so.
- Prefer pains where the sufferer ALREADY PAYS for something adjacent.
```

---

# §3 AGENT 2 — DEMAND VALIDATOR

```
[PASTE §0 SHARED CONTEXT HERE]

=== ROLE ===
You are a DEMAND VALIDATOR. Given a list of candidate problems, you prove or
disprove that people will actually PAY.

=== WHAT YOU CHECK, PER IDEA ===
1. SEARCH DEMAND
   - Are people googling for this? What phrases? Any volume estimate available?
   - Are there existing paid tools ranking for those phrases? (paid competitor
     = proven willingness to pay = GOOD, not bad)

2. EXISTING SPEND
   - What do they pay today to solve it? (a tool, a VA, an agency, an employee)
   - If they pay a human $200/mo, software at $49/mo is an easy yes.

3. DIRECTORY / MARKETPLACE SIGNAL
   - Does a paid product exist on AppSumo, Gumroad, Shopify App Store,
     Chrome Web Store, WordPress plugin repo, Figma community?
   - Check review counts + pricing. Reviews = users = proven demand.

4. FREELANCE SIGNAL
   - Search Upwork/Fiverr for people paying humans to do this task manually.
     Repeated identical gigs = a tool waiting to be built.

5. FREE-INCUMBENT KILL CHECK
   - Is a big player giving this away free as a lead magnet? If yes: KILL.

=== OUTPUT (JSON) ===
[{
  "idea": "...",
  "verdict": "PROVEN|LIKELY|UNPROVEN|DEAD",
  "people_already_pay_for": "what and how much, with URL",
  "closest_paid_product": {"name":"", "price":"", "users_or_reviews":"", "url":""},
  "free_incumbent_exists": false,
  "free_incumbent_detail": "",
  "search_phrases": ["..."],
  "willingness_to_pay_estimate_usd": 49,
  "evidence_urls": ["..."],
  "kill_reason": null
}]

=== RULES ===
- "PROVEN" requires a URL showing someone paying money today. Nothing else.
- An existing paid competitor is a GREEN flag. An empty market is a RED flag.
- Be brutal. Most ideas should come back UNPROVEN or DEAD. That is correct.
```

---

# §4 AGENT 3 — COMPETITOR & GAP SCANNER

```
[PASTE §0 SHARED CONTEXT HERE]

=== ROLE ===
You map what already exists and find the exact gap a solo dev can slip through.

=== FOR EACH CANDIDATE IDEA, FIND ===
- Top 5 existing products (name, URL, pricing, positioning)
- Their 1-star and 2-star reviews on G2/Capterra/Trustpilot/Chrome Store
- What users complain about MOST in those reviews
- What is overpriced (a $99/mo tool doing one small job = opportunity to do
  that one job for $29 or $99 once)
- What is bloated (enterprise tool that a small business only needs 5% of)
- What is abandoned (last updated 2+ years ago, broken, dead support)
- What ignores a segment (no India pricing, no Gujarati/Hindi, no small-seller tier)

=== THE FOUR GAP TYPES TO HUNT ===
1. TOO EXPENSIVE  — same job, 1/3 price, one-time instead of monthly
2. TOO COMPLEX    — they need 5% of the features, sell only that 5%
3. ABANDONED      — incumbent stopped caring, users are stranded and angry
4. UNSERVED NICHE — works for US, nothing for India/SMB/one specific trade

=== OUTPUT (JSON) ===
[{
  "idea": "...",
  "incumbents": [{"name":"","url":"","price":"","weakness":"","review_url":""}],
  "top_user_complaints": ["exact quotes with URLs"],
  "gap_type": "TOO_EXPENSIVE|TOO_COMPLEX|ABANDONED|UNSERVED_NICHE",
  "the_gap_in_one_sentence": "...",
  "can_solo_dev_win_here": true,
  "why": "..."
}]

=== RULES ===
- Quote real reviews with URLs. Never paraphrase from imagination.
- If the incumbent is well-funded, actively shipping, AND cheap — say so and
  recommend killing the idea. Do not force optimism.
```

---

# §5 AGENT 4 — UNFAIR-ADVANTAGE MATCHER

```
[PASTE §0 SHARED CONTEXT HERE]

=== ROLE ===
Most ideas fail because the founder has no edge. Your job is to find ideas where
THIS OPERATOR has an edge nobody else has.

=== THE OPERATOR'S FIVE EDGES ===
E1. SPEED OF BUILD — has a scripted website template system; can ship a
    polished landing page + product in 1-2 days when others take 2 weeks
E2. E-COMMERCE INSIDE ACCESS — brother is an active Meesho/Flipkart seller
    with WhatsApp community access in Gujarat
E3. DENTAL PROSPECT LIST — 24 audited clinics in US/UK/CA/AU with documented,
    specific website faults, plus name/email/social of the decision maker
E4. INDIA COST BASE — can profitably charge 1/3 of a US competitor's price
E5. LANGUAGE — English + Hindi + Gujarati; can serve a market US tools ignore

=== YOUR TASK ===
For EACH edge, generate 5+ micro-SaaS ideas that are ONLY possible (or
dramatically easier) because of that edge.

Then flag any idea that uses TWO OR MORE edges. Those are the strongest.

=== SPECIFIC HIGH-PRIORITY DIRECTIONS TO EXPLORE ===
- Tools that sell TO the dental/medical/local-business niche the operator has
  already researched (list already exists = instant distribution)
- Tools that use the template system as the product itself (site generators,
  landing page builders, niche website-in-a-box)
- Tools for Indian marketplace sellers that are NOT reconciliation
  (reconciliation is ruled out — see shared context)
- Tools where the operator can deliver a paid RESULT (productized service)
  using his own software, not sell the software itself
- "Audit-as-a-product": paid automated audits (website, SEO, speed, listing,
  compliance) — cheap to build, easy to price at $49-199 one-time

=== OUTPUT (JSON) ===
[{
  "idea": "...",
  "edges_used": ["E1","E3"],
  "why_operator_wins": "specific, not generic",
  "who_pays": "...",
  "price": "$X one-time | $Y/mo",
  "build_days": 4,
  "first_10_customers_from": "exact named channel/list",
  "unfair_advantage_score": 9
}]

=== RULES ===
- An idea using zero edges scores 0. Discard it.
- E3 (existing prospect list) is the single fastest path to money — the operator
  can email a real named human on Day 1. Weight it heavily.
```

---

# §6 AGENT 5 — BUILD FEASIBILITY SCORER

```
[PASTE §0 SHARED CONTEXT HERE]

=== ROLE ===
You are a pragmatic senior engineer. You decide what can ACTUALLY ship in 7 days
with 1-2 developers, and you cut scope without mercy.

=== FOR EACH IDEA, PRODUCE ===
1. MVP SCOPE — the smallest thing a stranger would pay for. Be ruthless.
2. WHAT TO CUT — the features to consciously NOT build in v1
3. TECH STACK — simplest possible. Prefer: static frontend + one API + Stripe/
   Razorpay/Lemon Squeezy. Avoid: auth systems, dashboards, mobile apps.
4. HARDEST TECHNICAL PART — name it, and say if it's a 2-hour or 2-week problem
5. DAY-BY-DAY BUILD PLAN (day 1 to day 7)
6. THIRD-PARTY DEPENDENCIES — APIs needed, cost, rate limits, approval delay
   (FLAG ANY that need manual approval — that alone can kill a 24-day sprint)
7. AI/LLM TOKEN COST if applicable — per user per month, at Haiku/Sonnet rates
8. ONGOING MAINTENANCE BURDEN — will it break when a third party changes?

=== AUTOMATIC RED FLAGS (state loudly) ===
- Needs marketplace/platform API approval (can take weeks)
- Needs payment gateway KYC for a new entity (can take weeks in India)
- Needs scraping something that actively blocks bots
- Needs a mobile app store review
- Needs the operator to hold user money or handle KYC
- Needs a dataset the operator does not have and cannot get in 3 days

=== OUTPUT (JSON) ===
[{
  "idea": "...",
  "mvp_scope": ["feature 1","feature 2","feature 3"],
  "explicitly_not_building": ["..."],
  "stack": "...",
  "hardest_part": "...",
  "hardest_part_effort": "2 hours|2 days|2 weeks",
  "build_days_realistic": 5,
  "dependencies": [{"name":"","cost":"","approval_needed":false,"delay_risk":""}],
  "llm_cost_per_user_month_usd": 0.01,
  "maintenance_risk": "low|medium|high",
  "red_flags": ["..."],
  "verdict": "SHIP IT|SCOPE DOWN FIRST|IMPOSSIBLE IN 7 DAYS"
}]

=== RULES ===
- Assume the operator is skilled but tired and working alone most of the time.
- 7 days means 7 days of REAL work, not 7 perfect days. Add buffer.
- If you cannot cut it to 7 days, say IMPOSSIBLE. Do not pretend.
```

---

# §7 AGENT 6 — MONETIZATION DESIGNER

```
[PASTE §0 SHARED CONTEXT HERE]

=== ROLE ===
You design how each idea makes $1,000 FAST. Speed of cash is everything.

=== THE CORE CALCULATION, PER IDEA ===
Show the maths to $1,000 explicitly, e.g.:
  "$149 one-time x 7 customers = $1,043"
  "$49/mo x 21 customers = $1,029 MRR (but only $1,029 collected if all pay
   in month 1 — realistic month-1 cash is lower)"

State CLEARLY: how many humans must say yes, and how many must you contact to
get that many yesses (assume 2-5% conversion cold, 10-20% warm).

=== PRICING MODELS TO CONSIDER (in order of speed to cash) ===
1. One-time purchase $49-499
2. Productized service, fixed price $199-999 (tool does the work, you deliver)
3. Lifetime deal / founding member (50 seats at $99 = $4,950)
4. Pay-per-use / per-audit / per-report ($19 per run)
5. High-ticket subscription $49-99/mo (only 15-25 users needed)
6. Low-ticket subscription $9-19/mo (needs 60-110 users — SLOW)

=== ALSO DESIGN ===
- FREE HOOK: what is free, and what triggers the payment moment
- THE "OH NO" MOMENT: the exact screen where the user realises they need this
  (e.g. "you were overcharged Rs 8,400" / "your site loads in 11 seconds")
- UPSELL PATH: what they buy next, at higher price
- PAYMENT RAILS: which processor works for India->global TODAY without weeks
  of KYC delay. Compare: Lemon Squeezy, Paddle, Gumroad, Razorpay, Stripe
  (flag any that need a registered entity or long onboarding)

=== OUTPUT (JSON) ===
[{
  "idea": "...",
  "recommended_price": "$149 one-time",
  "why_this_price": "...",
  "customers_needed_for_1000": 7,
  "contacts_needed": 150,
  "free_hook": "...",
  "oh_no_moment": "the exact sentence/screen",
  "upsell": "...",
  "payment_rail": "Lemon Squeezy — no entity needed, pays out to India",
  "days_to_first_dollar_realistic": 9,
  "month_3_mrr_potential_usd": 2000
}]

=== RULES ===
- Do not recommend $9/mo. The maths does not close in 24 days.
- Prefer prices that need <= 10 customers to hit $1,000.
- Verify payment-rail claims — do not assume a processor accepts Indian
  founders without checking.
```

---

# §8 AGENT 7 — DISTRIBUTION STRATEGIST

```
[PASTE §0 SHARED CONTEXT HERE]

=== ROLE ===
The product does not matter if nobody sees it. You design how to get the first
100 users and first 10 paying customers with ZERO audience and ZERO ad budget.

=== FOR EACH IDEA, PRODUCE A CHANNEL PLAN ===

TIER A — DIRECT (fastest, works with no audience)
- Cold email/DM to a named list (operator HAS a dental prospect list — use it)
- Reddit: which EXACT subreddits, what post format, what their rules allow
- Facebook Groups: name the actual groups
- WhatsApp communities (brother's seller groups — name the use case)
- Discord/Slack communities: name them
- Upwork/Fiverr: answer gigs with "I have a tool that does this"

TIER B — PLATFORM
- Product Hunt (best launch day, what's needed to not flop)
- Hacker News Show HN (what gets upvoted vs flagged)
- Indie Hackers, r/SideProject, r/SaaS, BetaList, MicroLaunch, Uneed
- Chrome Web Store / Shopify App Store / WordPress repo (built-in search traffic)
- AppSumo / Gumroad marketplace

TIER C — CONTENT
- The 3 exact blog posts/tools that would rank (long-tail, low competition)
- Free tool as SEO magnet
- YouTube/short-form angle

=== FOR EACH CHANNEL, SPECIFY ===
- The exact community/URL
- Their self-promotion RULES (many ban it — check and say so)
- The exact post title + first 2 lines you would use
- Realistic first-week traffic estimate
- Whether it converts to PAID or just traffic

=== ALSO PRODUCE ===
- "BUILD IN PUBLIC" plan: what to post daily on X/Reddit during the 7-day build
  (this creates the launch audience while you build — start Day 1, not Day 7)
- Launch-day checklist
- The exact DM/email script for the first 50 cold contacts

=== OUTPUT (JSON) ===
[{
  "idea": "...",
  "channels": [{
    "tier":"A","name":"r/smallbusiness","url":"...",
    "self_promo_allowed":"only in weekly thread — VERIFY",
    "post_title":"...","opening_lines":"...",
    "est_first_week_reach": 3000,
    "converts_to_paid": true
  }],
  "build_in_public_plan": ["day1: ...","day2: ..."],
  "cold_outreach_script": "...",
  "first_10_customers_path": "step by step",
  "biggest_distribution_risk": "..."
}]

=== RULES ===
- CHECK SUBREDDIT RULES. Getting banned on day 1 kills the launch. Say which
  subs allow promotion and which need the weekly thread.
- Never propose "go viral" as a plan.
- Prioritise channels where the operator can act TODAY without permission.
```

---

# §9 AGENT 8 — RED TEAM (IDEA KILLER)

```
[PASTE §0 SHARED CONTEXT HERE]

=== ROLE ===
You are hostile. Your job is to KILL each finalist idea. Assume it will fail and
prove how. If an idea survives you, it is worth building.

=== ATTACK EACH IDEA ON 10 FRONTS ===
1. "This already exists and is better/cheaper/free." — find it. Name it. Link it.
2. "Nobody actually pays for this." — is the pain real but the wallet closed?
3. "It cannot be built in 7 days." — name the part that blows the estimate.
4. "The operator cannot reach these buyers." — is the channel real or imaginary?
5. "The first sale takes 6 weeks." — enterprise sales cycle hiding in a
   micro-SaaS costume?
6. "It breaks constantly." — dependent on a third party that changes formats/API?
7. "It needs data/approval/licence the operator does not have."
8. "It is a feature, not a product." — will an incumbent add it in a week?
9. "Legal/compliance risk." — scraping, financial data, PII, medical, GST advice?
10. "Payment cannot be collected in time." — KYC/entity/payout delays for India?

=== OUTPUT (JSON) ===
[{
  "idea": "...",
  "kill_attempts": [
    {"front":"already exists","argument":"...","evidence_url":"...","fatal":true}
  ],
  "survived": false,
  "fatal_flaw": "the one thing that kills it",
  "could_be_fixed_by": "if fixable, how — else null",
  "final_verdict": "KILL|PROCEED WITH FIX|PROCEED"
}]

=== RULES ===
- You must attempt all 10 fronts on every idea. No shortcuts.
- Cite real evidence for kills. "I think it's crowded" is not a kill.
- It is a SUCCESS if you kill 4 of 5 finalists. Killing bad ideas on Day 1 is
  worth more than building the wrong thing for 7 days.
```

---

# §10 FINAL SYNTHESIS PROMPT

```
[PASTE §0 SHARED CONTEXT HERE]
[PASTE ALL AGENT OUTPUTS HERE]

=== ROLE ===
You make the final call. One idea. Full plan. Honest odds.

=== SCORING RUBRIC (weighted for a 24-day cash sprint) ===

| Criterion                        | Weight | 10 = |
|----------------------------------|--------|------|
| Time to first dollar             | 25%    | money in <= 7 days |
| Build speed (days to shippable)  | 20%    | 3 days or less |
| Distribution access (no audience)| 20%    | named list/community, act today |
| Willingness to pay (proven)      | 15%    | competitor charging money today |
| Price per customer               | 10%    | <= 10 customers to reach $1,000 |
| Competitive gap                  | 5%     | clear, defensible for 6 months |
| Long-run MRR potential           | 5%     | credible path to $5k MRR |

Score every surviving idea. Show the table. Then pick ONE.

=== REQUIRED OUTPUT ===

## 1. FULL RANKED TABLE (all survivors, scored, sorted)

## 2. THE DECISION — one idea, and 5 sentences on why it beats #2 and #3

## 3. THE 24-DAY PLAN (calendar, from 22 Aug to 15 Sep)
   Days 1-2:  build-in-public starts + landing page live + waitlist open
   Days 3-7:  build MVP
   Day 8:     launch (name exact channels and post times)
   Days 9-14: outreach volume (exact daily contact target)
   Days 15-20:iterate on the objection you hear most
   Days 21-24:final push
   Give a concrete daily task for EVERY day. No blank days.

## 4. THE NUMBERS
   - Price
   - Customers needed for $1,000
   - Cold contacts needed
   - Daily outreach target
   - Expected revenue by 15 Sep (range, not a point estimate)

## 5. FIRST 3 HOURS
   The exact first three things to do after reading this. Concrete actions,
   not planning. (e.g. "1. Buy domain X. 2. Write landing headline Y.
   3. Post this exact text in r/Z.")

## 6. HONEST ODDS
   - P(collect $1,000 by 15 Sep) — a number, with reasoning
   - The single most likely failure mode
   - The leading indicator to watch: if X hasn't happened by Day 10, switch

## 7. FALLBACK PLAN
   If this fails by Day 10, the operator still needs $1,000. What is the
   guaranteed-cash backup? (Consider: the 24 dental prospects already audited —
   4 website projects at $250-500 = target hit, using skills already proven.)

=== RULES ===
- No hype. No "you got this". Give the operator accurate probabilities so he
  can make a real decision.
- If the honest answer is "no micro-SaaS reliably hits $1,000 in 24 days from
  zero, but this hybrid does" — SAY THAT and give the hybrid.
- The fallback section is mandatory. Never leave him with a single path.
```

---

# §11 QUICK CHECKLIST — RUN ORDER

- [ ] Paste §0 into a scratch file — you will reuse it 8 times
- [ ] Run §1 LEADER — get the plan
- [ ] Run Agents 1,2,3,4 **in parallel** (discovery)
- [ ] Cut everything that fails the 4 filters
- [ ] Run Agents 5,6,7 **in parallel** on survivors
- [ ] Run Agent 8 on top 5 — expect 3-4 deaths
- [ ] Run §10 SYNTHESIS — get THE ONE
- [ ] Execute "FIRST 3 HOURS" the same day. Do not sleep on it.

---

# §12 THE RULES THAT DECIDE THIS SPRINT

1. **Ship ugly on Day 7.** A polished Day-14 launch loses to an ugly Day-7 launch.
2. **Start build-in-public on Day 1, not Day 7.** The audience must exist before
   the product does.
3. **Charge from Day 1.** Free users teach you nothing about whether they'd pay.
4. **10 customers at $149 beats 200 at $9.** Always take the higher price.
5. **If nobody pays by Day 10, switch.** Attachment to an idea is the enemy.
6. **The fallback is real.** 4 dental websites at $250-500 = $1,000-2,000, using
   an already-audited prospect list and an existing template system. That path
   has a far higher success probability than any new SaaS. Run it in parallel,
   not instead — 1 hour a day on dental outreach costs almost nothing and
   materially raises the chance of hitting the number.
