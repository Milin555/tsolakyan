import sys
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Import the SMTP configuration and templates directly from your existing campaign manager
from campaign_manager import load_smtp_accounts, send_smtp_email, INITIAL_TEMPLATES, parse_spintax

if len(sys.argv) < 2:
    print("Usage: python test_spam.py <your_alternative_email> [account_index]")
    print("If no account index is provided, it defaults to 0 (the first account).")
    sys.exit(1)

alt_email = sys.argv[1]

# Load your existing SMTP accounts
accounts = load_smtp_accounts()
if not accounts:
    print("No email accounts found in email_accounts.txt")
    sys.exit(1)

account_index = 0
if len(sys.argv) >= 3:
    account_index = int(sys.argv[2])

if account_index >= len(accounts):
    print(f"Error: Account index {account_index} is out of range. You only have {len(accounts)} accounts.")
    sys.exit(1)

# Use the selected account to send the test
account = accounts[account_index]

# Use the very first template from campaign_manager.py
template = INITIAL_TEMPLATES[0]

# Populate it with test data
test_name = "Milin"
subject = template["Subject"].replace("{Name}", test_name)
body = template["Body"].replace("{Name}", test_name)

# Process any spintax if present
subject = parse_spintax(subject)
body = parse_spintax(body)

print(f"=========================================")
print(f"Sending test email...")
print(f"From: {account['email']}")
print(f"To:   {alt_email}")
print(f"=========================================")

success = send_smtp_email(account, alt_email, subject, body)

if success:
    print("\n[SUCCESS] Test email sent successfully! Please check your inbox and spam folder.")
else:
    print("\n[FAILED] Failed to send test email. Check your SMTP settings and password.")
