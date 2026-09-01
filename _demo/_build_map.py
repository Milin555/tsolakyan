# -*- coding: utf-8 -*-
import json, glob, os, collections

ROOT = r"C:\Users\Promise\Desktop\outreach"
TEMPLATES = ["Lura Dentist", "Gary Solnit Dentist", "Modern Smile Center Dentist", "Ritter Ramsey Dentist"]

CORPUS = {}
for t in TEMPLATES:
    CORPUS[t] = {}
    for f in sorted(glob.glob(os.path.join(ROOT, t, "*.html"))):
        CORPUS[t][os.path.basename(f)] = open(f, encoding="utf-8").read()

def count(t, s):
    return sum(v.count(s) for v in CORPUS[t].values())

def files_with(t, s):
    return [k for k, v in sorted(CORPUS[t].items()) if s in v]

def brands(t, lst):
    out = []
    for s in lst:
        n = count(t, s)
        if n == 0:
            print("DROP brand %s :: %r" % (t, s)); continue
        out.append({"text": s, "count": n})
    return out

def keep(t, lst):
    out = []
    for s in lst:
        if count(t, s) == 0:
            print("DROP %s :: %r" % (t, s)); continue
        out.append(s)
    return out

def docs(t, lst):
    out = []
    for n in lst:
        fs = files_with(t, n)
        if not fs:
            print("DROP doctor %s :: %r" % (t, n)); continue
        out.append({"name": n, "files": fs})
    return out

SHARED_HIDDEN = ["LUMORA CLINIC CAREERS", "PANNU DENTAL GROUP"]
SHARED_PLACEHOLDER_ADDR = [
    "123 Smile Avenue, Suite 200 New York, NY 10001",
    "456 Bright Dental Blvd, Floor 3 Los Angeles, ",
    "45 King’s Road, Chelsea,  SW3 5UZ",
]
ABOUT_H = "Trusted Dental Experts, Decades of Care"
ABOUT_B = ("At Foundation Dental Alliance Dentistry, we combine compassion, innovation, "
           "and expertise to provide care you can trust. Your smile is our mission, and "
           "your comfort is our priority.")
SERVICES = ["Preventive dentistry", "Cosmetic dentistry", "Restorative treatments", "Strategic Inner Circle"]
CTA = ["Book Appointment", "Book An Appointment", "Get Appointment", "Get Started",
       "Make A Call", "See All Services", "View Details", "Schedule Consultation",
       "Schedule a Clean & Exam", "Schedule Assessment", "Apply Now", "Learn More",
       "Read More", "See All Blogs", "View All Doctors"]
TAGLINE = "Advanced technology, a caring team, and treatments designed to keep your smile healthy for life. "

D = {}

D["Lura Dentist"] = dict(
    brand_names=["Foundation Dental Alliance", "Foundation Dental Alliance Dentistry",
                 "Foundation Dental Alliance DDS", "Foundation Dental Alliance DDS Careers",
                 "585dentist", "foundationdentalalliance", "PROSTHODONTICS",
                 "Family Dentistry"] + SHARED_HIDDEN,
    hero_h1="Trusted Dental Care for Every Generation",
    hero_sub="We combine modern technology with heartfelt service to ensure every generation.",
    emails=["info@foundationdentalalliance.com", "edrumm@585dentist.com", "john@example.com"],
    phones=["310-888-1850", "tel:310-888-1850", "+357 70005758", "tel:+357 70005758", "tel:+35770005758"],
    addresses=["9675 Brighton Way, Suite 330, Beverly Hills, CA 90210"] + SHARED_PLACEHOLDER_ADDR,
    doctor_names=["Dr. Emilie Drumm", "Dr. Daniel Ahmed", "Dr. Emman Collins", "Dr. Marcus Rishi",
                  "Dr. Jim Arnold, DDS", "Dr. Kathryn Alderman", "Debra Englehardt-Nash",
                  "Dr. Thompson", "Dr. Rishi", "Dr. Collins", "Dr. Gary Solnit, DDS"],
)
D["Gary Solnit Dentist"] = dict(
    brand_names=["Dr. Gary Solnit, DDS, MS", "Dr. Gary Solnit, DDS", "Dr. Gary Solnit", "Gary Solnit",
                 "Gary Solnit, DDS, MS", "Dr. Gary Solnit DDS",
                 "THE BEVERLY HILLS CENTER", "FOR AESTHETIC &amp; RESTORATIVE DENTISTRY",
                 "FOR AESTHETIC AND RESTORATIVE DENTISTRY",
                 "Beverly Hills Prosthodontics",
                 "Beverly Hills Center for Aesthetic and Restorative Dentistry",
                 "Dr. Neo Boutique Dental Clinic", "garysolnitdds",
                 "Foundation Dental Alliance", "Foundation Dental Alliance Dentistry",
                 "Foundation Dental Alliance DDS", "PROSTHODONTICS"] + SHARED_HIDDEN,
    hero_h1="Beverly Hills Prosthodontics & Esthetic Dentistry",
    hero_sub=("Dr. Gary Solnit delivers world-class smile restorations, porcelain veneers, "
              "and reconstructive care designed to look and feel completely natural."),
    emails=["info@garysolnitdds.com", "drneodentistry@gmail.com",
            "info@foundationdentalalliance.com", "john@example.com"],
    phones=["310-888-1850", "tel:310-888-1850", "+357 70005758", "tel:+357 70005758", "tel:+35770005758"],
    addresses=["9675 Brighton Way, Suite 330, Beverly Hills, CA 90210",
               "9675 Brighton Way, Suite 330", "Beverly Hills, CA 90210"] + SHARED_PLACEHOLDER_ADDR,
    doctor_names=["Dr. Gary Solnit, DDS, MS", "Dr. Gary Solnit, DDS", "Dr. Neofytos Ioannides",
                  "Dr. Daniel Ahmed", "Dr. Emman Collins", "Dr. Marcus Rishi",
                  "Dr. Jim Arnold", "Dr. Kathryn Alderman", "Debra Englehardt-Nash"],
)
D["Modern Smile Center Dentist"] = dict(
    brand_names=["MODERN SMILE CENTER", "GENERAL &amp; COSMETIC DENTISTRY",
                 "Modern Smile Center, DDS, MS", "Modern Smile Center",
                 "Dr. Michael Cimino, DDS, MS", "Dr. Michael Cimino, DDS", "Dr. Michael Cimino",
                 "Michael Cimino",
                 "The Woodlands Center for Aesthetic and Restorative Dentistry",
                 "Dr. Neo Boutique Dental Clinic", "mcim21",
                 "Foundation Dental Alliance", "Foundation Dental Alliance Dentistry",
                 "Foundation Dental Alliance DDS", "PROSTHODONTICS"] + SHARED_HIDDEN,
    hero_h1="The Woodlands Cosmetic & Esthetic Dentistry",
    hero_sub=("Dr. Michael Cimino delivers world-class smile restorations, porcelain veneers, "
              "and reconstructive care designed to look and feel completely natural."),
    emails=["mcim21@gmail.com", "drneodentistry@gmail.com",
            "info@foundationdentalalliance.com", "john@example.com"],
    phones=["(281) 516-7100", "tel:(281) 516-7100", "+357 70005758", "tel:+357 70005758", "tel:+35770005758"],
    addresses=["8850 Six Pines Drive, Suite 270, The Woodlands, TX 77380",
               "8850 Six Pines Drive, Suite 270", "The Woodlands, TX 77380"] + SHARED_PLACEHOLDER_ADDR,
    doctor_names=["Dr. Michael Cimino, DDS, MS", "Dr. Michael Cimino, DDS", "Dr. Neofytos Ioannides",
                  "Dr. Daniel Ahmed", "Dr. Emman Collins", "Dr. Marcus Rishi",
                  "Dr. Jim Arnold", "Dr. Kathryn Alderman", "Debra Englehardt-Nash"],
)
D["Ritter Ramsey Dentist"] = dict(
    brand_names=["RITTER & RAMSEY", "ESTHETIC &amp; COSMETIC DENTISTRY",
                 "FOR AESTHETIC AND RESTORATIVE DENTISTRY",
                 "Ritter & Ramsey, DDS, MS", "Drs. Ritter & Ramsey, DDS", "Drs. Ritter & Ramsey",
                 "Ritter & Ramsey", "Ritter &amp; Ramsey", "Ritter and Ramsey", "ritterandramsey",
                 "Ritter & Ramsey General & Cosmetic Dentistry",
                 "Dr. Neo Boutique Dental Clinic",
                 "Foundation Dental Alliance", "Foundation Dental Alliance Dentistry",
                 "Foundation Dental Alliance DDS", "PROSTHODONTICS"] + SHARED_HIDDEN,
    hero_h1="Jupiter Cosmetic & Restorative Dentistry",
    hero_sub=("Drs. Ritter & Ramsey delivers world-class smile restorations, porcelain veneers, "
              "and reconstructive care designed to look and feel completely natural."),
    emails=["info@ritterandramsey.com", "drneodentistry@gmail.com",
            "info@foundationdentalalliance.com", "john@example.com"],
    phones=["561-626-6667", "tel:561-626-6667", "+357 70005758", "tel:+357 70005758", "tel:+35770005758"],
    addresses=["9675 Brighton Way, Suite 330", "Jupiter, FL 90210"] + SHARED_PLACEHOLDER_ADDR,
    doctor_names=["Dr. Robert G. Ritter", "Dr. Christopher Ramsey", "Dr. Isabelle Ritter",
                  "Dr. Jim Arnold", "Dr. Kathryn Alderman", "Debra Englehardt-Nash"],
)

OUT = {}
for t in TEMPLATES:
    d = D[t]
    o = collections.OrderedDict()
    o["brand_names"]    = brands(t, d["brand_names"])
    o["hero_h1"]        = (d["hero_h1"] if count(t, d["hero_h1"]) else None)
    o["hero_sub"]       = (d["hero_sub"] if count(t, d["hero_sub"]) else None)
    o["about_heading"]  = (ABOUT_H if ABOUT_H in CORPUS[t]["about.html"] else None)
    o["about_body"]     = (ABOUT_B if ABOUT_B in CORPUS[t]["about.html"] else None)
    o["service_names"]  = keep(t, SERVICES)
    o["emails"]         = keep(t, d["emails"])
    o["phones"]         = keep(t, d["phones"])
    o["addresses"]      = keep(t, d["addresses"])
    o["doctor_names"]   = docs(t, d["doctor_names"])
    o["cta_text"]       = keep(t, CTA)
    o["footer_tagline"] = (TAGLINE if count(t, TAGLINE) else None)
    OUT[t] = o

p = os.path.join(ROOT, "_demo", "token_map.json")
with open(p, "w", encoding="utf-8") as fh:
    json.dump(OUT, fh, indent=2, ensure_ascii=False)
print("WROTE", p)
for t in TEMPLATES:
    print(t, "brands:", len(OUT[t]["brand_names"]),
          "emails:", len(OUT[t]["emails"]), "phones:", len(OUT[t]["phones"]),
          "addrs:", len(OUT[t]["addresses"]), "docs:", len(OUT[t]["doctor_names"]))
