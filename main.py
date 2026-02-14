from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from sqlalchemy import func
import time

from database import SessionLocal
from models import Hackathon
from schemas import HackathonResponse
from filter_query import apply_filters
from nl_parser import parse_query


app = FastAPI(title="Hackathon Finder API")


# ======================================================
# In-memory LLM Cache
# ======================================================

LLM_CACHE = {}
CACHE_TTL = 300  # 5 minutes


# ======================================================
# DB Dependency
# ======================================================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ======================================================
# Health & Root
# ======================================================

@app.get("/")
def root():
    return {"status": "Hackathon Finder API running"}


@app.get("/health")
def health():
    return {"status": "ok"}


# ======================================================
# Stats Endpoint
# ======================================================

@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):

    total = db.query(func.count(Hackathon.id)).scalar()

    online = (
        db.query(func.count(Hackathon.id))
        .filter(Hackathon.is_online == True)
        .scalar()
    )

    offline = (
        db.query(func.count(Hackathon.id))
        .filter(Hackathon.is_online == False)
        .scalar()
    )

    by_source = (
        db.query(Hackathon.source, func.count(Hackathon.id))
        .group_by(Hackathon.source)
        .all()
    )

    return {
        "total_hackathons": total,
        "online": online,
        "offline": offline,
        "by_source": {source: count for source, count in by_source}
    }


# ======================================================
# Structured Filter Search
# ======================================================

@app.get(
    "/search",
    response_model=List[HackathonResponse],
    response_model_exclude_none=True
)
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

    results = (
        filtered_query
        .offset(offset)
        .limit(limit)
        .all()
    )

    return results


# ======================================================
# LLM Natural Language Search
# ======================================================

@app.get(
    "/chat_search",
    response_model=List[HackathonResponse],
    response_model_exclude_none=True
)
def chat_search(
    query: str,
    limit: int = Query(20, le=100),
    offset: int = 0,
    db: Session = Depends(get_db)
):

    current_time = time.time()

    # -------- LLM Caching --------
    if query in LLM_CACHE:
        cached_data = LLM_CACHE[query]
        if current_time - cached_data["timestamp"] < CACHE_TTL:
            filters = cached_data["filters"]
        else:
            filters = parse_query(query)
            LLM_CACHE[query] = {
                "filters": filters,
                "timestamp": current_time
            }
    else:
        filters = parse_query(query)
        LLM_CACHE[query] = {
            "filters": filters,
            "timestamp": current_time
        }

    # -------- Apply Filters --------
    base_query = db.query(Hackathon)
    filtered_query = apply_filters(base_query, filters)

    results = (
        filtered_query
        .offset(offset)
        .limit(limit)
        .all()
    )

    return results
