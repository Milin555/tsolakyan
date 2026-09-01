import csv
import os

CRM_FILE = "c:/Users/Promise/Desktop/outreach/data/campaign_crm.csv"

def unsubscribe_lead():
    email_to_find = input("Enter dentist email to unsubscribe: ").strip().lower()
    if not email_to_find:
        return
        
    leads = []
    found = False
    
    with open(CRM_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            if row.get("Email", "").strip().lower() == email_to_find:
                row["Status"] = "unsubscribed"
                found = True
            leads.append(row)
            
    if found:
        with open(CRM_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(leads)
        print(f"Success! {email_to_find} has been unsubscribed.")
    else:
        print("Email address not found in your database.")

if __name__ == "__main__":
    unsubscribe_lead()
