import requests
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

SEARCH_URL = "https://api.devfolio.co/api/search/hackathons"
PAGE_SIZE = 10
TIMEOUT = 15


# ===============================
# Session Setup (Stable)
# ===============================

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Origin": "https://devfolio.co",
    "Referer": "https://devfolio.co/",
}

session = requests.Session()
session.headers.update(HEADERS)

retry_strategy = Retry(
    total=3,
    backoff_factor=2,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["POST"],
)

adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)


# ===============================
# Build Search Blob
# ===============================

def build_search_blob(source):
    text_parts = [
        source.get("name", ""),
        source.get("city", ""),
        source.get("country", ""),
        source.get("location", ""),
        source.get("type", ""),
        "devfolio"
    ]

    return " ".join(str(p) for p in text_parts if p).lower()


# ===============================
# Extract State (Optional India logic)
# ===============================

def extract_state(location_text):
    if not location_text:
        return None

    parts = [p.strip() for p in location_text.split(",")]

    if len(parts) >= 2:
        return parts[-2]

    return None


# ===============================
# Main Scraper
# ===============================

def scrape_devfolio():
    print("Scraping Devfolio...")

    hacks = []
    seen = set()
    page = 0

    while True:
        payload = {
            "type": "application_open",
            "from": page * PAGE_SIZE,
            "size": PAGE_SIZE
        }

        response = session.post(SEARCH_URL, json=payload, timeout=TIMEOUT)

        if response.status_code != 200:
            break

        data = response.json()
        hits = data.get("hits", {}).get("hits", [])

        if not hits:
            break

        for item in hits:
            source = item.get("_source", {})
            slug = source.get("slug")

            if not slug or slug in seen:
                continue

            seen.add(slug)

            location_text = source.get("location")
            state = extract_state(location_text)

            hacks.append({
                "name": source.get("name"),
                "url": f"https://{slug}.devfolio.co",
                "start_date": source.get("starts_at"),
                "end_date": source.get("ends_at"),
                "registration_deadline": source.get("reg_ends_at"),
                "is_online": source.get("is_online"),
                "participants_count": source.get("participants_count", 0),
                "themes": None,
                "city": source.get("city"),
                "state": state,
                "country": source.get("country"),
                "location_text": location_text,
                "search_blob": build_search_blob(source),
                "source": "devfolio"
            })

        page += 1
        time.sleep(1)

    print(f"Total Devfolio hackathons: {len(hacks)}")
    return hacks
