from database import SessionLocal
from models import Hackathon
from filter_query import apply_filters

db = SessionLocal()

filters = {
    "location": "Mumbai",
    "is_online": False,
    "participants_min": 100,
    "registration_deadline_before_days": 10,
    "sort_by": "deadline"
}

query = db.query(Hackathon)
query = apply_filters(query, filters)

results = query.all()

for hack in results:
    print(hack.name, hack.city, hack.state)
