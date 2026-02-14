import requests
from datetime import datetime
import re


# --------------------------------------
# Helpers
# --------------------------------------

def parse_devpost_deadline(deadline_str):
    """
    Converts:
    'Feb 02 - Mar 16, 2026'
    → datetime(2026, 3, 16)
    """
    if not deadline_str:
        return None

    try:
        end_part = deadline_str.split("-")[-1].strip()
        return datetime.strptime(end_part, "%b %d, %Y")
    except:
        return None


def parse_iso_date(date_str):
    """
    Converts ISO string to datetime.
    Handles None safely.
    """
    if not date_str:
        return None

    try:
        # Devpost usually gives ISO format
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except:
        return None


# --------------------------------------
# Main Scraper
# --------------------------------------

def scrape_devpost():

    print("Scraping Devpost (LIVE only)...")

    base_url = "https://devpost.com/api/hackathons"

    page = 1
    hackathons = []

    while True:

        print(f"Fetching page {page}...")

        params = {
            "page": page,
            "status": "open"
        }

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(base_url, params=params, headers=headers)

        if response.status_code != 200:
            break

        data = response.json()
        results = data.get("hackathons", [])

        if not results:
            break

        for item in results:

            location_data = item.get("location", {})

            city = location_data.get("city")
            state = location_data.get("state")
            country = location_data.get("country")

            location_text = ", ".join(
                [x for x in [city, state, country] if x]
            ) if (city or state or country) else None

            # 🔥 Proper parsing
            parsed_start = parse_iso_date(item.get("start_date"))
            parsed_end = parse_iso_date(item.get("end_date"))
            parsed_deadline = parse_devpost_deadline(
                item.get("submission_period_dates")
            )

            # Optional: if no start_date, use deadline for sorting
            if not parsed_start and parsed_deadline:
                parsed_start = parsed_deadline

            hackathons.append({
                "name": item.get("title"),
                "url": item.get("url"),
                "start_date": parsed_start,
                "end_date": parsed_end,
                "registration_deadline": parsed_deadline,
                "is_online": item.get("online", False),
                "participants_count": item.get("participants_count", 0),
                "themes": item.get("themes", []),
                "city": city,
                "state": state,
                "country": country,
                "location_text": location_text,
                "search_blob": f"{item.get('title', '')} {city or ''} {state or ''} {country or ''} devpost".lower(),
                "source": "devpost"
            })

        page += 1

    print("Total LIVE Devpost hackathons:", len(hackathons))
    return hackathons
