import time
import random
import sys
from campaign_manager import load_smtp_accounts, send_smtp_email, INITIAL_TEMPLATES, parse_spintax

# Load all SMTP accounts
accounts = load_smtp_accounts()
if not accounts or len(accounts) < 2:
    print("Need at least 2 email accounts in email_accounts.txt to cross-send.")
    sys.exit(1)

print(f"Found {len(accounts)} accounts. Starting warm-up cross-check...\n")

template = INITIAL_TEMPLATES[0]

for i, sender_acc in enumerate(accounts):
    # Pick a random receiver that is NOT the sender
    possible_receivers = [acc for acc in accounts if acc['email'] != sender_acc['email']]
    receiver_acc = random.choice(possible_receivers)
    receiver_email = receiver_acc['email']
    
    test_name = f"Warmup Clinic {i+1}"
    subject = template["Subject"].replace("{Name}", test_name)
    body = template["Body"].replace("{Name}", test_name)
    
    subject = parse_spintax(subject)
    body = parse_spintax(body)
    
    print(f"[{i+1}/{len(accounts)}] Sending email...")
    print(f"  From: {sender_acc['email']}")
    print(f"  To:   {receiver_email}")
    
    success = send_smtp_email(sender_acc, receiver_email, subject, body)
    
    if success:
        print(f"  [SUCCESS] Email sent.")
    else:
        print(f"  [FAILED] Failed to send.")
        
    if i < len(accounts) - 1:
        delay = 10
        print(f"  Waiting {delay} seconds before next send...\n")
        time.sleep(delay)

print("\nWarm-up check completed! All 8 accounts have sent 1 email to another random account.")
