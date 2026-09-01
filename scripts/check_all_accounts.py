import sys
import time
import random
from campaign_manager import load_smtp_accounts, send_smtp_email, INITIAL_TEMPLATES, parse_spintax

alt_email = "milindholiya0108@gmail.com"

# Load your existing SMTP accounts
accounts = load_smtp_accounts()
if not accounts:
    print("No email accounts found in email_accounts.txt")
    sys.exit(1)

print(f"Found {len(accounts)} accounts. Starting test to {alt_email}...\n")

template = INITIAL_TEMPLATES[0]

for i, account in enumerate(accounts):
    test_name = f"Test Clinic {i+1}"
    subject = template["Subject"].replace("{Name}", test_name)
    body = template["Body"].replace("{Name}", test_name)
    
    subject = parse_spintax(subject)
    body = parse_spintax(body)
    
    print(f"[{i+1}/{len(accounts)}] Sending test email from {account['email']}...")
    success = send_smtp_email(account, alt_email, subject, body)
    
    if success:
        print(f"  [SUCCESS] from {account['email']}")
    else:
        print(f"  [FAILED] from {account['email']}")
        
    if i < len(accounts) - 1:
        delay = random.uniform(7, 8)
        print(f"  Waiting {delay:.2f} seconds before next account...\n")
        time.sleep(delay)

print("\nDone! Check your inbox/spam for all test emails.")
