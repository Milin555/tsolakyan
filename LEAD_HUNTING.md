also+

 BUYER-INTENT HUNTING — DAILY SYSTEM

**Why you run this, not me:** native platform search (logged in) sees posts from the last hour. Google indexes SEO articles about hiring developers, not the person hiring one this morning. I verified this across 6 searches — yield was 1 usable lead, 27 days stale.

**30 minutes/day. Target: 5–15 real leads.**

---

## 1. SET UP ALERTS FIRST (20 minutes, once)

These work while you sleep. Do this before any manual searching.

### F5Bot — free, emails you when keywords hit Reddit

**f5bot.com** — no account friction, just an email. Add these keywords:

```
need a website
need a web developer
looking for a web developer
website developer needed
need a landing page
need an ecommerce website
developer ghosted
finish my website
website redesign
need a shopify developer
```

**This is the single highest-value automation in this document.** Reddit is where people post real, urgent, paid requests — and F5Bot pushes them to you within minutes.

### Google Alerts

**google.com/alerts** — set to "As-it-happens":

```
"looking for a web developer"
"need someone to build my website"
"web designer recommendations"
```

### LinkedIn saved searches

Run a search, then **Posts** filter → **Past 24 hours** → bookmark that URL. Open the bookmark daily.

---

## 2. LINKEDIN — highest ticket

**Search, then filter: Posts → Past 24 hours.** The date filter is the whole trick.

```
"looking for a web developer"
"need a web developer"
"hiring a web designer"
"looking for a freelance developer"
"need someone to build our website"
"web developer recommendations"
"our developer ghosted"
"need to finish our website"
"launching soon" website developer
"looking for a Shopify developer"
"need a landing page built"
```

**Verify the real post age before messaging.** LinkedIn's "3 weeks ago" is vague and posts get bumped. Copy the `activity-XXXXXXXXXX` number from the URL and run:

```
! python check_post_age.py 7485604048881229836
```

**Rules:**
- Comment publicly **and** DM. Comments get seen by others hiring too.
- Under 48 hours old, or skip it.
- Lead with a portfolio link, not "I'm interested."

---

## 3. REDDIT — highest volume, most urgent

Browse these directly, sorted **New**:

| Subreddit | What's there |
|---|---|
| **r/forhire** | `[Hiring]` posts — filter for those, ignore `[For Hire]` |
| **r/DesignJobs** | Design + web work |
| r/slavelabour | Small budgets, fast cash, easy first reviews |
| r/smallbusiness | Owners asking for recommendations |
| r/entrepreneur | Founders pre-launch |
| r/Emailmarketing, r/shopify | Platform-specific asks |

**Reddit search syntax:**
```
title:[Hiring] website
title:[Hiring] developer
"need a website" self:yes
```

**Rules:**
- Sort by **New**, not Hot. Hot means everyone already applied.
- Under 6 hours old = your best odds.
- Read the sub's rules before commenting — some require a specific reply format and ban you for missing it.
- Reply in-thread first, then DM.

---

## 4. FACEBOOK GROUPS — least competition

Search Facebook for groups: `[your city] business owners`, `entrepreneurs [country]`, `startup founders`, `[city] small business`.

Join 10. Then use the **search-within-group** box:

```
website
web developer
need help website
recommend developer
```

**Why this beats everything else:** almost no freelancers do it. Group posts are invisible to Google, so you're not competing with 200 applicants. Local groups convert especially well because you can meet in person.

---

## 5. THE SCORING FILTER

Only contact a lead if it clears **60**:

| Signal | Points |
|---|---|
| Explicitly asking for a developer | 30 |
| Asking for recommendations | 25 |
| Describes an upcoming project | 15 |
| **Posted under 24 hrs** | **20** |
| Posted 1–3 days | 12 |
| Posted 4–7 days | 5 |
| Over 14 days | **0 — skip** |
| States a budget | 20 |
| Project looks $1,000+ | 15 |
| Can DM directly | 10 |
| Exact skill match | 15 |

**Under 60 = ignore.** Chasing weak leads is what produced 0 from 1,751 emails.

---

## 6. HOW TO REPLY

**Speed beats quality.** On r/forhire the first 5 replies get read; #30 does not. A good message in 10 minutes beats a perfect one in 3 hours.

### Reddit / public comment
```
Sent you a DM. Portfolio: [link]
Built similar: [most relevant demo]
Can start today.
```

Short. The DM does the work.

### DM / LinkedIn
```
Hi [Name] — saw your post about [exact thing they asked for].

I build [that]. Recent work: [portfolio link]

For your project I'd [one specific detail from their post].
Timeline: [X] days. Budget: [their number, or your quote].

One question: [something specific]?
```

**Three rules:**
1. Quote their own words — proves you read it
2. Link the portfolio in message one
3. **End with a question** — makes replying easy

### Never
- "I am interested in your project"
- "I have 5 years experience" *(you have no clients — don't invite the question)*
- Any invented client, review, or credential

---

## 7. DAILY ROUTINE — 30 MIN

| Min | Task |
|---|---|
| 0–5 | Check F5Bot + Google Alerts email |
| 5–12 | r/forhire + r/DesignJobs, sorted New |
| 12–20 | LinkedIn saved searches, past 24h |
| 20–26 | Facebook groups, search "website" |
| 26–30 | Send 5–10 messages |

**Do this at 9am and 6pm.** Posts get answered within hours — twice a day roughly doubles your hit rate.

---

## 8. TRACK IT

`hot_leads.csv`:

```
Date | Platform | Person | PostURL | What | Budget | PostAge | Score | Contacted | Replied | Outcome
```

**After 30 leads, check which platform actually produced replies. Drop the other two.** Don't run all four channels for 29 days out of loyalty to a plan.

---

## 9. WHAT TO EXPECT — REAL NUMBERS

| Metric | Realistic |
|---|---|
| Leads found/day | 5–15 |
| Worth contacting | 3–8 |
| Reply rate | **10–25%** |
| Reply → real conversation | 40% |
| Conversation → close | 15–25% |
| **Closes/week** | **1–2** |

**Compare: cold email was 0 out of 1,751.** Even 10% replies from people who raised their hand is a different universe.

**[ASSUME]** — these are estimates, not verified. Replace them with your own numbers after week 1.

---

## 10. THE ONE THAT MATTERS

**F5Bot.** Set it up today.

Everything else needs you at a screen. F5Bot emails you the moment someone on Reddit types "I need a website" — and the person who replies in the first 10 minutes usually wins.
