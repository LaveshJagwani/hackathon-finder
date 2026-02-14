import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def scrape_hackerearth():

    print("Scraping HackerEarth LIVE hackathons...")

    url = "https://www.hackerearth.com/challenges/hackathon/"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print("Failed:", response.status_code)
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    all_hackathons = []
    seen = set()

    # LIVE hackathons are inside cards with REGISTER button
    cards = soup.find_all("div", class_="challenge-card-modern")

    for card in cards:

        # Only keep cards that have a REGISTER button (LIVE ones)
        register_btn = card.find("a", string=lambda s: s and "REGISTER" in s.upper())
        if not register_btn:
            continue

        title_tag = card.find("div", class_="challenge-name")
        if not title_tag:
            continue

        title = title_tag.get_text(strip=True)

        link_tag = card.find("a", href=True)
        if not link_tag:
            continue

        full_url = urljoin("https://www.hackerearth.com", link_tag["href"])

        if full_url in seen:
            continue

        seen.add(full_url)

        all_hackathons.append({
            "name": title,
            "url": full_url,
            "start_date": None,
            "end_date": None,
            "registration_deadline": None,
            "is_online": True,  # HackerEarth hackathons are online by default
            "participants_count": 0,
            "themes": [],
            "source": "hackerearth"
        })

    print("Total HackerEarth LIVE hackathons:", len(all_hackathons))

    return all_hackathons
