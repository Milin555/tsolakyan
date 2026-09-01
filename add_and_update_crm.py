import csv
import os

CRM_FILE = r"c:\Users\Promise\Desktop\outreach\data\campaign_crm.csv"
NEW_LEADS_FILE = r"c:\Users\Promise\Desktop\outreach\Merged_Leads_6_7_8_9.csv"

def update_and_add():
    # 1. Read existing CRM
    crm_data = []
    existing_emails = set()
    
    with open(CRM_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            crm_data.append(row)
            existing_emails.add(row['Email'].strip().lower())
            
    print(f"Original CRM rows: {len(crm_data)}")
    
    # 2. Update status of the last 1200 leads to "Friend_Checking"
    update_count = 1200
    if update_count > len(crm_data):
        update_count = len(crm_data)
        
    start_index = len(crm_data) - update_count
    for i in range(start_index, len(crm_data)):
        if crm_data[i]['Status'] == 'Active':
            crm_data[i]['Status'] = 'Friend_Checking'
            
    print(f"Updated the last {update_count} rows to 'Friend_Checking' status.")
    
    # 3. Read new leads and add non-duplicates
    new_added = 0
    with open(NEW_LEADS_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row.get('Email', '').strip()
            if not email:
                continue
                
            email_lower = email.lower()
            if email_lower not in existing_emails:
                # Format to CRM structure
                # campaign_crm: Email,Name,Category,Phone,Website,Country,Username,Step,Last_Sent_Date,Assigned_Sender,Status
                first_name = row.get('First Name', '').strip()
                last_name = row.get('Last Name', '').strip()
                name = f"{first_name} {last_name}".strip()
                
                category = row.get('companyName', '').strip()
                phone = row.get('phone_numbers', '').strip()
                website = row.get('companyDomain', '').strip()
                country = row.get('location', '').strip()
                
                new_lead = {
                    'Email': email,
                    'Name': name,
                    'Category': category,
                    'Phone': phone,
                    'Website': website,
                    'Country': country,
                    'Username': '',
                    'Step': '1',
                    'Last_Sent_Date': '',
                    'Assigned_Sender': '',
                    'Status': 'Active'
                }
                crm_data.append(new_lead)
                existing_emails.add(email_lower)
                new_added += 1
                
    print(f"Added {new_added} new leads from Merged_Leads_6_7_8_9.csv")
    print(f"Total CRM rows now: {len(crm_data)}")
    
    # 4. Write back to CRM
    with open(CRM_FILE, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(crm_data)
        
if __name__ == "__main__":
    update_and_add()
