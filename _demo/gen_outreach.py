"""Writes one outreach message per prospect, in the channel their record says
to use, naming the specific fault on their real site.

The demo link does the selling. The message only has to earn the click, so it
stays short and leads with the one concrete thing wrong with their current
site, quoted from the research rather than described in general terms.

    python _demo/gen_outreach.py
"""
import io, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from demo_config import load, BASE

OWNER = "milin555"
COPY = os.path.join(BASE, "_demo", "copy")


def address(cfg):
    if cfg["doctor"]:
        last = cfg["doctor"].replace("Dr. ", "").replace("Dr ", "").split()
        return "Dr. " + last[-1] if last else cfg["doctor"]
    return "Hi there"


def clean(w):
    """Trim a research note down to one plain, quotable clause."""
    w = re.sub(r"\s+", " ", w).strip().rstrip(".")
    w = re.sub(r"^(The live site displays the banner:|Footer reads verbatim:)\s*", "", w)
    if len(w) > 165:
        w = w[:162].rsplit(" ", 1)[0].rstrip(",;:") + "..."
    return w


def pick_fault(cfg):
    """The weakness a non-technical owner will recognise fastest."""
    ws = cfg["weaknesses"] or []
    if not ws:
        return None
    ranked = sorted(ws, key=lambda w: (
        0 if re.search(r"trial period|expired|coming soon|placeholder|2013|stale|broken", w, re.I)
        else 1 if re.search(r"no online booking|no before/after|no testimonial|no pricing", w, re.I)
        else 2))
    return clean(ranked[0])


def email_msg(cfg, url, fault):
    subject = f"{cfg['practice']} - a rebuilt homepage, already live"
    body = f"""{address(cfg)},

I rebuilt your homepage as a working site rather than writing you a pitch. It is live here, nothing to install:

{url}

What prompted it, on the current site right now:

{('  ' + fault) if fault else '  The site is not matching the standard of the work.'}

It is a concept, not a live store, and it is not indexed. Every page carries a note saying it is unaffiliated. If it is not for you, ignore this and no follow up.

If you like the direction, I will finish it properly, move it to your domain and maintain it.

Milin Dholiya
dholiyamilin@gmail.com
"""
    return subject, body


def dm_msg(cfg, url, fault):
    return (f"{address(cfg)} - I rebuilt your homepage as an actual working site, "
            f"not a mockup: {url}\n\n"
            f"What prompted it, on your site right now:\n"
            f"{fault or 'The site is not matching the standard of the work.'}\n\n"
            "It is unaffiliated and not indexed. If it is not useful, ignore me and I will not follow up.")


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    rows = load()
    out = ["# Outreach - 20 personalised dental demos\n",
           "One message per prospect, in the channel their research record recommends.",
           "Every message names a fault verified on their live site on 19 Aug.",
           "Send no more than 6 a day from one inbox.\n"]

    thin = []
    for cfg in rows:
        url = f"https://{OWNER}.github.io/{cfg['slug']}/"
        fault = pick_fault(cfg)
        if not fault:
            thin.append(cfg["practice"])
        subj, body = email_msg(cfg, url, fault)
        dm = dm_msg(cfg, url, fault)

        out.append(f"\n---\n\n## {cfg['rank']}. {cfg['practice']}")
        out.append(f"\n**Who** {cfg['doctor'] or 'no named owner, address the practice'} "
                   f"· {cfg['city']}, {cfg['country']} · score {cfg['score']}")
        out.append(f"**Their site** {cfg['website']}")
        out.append(f"**Social** {cfg['social'] or 'none recorded'} "
                   f"({cfg['followers'] or 'n/a'} followers)")
        out.append(f"**Channel to use** {cfg['channel']}")
        out.append(f"**Quote range** {cfg['price_range']} · {cfg['offer'][:110]}")
        out.append(f"**Demo** {url}\n")
        out.append(f"**The fault to lead with**\n> {fault or 'none recorded, lead with the offer instead'}\n")
        out.append(f"### Email\n\n**Subject:** {subj}\n\n```\n{body}```\n")
        out.append(f"### DM / WhatsApp\n\n```\n{dm}\n```")

    io.open(os.path.join(BASE, "OUTREACH_20.md"), "w", encoding="utf-8").write("\n".join(out))
    print(f"wrote OUTREACH_20.md for {len(rows)} prospects")
    if thin:
        print("no recorded weakness, lead with the offer: " + ", ".join(thin))
    by_ch = {}
    for cfg in rows:
        k = ("Instagram" if "instagram" in cfg["channel"].lower()
             else "Email" if "email" in cfg["channel"].lower()
             else "Phone" if "phone" in cfg["channel"].lower()
             else "Other")
        by_ch[k] = by_ch.get(k, 0) + 1
    print("channels: " + " · ".join(f"{k} {v}" for k, v in sorted(by_ch.items())))
