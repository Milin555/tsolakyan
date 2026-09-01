# -*- coding: utf-8 -*-
import json, os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "copy")

data = [
{
  "slug": "cosmetic-dentistry-of-san-antonio",
  "rank": 6,
  "practice": "Cosmetic Dentistry of San Antonio",
  "meta_title": "Cosmetic Dentistry of San Antonio | Veneers in San Antonio, TX",
  "meta_desc": "Veneers, Lumineers, Invisalign and full-mouth reconstruction in San Antonio, TX, with virtual consultations for patients traveling in.",
  "hero_h1": "Veneers and full-mouth care in San Antonio",
  "hero_sub": "Cosmetic dentistry led by Dr. Edward J. Camacho, with virtual consultations before you travel.",
  "cta_primary": "Book a consultation",
  "cta_secondary": "See our work",
  "about_heading": "Cosmetic dentistry, planned before you travel",
  "about_body": "Dr. Edward J. Camacho leads a cosmetic practice in San Antonio built around veneers, Lumineers and full-mouth reconstruction, with Invisalign and CEREC restorations handled in the same office.\n\nPatients coming in from out of town can start with a Smile Virtual consultation, so the plan and the timeline are settled before anyone books a flight.",
  "services": [
    {"name": "Porcelain veneers", "blurb": "Veneers and Lumineers designed for the shape, shade and proportion you want to keep."},
    {"name": "Full-mouth reconstruction", "blurb": "Rebuilding function and appearance across the whole mouth as one planned case."},
    {"name": "Invisalign", "blurb": "Clear aligner treatment to correct alignment before or alongside cosmetic work."},
    {"name": "CEREC restorations", "blurb": "Crowns and restorations milled in the practice, so fewer visits and no temporary stage."}
  ],
  "footer_tagline": "Cosmetic dentistry in San Antonio, for local and visiting patients.",
  "why_this_angle": "Led on the Smile Virtual consultation and out-of-town patient program from growth_trigger, because that is what separates this practice from every other cosmetic office in the city."
},
{
  "slug": "the-grove-family-dental",
  "rank": 7,
  "practice": "The Grove Family Dental",
  "meta_title": "The Grove Family Dental | Family and implant dentistry in Glendale, AZ",
  "meta_desc": "General, cosmetic and implant dentistry in Glendale, Arizona, from a father-and-son team working in a purpose-built new office.",
  "hero_h1": "Family, cosmetic and implant care in Glendale",
  "hero_sub": "A father-and-son dental team, now practicing in a purpose-built new office.",
  "cta_primary": "Book an appointment",
  "cta_secondary": "See our services",
  "about_heading": "Two generations of dentists, one practice",
  "about_body": "The Grove Family Dental is run by Dr. Todd Garrett and Dr. Brady Garrett, a father and son practicing together in Glendale. General, cosmetic and implant care all sit under one roof.\n\nThe practice now works from an office built from the ground up for it, so families can see the same team for routine visits, cosmetic treatment and implants without being sent across town.",
  "services": [
    {"name": "General dentistry", "blurb": "Routine care for every age, from children through to grandparents, in one practice."},
    {"name": "Cosmetic dentistry", "blurb": "Treatment aimed at how your teeth look, planned around what you actually want changed."},
    {"name": "Dental implants", "blurb": "Replacing missing teeth with implants placed and restored by the same team."},
    {"name": "New patient visits", "blurb": "A first appointment in the new Glendale office, with time to talk through options."}
  ],
  "footer_tagline": "Family, cosmetic and implant dentistry in Glendale, Arizona.",
  "why_this_angle": "Built the page around the purpose-built new office from growth_trigger and the father-and-son ownership in role, since the new building is the news and the current site buries it."
},
{
  "slug": "my-smile-miami",
  "rank": 8,
  "practice": "My Smile Miami",
  "meta_title": "My Smile Miami | Veneers and Invisalign in Miami, FL",
  "meta_desc": "Veneers, Invisalign, implants and Fotona laser treatment in Miami, FL, with Dr. Grisel Martos, a Blue Diamond Plus Invisalign provider.",
  "hero_h1": "Veneers and Invisalign in Miami",
  "hero_sub": "Cosmetic and alignment cases with Dr. Grisel Martos, Blue Diamond Plus Invisalign provider.",
  "cta_primary": "Book a consultation",
  "cta_secondary": "See our cases",
  "about_heading": "Cosmetic and alignment work in one practice",
  "about_body": "Dr. Grisel Martos owns My Smile Miami, a Miami practice built around veneers, Invisalign, implants and Fotona laser treatment.\n\nShe holds Blue Diamond Plus status with Invisalign, and cosmetic, alignment and implant work is planned in the same place rather than split across referrals, so one plan carries a case from first consultation to finished result.",
  "services": [
    {"name": "Porcelain veneers", "blurb": "Veneer cases designed around your face, not a single stock shade and shape."},
    {"name": "Invisalign", "blurb": "Clear aligner treatment from a Blue Diamond Plus provider, planned in house."},
    {"name": "Dental implants", "blurb": "Replacing missing teeth and restoring them within the same treatment plan."},
    {"name": "Fotona laser dentistry", "blurb": "Laser treatment used where it means less cutting and a more comfortable visit."}
  ],
  "footer_tagline": "Veneers, Invisalign and implants in Miami, Florida.",
  "why_this_angle": "Anchored on the Blue Diamond Plus Invisalign milestone in growth_trigger and paired it with the veneer and Fotona services from specialty, so the page matches the work her Instagram audience already follows."
},
{
  "slug": "ocean-vibe-dental",
  "rank": 9,
  "practice": "Ocean Vibe Dental",
  "meta_title": "Ocean Vibe Dental | Implants and clear aligners in Fort Myers, FL",
  "meta_desc": "General dentistry, implants and clear aligners in Fort Myers, FL, with bilingual care and CBCT implant planning from Dr. Alexandra Zabala.",
  "hero_h1": "General, implant and aligner care in Fort Myers",
  "hero_sub": "A new Fort Myers practice owned and run by Dr. Alexandra Zabala, with bilingual care.",
  "cta_primary": "Book an appointment",
  "cta_secondary": "Meet Dr. Zabala",
  "about_heading": "A new practice, run by the dentist who owns it",
  "about_body": "Ocean Vibe Dental opened in Fort Myers under Dr. Alexandra Zabala, who owns the practice and treats the patients herself. Care covers general dentistry, implants and clear aligners.\n\nImplant cases are planned from a CBCT scan before treatment starts, and the practice is bilingual, so you can talk through the options in the language you are most comfortable in.",
  "services": [
    {"name": "General dentistry", "blurb": "Everyday care for new and returning patients, with the same dentist each visit."},
    {"name": "Dental implants", "blurb": "Missing teeth replaced with implants, placed to a plan made before treatment begins."},
    {"name": "Clear aligners", "blurb": "Straightening treatment using removable clear aligners rather than fixed braces."},
    {"name": "CBCT implant planning", "blurb": "Scan-based planning, so where an implant goes is decided before the day of surgery."}
  ],
  "footer_tagline": "Bilingual general, implant and aligner dentistry in Fort Myers.",
  "why_this_angle": "Played the new practice launch, bilingual care and CBCT implant planning from growth_trigger and role as the whole story, because an owner-run first-year practice is the one thing a chain in Fort Myers cannot claim."
},
{
  "slug": "circle-c-dental",
  "rank": 10,
  "practice": "Circle C Dental",
  "meta_title": "Circle C Dental | General and cosmetic dentistry in Austin, TX",
  "meta_desc": "General and cosmetic dentistry in suburban Austin, TX, with Dr. Blake Mulgrew handling routine care and cosmetic work in one practice.",
  "hero_h1": "General and cosmetic dentistry in Austin",
  "hero_sub": "Routine care and cosmetic treatment with Dr. Blake Mulgrew, in one suburban Austin practice.",
  "cta_primary": "Book an appointment",
  "cta_secondary": "See our services",
  "about_heading": "One dentist, routine care and cosmetic work",
  "about_body": "Circle C Dental is Dr. Blake Mulgrew's practice in suburban Austin, covering general dentistry and cosmetic treatment for people who live nearby.\n\nEveryday care and cosmetic work are handled by the same dentist, so a checkup, a repair and a change to how your smile looks are part of one conversation rather than a set of referrals.",
  "services": [
    {"name": "General dentistry", "blurb": "Checkups, cleanings and everyday treatment for adults and children in the neighborhood."},
    {"name": "Cosmetic dentistry", "blurb": "Treatment focused on the appearance of your teeth, discussed before anything starts."},
    {"name": "New patient visits", "blurb": "A first appointment with time to look properly and explain what you actually need."},
    {"name": "Smile consultations", "blurb": "A sit-down about what you would change, with the options and costs set out plainly."}
  ],
  "footer_tagline": "General and cosmetic dentistry in suburban Austin, Texas.",
  "why_this_angle": "The record is thin beyond a general and cosmetic specialty, so I leaned on the suburban Austin, owner-dentist positioning in city and role and kept every claim to what a one-dentist practice can honestly say."
}
]

for rec in data:
    p = os.path.join(OUT, rec["slug"] + ".json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("wrote", p)
