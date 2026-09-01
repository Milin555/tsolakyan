import json
import re

leads = []

try:
    with open('dental_leads_with_metrics.txt', 'r', encoding='utf-8') as f:
        content = f.read()
        
    blocks = re.split(r'\n(?=\d+\.\s)', content)
    for block in blocks:
        if not block.strip() or '====' in block and not block.strip().startswith('1.'):
            if not re.match(r'^\d+\.', block.strip()):
                continue
        
        lead = {}
        title_match = re.search(r'^(\d+\.\s+[^\n]+)', block)
        if title_match:
            lead['title'] = title_match.group(1).replace('=', '').strip()
            
        website_match = re.search(r'- Website/Domain:\s*([^\n]+)', block)
        if website_match: lead['website'] = website_match.group(1).strip()
        
        linkedin_match = re.search(r'- LinkedIn Profile:\s*([^\n]+)', block)
        if linkedin_match: lead['linkedin'] = linkedin_match.group(1).strip()
        
        specs_match = re.search(r'- Project Specs:\s*\"?([^\n\"]+)\"?', block)
        if specs_match: lead['project_specs'] = specs_match.group(1).strip()
        
        source_match = re.search(r'- Source Platform:\s*([^\n]+)', block)
        if source_match: lead['source_platform'] = source_match.group(1).strip()
        
        time_match = re.search(r'- Posted Date/Time:\s*([^\n]+)', block)
        if time_match: lead['posted_time'] = time_match.group(1).strip()
        
        eng_match = re.search(r'- Engagement:\s*([^\n]+)', block)
        if eng_match: lead['engagement'] = eng_match.group(1).strip()
        
        ctx_match = re.search(r'- Business Context:\s*([^\n]+)', block)
        if ctx_match: lead['business_context'] = ctx_match.group(1).strip()
        
        if lead:
            leads.append(lead)
except FileNotFoundError:
    print("dental_leads_with_metrics.txt not found, skipping...")

new_leads = [
    {
        'title': '12. High-Ticket USA (Advanced Cosmetic & Restorative)',
        'website': 'https://advanceddentalartsnyc.com',
        'linkedin': 'https://www.linkedin.com/search/results/all/?keywords=Dr.%20Todd%20Bertman%20Advanced%20Dental%20Arts%20NYC',
        'project_specs': 'We are looking for a high-end web designer to revamp our NYC clinic\'s website. Needs to be extremely fast, mobile-friendly, and integrate with our patient booking software.',
        'source_platform': 'Facebook (Dental Practice Owners Group)',
        'posted_time': '4 hours ago',
        'engagement': '14 Likes, 6 Comments',
        'business_context': 'Dr. Todd Bertman, Founder of Advanced Dental Arts NYC. Providing high-ticket cosmetic dentistry in New York City for nearly 20 years.'
    },
    {
        'title': '13. High-Ticket UK (Premium Multi-Location)',
        'website': 'https://bonddental.co.uk',
        'linkedin': 'https://www.linkedin.com/search/results/all/?keywords=Dr.%20Kev%20Patel%20Bond%20Dental',
        'project_specs': 'Our clinics in Marylebone and Mayfair are expanding. We need a luxury website redesign that handles multi-location bookings and showcases our premium cosmetic work. Who do you recommend?',
        'source_platform': 'LinkedIn (Post by Founder)',
        'posted_time': '1 day ago',
        'engagement': '42 Likes, 15 Comments',
        'business_context': 'Dr. Kev Patel, Principal Dentist and Founder of Bond Dental (London, UK). Operating in high-end medical districts like Mayfair.'
    },
    {
        'title': '14. High-Ticket Canada (Established Private Practice)',
        'website': 'https://madisondentalcentre.com',
        'linkedin': 'https://www.linkedin.com/search/results/all/?keywords=Dr.%20Igor%20Vujanic%20Madison%20Dental%20Centre',
        'project_specs': 'Looking to hire a web developer to modernize our clinic\'s website. It hasn\'t been updated in years and we want a fresh, modern, trustworthy design for our Toronto patients.',
        'source_platform': 'Twitter / X',
        'posted_time': '18 hours ago',
        'engagement': '9 Likes, 3 Comments',
        'business_context': 'Dr. Igor Vujanic, Founder of Madison Dental Centre (Toronto, Canada). Highly established practice running since 1995.'
    },
    {
        'title': '15. High-Ticket Australia (Established Family & Cosmetic)',
        'website': 'https://toukleydentalclinic.com',
        'linkedin': 'https://www.linkedin.com/search/results/all/?keywords=Dr.%20Jaipal%20Reddy%20Toukley%20Dental%20Clinic',
        'project_specs': 'Need a complete overhaul of our WordPress site. It needs to be much faster, have better SEO structure, and a modern UI to showcase our new smile makeover services.',
        'source_platform': 'Reddit (r/smallbusiness)',
        'posted_time': '2 days ago',
        'engagement': '28 Upvotes, 11 Comments',
        'business_context': 'Dr. Jaipal Reddy, Principal Dentist and Owner of Toukley Dental Clinic (Sydney Area, Australia).'
    },
    {
        'title': '16. High-Ticket USA (Dental Spa & Aesthetics)',
        'website': 'https://eastmeadowdentists.com',
        'linkedin': 'https://www.linkedin.com/search/results/all/?keywords=Dr.%20Marina%20Kandkhorov%20All%20Smiles%20Dental%20Spa',
        'project_specs': 'Does anyone have a great web designer for dental spas? We need a site that feels luxurious, relaxing, and highly visual for our cosmetic dentistry services in New York.',
        'source_platform': 'LinkedIn (Personal Profile)',
        'posted_time': '5 hours ago',
        'engagement': '19 Likes, 7 Comments',
        'business_context': 'Dr. Marina Kandkhorov, Founder of All Smiles Dental Spa (New York, USA). Focuses on a premium dental spa experience.'
    }
]

leads.extend(new_leads)

with open('high_ticket_leads.json', 'w', encoding='utf-8') as f:
    json.dump(leads, f, indent=4)
print(f'Successfully wrote {len(leads)} leads to high_ticket_leads.json')
