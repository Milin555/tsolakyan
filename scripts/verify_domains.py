import csv
import os
import dns.resolver
from concurrent.futures import ThreadPoolExecutor, as_completed

CRM_FILE = "c:/Users/Promise/Desktop/outreach/data/campaign_crm.csv"

# Global cache to avoid querying the same domain multiple times
DOMAIN_CACHE = {}

def check_domain(domain):
    if domain in DOMAIN_CACHE:
        return DOMAIN_CACHE[domain]
        
    if "." not in domain or len(domain) < 4:
        DOMAIN_CACHE[domain] = False
        return False
        
    try:
        # Check MX records
        dns.resolver.resolve(domain, 'MX')
        DOMAIN_CACHE[domain] = True
        return True
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.Timeout, Exception):
        DOMAIN_CACHE[domain] = False
        return False

def is_email_valid(email):
    if not email or "@" not in email:
        return False
    domain = email.split("@")[-1].strip().lower()
    return check_domain(domain)

def clean_database():
    if not os.path.exists(CRM_FILE):
        print(f"Error: {CRM_FILE} not found.")
        return

    print("Reading leads database...")
    leads = []
    with open(CRM_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            leads.append(row)

    total_leads = len(leads)
    print(f"Loaded {total_leads} leads from database.")
    print("Verifying domains in parallel (using 50 threads)...")

    # Separate already emailed leads (to preserve progress) from leads to check
    leads_to_skip = []
    leads_to_check = []
    for lead in leads:
        # If lead has Step > 0 or is Bounced (Step == -1), keep it without checking
        step_val = int(lead.get("Step", "0"))
        if step_val != 0:
            leads_to_skip.append(lead)
        else:
            leads_to_check.append(lead)

    print(f"Preserving {len(leads_to_skip)} active/emailed/bounced leads.")
    print(f"Checking {len(leads_to_check)} pending leads...")

    valid_checked_leads = []
    invalid_count = 0
    checked_count = 0

    # Run checks in parallel
    with ThreadPoolExecutor(max_workers=50) as executor:
        # Map each future to its lead row
        future_to_lead = {executor.submit(is_email_valid, lead.get("Email", "")): lead for lead in leads_to_check}
        
        for future in as_completed(future_to_lead):
            lead = future_to_lead[future]
            checked_count += 1
            try:
                is_valid = future.result()
                if is_valid:
                    valid_checked_leads.append(lead)
                else:
                    invalid_count += 1
            except Exception:
                invalid_count += 1

            if checked_count % 500 == 0 or checked_count == len(leads_to_check):
                print(f"Checked {checked_count}/{len(leads_to_check)} pending leads...")

    # Combine preserved leads with valid checked leads
    final_leads = leads_to_skip + valid_checked_leads

    # Save changes back to CRM_FILE
    with open(CRM_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(final_leads)

    print("\n=== Database Cleaning Complete ===")
    print(f"Removed: {invalid_count} dead/invalid emails.")
    print(f"Remaining active leads: {len(final_leads)}")

if __name__ == "__main__":
    # Install dnspython dependency if not present
    try:
        import dns
    except ImportError:
        print("Installing dnspython library...")
        os.system("pip install dnspython")
        
    clean_database()
