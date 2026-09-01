import csv
import os

CRM_FILE = "c:/Users/Promise/Desktop/outreach/data/campaign_crm.csv"
FILE_1 = "c:/Users/Promise/Desktop/outreach/data/all_unique_leads.csv"
FILE_2 = "c:/Users/Promise/Desktop/outreach/data/dataset_1-2-000-leads-apollo-scraper-replacement-b2b-b2c-leads_2026-06-30_09-11-46-752.csv"

# Target countries mapping
COUNTRIES = {
    "united states": "United States",
    "usa": "United States",
    "canada": "Canada",
    "ca": "Canada",
    "united kingdom": "United Kingdom",
    "uk": "United Kingdom",
    "great britain": "United Kingdom",
    "gb": "United Kingdom",
    "germany": "Germany",
    "de": "Germany",
    "deutschland": "Germany",
    "australia": "Australia",
    "au": "Australia"
}

def get_standard_country(country_str):
    if not country_str:
        return None
    c_clean = country_str.strip().lower()
    # Check direct match
    if c_clean in COUNTRIES:
        return COUNTRIES[c_clean]
    # Check partial match
    for key, val in COUNTRIES.items():
        if key in c_clean:
            return val
    return None

def load_existing_crm_emails():
    emails = set()
    if os.path.exists(CRM_FILE):
        with open(CRM_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                email = row.get("Email", "").strip().lower()
                if email:
                    emails.add(email)
    return emails

def append_to_crm(new_leads):
    if not new_leads:
        return 0
    
    crm_exists = os.path.exists(CRM_FILE)
    fieldnames = ["Email", "Name", "Category", "Phone", "Website", "Country", "Username", "Step", "Last_Sent_Date", "Assigned_Sender", "Status"]
    
    mode = "a" if crm_exists else "w"
    with open(CRM_FILE, mode, newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not crm_exists:
            writer.writeheader()
        for lead in new_leads:
            writer.writerow(lead)
    return len(new_leads)

def process_file_1(existing_emails):
    new_leads = []
    if not os.path.exists(FILE_1):
        print(f"File 1 not found: {FILE_1}")
        return new_leads

    print(f"Reading {FILE_1}...")
    with open(FILE_1, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row.get("Email", "").strip()
            website = row.get("Website", "").strip()
            country_raw = row.get("Country", "").strip()
            name = row.get("Name", "").strip()
            
            if not email or not website:
                continue
                
            standard_country = get_standard_country(country_raw)
            if not standard_country:
                continue
            
            if email.lower() not in existing_emails:
                lead = {
                    "Email": email,
                    "Name": name,
                    "Category": row.get("Job Title", "Dentist").strip(),
                    "Phone": row.get("Phone", "").strip(),
                    "Website": website,
                    "Country": standard_country,
                    "Username": "",
                    "Step": "0",
                    "Last_Sent_Date": "",
                    "Assigned_Sender": "",
                    "Status": "Active"
                }
                new_leads.append(lead)
                existing_emails.add(email.lower())
    return new_leads

def process_file_2(existing_emails):
    new_leads = []
    if not os.path.exists(FILE_2):
        print(f"File 2 not found: {FILE_2}")
        return new_leads

    print(f"Reading {FILE_2}...")
    with open(FILE_2, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row.get("email", "").strip()
            website = row.get("website", "").strip()
            country_raw = row.get("country", "").strip()
            name = row.get("full_name", "").strip()
            
            if not name:
                first = row.get("first_name", "").strip()
                last = row.get("last_name", "").strip()
                name = f"{first} {last}".strip()

            if not email or not website:
                continue
                
            standard_country = get_standard_country(country_raw)
            if not standard_country:
                continue
                
            if email.lower() not in existing_emails:
                lead = {
                    "Email": email,
                    "Name": name,
                    "Category": row.get("title", "Dentist").strip(),
                    "Phone": row.get("mobile_phone", "").strip() or row.get("company_phone", "").strip(),
                    "Website": website,
                    "Country": standard_country,
                    "Username": "",
                    "Step": "0",
                    "Last_Sent_Date": "",
                    "Assigned_Sender": "",
                    "Status": "Active"
                }
                new_leads.append(lead)
                existing_emails.add(email.lower())
    return new_leads

def main():
    print("Loading existing CRM leads to prevent duplicates...")
    existing_emails = load_existing_crm_emails()
    print(f"Loaded {len(existing_emails)} existing leads.")

    leads_from_1 = process_file_1(existing_emails)
    print(f"Found {len(leads_from_1)} new unique leads in {os.path.basename(FILE_1)}.")

    leads_from_2 = process_file_2(existing_emails)
    print(f"Found {len(leads_from_2)} new unique leads in {os.path.basename(FILE_2)}.")

    all_new_leads = leads_from_1 + leads_from_2
    added_count = append_to_crm(all_new_leads)
    
    print(f"Success! Imported {added_count} total new unique leads into '{CRM_FILE}'.")

if __name__ == "__main__":
    main()
