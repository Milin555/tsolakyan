import csv
import json

CSV_FILE = "c:/Users/Promise/Desktop/outreach/data/Master_Leads_Clean.csv"
OUTPUT_FILE = "c:/Users/Promise/Desktop/outreach/outlook_drafts.json"
TXT_FILE = "c:/Users/Promise/Desktop/outreach/outlook_drafts.txt"

template_subject = "Concept Design: {Clinic Name}"

templates = [
    # Template 1 (Original)
    """Hi {First Name},

I'll keep this extremely short.

I came across {Clinic Name}'s website on Google Maps while looking at dental clinics in {City}, and felt there were a few opportunities to make it look more modern and create a stronger first impression for new patients.

I actually went ahead and created a custom website design specifically for your clinic.

If you'd like to see it, just reply "Yes", and I will send you a quick video walkthrough and a link to the live website so you can check it out.

Thanks,

Milin

P.S. I probably spent more time on it than I should have, so I'd genuinely love to hear what you think. 🙂""",

    # Template 2 (Variation A)
    """Hi {First Name},

I'll be super quick.

While researching dental clinics in {City}, I found {Clinic Name}'s website on Google Maps and noticed a few ways it could be updated to leave a much better first impression on new patients.

I actually went ahead and created a custom website design specifically for your clinic.

If you'd like to see it, just reply "Yes", and I will send you a quick video walkthrough and a link to the live website so you can check it out.

Best,

Milin

P.S. I stayed up pretty late working on this, so I'd love to get your honest thoughts. 🙂""",

    # Template 3 (Variation B)
    """Hi {First Name},

I know you're busy, so I'll get right to it.

I saw {Clinic Name}'s website on Google Maps while searching for dental practices in {City}. It's good, but I saw a couple of easy ways to modernize it and really boost how new patients see you.

I actually went ahead and created a custom website design specifically for your clinic.

If you'd like to see it, just reply "Yes", and I will send you a quick video walkthrough and a link to the live website so you can check it out.

Cheers,

Milin

P.S. I definitely put more hours into this than planned, so any feedback would be awesome! 🙂"""
]

drafts = []

with open(CSV_FILE, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        first_name = row.get("First Name", "").strip()
        clinic_name = row.get("Company Name", "").strip()
        email = row.get("Email", "").strip()
        city = row.get("City", "").strip()
        
        if not first_name:
            first_name = "there"
        if not clinic_name:
            clinic_name = "your clinic"
        if not city:
            city = "your area"
            
        # Rotate template every 5 emails
        template_index = (i // 5) % len(templates)
        template_body = templates[template_index]
            
        subject = template_subject.replace("{Clinic Name}", clinic_name)
        body = template_body.replace("{First Name}", first_name).replace("{Clinic Name}", clinic_name).replace("{City}", city)
        
        drafts.append({
            "To": email,
            "Subject": subject,
            "Body": body,
            "Template_Used": template_index + 1
        })

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(drafts, f, indent=4)
    
with open(TXT_FILE, "w", encoding="utf-8") as f:
    for i, draft in enumerate(drafts, 1):
        f.write(f"--- EMAIL {i} (Using Template {draft['Template_Used']}) ---\n")
        f.write(f"To: {draft['To']}\n")
        f.write(f"Subject: {draft['Subject']}\n")
        f.write(f"Body:\n{draft['Body']}\n")
        f.write("\n" + "="*50 + "\n\n")

print(f"Generated {len(drafts)} emails with rotating templates.")
