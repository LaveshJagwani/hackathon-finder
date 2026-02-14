from database import SessionLocal
from models import Hackathon
from filter_query import apply_filters
from nl_parser import parse_query


def chat_search(prompt):

    filters = parse_query(prompt)

    db = SessionLocal()
    query = db.query(Hackathon)

    query = apply_filters(query, filters)

    results = query.all()

    db.close()

    return results
