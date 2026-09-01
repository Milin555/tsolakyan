import smtplib
import time

emails = [
    "milindholiya10@gmail.com",
    "milindholiya11@gmail.com",
    "milindholiya12@gmail.com",
    "milindholiya13@gmail.com",
    "milindholiya8@gmail.com",
    "milindholiya7@gmail.com",
    "dholiyamilin8@gmail.com",
    "milindholiya0001@gmail.com",
    "milindholiya9@gmail.com",
    "dholiyamilin10@gmail.com"
]

passwords = [
    "prgayqukwxljqyso",
    "tipwffvgajakohsr",
    "bsbbzhvmohoufkks",
    "imkugslnwhrnfksf",
    "ujwnvgnpdfyckaur",
    "odjlrahyjsjuxgay",
    "palctliawlbjczqy",
    "xqwnmkzdglfpvyyz",
    "uhfbmmxusbsrdjkz",
    "wckbrovftcyvdord"
]

valid_matches = []

for email in emails:
    matched = False
    for pwd in passwords:
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(email, pwd)
            print(f"SUCCESS: {email} matches password {pwd}")
            valid_matches.append((email, pwd))
            server.quit()
            passwords.remove(pwd)
            matched = True
            break
        except Exception as e:
            pass
            # print(f"Failed {email} with {pwd}")
    if not matched:
        print(f"WARNING: Could not find password for {email}")

if valid_matches:
    print("\nAppending to email_accounts.txt...")
    with open("email_accounts.txt", "a", encoding="utf-8") as f:
        for email, pwd in valid_matches:
            f.write(f"{email},{pwd},smtp.gmail.com,587,10\n")
    print("Done!")
