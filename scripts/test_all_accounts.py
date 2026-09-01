import sys
import time
from campaign_manager import load_smtp_accounts, send_smtp_email, INITIAL_TEMPLATES, parse_spintax

if len(sys.argv) < 2:
    print("Usage: python test_all_accounts.py <your_alternative_email>")
    sys.exit(1)

alt_email = sys.argv[1]

accounts = load_smtp_accounts()
if not accounts:
    print("No email accounts found in email_accounts.txt")
    sys.exit(1)

print(f"Found {len(accounts)} accounts. Sending a test email from each one to {alt_email}...\n")

for i, account in enumerate(accounts):
    template = INITIAL_TEMPLATES[i % len(INITIAL_TEMPLATES)]
    test_name = f"Test Clinic (Account {i})"
    subject = template["Subject"].replace("{Name}", test_name)
    body = template["Body"].replace("{Name}", test_name)
    
    subject = parse_spintax(subject)
    body = parse_spintax(body)
    
    print(f"[{i}/{len(accounts)}] Sending from {account['email']}...")
    
    success = send_smtp_email(account, alt_email, subject, body)
    
    if success:
        print(f"   ✅ Success!")
    else:
        print(f"   ❌ Failed.")
        
    # Wait a few seconds between sends to avoid rate limits
    if i < len(accounts) - 1:
        time.sleep(3)

print("\nDone! Please check your inbox and spam folder for all test emails.")
