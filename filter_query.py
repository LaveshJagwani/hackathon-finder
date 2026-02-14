from sqlalchemy import or_, and_, case, func
from models import Hackathon
from india_geo import STATE_TO_CITIES
from datetime import datetime, timedelta


# ------------------------------------------------
# KEYWORD MATCHING
# ------------------------------------------------
def apply_keyword_filter(query, text):
    words = [w.strip() for w in text.lower().split() if w.strip()]

    for word in words:
        query = query.filter(
            Hackathon.search_blob.ilike(f"%{word}%")
        )

    return query


# ------------------------------------------------
# RELEVANCE SORTING
# ------------------------------------------------
def apply_relevance_sort(query, keyword):
    keyword = keyword.lower()

    relevance = case(
        (Hackathon.name.ilike(f"%{keyword}%"), 3),
        (Hackathon.search_blob.ilike(f"%{keyword}%"), 1),
        else_=0
    )

    return query.order_by(relevance.desc())


# ------------------------------------------------
# MAIN FILTER ENGINE
# ------------------------------------------------
def apply_filters(query, filters: dict):

    location = filters.get("location")
    theme = filters.get("theme")
    is_online = filters.get("is_online")
    participants_min = filters.get("participants_min")
    participants_max = filters.get("participants_max")
    source = filters.get("source")
    deadline_days = filters.get("registration_deadline_before_days")
    sort_by = filters.get("sort_by")

    now = datetime.utcnow()

    # -------------------------
    # HIDE EXPIRED EVENTS
    # -------------------------
    # --------------------------------
# DEFAULT: SHOW OPEN REGISTRATION
# --------------------------------
    query = query.filter(
        or_(
            # Registration still open
            Hackathon.registration_deadline >= now,

            # No registration info but event not ended
            and_(
                Hackathon.registration_deadline == None,
                Hackathon.end_date >= now
            )
        )
    )


    # -------------------------
    # LOCATION FILTER
    # -------------------------
    if location:
        location = location.lower().strip()

        if location in STATE_TO_CITIES:
            cities = STATE_TO_CITIES[location]

            query = query.filter(
                or_(
                    func.lower(Hackathon.state).like(f"%{location}%"),
                    func.lower(Hackathon.city).in_([c.lower() for c in cities]),
                    Hackathon.search_blob.ilike(f"%{location}%")
                )
            )
        else:
            query = query.filter(
                Hackathon.search_blob.ilike(f"%{location}%")
            )

    # -------------------------
    # THEME FILTER
    # -------------------------
    if theme:
        query = apply_keyword_filter(query, theme)
        query = apply_relevance_sort(query, theme)

    # -------------------------
    # ONLINE FILTER
    # -------------------------
    if is_online is not None:
        query = query.filter(Hackathon.is_online == is_online)

    # -------------------------
    # PARTICIPANTS FILTER
    # -------------------------
    if participants_min is not None:
        query = query.filter(
            Hackathon.participants_count != None,
            Hackathon.participants_count >= participants_min
        )

    if participants_max is not None:
        query = query.filter(
            Hackathon.participants_count != None,
            Hackathon.participants_count <= participants_max
        )

    # -------------------------
    # SOURCE FILTER
    # -------------------------
    if source:
        query = query.filter(Hackathon.source.ilike(f"%{source}%"))

    # -------------------------
    # DEADLINE FILTER
    # -------------------------
    if deadline_days is not None:
        cutoff = now + timedelta(days=deadline_days)

        query = query.filter(
            Hackathon.registration_deadline != None,
            Hackathon.registration_deadline >= now,
            Hackathon.registration_deadline <= cutoff
        )

    # -------------------------
    # SORTING
    # -------------------------
    if sort_by == "deadline":
        query = query.order_by(
            Hackathon.registration_deadline.asc().nullslast()
        )

    elif sort_by == "participants":
        query = query.order_by(
            Hackathon.participants_count.desc().nullslast()
        )

    elif sort_by == "start_date":
        query = query.order_by(
            Hackathon.start_date.asc().nullslast()
        )

    else:
        # Default: upcoming soonest first
        query = query.order_by(
            Hackathon.start_date.asc().nullslast()
        )

    return query
