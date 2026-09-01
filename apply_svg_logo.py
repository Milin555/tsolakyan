import os
import re

HTML_DIR = r"c:\Users\Promise\Desktop\outreach\Lura Dentist"

SVG_LIGHT = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 220 42" width="220" height="42">
    <text x="0" y="20" font-family="sans-serif" font-weight="800" font-size="22" fill="#ffffff">585dentist</text>
    <text x="0" y="36" font-family="sans-serif" font-weight="500" font-size="11" letter-spacing="2" fill="#e2e8f0">FAMILY DENTISTRY</text>
</svg>"""

SVG_DARK = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 220 42" width="220" height="42">
    <text x="0" y="20" font-family="sans-serif" font-weight="800" font-size="22" fill="#1a3b5c">585dentist</text>
    <text x="0" y="36" font-family="sans-serif" font-weight="500" font-size="11" letter-spacing="2" fill="#64748b">FAMILY DENTISTRY</text>
</svg>"""

def create_svgs():
    img_dir = os.path.join(HTML_DIR, 'assets', 'img')
    os.makedirs(img_dir, exist_ok=True)
    with open(os.path.join(img_dir, '585-logo-light.svg'), 'w', encoding='utf-8') as f:
        f.write(SVG_LIGHT)
    with open(os.path.join(img_dir, '585-logo-dark.svg'), 'w', encoding='utf-8') as f:
        f.write(SVG_DARK)
        
    # Also for variant-blue
    variant_img_dir = os.path.join(HTML_DIR, 'variant-blue', 'assets', 'img')
    if os.path.exists(variant_img_dir):
        with open(os.path.join(variant_img_dir, '585-logo-light.svg'), 'w', encoding='utf-8') as f:
            f.write(SVG_LIGHT)
        with open(os.path.join(variant_img_dir, '585-logo-dark.svg'), 'w', encoding='utf-8') as f:
            f.write(SVG_DARK)

IMG_HTML_LIGHT = '<img src="assets/img/585-logo-light.svg" alt="585dentist logo" style="height: 42px; width: 220px; object-fit: contain; display: block;" />'
IMG_HTML_DARK = '<img src="assets/img/585-logo-dark.svg" alt="585dentist logo" style="height: 42px; width: 220px; object-fit: contain; display: block;" />'

def process_directory(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".html"):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Replace the inline div with the clean image tag
                # We look for the anchor tag and replace its contents.
                # Since my previous script forced EVERYTHING to white inline styles, I'll just replace the contents of navbar_logo.
                
                # Determine if page should use dark or light logo.
                # Usually home pages use light over the hero, inner pages use dark.
                # For simplicity, if it's index.html we use light.
                if file == "index.html" or "variant-blue" in root:
                    img_html = IMG_HTML_LIGHT
                else:
                    img_html = IMG_HTML_DARK
                
                # Replace the inner contents of the navbar_logo anchor
                content = re.sub(r'(<a[^>]*class="[^"]*navbar_logo[^"]*"[^>]*>).*?(</a>)', r'\1' + img_html + r'\2', content, flags=re.DOTALL)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)

if __name__ == "__main__":
    create_svgs()
    process_directory(HTML_DIR)
    print("SVG logo fix complete!")
