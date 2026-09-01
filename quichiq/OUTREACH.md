# Quichiq — outreach pack

**Prospect:** Anvi Gupta, founder — Quichiq Creations (transformable / reversible clothing)
**Instagram:** @quichiqclothing · 401 posts · 799 followers · Founder: @founderanvigupta
**Site:** www.quichiq.com (Shopify) · **Phone:** +91 8652839959 · **Email:** info@quichiq.com
**Location:** Mumbai, Maharashtra
**Price band:** ₹1,839 – ₹11,899 · 83 products · 547 variants

---

## What is actually wrong with the site

Every claim below was checked against the live HTML and Shopify's own product API.
Do not send anything that is not on this list.

### 1. The sale price is displayed ABOVE the crossed-out price — 34 of 83 products (41%)

Rendered live on the product page:

```
Rs. 2,449.00   R̶s̶.̶ ̶1̶,̶7̶9̶9̶.̶0̶0̶
```

`compare_at_price` has been set to the *old, lower* price, so the "discount" reads as a
price rise. A shopper sees: this used to be ₹1,799 and now they want ₹2,449.

Examples (handle → shown price / struck-through price):

| Product | Shows | "Was" |
|---|---|---|
| triple-threat-golden-leaf | ₹2,449 | ₹1,799 |
| triple-threat-black | ₹3,379 | ₹2,499 |
| triple-threat-merlot | ₹3,379 | ₹2,499 |
| triple-threat-blush-satin | ₹2,359 | ₹2,199 |
| thryve-slit-mickey | ₹2,499 | ₹1,899 |
| thryve-slit-coin-legacy | ₹2,499 | ₹1,899 |

170 variant rows affected across 34 products. **This is the lead.** It costs her money,
it is embarrassing, and it is a 10-minute fix — which is exactly why telling her buys trust.

### 2. Homepage hero banners are WhatsApp exports

Actual filenames being served as hero imagery:

```
WhatsApp_Image_2025-10-29_at_5.35.56_PM.jpg     214 KB
WhatsApp_Image_2025-10-28_at_1.22.51_PM.jpg     215 KB
WhatsApp_Image_2025-10-28_at_3.33.57_PM.jpg     115 KB
```

WhatsApp recompresses every image that passes through it. Her hero shots are
second-generation JPEGs. On a ₹5,000 dress, hero image quality *is* the first
quality judgement a buyer makes.

### 3. Zero reviews, store-wide

Judge.me is installed and empty. Every product page renders the words **"No reviews"**
(verified on 4 products sampled across the catalogue). At ₹1,839–₹11,899 with no
social proof, a first-time visitor has nothing to lean on.

### 4. Page weight

- Homepage HTML alone: **990 KB** (before a single image)
- First 13 images: **2.87 MB**, including a single **1.11 MB PNG** (`1771683413010.png`) — a photo saved as PNG
- **544** distinct image URLs referenced on the homepage
- TTFB ~0.9–1.2s, full HTML ~2.1s on a desktop connection

On Indian mobile data this is where the drop-off is.

---

## Two things I checked and they are NOT true — do not mention these

A surface scan of the site suggests both of these. Both are wrong. Sending either
would blow the credibility the price bug earns.

- **"Everything is sold out."** False. The `Sold Out` badge sits on every product card
  in the markup, but carries `style="display: none;"`. Shopify's API reports
  **538 of 547 variants in stock**. The store sells fine.
- **"An 18+ age gate is blocking visitors."** False. The age-verifier markup exists in
  the theme but carries `data-enable="false"`. It never fires.

---

## Strategy note before you send

She is not going to agree her site needs rebuilding — it is a competent paid Shopify
theme and it looks fine to her. Leading with *"your site needs a rebuild"* gets a no.

Lead with the price bug as a **free gift**. It is specific, verifiable in 30 seconds,
and costs her money today. Founders always reply to that. The rebuild conversation
comes after she has thanked you, not before.

---

# THE MESSAGES

## A. Instagram DM — opener

Keep it this short. A DM from a non-follower lands in Requests; a wall of text there
is never opened. The only job of message 1 is to earn a reply.

> Anvi — quick heads up, not a pitch.
>
> Your Triple Threat Skirt (Golden Leaf) is showing ₹2,449 with ₹1,799 crossed out
> next to it, so it reads like the price went *up*.
>
> I checked and it's on 34 of your 83 products. Want me to send you the list?

**Why this works:** "not a pitch" disarms. The bug is checkable in 30 seconds, so you
are instantly credible. It ends on a yes/no question, which is the lowest-effort reply
possible. You are offering her something, not asking for anything.

## B. Instagram DM — after she replies

> Sending it over now.
>
> It's the compare-at price field — looks like when prices went up, the old price got
> left in the "was" box, so Shopify is crossing out the lower number. 10 minutes in the
> product editor and it's gone.
>
> Two other things I noticed while I was in there, if useful:
>
> 1. Your homepage banners are WhatsApp exports (filenames are literally
>    WhatsApp_Image_2025-10-29). WhatsApp recompresses everything, so your hero shots
>    are running at about half the quality you actually shot them at.
> 2. Every product page says "No reviews" — Judge.me is installed but empty. At
>    ₹2,000–₹11,000 that's the biggest thing between a first-timer and checkout.
>
> I design and build sites — couple of recent ones:
> https://sure-goals-776913.framer.app/
> https://flourished-zebra-897337.framer.app/
>
> Happy to record a 3-min walkthrough of your store the way a first-time buyer sees it.
> Free, yours either way. Want it?

## C. WhatsApp — +91 8652839959

WhatsApp gives you more room, but line 1 still has to earn lines 2–20.

> Hi Anvi — I'm Promise. Found Quichiq through your Instagram and went to quichiq.com
> to look properly. One thing you'll want to fix today:
>
> **On 34 of your 83 products the sale price is showing above the crossed-out price.**
> The Golden Leaf Triple Threat Skirt reads ₹2,449 with ₹1,799 struck through beside it.
> To a shopper that reads as "this was ₹1,799 and now they want ₹2,449." It's the
> compare-at price field holding the old price. Quick fix, but it's live on 41% of your
> catalogue right now.
>
> Two other things while I was in there:
>
> • Your homepage banners are WhatsApp exports — the filenames are
>   WhatsApp_Image_2025-10-29, WhatsApp_Image_2025-10-28. WhatsApp recompresses every
>   image it touches, so your hero shots are running at roughly half the quality of the
>   originals. On a ₹5,000 dress that's the first thing a buyer judges.
>
> • Every product page says "No reviews". Judge.me is installed and sitting empty. At
>   your price point that's the single biggest thing standing between a new visitor and
>   checkout.
>
> I design and build sites. Two recent ones:
> https://sure-goals-776913.framer.app/
> https://flourished-zebra-897337.framer.app/
>
> The reversible concept is genuinely good and the founder story on your About page is
> better than most — it's just not doing any work where people actually buy.
>
> Want me to send a 3-minute screen recording of your store the way a first-time buyer
> sees it? Free, and yours whether or not we ever work together.

---

## If she replies — handling the three likely answers

**"Thanks, we'll fix it."** (most likely)
> No problem at all. If you want the full list of the 34 I can drop it in a sheet.
>
> The bigger one is the reviews — you've got 401 posts of content and people clearly
> engaging, but nothing on the product page tells a stranger anyone has ever bought
> from you. Want me to show you what I'd change? 3-min recording, no charge.

**"What do you charge?"**
Do not quote a number yet — you have not scoped anything.
> Depends what we're fixing. If it's the conversion path — product pages, reviews,
> imagery, mobile speed — that's a different job from a full rebuild.
>
> Let me send the walkthrough first so we're talking about the same thing. If it's
> useful we'll talk numbers, if not you've lost nothing.

**No reply after 4 days** — bump once, on new information only. Never "just following up."
> Anvi — one more, then I'll leave you alone.
>
> Ran your homepage through a speed check: 990 KB of HTML before a single image loads,
> and one banner PNG on its own is 1.1 MB. On mobile data that's most of your Instagram
> traffic gone before the page paints.
>
> Still happy to send the walkthrough if you want it.

---

## Honest flag on the portfolio links

Both Framer links are **service/agency sites** — Neha Kikani (social content studio) and
Two Creatives (Surat, two-person content team). Neither is ecommerce, and neither is
Shopify. Quichiq is a Shopify fashion store with 83 products and 547 variants.

She may click and think "these are landing pages, my store is a different problem."

Two options:
1. **Frame them as design work, not store work** — "couple of recent builds" (as written
   above). Honest, and it shows craft.
2. **Better if you have time:** build one Shopify-style product page mock for Quichiq
   using their own product photos, and lead with that instead. It closes far harder than
   a generic portfolio link, and it is the same play that worked on the dental demos.
