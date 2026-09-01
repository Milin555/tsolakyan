import csv
import os
import sys

CRM_FILE = "c:/Users/Promise/Desktop/outreach/data/campaign_crm.csv"

def init_crm_usa(leads_csv_path):
    """
    Reads leads from the USA.csv file and populates the campaign_crm.csv database.
    Only imports leads that have a valid email address and website.
    Filters out rows that do not belong to the US target market to ensure optimal performance.
    """
    if not os.path.exists(leads_csv_path):
        print(f"Error: Source file '{leads_csv_path}' does not exist.")
        return

    # Load existing CRM database if it exists to avoid overwriting or duplicating
    existing_emails = set()
    crm_exists = os.path.exists(CRM_FILE)
    
    if crm_exists:
        with open(CRM_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_emails.add(row["Email"].strip().lower())
        print(f"Found existing CRM database with {len(existing_emails)} leads.")

    new_leads = []
    new_leads_added = 0
    
    # Read new leads
    with open(leads_csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        if "Email" not in headers:
            print("Error: The source CSV must contain an 'Email' column.")
            return
            
        for row in reader:
            email = row.get("Email", "").strip()
            website = row.get("Website", "").strip()
            country = row.get("Country", "").strip()
            
            # Basic validation: must have email, website, and be assigned to United States
            if not email or not website:
                continue
            if "united states" not in country.lower() and "usa" not in country.lower():
                continue
                
            if email.lower() not in existing_emails:
                new_row = {
                    "Email": email,
                    "Name": row.get("Name", "").strip(),
                    "Category": row.get("Category", "").strip(),
                    "Phone": row.get("Phone", "").strip(),
                    "Website": website,
                    "Country": "United States",
                    "Username": row.get("Username", "").strip(),
                    "Step": "0",                # 0 = not sent, 1 = initial sent, 2 = follow-up sent
                    "Last_Sent_Date": "",       
                    "Assigned_Sender": "",      
                    "Status": "Active"          
                }
                new_leads.append(new_row)
                existing_emails.add(email.lower())
                new_leads_added += 1

    if not new_leads:
        print("No new USA leads found to import.")
        return

    # Write to CRM database
    fieldnames = ["Email", "Name", "Category", "Phone", "Website", "Country", "Username", "Step", "Last_Sent_Date", "Assigned_Sender", "Status"]
    
    mode = "a" if crm_exists else "w"
    with open(CRM_FILE, mode, newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not crm_exists:
            writer.writeheader()
        for row in new_leads:
            writer.writerow(row)

    print(f"Successfully imported {new_leads_added} new USA leads into '{CRM_FILE}'.")

if __name__ == "__main__":
    source_file = "c:/Users/Promise/Desktop/outreach/data/USA.csv"
    init_crm_usa(source_file)
