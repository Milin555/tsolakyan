# D2C Storefront Template

A retail storefront for Indian clothing brands. Static — no framework, no
build step, no backend. Orders go to WhatsApp.

Modelled on the structure of Shopify stores like vedorakids.com, but it
runs on free static hosting instead of a ₹2,000+/month subscription.

```
index.html      home — carousel, shop grid, categories, reviews, FAQ
product.html    product detail — colour, size, quantity, add to cart
cart.html       bag — edit quantities, order via WhatsApp
assets/
  data.js       ← BRAND + products + copy. The whole template.
  site.css      ← six colour tokens at the top
  app.js        header, footer, drawer, cart, toast (shared)
  img/          generated placeholders (replace these)
build-placeholders.py
```

**676 KB total**, 43 images included.

---

## Rebranding for a new client — two files

### 1. `assets/data.js`

Everything the client sees lives here:

```js
const BRAND = {
  name: 'Vedora', nameAccent: 'Kids',   // accent half is coloured
  tagline: '…', blurb: '…',
  whatsapp: '917567617393',             // digits only, with country code
  phone: '+91 75676 17393',
  email: '…', instagram: '…', address: '…',
  currency: '₹', freeShipOver: 999, codAvailable: true
};
```

Then `TICKER`, `SLIDES`, `CATEGORIES`, `PRODUCTS`, `TESTIMONIALS`, `FAQ`.

Add a product by copying one object. Category chips, counts, related
items, the Instagram strip and the WhatsApp order text all update
themselves — nothing else to touch.

### 2. `assets/site.css` — six tokens

```css
--accent:      #C4903B;   /* buttons, prices, highlights   */
--accent-soft: #F3E4C6;   /* tints                         */
--ink:         #2B2724;   /* text, header, footer          */
--cream:       #FBF6F1;   /* page background               */
--paper:       #FFFFFF;   /* cards                         */
--sale:        #B3452F;   /* discount badges               */
```

Ready-made alternates:

```css
/* Rose & Slate  */ --accent:#B5687A; --accent-soft:#F2DDE2; --ink:#2A2530; --cream:#FAF6F7;
/* Indigo & Sand */ --accent:#4A5B8C; --accent-soft:#DEE3F0; --ink:#232733; --cream:#F7F5F1;
/* Emerald       */ --accent:#2F7A5B; --accent-soft:#D7EAE0; --ink:#1F2A25; --cream:#F5F8F5;
```

Fonts swap in one `<link>` per page — currently Fraunces + Outfit.

---

## Replacing the images

The placeholders are designed tiles, not broken boxes, so an unfinished
demo still looks deliberate. Replace before pitching.

Each product needs three files named after its `img` value:

```
assets/img/p01-600.webp     card         (600 × 900)
assets/img/p01-1000.webp    product page (1000 × 1500)
assets/img/p01-800.jpg      fallback     (800 × 1200)
```

Plus `c01–c04.webp` for category cards and `hero1–3.webp` for the
carousel. All product imagery is **2:3 portrait**.

`build-placeholders.py` regenerates the stand-ins (`pip install pillow`).
For real photos, use the `build-images.py` approach from the
`saidharanx-demo` project — it produces exactly this file set from a
folder of masters.

---

## How ordering works

There is no payment gateway. The cart lives in `localStorage`; pressing
**Place order on WhatsApp** opens a message with every line written out:

```
Hello VedoraKids, I'd like to order:

• VK-101 — Rose Blush Lehenga Choli
  Blush / 3-4Y × 2 = ₹2,598

Total: ₹2,598 (Free shipping)

Please confirm availability and share payment details.
```

This is how most small Indian brands actually sell, and it costs nothing
to run. If a client later wants real checkout, that's Shopify or
WooCommerce — a different project with monthly fees.

---

## Before it goes live

1. **Replace `REPLACE-WITH-LIVE-DOMAIN.com`** in `index.html` and
   `product.html`. The WhatsApp link preview will not render until
   `og:image` is an absolute URL.
2. **Swap in the client's photographs.**
3. **Check the WhatsApp number** in `BRAND.whatsapp` — digits only, with
   country code, no `+` or spaces.
4. **Confirm the offer copy** in `TICKER` and `BRAND.freeShipOver`
   against what the client actually offers.

---

## Built in

- Cart persists across pages and tabs; badge updates live
- Focus-trapped mobile drawer, skip link, `aria-pressed` on all pickers
- Reduced-motion respected — carousel autoplay and ticker stop
- WebP with JPEG fallback, `width`/`height` on every image, hero eager
  and everything else lazy
- Product schema on detail pages
- `<noscript>` fallback pointing at WhatsApp
- Print stylesheet

## Known limits

- **No real checkout.** WhatsApp handoff by design.
- **Product pages share one URL** (`product.html?sku=`). Fine for a demo;
  separate static URLs are stronger for SEO.
- **Cart is per-device.** No accounts, no server.
- **Stock isn't tracked.** Availability is confirmed on WhatsApp.
