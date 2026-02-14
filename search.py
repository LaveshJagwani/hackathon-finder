from database import SessionLocal
from models import Hackathon
from sqlalchemy import func

db = SessionLocal()

# -----------------------------
# SUMMARY BY SOURCE
# -----------------------------

print("\n===== SUMMARY BY SOURCE =====\n")

sources = db.query(Hackathon.source, func.count(Hackathon.id)) \
            .group_by(Hackathon.source) \
            .all()

for source, count in sources:
    print(f"{source}: {count} hackathons")

# -----------------------------
# FIELD COMPLETENESS CHECK
# -----------------------------

print("\n===== FIELD COMPLETENESS CHECK =====\n")

total = db.query(func.count(Hackathon.id)).scalar()

fields = [
    "start_date",
    "end_date",
    "registration_deadline",
    "is_online",
    "city",
    "country",
    "location_text",
    "search_blob"
]

for field in fields:
    missing = db.query(func.count(Hackathon.id)) \
                .filter(getattr(Hackathon, field) == None) \
                .scalar()
    print(f"{field}: {total - missing}/{total} populated")

# -----------------------------
# SAMPLE RECORDS PER SOURCE
# -----------------------------

print("\n===== SAMPLE RECORDS (Per Source) =====\n")

sources = db.query(Hackathon.source).distinct().all()

for (source,) in sources:
    print(f"\n--- {source.upper()} SAMPLE ---")

    sample = db.query(Hackathon) \
               .filter_by(source=source) \
               .limit(3) \
               .all()

    for h in sample:
        print("\nName:", h.name)
        print("Start:", h.start_date)
        print("End:", h.end_date)
        print("Deadline:", h.registration_deadline)
        print("Online:", h.is_online)
        print("City:", h.city)
        print("State:", h.state)
        print("Country:", h.country)
        print("Search Blob Exists:", bool(h.search_blob))
        print("-" * 40)

db.close()
