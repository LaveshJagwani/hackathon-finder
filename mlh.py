import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime


# -----------------------------
# Helpers
# -----------------------------

def parse_iso_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except:
        return None


def parse_mlh_location(raw_location):
    """
    Converts:
    'Boston, MA, US'
    'Houston, TX, US'
    'Everywhere, Worldwide'
    """

    if not raw_location:
        return None, None, None

    if "Worldwide" in raw_location or "Everywhere" in raw_location:
        return None, None, "Worldwide"

    parts = [p.strip() for p in raw_location.split(",")]

    city = None
    state = None
    country = None

    if len(parts) == 3:
        city, state, country = parts
    elif len(parts) == 2:
        city, country = parts
    elif len(parts) == 1:
        city = parts[0]

    return city, state, country


# -----------------------------
# Main Scraper
# -----------------------------

def scrape_mlh():

    print("Scraping MLH via embedded JSON...")

    url = "https://mlh.io/seasons/2026/events"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print("Failed:", response.status_code)
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    app_div = soup.find("div", id="app")
    if not app_div:
        return []

    data_page = app_div.get("data-page")
    if not data_page:
        return []

    json_data = json.loads(data_page)

    upcoming_events = json_data["props"].get("upcoming_events", [])

    hackathons = []

    for event in upcoming_events:

        link = event.get("website_url")
        if not link:
            continue

        raw_location = event.get("location")

        city, state, country = parse_mlh_location(raw_location)

        parsed_start = parse_iso_date(event.get("starts_at"))
        parsed_end = parse_iso_date(event.get("ends_at"))

        search_blob = f"""
        {event.get('name', '')}
        {raw_location or ''}
        mlh
        """.lower()

        hackathons.append({
            "name": event.get("name"),
            "url": link,
            "start_date": parsed_start,
            "end_date": parsed_end,
            "registration_deadline": None,
            "is_online": True if event.get("format_type") == "digital" else False,
            "participants_count": 0,
            "themes": [],
            "city": city,
            "state": state,
            "country": country,
            "location_text": raw_location,
            "search_blob": search_blob,
            "source": "mlh"
        })

    print("Total MLH hackathons:", len(hackathons))
    return hackathons
