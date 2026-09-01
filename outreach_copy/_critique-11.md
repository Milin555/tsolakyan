# DELIVERABILITY / SPAM AUDIT — link-in-bio 3-touch sequence

I audited the copy **and** the machine that will send it. The copy is the smaller problem. Findings are ordered by what actually burns you.

Files: `C:\Users\Promise\Desktop\outreach\campaign_manager.py`, `C:\Users\Promise\Desktop\outreach\email_accounts.txt`

---

## TIER 0 — THE SEQUENCE CANNOT BE SENT AS WRITTEN

### 0.1 There is no sending domain. There are 19 consumer Gmail accounts.
`email_accounts.txt` holds 19 active rows, all `@gmail.com`, all app-password SMTP, all named on the same pattern: `milindholiya01`, `milindholiya02`, `milindholiya03`, `dholiyamilin4`, `milindholiya0001`… at 35/day each = **665 cold emails/day**.

Every point below follows from this:
- **Nothing to warm.** Reputation on consumer Gmail is per-mailbox and non-transferable. You are not building an asset; you are consuming disposable accounts.
- **The From address destroys the pitch.** The recipient sees `milindholiya12@gmail.com`. The Surat signature was supposed to buy credibility by volunteering the truth — a numbered free-mail address spends that credit and more. No dentist believes a web developer who cannot afford a domain.
- **DMARC alignment is impossible.** From-domain is `gmail.com`, links are `milin.dev`. Nothing aligns, nothing accrues.
- **This is a textbook account farm.** Same surname + incrementing digits, one residential Surat IP authenticating 19 mailboxes, near-identical bodies. Google clusters on exactly these features. When one trips, the cluster trips — and Gmail's TOS prohibits bulk unsolicited mail, so the failure mode is *account termination*, not a spam-folder placement.
- **`List-Unsubscribe` is unavailable** from Gmail SMTP submission in any way receivers will trust.

**Fix (non-negotiable, do this before any other fix):** buy 2–3 dedicated `.com` domains that are **not** `milin.dev`. Real mailboxes (Google Workspace/Zoho), SPF + DKIM + DMARC `p=none` moving to `quarantine`. 4 weeks warmup. 20–30/day/mailbox, hard ceiling. Keep `milin.dev` off the sending path entirely so a burn never touches the domain your demos live on.

### 0.2 The live code has no opt-out. At all.
`grep -i unsubscribe campaign_manager.py` returns **zero** matches outside the `DEAD_STATUSES` set. None of the five deployed templates (lines 95–130) contains an unsubscribe link, a postal address, or an advertisement identification. The footer in your spec exists only in the spec.

Every email sent by this script today violates CAN-SPAM on three counts simultaneously: no functioning opt-out mechanism, no valid physical postal address, no identification as a solicitation. Spec Hard Rule 4 is not implemented.

**Fix:** append the footer inside `get_email_content()` so it cannot be omitted, and add `List-Unsubscribe` + `List-Unsubscribe-Post: List-Unsubscribe=One-Click` headers in `send_smtp_email()` (line 260). Both a `mailto:` and an `https:` value. That is not optional once you are on a real domain.

### 0.3 Fake `Re:` — deceptive subject header
`campaign_manager.py:113`

```
"Subject": "Re: Website Complete: {Name}"
```

There is no prior thread. This is a forged reply on a first-contact commercial email: a materially misleading subject line under CAN-SPAM §7704(a)(2), and simultaneously one of the highest-weighted cold-outbound heuristics at every major filter (unmatched `Re:` with no `In-Reply-To`/`References` header is trivially detectable and universally scored). "Website Complete" additionally implies a transaction that never happened.

**Fix:** delete the template. Never prepend `Re:` or `Fwd:`.

### 0.4 `"quick question"` — banned by your own rules, still in production
`campaign_manager.py:105`. This is among the most-filtered subject strings in commercial email. Your spec forbids it in Hard Rule 6 and it is shipping.

---

## TIER 1 — MERGE-FIELD FAILURES (confirmed in code, not hypothetical)

### 1.1 The `"there"` fallback the spec explicitly forbids
`campaign_manager.py`, `get_email_content()`:

```python
name = clean_emojis(lead.get("Name", ""))
if not name or name.startswith("+") or name.startswith("🦷"):
    category = clean_emojis(lead.get("Category", ""))
    if category and len(category) < 35:
        name = category
    ...
            name = "there"
```

Your field table says *"Suppress lead if missing — do NOT fall back to 'Doctor' or 'there'."* The code falls back through **Category**, then **Username**, then `"there"`. Real renders you are shipping:

- `Hey there -`
- `Hey Cosmetic Dentist & Invisalign Provider -` (Category)
- `Hey smilesbydrpatel_official -` (Username)
- Subject line: `smilesbydrpatel_official - here's the link anyway`

The username render is worse than "there", because it proves a scraper wrote the email. **Fix:** delete the fallback chain; `raise`/skip, same as the demo-link guard already does at line 166.

### 1.2 Dead guard
`name.startswith("🦷")` can never be true — `clean_emojis()` strips everything ≥ U+2600 on the preceding line. The branch is decorative.

### 1.3 Fields the suppression rules forget
Suppression covers `demo_url`, `first_name`, and personal-address UK leads. It does **not** cover `{{practice}}`, `{{link_platform}}`, or `{{instagram_handle}}`. Empty renders:

| Empty field | Renders as |
|---|---|
| `{{practice}}` in T1 subj. 2 | `" — I built you a website"` — subject opens on an em dash |
| `{{practice}}` in T2 subj. 1 | `"What Google shows for "` — trailing space, reads truncated |
| `{{practice}}` in footer | `"You're getting this because  is listed publicly as a dental practice."` |
| `{{link_platform}}` in T1 subj. 1 | `"Your Instagram link goes to "` |
| `{{instagram_handle}}` in T1 body | `"the only link on  goes to Linktree"` |

**Fix:** gate all five fields, not two. No field, no send.

### 1.4 `{{practice}}` is scraped from an IG bio and will be filthy
Bio names carry pipes, bullets, ALL CAPS, and taglines. Real renders:

- `What Google shows for WILLOW LANE DENTAL | LEEDS • BOOK NOW` — a subject line that looks scraped because it is.
- `SMILE STUDIO — I built you a website` — shouting.

`clean_emojis()` handles emoji and nothing else. **Fix:** whitelist `[A-Za-z0-9&'\-. ]`, cut at the first `|`/`•`/`—`, title-case anything fully uppercase, cap at ~28 chars, suppress on failure.

### 1.5 `{{first_name}}` will frequently equal the practice
For solo practices IG "Name" is the business. `Willow Lane Dental — the only link on @willowlanedental goes to Linktree` is instantly a robot. **Fix:** if `first_name` is a substring of `practice`, suppress.

### 1.6 `{{link_platform}}` breaks the sentence grammatically
Your own example values are `Linktree / Facebook page / WhatsApp link / bit.ly`. Dropped into the body:

> `the only link on @x goes to Facebook page`
> `lands on WhatsApp link or nothing at all`
> `Your Instagram link goes to bit.ly`

Two of four values are ungrammatical. **Fix:** store the label with its article pre-baked — `Linktree`, `your Facebook page`, `a WhatsApp link`, `a shortened link`. And see 2.1.

---

## TIER 2 — CONTENT AND STRUCTURE

### 2.1 `pitch_hook` puts a URL shortener in the body
```
The only link on {{instagram_handle}} goes to {{link_platform}} ({{link_url}}), and no website domain was found...
```
Your notes say `link_url` is *"Held in reserve — only used in `pitch_hook`, not in the body"* — but the very next section says *"Touch 1 body below is written so `{{pitch_hook}}` can be dropped straight into sentence one."* Those two statements contradict. If anyone follows the second, Touch 1 body ships a live `bit.ly/…` or `linktr.ee/…`.

Even without it: the bare string `bit.ly` or `linktr.ee` as a `link_platform` label gets **auto-linkified by Gmail and Outlook into a live shortener URL**. A cold, unauthenticated message containing a shortener is one of the cleanest spam signals available. **Fix:** never emit a domain string as a label; never merge `link_url` into a sent body. Drop `link_url` from the template entirely.

### 2.2 Guaranteed base64-encoded body — a bulk-tool fingerprint
`send_smtp_email()` line 260:
```python
msg = MIMEMultipart()
msg.attach(MIMEText(body, 'plain'))
```
Two defects:
- `MIMEMultipart()` defaults to **`multipart/mixed` carrying a single text part and no attachments**. No human mail client produces that shape. It is a tooling signature.
- `MIMEText(body, 'plain')` with no charset: your copy contains em dashes (`—`), curly apostrophes (`There's`, `it's`, `can't`) and curly quotes (`"keep it"`). Python therefore promotes the part to UTF-8 and **base64-encodes the entire body**. A short English message delivered as an opaque base64 blob scores against you at every content filter; legitimate clients use quoted-printable for near-ASCII text. The subject `{{practice}} — I built you a website` similarly becomes an RFC 2047 encoded-word.

**Fix:** send a single-part `MIMEText(body, 'plain', 'utf-8')` with quoted-printable CTE — or better, **strip the copy to pure ASCII**: replace `—` with ` - `, curly quotes with straight. Keeps the subject unencoded too.

### 2.3 Touch 3 is byte-identical across your entire list
```
Subject: Last email from me       (no merge fields)
Subject: Closing this out         (no merge fields)
Subject: Taking the demo down Friday (no merge fields)
```
Body varies only by `{{first_name}}` and `{{demo_url}}`. 600+ near-identical messages/day cluster trivially under content fingerprinting. `parse_spintax()` exists and **no template uses a single spin block** — the capability is built and unused.

Additionally, `"Last email from me"` and `"Closing this out"` are the two most-templated breakup subjects in commercial outbound; filters are trained on them at scale.

**Fix:** put `{{practice}}` or `{{city}}` in every subject, and spin 3+ variants per sentence. Also: `{{city}}` is documented as *"used in Touch 2 variant subject only"* — no Touch 2 subject contains it. Dead spec.

### 2.4 The SEO-spam vocabulary cluster
Highest-weight tokens in the whole sequence, because every SEO spammer who has ever emailed a dentist writes exactly this:

> `"nothing for Google to show"` · `"can't rank"` · `"can't hold your reviews"` · `"What Google shows for {{practice}}"`

Combined with `"Milin, web developer"` and `"$495"`, you have the complete website/Google/price triad these mailboxes have been trained on for a decade. Hard Rule 8 forbids hiding the Surat line and it should stay — so buy the margin back by **cutting the Google/ranking language**. Rewrite T2 as the concrete moment, no SEO nouns: *"someone hears the name, searches for you, and finds a Linktree."* Drop `"can't rank"` entirely.

### 2.5 Other flagged strings
- `"Want it? Reply with one word."` and `reply "keep it"` — prescribed-token CTAs are a signature of Lemlist/Reply.io-class tooling. Keep one, not both.
- `"$495 to own it outright"` repeated in T3 — two `$` instances across the sequence is fine; do not add a third.
- `"Your demo site, and the price"` — `price` is unnecessary commercial weight in a header. Use `"Your demo site, and what it costs"` or drop.
- `"Your Instagram link goes to …"` — leading `Your` is a heavily-weighted subject opener (`Your account`, `Your invoice`). Prefer subject 3, `"A real site behind your bio link"`, as the primary.

### 2.6 What is clean — do not "fix" it
Zero exclamation marks. No `free`, `guarantee`, `act now`, `click here`, `100%`, no ALL CAPS, no attachments, no images, no tracking pixel, no HTML. Word counts are correct for a phone. Keep all of it. Specifically: **never add an open-tracking pixel and never route the demo link through a click-tracking redirect domain** — a shared tracker domain would be a worse deliverability decision than everything in Tier 1 combined. Use server-side hits on the unique demo slug as your engagement signal; you already have unique slugs.

### 2.7 Do not preserve the source hard-wraps
The bodies are wrapped at ~62 chars in the spec. Ship them wrapped and every phone renders a ragged column — a visible "pasted out of a tool" tell. Send unwrapped, one paragraph per line.

---

## TIER 3 — SENDING BEHAVIOUR

- **`START_HOUR = 0` / `END_HOUR = 24`** (lines 18–19). The script will send at 03:14 local. Set to the *recipient's* 08:00–17:00, not yours — the US/UK/AU spread means a single window is wrong for two of three regions.
- **`MIN_DELAY_SECONDS = 6` / `MAX_DELAY_SECONDS = 10`** (lines 22–23). One email every 6–10 seconds, indefinitely. No human does this. Widen to 90–400s and cap the daily burst.
- **`DAILY_LIMIT_PER_ACCOUNT = 25`** is overridden to 35 by every row in `email_accounts.txt`, and `CONSUMER_GMAIL_SAFE_LIMIT = 20` is bypassable with `--i-know-the-risk`. The guardrail is real, correct, and built to be ignored. Honour it.
- **No pre-send address verification anywhere.** `bounced_addresses.txt` has 46 entries — reactive only. IG-derived addresses bounce hard. Above ~2–3% hard bounces you are done. Verify the whole list before Touch 1.
- **Role accounts.** Practice contacts are overwhelmingly `info@`/`reception@`. The receptionist is not the buyer and marks agency pitches as spam reflexively. Complaint rate above 0.3% is a Gmail throttle. Deprioritise role addresses or accept the lower volume.
- **AU is unhandled.** Country filtering excludes Canada/EU. Australia's Spam Act 2003 requires consent — conspicuous-publication inferred consent exists but is narrower than CAN-SPAM and requires role relevance plus accurate sender identification. 622 leads sitting outside your compliance model.
- **No engagement gate.** Send Touch 3 only if the demo slug was actually hit. Emailing a third time into silence is where complaints come from.
- **Credentials.** `email_accounts.txt` stores 19 Gmail app passwords in plaintext on the Desktop. Move to a credential store; rotate everything currently in that file.

---

## TIER 4 — DOMAIN-BURN VECTOR OUTSIDE EMAIL

`milin.dev/d/willow-lane` hosts an unauthorised reproduction of a practice's **name, logo and brand colours**, and you email the URL to the brand owner unsolicited. One annoyed dentist reporting that page as a phishing/impersonation site to Google Safe Browsing flags `milin.dev` — and every link in every email you have ever sent dies at once, retroactively.

Also: `/d/<readable-slug>` is walkable. A prospect who edits the URL sees hundreds of other practices' demo pages, and the 1:1 illusion is gone in one click.

**Fix:** `noindex` + `robots.txt` disallow on all demos (or Google indexes thousands of near-duplicate pages using other people's trademarks); no directory listing; unguessable slug suffix; a visible line on the page — *"Unofficial demo built by Milin. Not affiliated with this practice."*; a one-click takedown link on the page itself. Also reconsider `.dev` — several corporate gateways (Mimecast/Barracuda rulesets) weight newer gTLDs. `.com` for both sending and demo hosting.

---

## THE ONE THING

Fixing subject lines while sending from `milindholiya12@gmail.com` is rearranging furniture. **Order of operations: real domains + auth + warmup (0.1) → unsubscribe + headers (0.2) → delete the fake `Re:` and `"quick question"` templates (0.3, 0.4) → suppress on empty merge fields (1.1) → ASCII-only single-part MIME (2.2) → everything else.**

Not legal advice — have the CAN-SPAM/PECR/Spam Act footer wording reviewed before launch.