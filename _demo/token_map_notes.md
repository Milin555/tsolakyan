# Token map notes

Companion to `token_map.json`. Scope: the four template roots only
(`Lura Dentist`, `Gary Solnit Dentist`, `Modern Smile Center Dentist`,
`Ritter Ramsey Dentist`). `variant-*` subfolders, `assets/`, and `.git` were
excluded. 19–20 `.html` files per template (not 29).

Every string in `token_map.json` was verified present by literal substring
match against the concatenated `.html` of its template — 248 strings checked,
0 failures, and every `brand_names.count` matches a live recount.

---

## 1. Strings that are UNSAFE to blind-replace

### 1a. Hard blockers — replacing these breaks the page

| String | Where | Why it breaks |
|---|---|---|
| `lumora` (lowercase) | `assets/css/lumora.css?v=20260614f` — 13–14 `<link href>` per template | It is the **stylesheet filename**. Replacing it 404s the CSS and the whole site renders unstyled. |
| `lumora` (lowercase) | `lumoraLead` — JS function name, declared once and referenced once per `index.html` (`onsubmit="return lumoraLead(event)"`) | A partial rename desynchronises declaration from call site and the homepage lead form throws. |
| `585` | `assets/img/585-logo-light.svg`, `assets/img/585-logo-dark.svg` (Lura only) | Image paths. Note the token `585dentist` is safe here — the paths contain `585-logo`, not `585dentist` — but a looser `585` rule would break them. |
| `lumora` | `assets/img/lumora-logo.svg` (Lura only) | Image path. |
| `solnit` | `assets/img/dr_solnit.jpg` (Gary Solnit **and** Modern Smile Center) | Image path. See §3 — Modern Smile Center genuinely points at Gary Solnit's photo. |

**Rule for the build script:** never apply brand replacement inside
`href=`/`src=`/`srcset=`/`url(...)` values, or inside `<script>` bodies.
Restrict replacement to text nodes plus a whitelist of attributes
(`title`, `alt`, `content`, `aria-label`, `placeholder`, `onclick` string
literals).

### 1b. Common-word / over-broad tokens

| String | Risk |
|---|---|
| `Ritter` (124 hits), `Ramsey` (105) | Bare surnames. They are substrings of the doctor names `Dr. Robert G. Ritter`, `Dr. Isabelle Ritter`, `Dr. Christopher Ramsey` and of the page filenames `doctor-rob-ritter.html`, `doctor-isabelle-ritter.html`, `doctor-chris-ramsey.html` (which appear in `href=`). **Only the multi-word forms are in the map.** Do not add bare `Ritter`/`Ramsey`. |
| `Modern Smile Center` (3 title-case hits) | `Modern` and `Smile` are ordinary words all over this template's body copy (`modern dental clinic`, `Every Smile`, `Smile Makeovers`). Replace only the full 3-word phrase, never the parts. |
| `Family Dentistry` (Lura, 8) | This is the logo sub-label, but the identical phrase also appears in prose (`establishing the Family & Implant Dentistry`). Match it only inside the brand lockup `<span>`. |
| `PROSTHODONTICS` | Logo sub-label. Also a genuine specialty word appearing in prose and `<title>` (`Beverly Hills Prosthodontics`) in different casing. Replace the all-caps form only. |
| `Beverly Hills` (57 in Gary Solnit) | Both brand-name component **and** a real geographic reference in prose/maps. Replacing it wholesale rewrites map links and "We are located in Beverly Hills, California". Treat as a *location* token, not a brand token. Same for `Jupiter` (41) and `Woodlands` (61). |
| `Dr. Neo` (77) vs `Dr. Neo Boutique Dental Clinic` (66) | The 11-hit remainder is `Dr. Neofytos Ioannides`. Replacing `Dr. Neo` corrupts that doctor's name. **Always replace the long form first**, and never ship a bare `Dr. Neo` rule. |

### 1c. Ordering hazards (nested / overlapping strings)

These must be replaced **longest-first** or the short form will shred the long
one. Counts below are raw substring counts, so shorter entries include the
longer ones.

- Lura: `Foundation Dental Alliance DDS Careers` (3) → `Foundation Dental Alliance DDS` (12) → `Foundation Dental Alliance Dentistry` (15) → `Foundation Dental Alliance` (81)
- Gary Solnit: `Dr. Gary Solnit, DDS, MS` (7) → `Dr. Gary Solnit, DDS` (43) → `Dr. Gary Solnit` (63) → `Gary Solnit, DDS, MS` (10) → `Gary Solnit` (66)
- Modern Smile Center: `Dr. Michael Cimino, DDS, MS` (7) → `Dr. Michael Cimino, DDS` (43) → `Dr. Michael Cimino` (63) → `Michael Cimino` (63)
- Ritter Ramsey: `Ritter & Ramsey General & Cosmetic Dentistry` (21) → `Drs. Ritter & Ramsey, DDS` (33) → `Drs. Ritter & Ramsey` (56) → `Ritter & Ramsey, DDS, MS` (3) → `Ritter & Ramsey` (81)

Also note `edrumm@585dentist.com` **contains** `585dentist`, and
`info@foundationdentalalliance.com` contains `foundationdentalalliance`.
Replace the full email addresses before the brand tokens, or the emails will be
mangled into half-rebranded strings.

### 1d. Entity-encoded and whitespace-sensitive literals

The HTML mixes raw and entity-escaped ampersands. Both forms are in the map and
both must be handled:

- `Ritter & Ramsey` (81) **and** `Ritter &amp; Ramsey` (2) — plus one lone `Ritter and Ramsey`
- `FOR AESTHETIC &amp; RESTORATIVE DENTISTRY`, `GENERAL &amp; COSMETIC DENTISTRY`, `ESTHETIC &amp; COSMETIC DENTISTRY` — the SVG wordmark sub-labels are **always** entity-escaped
- `hero_h1` values contain **raw** `&` (`Beverly Hills Prosthodontics & Esthetic Dentistry`)

Whitespace literals that will silently fail an exact match if normalised:
- `footer_tagline` ends with a **trailing space** before `</p>`
- `"456 Bright Dental Blvd, Floor 3 Los Angeles, "` ends with a **trailing space** and has no city/state
- `"45 King’s Road, Chelsea,  SW3 5UZ"` uses a curly apostrophe (U+2019) and **two non-breaking spaces** (U+00A0)

### 1e. Strings deliberately EXCLUDED from the map as too risky

- bare `Ritter`, bare `Ramsey`, bare `Neo`, bare `585`, bare `Modern`, bare `Smile`
- `lumora` / `Lumora` in any lowercase form (asset path + JS identifier — see §1a). Only the all-caps display string `LUMORA CLINIC CAREERS` is included, and it is genuinely visible text.
- `RapidXAI` (4 hits per template, in the footer credit `Crafted by RapidXAI`) — this is the **agency's own** credit line, not the practice brand. Excluded so the build script does not accidentally strip its own attribution.
- `Santorini` / `Luxury Dental Retreats` (5 hits, `retreats.html`) — a separate campaign page, not practice branding.

---

## 2. Brands that are NOT visible in the page chrome (easy to miss)

Two placeholder brands survive in **all four** templates, buried inside
JavaScript-driven confirmation receipts. Neither appears in nav, footer, or any
`<title>`, so a visual QA pass will not catch them — they only render after a
user completes a form:

- `LUMORA CLINIC CAREERS` — `apply.html`, inside `<div class="receipt-header"><h4>`
- `PANNU DENTAL GROUP` — `booking.html`, inside `<div class="receipt-header"><h4>`

`PANNU DENTAL GROUP` is a fifth, otherwise-unrelated practice name. Both are in
the map under `brand_names`.

A third easy-miss category: in Gary Solnit / Modern Smile Center / Ritter
Ramsey the **visible logo wordmark is `<text>` inside an inline `<svg>`**, not
an `<img>` and not ordinary body text — e.g. `THE BEVERLY HILLS CENTER` (32),
`MODERN SMILE CENTER` (32), `RITTER & RAMSEY` (30). Any DOM-text-only or
`<img alt>`-only replacement strategy will miss the logo on every page of three
of the four templates.

---

## 3. Cross-contamination: unconverted content from other practices

These templates were themselves produced by rebranding an earlier site, and the
job was **not finished**. Each template still carries a previous practice's
identity on its secondary pages. This is not a risk so much as required work —
the build script must treat these as tokens too, otherwise the rebranded sites
ship with a stranger's name on half their pages.

**Consistent split:** the "converted" pages are `index / about / service / blog
/ booking / apply`. The "unconverted" pages are `404`, `cookies`, `licenses`,
`privacy`, `terms`, `doctor-*.html`, and `service-{cosmetic,orthodontics,preventive,restorative}.html`.

| Template | Legacy brand still on secondary pages | Count |
|---|---|---|
| Lura Dentist | `585dentist` (+ `edrumm@585dentist.com`) | 145 |
| Gary Solnit Dentist | `Dr. Neo Boutique Dental Clinic` (+ `drneodentistry@gmail.com`) | 66 |
| Modern Smile Center Dentist | `Dr. Neo Boutique Dental Clinic` (+ `drneodentistry@gmail.com`) | 66 |
| Ritter Ramsey Dentist | `Dr. Neo Boutique Dental Clinic` (+ `drneodentistry@gmail.com`) | 56 |

Additional leakage in the other direction — **`Foundation Dental Alliance` (the
Lura brand) appears in all four templates**, 25–26 times each in Gary Solnit,
Modern Smile Center and Ritter Ramsey. It is the source template, and it is
still visible in:

- `about.html` — the `about-hero_para` body text is *byte-identical in all four templates* and reads "At **Foundation Dental Alliance** Dentistry, we combine compassion…". This is why `about_heading` and `about_body` are the same string in all four entries of the JSON.
- `apply.html` — `<title>Apply Now | Careers | Foundation Dental Alliance DDS`, in all four
- the homepage services intro paragraph
- one footer brand lockup per template (`Foundation Dental Alliance` + `PROSTHODONTICS`)

Other stray artefacts confirmed present:

- **Cyprus phone `+357 70005758`** (with two spellings of the `tel:` href — `tel:+357 70005758` and `tel:+35770005758`, inconsistently) on the doctor and service-detail pages of **all four** templates, alongside the correct US number in the footer of the main pages.
- **Lura Dentist** `booking.html` and `apply.html` contain **Gary Solnit's** address (`9675 Brighton Way, Suite 330, Beverly Hills, CA 90210`), a `selectDentist('Dr. Gary Solnit, DDS')` option, an `alt="Dr. Gary Solnit, DDS"` image, and a Google Maps embed for `Dr. Neofytos Ioannides - Boutique Dental Clinic, Nikodimou Milona 10A, Limassol`. Lura has **no address of its own**.
- **Modern Smile Center** uses `assets/img/dr_solnit.jpg` as its `og:image` and `twitter:image` — Gary Solnit's headshot.
- **Ritter Ramsey** footer address is a hybrid: `Ritter & Ramsey General & Cosmetic Dentistry` / `9675 Brighton Way, Suite 330` / `Jupiter, FL 90210` — Beverly Hills street address and Beverly Hills ZIP with a Jupiter city line. Its SVG wordmark sub-label also still reads `FOR AESTHETIC AND RESTORATIVE DENTISTRY` (5) alongside the correct `ESTHETIC &amp; COSMETIC DENTISTRY` (25).
- All four `about.html` files carry three fictional placeholder locations (`123 Smile Avenue…`, `456 Bright Dental Blvd…`, `45 King’s Road, Chelsea…`) in `location_para` elements.
- `john@example.com` is a form placeholder in all four; harmless but listed for completeness.

---

## 4. Structural differences between templates

The four are near-identical Webflow exports of the same base theme; the only
real divergences are:

1. **`Lura Dentist` renders its logo differently from the other three.** It uses
   `<img src="assets/img/585-logo-*.svg">` plus a plain `<span>` text lockup.
   The other three use an inline `<svg>` with `<text>` wordmarks. A build script
   with a single logo strategy will only work on one group. Lura is also the
   only template whose `<img alt>` carries a brand (`alt="585dentist logo"` ×12,
   `alt="Foundation Dental Alliance logo"` ×7).

2. **`Ritter Ramsey Dentist` has 19 pages; the others have 20.** It ships
   **3** doctor pages (`doctor-rob-ritter`, `doctor-isabelle-ritter`,
   `doctor-chris-ramsey`) where the others ship **4**. Lura's fourth is
   `doctor-emilie-drumm`; Gary Solnit's and Modern Smile Center's is
   `doctor-neofytos-ioannides`. Consequently Ritter Ramsey is the only template
   with **no `Neofytos Ioannides` content at all** and the only one whose
   `cta_text` omits `Apply Now` from the button set.

3. **`View All Doctors` exists only in `Lura Dentist`.** The other three have no
   such button. Verified absent (dropped during validation).

4. **Lura's doctor roster is fictional/template placeholders**
   (`Dr. Emilie Drumm`, `Dr. Daniel Ahmed`, `Dr. Emman Collins`,
   `Dr. Marcus Rishi`), and its `about.html`/`index.html` team section lists a
   *different*, third set of names (`Dr. Jim Arnold, DDS`, `Dr. Kathryn
   Alderman`, `Debra Englehardt-Nash`, `Dr. Thompson`) that have no
   corresponding `doctor-*.html` page. Gary Solnit and Modern Smile Center have
   the same problem: one real doctor plus three inherited placeholder doctor
   pages. **Only `Ritter Ramsey Dentist` has a doctor roster that is internally
   consistent** — 3 real doctors, 3 matching pages, all cross-linked from
   `about.html`, `index.html` and `booking.html`.

5. **The service list is identical in all four and does not match the site's own
   pages.** `service.html` and `index.html` both list exactly four items:
   `Preventive dentistry`, `Cosmetic dentistry`, `Restorative treatments`,
   `Strategic Inner Circle`. But every template also ships a
   `service-orthodontics.html` page — and the string `Orthodontics` appears
   **zero** times in `service.html` in all four. `Strategic Inner Circle` is
   also not a dental treatment; it looks like a coaching/retreat upsell that
   displaced the Orthodontics card. Flag for human review before rebranding.

6. **No JSON-LD anywhere.** Zero `application/ld+json` blocks across all 79
files. There is no structured-data brand token to swap — the brand surfaces
   are `<title>`, `<meta name/property>` (description, `og:title`,
   `og:description`, `twitter:title`, `twitter:description`), `<img alt>`,
   inline `<svg><text>`, `mailto:`/`tel:` hrefs, Google Maps `?q=` embeds,
   `onclick="selectDentist('…')"` handlers, and WhatsApp message template
   literals (`` const msg = `Hi <BRAND>, I would like to …` ``).

---

## 5. Recommended replacement order for the build script

1. Full email addresses, then full phone numbers (longest first).
2. Full street addresses (longest first).
3. Multi-word brand phrases, **longest-first within each family** (§1c).
4. All-caps SVG wordmarks and their sub-labels (entity-escaped `&amp;` forms).
5. Doctor names, longest-first (`Dr. X, DDS, MS` → `Dr. X, DDS` → `Dr. X`).
6. Never touch: `href`/`src`/`srcset`/`url()` values, `<script>` bodies,
   class names, `data-w-id`/`data-wf-*` attributes, `w-node-*` ids.
