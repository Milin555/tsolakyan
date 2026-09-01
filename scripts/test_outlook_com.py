import win32com.client
import sys

def test_outlook():
    try:
        print("Attempting to connect to Outlook Desktop App...")
        outlook = win32com.client.Dispatch("Outlook.Application")
        namespace = outlook.GetNamespace("MAPI")
        
        print("\nAvailable Outlook Accounts configured on your PC:")
        accounts = namespace.Accounts
        for i, acc in enumerate(accounts):
            print(f"[{i}] {acc.DisplayName} (Type: {acc.AccountType})")
            
        if len(accounts) == 0:
            print("No accounts found in Outlook. Please add your accounts first.")
            return
            
        print("\nTrying to create a draft email to verify connection...")
        mail = outlook.CreateItem(0)
        mail.Subject = "Antigravity Outlook COM Test"
        mail.Body = "This is a test email created via python to verify Outlook COM integration."
        
        # Try to set the sender to the first account display name
        mail.SendUsingAccount = accounts[0]
        mail.To = "milin9063@gmail.com" # Send a test mail to yourself
        
        # Save as draft first to check
        mail.Save()
        print("Success! Created a draft email in your Outlook Outbox/Drafts.")
        print("Your system supports Outlook Desktop COM integration!")
        
    except Exception as e:
        print(f"\nError: {e}")
        print("Could not connect to Classic Outlook. Make sure CLASSIC Outlook (not 'New Outlook') is running and configured.")

if __name__ == "__main__":
    test_outlook()
