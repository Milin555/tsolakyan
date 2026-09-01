# DELIVERABILITY / SPAM AUDIT — `broken-site` sequence
Assumption stated in brief: **cold domain, zero reputation.** Every score below is judged against that.

**Headline verdict:** the copy is good. The *shape* is a phishing template. An unsolicited stranger, foreign sender, telling a clinician their SSL is expired / site is broken, with a link on a free hosting subdomain that carries their brand name in the path, closing with "reply and I'll send the two things I need from you." That is, end to end, the anatomy of a credential-harvest lure. Gmail's and Microsoft Defender's ML classifiers are trained hard on exactly this shape. Nothing in the doc addresses it. Fix that or the other 20 findings don't matter.

---

## CRITICAL — will burn the domain

### C1. `github.io` demo links
> `https://milin555.github.io/northgate-family-dental/`

Three compounding problems in one URL:
- **Free-host subdomain.** `github.io`, `pages.dev`, `netlify.app`, `vercel.app` are the top abused free-host TLD-alikes. Defender SmartScreen, Proofpoint URL Defense and Barracuda all carry heuristic penalties on them, and shared-domain reputation means someone else's phishing page on `*.github.io` degrades yours.
- **Brand impersonation in the path.** `/northgate-family-dental/` on a host that is not Northgate is literally the URL pattern of a cloned-login phish. Some scanners will fetch, render, and see a copy of the prospect's homepage on a third-party host — which is a *high-confidence* phish signal, not a low one.
- **Domain misalignment.** From-domain ≠ link-domain ≠ referenced-domain. SpamAssassin scores host mismatch; Gmail weights "does the sender own what they link to" heavily for unknown senders.

**Fix:** demos move to `demo.<sendingdomain>.tld` — same registrable domain as the From address, real cert, SPF/DKIM/DMARC aligned, `X-Robots-Tag: noindex`, and a visible banner on the page reading "Unofficial concept demo by Milin Dholiya. Not affiliated with {{practice}}." Non-negotiable. This alone is probably worth more than the rest of this audit.

### C2. The security-scare-plus-link shape
> `The SSL certificate on northgatefamilydental.com expired on 14 Aug, so Chrome and Safari now show a full-page "Not secure" warning`
> `Reply "fix it" and I'll send the two things I need from you.`

The "two things I need from you" line reads, to a security-aware office manager and to a classifier, as a prelude to asking for DNS or hosting credentials. Combined with an SSL/DNS alarm from an unknown overseas sender, this is textbook. Expect manual phishing reports, not just spam reports — and a phishing report is roughly an order of magnitude worse for a young domain than a spam report.

**Fix:** name the two things inline so nothing is withheld: `Reply "fix it" and I'll tell you exactly what I need — read-only access to your DNS panel, or a 10-minute call with whoever hosts it. I never ask for passwords by email.` Longer, and worth it. The explicit "I never ask for passwords by email" line is the single cheapest de-phishing move available.

### C3. Subject line 1 is a known scam template
> `{{domain}} — {{fault_label}}` → `northgatefamilydental.com — SSL expired`

A subject that *opens with a bare hostname* followed by a technical fault is near-identical to the "Domain Notification / SSL renewal required" registrar scam — one of the highest-volume, most-reported small-business fraud categories in the US and UK. Filters are tuned tightly against it. Additionally:
- Bare hostnames in subjects trip subject-URI rules in SpamAssassin and equivalents.
- Gmail mobile truncates around 35 chars; `northgatefamilydental.com — SSL exp…` puts nothing useful in view and looks *more* like an automated alert, not less.

**Fix:** kill subject 1. Human-shaped, human-length, sender-agentive: `Found a fault on your site` / `Your www address isn't resolving` / `Noticed your SSL lapsed`. Put the domain in the first body line where it proves specificity without pattern-matching to a scam.

### C4. `Closing your file`
> Subject: `Closing your file`

Worst subject in the document. Three separate failures:
- **Debt-collection / legal-notice pattern.** "Closing your file", "Regarding your account", "Final notice" are core collections-scam phrasing and are aggressively filtered.
- **Deceptive subject under CAN-SPAM §5(a)(2).** There is no file. Implying a pre-existing relationship where none exists is precisely the misleading-subject prohibition — this is the one genuine legal exposure in an otherwise careful compliance section.
- Highest complaint-rate subject in the set, on the segment the doc *itself* calls "highest-complaint."

**Fix:** delete. `Last one from me` is honest and safe. Use it.

### C5. Nested merge fields will ship raw
> `fault_label` for `http_5xx` = `site returning {{status_code}}`

`pitch_hook`, `fault_label` and `fix_instruction` all contain second-level tokens (`{{status_code}}`, `{{expiry_date}}`, `{{fail_count}}`, `{{check_count}}`, `{{first_seen}}`, `{{broken_count}}`, `{{total_count}}`, `{{second_area}}`). **No mainstream cold-email platform recurses merge fields** — Instantly, Smartlead, Lemlist and Mailshake all do a single pass. Every `http_5xx` lead ships with a subject line reading `site returning {{status_code}}`. That is an instant, visible, unrecoverable "this is a bot" for the exact clinician you most needed to convince, and a complaint.

**Fix:** the scanner renders every one of these to a **flat literal string** before CSV upload. Then add a hard pre-send gate: reject any row where any field matches `/\{\{|\}\}|\[.*?\]/`. Same gate catches the `[street address]` and `[link]` placeholders sitting in the rendered example.

---

## HIGH — foldering and credibility

### H1. "One link in touch 2" is false; every touch has more links than claimed
> Sending notes: `One link in touch 1 and 3, zero in touch 2 besides unsubscribe.`

Bare domains render as clickable in Gmail, Outlook, Apple Mail and every mobile client. So:
- Touch 1 actually carries **three** URI hosts: the autolinked `{{domain}}` in the hook, the demo, and the unsubscribe.
- Touch 2 carries the autolinked `{{domain}}` in the subject *and* in `fix_instruction` (`pointing at {{domain}}`), plus unsubscribe.

Worse: **you are autolinking a URL that is currently broken.** Defender Safe Links, Proofpoint and Mimecast fetch every URL at delivery. A message whose links resolve to an expired cert, an NXDOMAIN, or a 5xx scores as malicious-or-dead infrastructure. You are voluntarily attaching the prospect's own broken TLS state to your reputation.

**Fix:** suppress autolinking — write the domain so clients won't linkify it, or accept it and understand the cost. Minimum: strip the domain from touch 2's subject entirely. Never let `www.{{domain}}` render as a live link in the `dns_www_nxdomain` variant; that one resolves to nothing and is the worst of the four.

### H2. Link-to-text ratio, touch 3
> ~38 words, two URLs.

One link per 19 words on a cold domain, in a message with almost no content. Bulk classifiers read low-word-count + high-link-density as a redirect shell. Touch 3 is also the touch with the least to say.

**Fix:** drop `{{demo_url}}` from touch 3. Replace with `The demo I built is still up — reply and I'll resend the link.` Now touch 3 has exactly one URL (unsubscribe), reads as more human, and doubles as a reply prompt.

### H3. Four body variants across thousands of sends
> `Don't spin this copy. The evidence line is already unique per lead — that's the variation.`

Wrong at the filter layer. Gmail and Outlook near-dupe cluster on fuzzy body hashes (shingling / Nilsimsa-class). One variable sentence inside a fixed ~60-word frame does not move the hash meaningfully. With four `fault_type` values you are effectively sending **four identical emails** at volume. Every one of these is byte-identical on every send:

> `Fixing that is {{fix_scope}}, not a rebuild. I can do it today.`
> `I also rebuilt your homepage, so you can judge the work instead of the email:`
> `Concept demo, not indexed, unaffiliated with {{practice}}.`
> `Still showing on {{recheck_date}}. Here's the fix, so whoever manages your site can just do it:`
> `Last one from me — I won't email again.`

**Fix:** you don't need spintax, you need *structural* variance. Write 3 genuinely distinct hand-authored versions of each touch (different sentence order, different length, different closing) and rotate. Also rotate greeting punctuation and whether the demo line sits before or after the fix line. Target: no two consecutive sends from one inbox sharing a 7-word shingle outside the signature.

### H4. Merge-failure blast radius
- **`{{salutation}}` omitted** → the template hardcodes the comma, so a name-less lead renders a line containing only `,`. Put the comma *inside* the field and conditional-block the whole line.
- **`{{practice}}` empty** → `Concept demo, not indexed, unaffiliated with .` Credibility dead on the one line whose job is trust.
- **`{{fault_label}}` in touch 3 is grammatically broken for all four faults:**
  > `If SSL expired is still there next month` / `If www not resolving is still there next month` / `If homepage images 404 is still there next month`

  Every single one is malformed English. This is not an edge case — it is 100% of touch 3.
  **Fix:** `If the site's still doing that next month, this address still works.` No merge at all.
- **`Still showing on {{recheck_date}}.`** — subjectless fragment. And if the recheck runs before the queue drains, you are asserting a state on a date that hasn't happened. Rewrite: `I checked again on {{recheck_date}} and it's still showing.`
- **`Truncate {{domain}} over 26 chars to the registrable name only`** is a no-op — the registrable name *is* the domain minus `www`. The rule does nothing; long domains still blow the subject. Delete or specify real truncation.
- **Sample data is wrong:** `{{scan_date}}` = 14 Aug and cert `expired on 14 Aug`. A cert expiring the same day you scanned undercuts the whole evidence claim. Add a validator: `expiry_date < scan_date`.

### H5. Em dashes and curly quotes everywhere
> `Milin Dholiya — web developer, Surat, India`
> `I'll do it today — $299 flat`
> `Last one from me — I won't email again.`
> `{{postal_address}} · Unsubscribe:` (U+00B7)
> `"Not secure"` (typographic quotes)

Two costs. (1) Non-ASCII forces quoted-printable/UTF-8 encoding on what should be trivially clean plain text. (2) More importantly in 2026: **dense em-dash usage is now a widely-used LLM-authored-text signal**, and the major providers are visibly clustering machine-written cold outreach. You have an em dash in every touch and in a subject line.

**Fix:** ASCII only. Hyphens or full stops. Straight quotes. Replace `·` with `|`. Costs nothing.

---

## MEDIUM

### M1. Money in every follow-up
> `$299 flat, nothing else attached.` · `Same $299.`

`$` + figure + `flat` is a mild but real Bayesian contributor, and `nothing else attached` unfortunately reads as attachment-adjacent language. Not fatal. But note the *pattern*: touch 2 and touch 3 both contain a price and almost nothing else. A 38-word email whose content is a price and a link is what a bulk filter thinks an ad is.

**Fix:** keep the $299 — it's the right strategy — but bulk out touches 2 and 3 with one more sentence of substance so price isn't the message's centre of mass.

### M2. Reply-keyword CTA
> `Reply "fix it" and I'll send the two things I need from you.`

Reply-with-a-keyword is a mass-send tell to any recipient who has seen one before, which for a dentist is weekly. It also colocates with C2's phishing read.

**Fix:** `Reply and I'll tell you what I need.` Plain, human, same function.

### M3. Fresh thread on touch 2 is the wrong call for deliverability
> `Do not reply into the touch-1 thread. Fresh subject, fresh thread`

Defensible as copy strategy; costly as deliverability. In Gmail, threading a follow-up onto touch 1 (a) inherits any positive engagement signal, (b) presents one complaint surface instead of three, (c) reduces unread-cold-message count in the inbox, which is itself a foldering input. Three separate unread cold threads from one unknown sender in seven days is a worse profile than one thread with two replies.

**Fix:** thread touch 2 onto touch 1 with a changed subject (`Re:`-less, new `Subject:`, same `References:`/`In-Reply-To:` headers) — you keep the "not chasing" feel and the thread consolidation. If you won't, at minimum thread touch 3 onto touch 2.

### M4. Unsubscribe is functional but weak
> `{{postal_address}} · Unsubscribe: {{unsubscribe_url}}`

- Buried at the end of a run-on footer line, mid-dot separated, sharing a line with a street address. Low-visibility unsubscribe **raises** complaint rate — people who can't find the link hit "Report spam," which is the outcome you are trying to avoid.
- Footer order is inconsistent (touch 1: address then unsub; touches 2/3: unsub then address). Inconsistency across a sequence is itself a sloppiness signal.
- If `{{unsubscribe_url}}` sits on a shared ESP domain, that's a second unrelated URI host in every message.

**Fix:** own line, plain language, own domain:
```
Don't want these? Unsubscribe here: https://<sendingdomain>/u/<token>
Or just reply STOP and I'll remove you myself.
Milin Dholiya, <street>, Surat, Gujarat 395007, India
```
The reply-STOP option is a genuine complaint-rate reducer.

### M5. Google/Yahoo bulk-sender requirements are under-specified
> `Working one-click unsubscribe plus a List-Unsubscribe header`

One-click requires **both**:
```
List-Unsubscribe: <https://.../u/TOKEN>, <mailto:unsub@...>
List-Unsubscribe-Post: List-Unsubscribe=One-Click
```
and the URL must accept an unauthenticated **POST** and act on it. A GET-only endpoint fails the spec and Gmail will treat the header as absent. The doc names the header but not the `-Post` companion or the POST handler — the most commonly botched half.

Also required and absent from the doc: SPF + DKIM + DMARC (`p=none` minimum, aligned), valid forward-confirmed PTR, TLS on delivery, **and spam complaint rate held under 0.3%** — on the segment the doc explicitly calls its highest-complaint copy.

### M6. The doc identifies its own biggest infra risk and then does nothing
> `a complaint spike here poisons every other segment on the same domain`

Correct, and unaddressed. The cap of 6/inbox/day doesn't help if all five segments share one sending domain.

**Fix:** dedicated sending domain and inbox pool for `broken-site`, firewalled from the other four. Different registrable domain, not a subdomain — DMARC/reputation inheritance is real. Accept that this segment may torch its own domain; make sure it can only torch its own.

### M7. No warmup, no list hygiene, no monitoring in the doc
On a cold domain, absent from the spec and all mandatory:
- **Warmup:** 3–4 weeks minimum before any cold volume; start 5–10/day/inbox and ramp.
- **Role addresses:** scraped clinic lists are `info@`, `hello@`, `reception@`. High role-account density to Microsoft 365 tenants is a direct bulk-foldering input.
- **Catch-all domains** verify as "valid" and are the single largest source of spam-trap hits. Segment catch-alls out or send them last, after reputation exists.
- **Google Postmaster Tools** + seed-list testing per major provider, monitored weekly. With no tracking pixel (correctly), complaint and bounce are your *only* signals — so you must actually collect them.
- **Global suppression** across all five segments on any unsubscribe or complaint. The doc scopes suppression to this sequence only.

### M8. Text/plain-only single-part
Correct decision — do **not** add HTML. Note only that some filters apply a token penalty to text/plain-only bulk mail. It is far smaller than the penalty for an HTML cold email with a tracking pixel. Keep as is; just don't be surprised by it in seed tests.

### M9. Internal inconsistency in the compliance section
> `Real postal address in all three footers — CAN-SPAM requires it and the current templates omit it.`

The templates shown *include* it. Either the note is stale or the live templates have drifted from this document. Verify the shipping templates against this doc before send — a CAN-SPAM footer that exists in the spec and not in production is the classic way this goes wrong.

---

## Priority order

1. **C1** — move demos off `github.io` to the sending domain. Everything else is secondary.
2. **C5** — flatten nested merges + add a `{{`/`[` pre-send reject gate.
3. **C3 / C4** — delete subject 1 and `Closing your file`.
4. **C2** — de-phish the CTA; add "I never ask for passwords by email."
5. **M6** — separate sending domain for this segment.
6. **H4** — fix the four broken `{{fault_label}}` renders in touch 3 and the orphan comma.
7. **H3 / H5** — three real body variants per touch; strip all non-ASCII.
8. **M5 / M7** — `List-Unsubscribe-Post` + POST handler, warmup, catch-all segmentation, Postmaster Tools.