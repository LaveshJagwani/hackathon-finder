from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from database import SessionLocal
from models import Hackathon
from filter_query import apply_filters
from nl_parser import parse_query
import time

# Simple in-memory cache
LLM_CACHE = {}
CACHE_TTL = 300  # seconds


app = FastAPI(title="Hackathon Finder API")


# ---------------------------------------
# DB Dependency
# ---------------------------------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------
# Health Check
# ---------------------------------------

@app.get("/")
def root():
    return {"status": "Hackathon Finder API running"}


# ---------------------------------------
# Basic Filter Search
# ---------------------------------------

@app.get("/search")
def search_hackathons(
    location: Optional[str] = None,
    theme: Optional[str] = None,
    is_online: Optional[bool] = None,
    participants_min: Optional[int] = None,
    participants_max: Optional[int] = None,
    registration_deadline_before_days: Optional[int] = None,
    source: Optional[str] = None,
    sort_by: Optional[str] = None,
    limit: int = Query(20, le=100),
    offset: int = 0,
    db: Session = Depends(get_db)
):

    filters = {
        "location": location,
        "theme": theme,
        "is_online": is_online,
        "participants_min": participants_min,
        "participants_max": participants_max,
        "registration_deadline_before_days": registration_deadline_before_days,
        "source": source,
        "sort_by": sort_by
    }

    base_query = db.query(Hackathon)
    filtered_query = apply_filters(base_query, filters)

    total = filtered_query.count()

    results = (
        filtered_query
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "results": [
            {
                "name": h.name,
                "url": h.url,
                "start_date": h.start_date,
                "end_date": h.end_date,
                "registration_deadline": h.registration_deadline,
                "is_online": h.is_online,
                "city": h.city,
                "state": h.state,
                "country": h.country,
                "source": h.source
            }
            for h in results
        ]
    }

# ---------------------------------------
# LLM Natural Language Search
# ---------------------------------------
@app.get("/chat-search")
def chat_search(
    q: str,
    limit: int = Query(20, le=100),
    offset: int = 0,
    db: Session = Depends(get_db)
):

    now = time.time()

    # -------------------------
    # CHECK CACHE
    # -------------------------
    if q in LLM_CACHE:
        cached_entry = LLM_CACHE[q]

        if now - cached_entry["timestamp"] < CACHE_TTL:
            filters = cached_entry["filters"]
        else:
            # expired
            filters = parse_query(q)
            LLM_CACHE[q] = {
                "filters": filters,
                "timestamp": now
            }
    else:
        filters = parse_query(q)
        LLM_CACHE[q] = {
            "filters": filters,
            "timestamp": now
        }

    base_query = db.query(Hackathon)
    filtered_query = apply_filters(base_query, filters)

    total = filtered_query.count()

    results = (
        filtered_query
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "extracted_filters": filters,
        "cached": q in LLM_CACHE,
        "total": total,
        "limit": limit,
        "offset": offset,
        "results": [
            {
                "name": h.name,
                "url": h.url,
                "start_date": h.start_date,
                "registration_deadline": h.registration_deadline,
                "city": h.city,
                "country": h.country,
                "source": h.source
            }
            for h in results
        ]
    }
