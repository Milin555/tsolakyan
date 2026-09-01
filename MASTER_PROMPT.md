# MASTER PROMPT — 20 personalised dental demos, built and shipped

## Situation

Milin has ₹0 revenue and a ~₹49,000/month burn. The fastest realistic path to a
first paying client is not more cold DMs — it is putting a **finished, personalised
site in the prospect's hands** so the conversation starts at "when can you start"
instead of "who are you".

Everything needed already exists on this machine. Nothing needs to be researched
from scratch and nothing may be invented.

## Assets on hand (verified, 22 Aug)

| Asset | Location | State |
|---|---|---|
| 24 verified prospects | `dental-prospects.json` | Ranked 1–24, live-audited 19 Aug. Real websites, real weaknesses, real social URLs, price ranges, outreach channel. |
| 4 dental site templates | `Lura Dentist/`, `Gary Solnit Dentist/`, `Modern Smile Center Dentist/`, `Ritter Ramsey Dentist/` | Webflow exports, 28–29 pages each, already deployed once |
| Deploy automation | `deploy_all.py` | Works, but the project list is hardcoded |
| Rebrand automation | `rebrand_automation.py` | Works, but is `input()`-driven — cannot run 20× unattended |
| GitHub | `gh` CLI | Authed as `Milin555`, scopes include `repo` |

## The deliverable

**20 folders, 20 public repos, 20 live GitHub Pages URLs**, one per prospect,
each reading as a site built for that specific practice — plus a ready-to-send
outreach message per prospect that names the real fault on their real site.

## Hard rules

1. **Never invent a fact about a prospect.** Every name, city, specialty and
   website weakness comes from `dental-prospects.json`. If a field is missing,
   leave the generic copy — do not guess. Prospect 18, 22, 23, 24 have no named
   owner; address the practice, not a person.
2. **Scrub every leftover token.** The templates currently leak:
   - `Foundation Dental Alliance` — 81 occurrences
   - `Lumora` — 36 occurrences
   - `edrumm@585dentist.com` — 46 occurrences, **a real third party's email**
   - `info@foundationdentalalliance.com`, `310-888-1850`, `john@example.com`
   A demo that ships with any of these is a failed demo. This is a blocking check.
3. **Each demo must be visually distinct.** Rotate the 4 template image sets
   across 5 colour themes so no two prospects receive a site that looks like
   the same file with the name swapped. Two prospects in the same city or
   specialty must never get the same template *and* theme.
4. **Every page carries `noindex`** and a discreet footer line marking it a
   concept proposal by Milin. This keeps it honest, keeps it out of search, and
   means it can never be mistaken for the practice's real site.
5. **Keep the repo small.** Delete `variant-*/` (30 MB dead weight) and
   recompress JPGs over 300 KB. Target under 15 MB per repo.
6. **No AI or assistant mentions** anywhere — commits, README, page source.

## Pipeline

```
demo_config.py     20 prospects -> slug, practice, doctor, city, contact, theme, template
   |
copy agents        per-prospect hero / about / services copy, grounded in real specialty
   |
build_demos.py     copy template -> scrub tokens -> inject copy + theme -> optimise images
   |
verify_demos.py    the checklist below, per demo, in a real browser
   |
deploy_demos.py    gh repo create -> push -> enable Pages
   |
outreach.md        per-prospect message naming their real site fault + the live link
```

## Verification checklist — every demo must pass all of it

| # | Check | Fail condition |
|---|---|---|
| 1 | Token scrub | any of the six leaked strings survives anywhere in the repo |
| 2 | Practice name | absent from `<title>`, nav, hero or footer |
| 3 | Doctor name | absent where the prospect has one named |
| 4 | City | absent from footer/contact |
| 5 | Contact | email or phone still points at a template value |
| 6 | Pages load | any page 404s or throws a console error |
| 7 | Images | any `<img>` with `naturalWidth === 0` |
| 8 | noindex | missing from any page |
| 9 | Disclosure | footer concept line missing |
| 10 | Distinctness | template+theme pair collides with another prospect |
| 11 | Responsive | horizontal scroll at 390 px |
| 12 | Size | repo over 15 MB |
| 13 | Live | Pages URL not returning 200 |

A demo is **done** only when all 13 pass. Log every failure to
`_dev/DEMO_FAILURES.md` with what broke and what fixed it.

## Definition of done

- `LIVE_LINKS_20.md` lists 20 working URLs
- `OUTREACH_20.md` holds 20 messages, each naming that prospect's real site fault
- All 13 checks green on all 20
- Nothing fabricated, nothing leaked
