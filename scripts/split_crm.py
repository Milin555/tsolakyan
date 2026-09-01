import csv
import os

CRM_FILE = "c:/Users/Promise/Desktop/outreach/data/campaign_crm.csv"
MILIN_OUT = "c:/Users/Promise/Desktop/outreach/data/campaign_crm_milin.csv"
FRIEND_OUT = "c:/Users/Promise/Desktop/outreach/data/campaign_crm_friend.csv"

def split_database():
    if not os.path.exists(CRM_FILE):
        print(f"Error: {CRM_FILE} does not exist.")
        return

    print(f"Reading {CRM_FILE}...")
    leads = []
    with open(CRM_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            leads.append(row)

    total_leads = len(leads)
    if total_leads == 0:
        print("No leads to split.")
        return

    midpoint = total_leads // 2
    milin_leads = leads[:midpoint]
    friend_leads = leads[midpoint:]

    print(f"Total Leads: {total_leads}")
    print(f"Milin's Leads: {len(milin_leads)}")
    print(f"Friend's Leads: {len(friend_leads)}")

    # Write Milin's file
    with open(MILIN_OUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(milin_leads)

    # Write Friend's file
    with open(FRIEND_OUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(friend_leads)

    print("Success! Database split successfully:")
    print(f" -> Milin's part: {MILIN_OUT}")
    print(f" -> Friend's part: {FRIEND_OUT}")

if __name__ == "__main__":
    split_database()
