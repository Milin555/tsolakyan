## Reacting as the dentist

**The exact word I stop at: "rebuilt."**

"I also rebuilt your homepage, so you can judge the work instead of the email"

Up to that line I'm reading a stranger who noticed something real. At "rebuilt" I understand the SSL finding was the wrapper and the redesign is the product. The whole email retroactively becomes a pitch. You spent your credibility to buy a click. On my phone, that's the delete.

**What makes it read mass-sent:**

1. `Reply "fix it" and I'll send the two things I need from you.` — Nobody types a keyword to a human. Keyword-reply is a funnel mechanic and I've seen it in the last three pitches I deleted. Also "the two things I need" is a curiosity gap. I hate curiosity gaps.
2. `Fixing that is a certificate renewal, not a rebuild.` — "not a rebuild" is a copywriter's antithesis. Real people don't preemptively negate the thing nobody said.
3. `Concept demo, not indexed, unaffiliated with Northgate Family Dental.` — This is the tell. A one-off email from a person doesn't carry a legal disclaimer block. This line exists because you send this at volume and someone got nervous. It also makes me think about lawyers, which is the last thing you want me thinking about while deciding whether to trust you.
4. Three-line signature with title, city, country, address, unsubscribe. It's correct, and it's an ESP footprint.

**Is the observation credible?**

The SSL and NXDOMAIN ones, yes — genuinely the best thing here. Dated, falsifiable in five seconds on my own phone. That's rare and it's most of your value.

But you're missing something. **If my SSL expired, I probably already know.** My host emailed me, my office manager mentioned it, a patient called. By the time you email, this is often not news — it's the fourth notification about a problem I already know about and haven't had ten minutes to deal with. Your email is written as a revelation. It should be written as *relief*. Those are different emails.

The `images_404` version is the weak one — "the hero photo and {{second_area}} load as empty boxes" reads generated, because it is. And honestly, broken images don't feel like an emergency to me. Don't sell that one at $299 urgency.

**Would I click the demo?** No.

`https://milin555.github.io/northgate-family-dental/` — an unknown personal subdomain, from an unsolicited email, from a country I have no relationship with, containing my practice's name. That is the exact shape of a phishing link. My IT guy has told me not to click that shape. The demo is your best asset and you've hosted it at the least trustworthy-looking URL possible. Put it on your own domain. `milin.dev/demo/northgate` is a different psychological object than a github.io path.

**The single sentence that would make me reply:**

Nothing in the current email. The one that would is the one that isn't there:

> **You don't pay until it's showing secure in your browser, and I don't need your passwords.**

That removes the two things actually stopping me — not price, and not doubt about whether it's broken. It's *"who is this person and why would I give a stranger overseas access to my website."* You never address it. You address it with a disclaimer about the demo instead, which is solving the wrong fear.

**Price timing — you're wrong.**

"I can do it today" with no number is the setup for a quote call, and I've been burned by that. Withholding the price doesn't make it less of a sales email, it makes it a sales email that's hiding something. $299 is *cheap*. $299 is less than one crown. The number is your best de-escalator — it proves this is a task, not a project. Say it in touch 1, in the same breath as the fix.

The touch-2 "give the fix away, then name the price" move is genuinely good and I'd respect it. But you can do both — give me the price in touch 1 and the instruction in touch 2. Nothing is lost.

**Condescending / threatening?**

Not threatening — you handled that well. The finding-without-consequence discipline works. Nothing made me feel scared, which is why I kept reading as long as I did.

Condescending: `so you can judge the work instead of the email` presumes I want to judge anything. I want to see a patient at 2:15. And `Reply "fix it"` is you giving me an instruction in the imperative. Small thing, but I'm the one who gets to give instructions in my building.

Touch 3's `Closing your file` — don't. I'm not a file, I'm not in your CRM as far as I'm concerned, and the phrase implies a relationship that never existed. "Last one from me" is honest and better.

**What beats this email:**

- A screenshot. One image of my own site with the browser warning on it, and I'd believe it without checking. You've banned images for deliverability, which is a defensible tradeoff, but understand what it costs — you're asking me to do the verification work.
- A name I recognize. "I fixed this for Dr. Patel over on Hillcrest last month — call her." One local reference obliterates the country-distance problem instantly. If you don't have one yet, the first three jobs should be priced at whatever gets you a referenceable name.
- The phone. Whoever calls my front desk and tells my office manager "your site's showing a security warning, here's the fix, no charge" wins the relationship, and I never see the email.

---

## TOUCH 1, rewritten

```
Subject: SSL expired on northgatefamilydental.com

Dr. Reyes,

Your security certificate expired 14 Aug. Chrome and Safari now put a
full-page "Not secure" warning in front of the site. Pull it up on your
phone — five seconds and you'll see it.

It's a renewal, not a rebuild. $299 flat, and you don't pay until it's
showing secure in your own browser. I don't need your passwords —
your host can do it in ten minutes for free, or I can do it today,
whichever is less hassle for you.

I'm a web developer in Surat, India. Not an agency, not local, and I
won't call you.

Reply if you want it done and I'll tell you what I need.

Milin Dholiya
[street address], Surat, Gujarat 395007, India
Unsubscribe: [link]

(I also rebuilt your homepage while I was looking at it, in case you
ever want it: milin.dev/demo/northgate)
```

**What changed and why:**

- **Price in the first breath.** $299 next to "renewal, not rebuild" makes it a chore, not a purchase.
- **"You don't pay until it's showing secure in your own browser."** This is the load-bearing sentence. It's also true and costs you nothing on a ten-minute job.
- **"I don't need your passwords."** Answers the real objection.
- **"Your host can do it for free."** Handing away the fix in touch 1, not touch 2. This is the single highest-trust line available and you were saving it for day 3 — by which point I've already deleted you. Give it immediately. It costs you the leads who were never going to pay you anyway, and it converts the ones who don't have a web person, which is exactly the segment you want.
- **"Not an agency, not local, and I won't call you."** Your foreignness is a liability you were being quietly honest about. Make it an asset — I'm not being recruited into a relationship.
- **Demo demoted to a parenthetical P.S., on your own domain.** It's no longer the reason for the email, so it stops contaminating the repair offer. And it's now something I might click *after* I've decided you're real, which is when clicking actually happens.
- **Killed:** the keyword reply, "the two things I need from you" as a tease, the legal disclaimer line, "so you can judge the work."
- **Word count: 118.** Longer than your 69. I don't care about word count, I care about how many sentences I have to read before I know what this is and whether it's safe. Your 69 words made me read all of them before I found the pitch. My 118 tells me in the first two lines and lets me stop.

**On touch 2:** since the fix instruction moved into touch 1 conceptually, touch 2 should become the *specific* instruction (the CNAME record, the Let's Encrypt one-click) — the detail, not the concept. That still works, and it's still your best email.

**One thing you should not change:** the branch rule that a cleared fault kills the sequence, and the one-line "saw it's sorted, ignore my last email, good luck" note. That note will make you more money than the entire sequence. It's the only email in this document a dentist would forward to another dentist.