from database import SessionLocal
from models import Hackathon
from datetime import datetime
import re

db = SessionLocal()

print("\n=== NORMALIZATION STARTED ===\n")


# --------------------------------
# 1️⃣ Parse Devpost Deadline Strings
# --------------------------------
def parse_devpost_deadline(deadline_str):
    """
    Converts: 'Feb 02 - Mar 16, 2026'
    → datetime(2026, 3, 16)
    """
    if not deadline_str:
        return None

    try:
        # Extract final date part
        end_part = deadline_str.split("-")[-1].strip()
        return datetime.strptime(end_part, "%b %d, %Y")
    except:
        return None


devposts = db.query(Hackathon).filter_by(source="devpost").all()

for hack in devposts:
    if hack.registration_deadline and isinstance(hack.registration_deadline, str):
        parsed = parse_devpost_deadline(hack.registration_deadline)
        if parsed:
            hack.registration_deadline = parsed

print("✔ Devpost deadlines normalized")


# --------------------------------
# 2️⃣ Extract Location From location_text
# --------------------------------

def extract_location_fields(hack):
    if not hack.location_text:
        return

    parts = [p.strip() for p in hack.location_text.split(",")]

    if len(parts) >= 1 and not hack.city:
        hack.city = parts[-3] if len(parts) >= 3 else None

    if len(parts) >= 2 and not hack.state:
        hack.state = parts[-2]

    if len(parts) >= 1 and not hack.country:
        hack.country = parts[-1]


all_hacks = db.query(Hackathon).all()

for hack in all_hacks:
    extract_location_fields(hack)

print("✔ Location fields extracted where possible")


# --------------------------------
# 3️⃣ Normalize Country Names
# --------------------------------

COUNTRY_MAP = {
    "CA": "United States",
    "Sussex": "United Kingdom",
    "UK": "United Kingdom",
    "US": "United States"
}

for hack in all_hacks:
    if hack.country in COUNTRY_MAP:
        hack.country = COUNTRY_MAP[hack.country]

print("✔ Country names normalized")


# --------------------------------
# 4️⃣ Infer Online If No Location
# --------------------------------

for hack in all_hacks:
    if not hack.city and not hack.location_text:
        hack.is_online = True

print("✔ Online inference applied")


# --------------------------------
# 5️⃣ Fix Missing Dates If Possible
# --------------------------------

# If start_date is None but deadline exists,
# treat deadline as start proxy (optional logic)

for hack in all_hacks:
    if not hack.start_date and hack.registration_deadline:
        hack.start_date = hack.registration_deadline

print("✔ Date fallback applied")


db.commit()
db.close()

print("\n=== NORMALIZATION COMPLETE ===\n")
