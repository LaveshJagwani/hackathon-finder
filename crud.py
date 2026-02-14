from sqlalchemy.orm import Session
from models import Hackathon


def normalize_themes(themes):

    if not themes:
        return None

    if isinstance(themes, list):
        cleaned = []

        for t in themes:
            if isinstance(t, dict):
                cleaned.append(t.get("name") or t.get("title") or "")
            else:
                cleaned.append(str(t))

        return ", ".join([c for c in cleaned if c])

    return str(themes)


def build_search_blob(hack):

    themes = hack.get("themes")

    if isinstance(themes, list):
        theme_text = " ".join(
            t.get("name") if isinstance(t, dict) else str(t)
            for t in themes
        )
    elif isinstance(themes, str):
        theme_text = themes
    else:
        theme_text = ""

    parts = [
        hack.get("name") or "",
        theme_text or "",
        hack.get("location_text") or "",
        hack.get("city") or "",
        hack.get("state") or "",
        hack.get("country") or "",
        hack.get("source") or ""
    ]

    return " ".join(parts).lower()


def save_hackathons(db: Session, hackathon_list):

    for hack in hackathon_list:

        if not hack.get("url"):
            continue

        existing = db.query(Hackathon).filter_by(url=hack["url"]).first()

        if existing:
            continue

        search_blob = build_search_blob(hack)

        new_hack = Hackathon(
            name=hack.get("name"),
            url=hack.get("url"),
            start_date=hack.get("start_date"),
            end_date=hack.get("end_date"),
            registration_deadline=hack.get("registration_deadline"),
            is_online=hack.get("is_online"),
            participants_count=hack.get("participants_count", 0),
            themes=normalize_themes(hack.get("themes")),
            city=hack.get("city"),
            state=hack.get("state"),
            country=hack.get("country"),
            location_text=hack.get("location_text"),
            source=hack.get("source"),
            search_blob=search_blob
        )

        db.add(new_hack)

    db.commit()
