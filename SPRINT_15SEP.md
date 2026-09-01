# SPRINT 15 SEP — 26 Aug to 15 Sep 2026
**Target: $1,000 collected. 20 days. Written after auditing the actual repo, not from assumptions.**

Supersedes the plan portion of `SPRINT-DECISION.md` (22 Aug). That document's strategy was
right. Its execution never started.

---

## 0. WHAT THE AUDIT FOUND

| Check | Finding |
|---|---|
| `sent_log.csv` | **Header row only. Zero emails sent since 22 Aug.** |
| Dry run of `campaign_manager.py` | Runs clean. **Plans 0 sends.** |
| Reason | `Skipped - NO DEMO LINK ..... 1213` |
| `demos.json` | 9 entries, keyed by **Instagram username** |
| CRM eligible rows | 1,213 US leads keyed by **email**, `Username` column blank |
| `LIVE_LINKS_20.md` | 20 live demos that are **not in `demos.json` at all** |
| July campaign result | ~1,750 sends → 34 genuine external responses → **0 closes** |
| Unworked warm replies | **3 prospects said yes/ok in July and were never followed up** |

### The blocker, precisely

`campaign_manager.py:598` has a safety rail:

```python
# THE DEMO LINK RAIL: no personal demo URL -> no email at all. Loudly.
demo_link = resolve_demo_link(lead, demos)
if not demo_link:
    stats["no_demo_link"] += 1
```

**The rail is correct. Do not remove it.** It is the only thing standing between you and
1,213 generic emails that would repeat July's 0-close result. The fix is to *feed* it demos,
not to bypass it.

### The real lesson from July

1,750 generic emails ("I spent 10 hours building a version of your site" — with no link)
produced **4 CRM-recorded replies and zero revenue.** One send even went out with an
unrendered `{{Last Name}}` merge field.

Volume is not your lever. **Demo-in-hand is your lever.** You have 20 of them built and unsent.

---

## SECTION 3: TOP 2 PATHS — DEEP DIVE

### PATH A (#1): Demo-in-Hand Rescue — the 20 already built

**1. THE VALUE OFFER**

Not "I can build you a website." That is a commodity with a thousand sellers.

The offer is: *"Your site has a specific, verifiable defect that is costing you patients
right now. I already rebuilt it. Here is the live URL. Look at it before you reply."*

The defect is never invented — it comes from `dental-prospects.json` / `scan_results.json`,
audited on their live site. Examples already on hand:

| Prospect | Verified fault | Why it converts |
|---|---|---|
| Waimea Dental Studio | Footer reads `DESIGN AND CONTENT © 2013-2026 BY DENTALFONE` | Practice opened 2025 and is running a PR campaign — a 2013 template contradicts their own positioning |
| Art of Aesthetics (140K IG) | Bio link is a raw Calendly with `?month=2023-07` hardcoded | 140K followers hitting a dead 2023 booking month |
| Jill Peters Aesthetics | Instagram bio link returns HTTP 403 | Every follower who taps it lands on an error page |
| Dr. Oldfield | SSL hostname mismatch → full-screen browser privacy warning | Patients literally cannot reach the site |

This is why demo-in-hand beats volume: you are not asking them to imagine a benefit.
You are showing them a working page and a broken page, side by side.

**2. CONVERSION MATH**

July baseline: 1,750 sends → 0.23% CRM-recorded reply → 0 closes.
Demo-in-hand to a hand-picked HOT prospect is a different mechanism entirely.

| Stage | Rate | From 20 sends | From 50 sends |
|---|---|---|---|
| Reply | 15–25% | 3–5 | 8–12 |
| Reply → live conversation | 50% | 2 | 4–6 |
| Conversation → quote sent | 70% | 1–2 | 3–4 |
| Quote → deposit paid | 40–50% | **1** | **1–2** |

**Pricing — the structure matters more than the number:**

| Offer | Price | Deposit (collect now) | Balance |
|---|---|---|---|
| Emergency fix (SSL / DNS / dead link) | $299 | 100% upfront | — |
| Linktree or bio-link → real site | $495 | 100% upfront | — |
| Full rebuild (the 20 demos) | $995–1,495 | **50% = $500–750** | on delivery |
| Premium cosmetic rebuild | $2,500–4,000 | **50% = $1,250+** | on delivery |

> **The single most important number in this document: $500.**
> Two 50% deposits on $995 rebuilds = $1,000 collected. You do not need two clients to
> pay in full. You need **two clients to say yes and pay half.** That roughly halves the
> difficulty of the target, and deposits clear faster than final invoices.

Quote the rebuild at **$995**, not $2,500, for anyone who hesitates. A $500 deposit inside
20 days beats a $2,500 quote that closes in October.

**3. TECH STACK** — all of it already on disk and working:

| Tool | File | State |
|---|---|---|
| Fault scanner | `scanner.py` | Working — 200 sites scanned |
| Demo builder | `demo_generator.py` | Working — 20 demos live |
| Deploy | `deploy_all.py` + `gh` CLI | Authed as `Milin555` |
| Sequencer | `campaign_manager.py` | Working: 5-touch, CASL/GDPR rails, bounce + suppression handling |
| End-to-end | `pipeline.py` | scan → stage → demo → deploy |
| Reply monitor | `check_replies.py` | Working |
| Copy | `OUTREACH_20.md` | **20 messages already written** |

Cash cost to run Path A: **$0.**

---

### PATH B (#2): Instagram DM Linktree Rebuild

**1. THE VALUE OFFER** — 168 linktr.ee + 44 bit.ly practices. Their entire web presence is
a rented link page they do not own. Offer: a real site on their own domain, $495, demo first.

**2. CONVERSION MATH** — DM reply rates run 20–35%, far above email, but throughput is
capped by your hands at ~30–40/day. 40 DMs → ~10 replies → ~2 quotes → 1 close.

**3. TECH STACK** — same demo generator; **send manually.** Automated IG DM at volume gets
accounts banned, and a banned account takes the whole channel with it.

**Why B is #2, not #1:** it needs demos built before you can send. Path A's are already live.

---

## SECTION 4: PLUG-AND-PLAY BLUEPRINT (PATH A)

### 4.1 THE AUTOMATION PIPELINE

```
+-- TRACK 0 . TODAY, MANUAL, 45 MIN ----------------------------+
|  3 warm July replies, never followed up:                      |
|    drneodentistry@gmail.com  -> replied "yes"  (3 Jul)        |
|    lapeiradental@gmail.com   -> replied "ok"   (6 Jul)        |
|    pannudds                  -> demo sent      (29 Jun)       |
|  Highest close probability in the entire dataset. Send first. |
+---------------------------------------------------------------+
              |
+-- TRACK A . TODAY, MANUAL, 2 HRS -----------------------------+
|  OUTREACH_20.md   -> 20 messages, already written             |
|  LIVE_LINKS_20.md -> 20 demos, already live                   |
|  Send in the channel each record specifies (email / IG / phone)|
|  NO CODE REQUIRED. This is copy-paste.                        |
+---------------------------------------------------------------+
              |
+-- TRACK B . DAYS 2-5, AUTOMATED ------------------------------+
|  scan_results.json (200 scanned, faults + hooks ready)        |
|      | rank by score                                          |
|  pipeline.py --limit 30 --deploy-demos                        |
|      | writes CRM rows + builds + deploys demos               |
|  UPDATE demos.json  <- THE FIX. Map every new demo.           |
|      | verify: campaign_manager.py --dry-run must show > 0    |
|  campaign_manager.py --send --max-sends 20                    |
|      | 5-touch sequence, auto follow-ups on days 3/7/12/18    |
|  check_replies.py -> daily                                    |
+---------------------------------------------------------------+
```

**The one gate that matters.** Never run `--send` until this prints a non-zero number:

```bash
python campaign_manager.py --dry-run --max-sends 20 | grep "Planned"
```

If it says `Planned ........ 0`, your `demos.json` mapping is broken. Fix that, not the rail.

### 4.2 COPY-PASTE OUTREACH SCRIPTS

**TRACK 0 — the three warm leads, full records (verified from `data/campaign_crm_old.csv`
and `data/campaign_crm_friend.csv`; none of them are in the current CRM, which is why they
were never followed up):**

| Prospect | Email | Site | Phone | What happened | Note |
|---|---|---|---|---|---|
| **DR NEO \| DENTIST** | drneodentistry@gmail.com | drneodentistry.com | +357 70005758 | **Replied "yes"** 3 Jul to "Website Complete" | Demo video exists: `dr neo.mp4` on Drive. Phone is Cyprus (+357), not US as the CRM claims — check timezone before calling. |
| **Dr. Carlos E Lapeira** | lapeiradental@gmail.com | carloslapeira.com | +57 315 725 5175 | **Replied "ok"** 6 Jul | Colombia (+57). Cosmetic dentist — highest-value segment. Spanish may convert better. |
| **Dr. Dalvir Pannu** | pannudds@pannudental.com | pannudental.com | — | Said "thanks for getting back to me", demo sent 29 Jun, never closed | Founder/CEO of a multi-doctor practice. Biggest ticket of the three. |

These three are worth more than the next 500 cold emails combined. They are the only people
in your entire dataset who have already said yes to you.

**(a) The warm re-engagement — send these three TODAY**

> **Subject:** Re: Website Complete: DR NEO | DENTIST
>
> Dr. Neo,
>
> You said yes back in July and I dropped the ball on getting it finished — that
> was on me, and I'm sorry.
>
> The build is still live and still yours if you want it. I've kept the whole
> sprint open through 15 September.
>
> To finish it properly — your domain, your booking system, your photos, and I
> maintain it after launch — it's $995, half up front.
>
> If you still want it, reply "go" and I'll send the payment link and start today.
> If you've moved on, tell me and I'll close the file for good.
>
> Milin

*Why it works: it opens by taking the blame, which resets a 7-week silence without making
them explain themselves. It restates the ask concretely. And it gives an explicit exit —
which is what makes a dead lead answer at all.*

**(b) The cold demo-in-hand — the pattern already in `OUTREACH_20.md`**

> **Subject:** {Practice Name} — a rebuilt homepage, already live
>
> {Dr. Name},
>
> I rebuilt your homepage as a working site rather than writing you a pitch.
> It's live here, nothing to install:
>
> {demo_url}
>
> What prompted it, on your current site right now:
>
>   "{verified_fault}"
>
> It's a concept, not a live store, and it isn't indexed. Every page carries a note
> saying it's unaffiliated. If it isn't for you, ignore this and there's no follow-up.
>
> If you like the direction, I'll finish it properly, move it to your domain and
> maintain it.
>
> Milin Dholiya
> {sender_email}

**Do not edit this template.** It already does the four things that matter: proof before ask,
a specific verified fault, an honest disclaimer, and a clean exit.

**(c) The reply → close, sent the moment anyone responds**

> {Name} — glad it landed.
>
> Here's what finishing it means: your domain, your real photos, {their_specific_fault}
> fixed, online booking wired up, and I maintain it after launch.
>
> $995 total, $500 to start, balance when it's live. I can have it up within 4 days.
>
> Payment link: {link}
>
> If you'd rather talk it through first, here's my calendar: {link}

**(d) Compliance — non-negotiable on every cold email**

Every cold send needs a physical postal address and a working one-click unsubscribe
(CAN-SPAM). Canada and the EU are already excluded by `campaign_manager.py` — leave that
exclusion on. `patricia@impactortho.com` asked to be removed in July; confirm she is in
`SUPPRESSION_LIST.txt` before any send.

### 4.3 INTERNAL CLAUDE PROMPT — does 90% of the delivered work

Paste this into a fresh Claude Code session in this directory once a deposit clears:

```
You are finishing a paid dental website build. The client has paid a deposit.
This is real client work — nothing here may be invented.

CLIENT
  Practice:   {practice_name}
  Doctor:     {doctor_name}
  City:       {city}
  Live demo:  {demo_url}
  Local dir:  demo_builds/{slug}/
  Real site:  {their_current_site}
  Paid fault: {the_fault_they_paid_to_fix}

DO THIS
1. Read demo_builds/{slug}/ in full before changing anything.
2. Pull real content from {their_current_site}: services, team bios, hours,
   address, phone, insurance accepted. Use THEIR facts, never invented ones.
   Any fact you cannot verify on their site, leave as a clearly marked TODO —
   do not guess. Guessing a dentist's credentials or services is a liability.
3. Fix {the_fault_they_paid_to_fix} explicitly. This is the deliverable they
   bought. Confirm it in writing when done.
4. Wire real booking. If they use an existing system, embed it; otherwise a
   form posting to their real email.
5. REMOVE the demo disclaimer footer and every `noindex` tag — this is now a
   real site that must be indexed.
6. Run the 13-point checklist in MASTER_PROMPT.md. Every item must pass.
7. Verify token scrub. These strings must not survive ANYWHERE in the repo:
      Foundation Dental Alliance | Lumora | edrumm@585dentist.com
      info@foundationdentalalliance.com | 310-888-1850 | john@example.com
   `edrumm@585dentist.com` is a real third party's address. Shipping it is a
   blocking failure.
8. Mobile: no horizontal scroll at 390px. Images: no naturalWidth === 0.
9. Deploy to their domain and confirm HTTP 200 on every page.

HARD RULES
- Never invent a credential, service, price, review or testimonial.
- No AI or assistant mentions in commits, README or page source.
- Report every checklist item you could NOT complete. Do not report done
  unless all 13 pass.

OUTPUT
  A) the live URL
  B) the 13-point checklist, pass/fail per item
  C) a plain-English note to the client describing the fault that was fixed
  D) anything blocked, and why
```

---

## SECTION 5: 20-DAY SPRINT CALENDAR

### DAYS 1–3 · 26–28 AUG — UNBLOCK AND SEND

**Day 1 (today) — the only day that decides this sprint**

- [ ] **Payment link live.** Whatever rail works — Razorpay, PayPal.me, direct bank.
      Send yourself $1 end-to-end and confirm it lands. Do not skip the test.
- [ ] **Send the 3 warm July replies** (Track 0). 45 minutes. Highest close probability you own.
- [ ] **Send 10 of the 20 from `OUTREACH_20.md`**, in each record's stated channel.
- [ ] Confirm `patricia@impactortho.com` is in `SUPPRESSION_LIST.txt`.
- [ ] **Success test for today: `sent_log.csv` has more than one line.**

**Day 2**
- [ ] Send the remaining 10 from `OUTREACH_20.md`
- [ ] `python pipeline.py --limit 30 --deploy-demos --min-score 60`
- [ ] Phone the top 5 US prospects — email plus a call in the same week converts far better

**Day 3 — the demos.json fix**
- [ ] Map every new demo into `demos.json`
- [ ] `python campaign_manager.py --dry-run --max-sends 20` → **must show Planned > 0**
- [ ] First automated send: `--send --max-sends 20`
- [ ] Follow up on Day-1 sends that went quiet

### DAYS 4–10 · 29 AUG – 4 SEP — VOLUME AND FIRST CLOSE

- [ ] 20–30 demo-backed sends/day (6/inbox max — consumer Gmail flags fast)
- [ ] 20–30 Instagram DMs/day on the linktr.ee list
- [ ] `python check_replies.py` every morning
- [ ] **Reply within 2 hours.** Speed beats polish on a warm reply.
- [ ] Batch-build 30 more demos
- [ ] **Close anything you can by 31 Aug** — safest payout date
- [ ] **Target: first deposit landed by 2 Sep**

### DAYS 11–20 · 5–15 SEP — DELIVER AND COLLECT

- [ ] Deliver every paid build using the Section 4.3 prompt — **same-day where possible**
- [ ] Ask every delivered client for one referral. Warmest lead you will ever get.
- [ ] Keep sending through 10 Sep, then stop selling
- [ ] **11–15 Sep: collection only.** Chase every unpaid balance daily.
- [ ] Offer a small discount for immediate payment. Cash today beats more tomorrow.

### CHECKPOINTS — be honest at each

| Date | Test | If failed |
|---|---|---|
| **26 Aug, end of day** | `sent_log.csv` > 1 line | Nothing else matters. Send tonight. |
| **29 Aug** | ≥ 25 demo-backed contacts made | Drop tooling work entirely, send manually |
| **2 Sep** | ≥ 1 reply in conversation | Price is not the problem — the channel is. Switch to phone. |
| **5 Sep** | ≥ 1 deposit collected | Drop to $495 flat; sell the fix, not the rebuild |
| **10 Sep** | ≥ $500 collected | Stop selling. Deliver and collect only. |

---

## THE NUMBERS

| Route to $1,000 | Deposits needed | Contacts required |
|---|---|---|
| 2 × $995 rebuild @ 50% deposit | **2** | ~60 demo-backed |
| 1 × $2,500 premium @ 50% | **1** | ~40 to HOT prospects |
| 4 × $299 emergency fix, paid in full | 4 | ~120 |
| Realistic mix | **2–3** | **~80 over 20 days** |

80 demo-backed contacts across 20 days is **4 per day.** You have 20 ready to send right now.

## HONEST ODDS

**P(collect $1,000 by 15 Sep): ~50%** — down from the 55–65% in `SPRINT-DECISION.md`,
because four days were spent and zero contacts were made.

**It goes up sharply if you send today.** Not build, not fix, not plan. Send.

**The most likely failure mode is not rejection. It is another four days of tooling.**
You have already built more machine than this target needs. The 20 messages in
`OUTREACH_20.md` are finished work sitting unsent — that is $1,000 of finished work that
has never been put in front of a human being.

## THE FIVE RULES

1. **Send before you build.** Every hour of tooling before the first send is an hour lost.
2. **Never bypass the demo rail.** It is the difference between this and July's 0 closes.
3. **Collect deposits, not invoices.** $500 now beats $995 in October.
4. **Reply within 2 hours.** Speed converts; polish does not.
5. **Never invent a fact about a prospect, and never promise an outcome you don't control.**
