import os
import shutil
import urllib.request
import re

def download_image(url, dest_path):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            with open(dest_path, 'wb') as f:
                f.write(resp.read())
        print(f"[SUCCESS] Successfully downloaded image to: {os.path.basename(dest_path)}")
        return True
    except Exception as e:
        print(f"[FAILED] Failed to download image from {url}. Error: {e}")
        return False

def rebrand_project():
    print("==================================================")
    print("      DENTAL WEBSITE REBRAND AUTOMATION SCRIPT    ")
    print("==================================================\n")
    
    # 1. Gather inputs
    src_dir = r"c:\Users\Promise\Desktop\outreach\Gary Solnit Dentist"
    base_dir = r"c:\Users\Promise\Desktop\outreach"
    
    target_folder = input("1. Enter new folder name (e.g. Estedent Dentist): ").strip()
    dest_dir = os.path.join(base_dir, target_folder)
    
    if os.path.exists(dest_dir):
        overwrite = input(f"Warning: {target_folder} already exists. Overwrite? (y/n): ").strip().lower()
        if overwrite != 'y':
            print("Operation cancelled.")
            return
        shutil.rmtree(dest_dir)
        
    practice_name = input("2. Enter Practice Name (e.g. Estedent Clinic): ").strip()
    doctor_name = input("3. Enter Lead Doctor Name (e.g. Dr. Monika Goroszewska): ").strip()
    phone = input("4. Enter Clinic Phone (e.g. 079 3601 5557): ").strip()
    email = input("5. Enter Clinic Email (e.g. dr.goros@gmail.com): ").strip()
    address = input("6. Enter Clinic Address (e.g. 179 Bilton Rd, Greenford): ").strip()
    
    headshot_url = input("7. Enter Doctor Headshot URL (leave blank to skip): ").strip()
    logo_url = input("8. Enter Clinic Logo URL (leave blank to skip): ").strip()
    
    # 2. Duplicate the template directory
    print("\nDuplicating Ritter Ramsey Dentist template...")
    try:
        shutil.copytree(src_dir, dest_dir, ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc'))
        print("[SUCCESS] Template copied successfully!")
    except Exception as e:
        print(f"[FAILED] Error copying template: {e}")
        return
        
    # 3. Download assets if URLs provided
    img_dir = os.path.join(dest_dir, "assets", "img")
    
    if headshot_url:
        print("\nDownloading doctor headshot...")
        # Save as dr_ritter.jpg (the template's lead doctor photo)
        download_image(headshot_url, os.path.join(img_dir, "dr_ritter.jpg"))
        
    if logo_url:
        print("\nDownloading logo...")
        download_image(logo_url, os.path.join(img_dir, "logo.png"))
        
    # 4. Perform text replacements across HTML files
    print("\nReplacing text in HTML files...")
    html_files = [f for f in os.listdir(dest_dir) if f.endswith('.html')]
    
    for filename in html_files:
        filepath = os.path.join(dest_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            # Perform replacements (handles both templates)
            content = content.replace("Ritter & Ramsey", practice_name)
            content = content.replace("Ritter Ramsey", practice_name)
            content = content.replace("Drs. Ritter & Ramsey", doctor_name)
            content = content.replace("Dr. Robert G. Ritter", doctor_name)
            content = content.replace("Dr. Robert Ritter", doctor_name)
            
            content = content.replace("Gary Solnit", practice_name)
            content = content.replace("Gary Solnit", practice_name)
            content = content.replace("Gary S. Solnit", doctor_name)
            content = content.replace("Drs. Gary Solnit", doctor_name)
            content = content.replace("Dr. Gary Solnit", doctor_name)
            
            # SVG Logo text replacements
            content = content.replace("THE BEVERLY HILLS CENTER", practice_name.upper())
            content = content.replace("RITTER & RAMSEY", practice_name.upper())
            content = content.replace("RITTER RAMSEY", practice_name.upper())
            content = content.replace("FOR AESTHETIC &amp; RESTORATIVE DENTISTRY", "GENERAL &amp; COSMETIC DENTISTRY")
            content = content.replace("FOR AESTHETIC AND RESTORATIVE DENTISTRY", "GENERAL &amp; COSMETIC DENTISTRY")
            
            # Contact details (handles both templates)
            content = content.replace("561-626-6667", phone)
            content = content.replace("310-888-1850", phone)
            
            content = content.replace("info@ritterandramsey.com", email)
            content = content.replace("info@garysolnitdds.com", email)
            
            content = content.replace("500 University Blvd, Ste 109, Jupiter, FL 33458", address)
            content = content.replace("9675 Brighton Way, Suite 330, Beverly Hills, CA 90210", address)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  Processed {filename}")
        except Exception as e:
            print(f"  [ERROR] Error processing {filename}: {e}")
            
    print("\n==================================================")
    print("                REBRAND COMPLETE!                 ")
    print(f" Project folder created: {dest_dir} ")
    print("==================================================")

if __name__ == "__main__":
    rebrand_project()
