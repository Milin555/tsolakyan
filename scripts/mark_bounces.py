import csv
import os

CRM_FILE = "c:/Users/Promise/Desktop/outreach/data/campaign_crm.csv"

# Bounced emails list provided by user
BOUNCED_EMAILS = [
    "drcastellanos1@yahoo.com",
    "jgoldberg@gdbosques.com",
    "marciasalesodonto@gmail.com",
    "californiasmileslb@yahoo.com",
    "esfd@dentalgrp.com",
    "oceanpacificdental@cox.net",
    "northolmsteddds@wowway.com",
    "renobowshop@outlook.com",
    "mbell@tidewaterdental.com"
]

def mark_bounces():
    if not os.path.exists(CRM_FILE):
        print(f"Error: {CRM_FILE} not found.")
        return

    bounced_set = set(email.strip().lower() for email in BOUNCED_EMAILS)
    leads = []
    marked_count = 0

    print("Reading database to locate bounced emails...")
    with open(CRM_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            email = row.get("Email", "").strip().lower()
            if email in bounced_set:
                row["Status"] = "Bounced"
                row["Step"] = "-1"  # Stop any further emails
                marked_count += 1
            leads.append(row)

    # Save changes back to CRM_FILE
    with open(CRM_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(leads)

    print(f"\nSuccess! Marked {marked_count} emails as 'Bounced' in the database.")
    print("These leads will never be emailed or followed up again.")

if __name__ == "__main__":
    mark_bounces()
