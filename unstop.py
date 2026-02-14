import requests


def scrape_unstop():

    print("Scraping Unstop via API pagination...")

    base_url = "https://unstop.com/api/public/opportunity/search-result"

    page = 1
    hackathons = []

    while True:

        print(f"Fetching page {page}...")

        params = {
            "opportunity": "hackathons",
            "page": page,
            "per_page": 18,
            "oppstatus": "open"
        }

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(base_url, params=params, headers=headers)

        if response.status_code != 200:
            print("Failed:", response.status_code)
            break

        data = response.json()
        results = data.get("data", {}).get("data", [])

        if not results:
            break

        for item in results:

            address = item.get("address_with_country_logo", {})

            city = address.get("city")
            state = address.get("state")

            country = None
            if address.get("country"):
                country = address["country"].get("name")

            location_text = ", ".join(
                [x for x in [city, state, country] if x]
            ) if (city or state or country) else None

            hackathons.append({
                "name": item.get("title"),
                "url": item.get("seo_url"),
                "start_date": item.get("approved_date"),
                "end_date": item.get("end_date"),
                "registration_deadline": item.get("regnRequirements", {}).get("end_regn_dt"),
                "is_online": True if item.get("region") == "online" else False,
                "participants_count": item.get("registerCount", 0),
                "themes": [skill["skill_name"] for skill in item.get("required_skills", [])],
                "city": city,
                "state": state,
                "country": country,
                "location_text": location_text,
                "source": "unstop"
            })

        page += 1

    print("Total Unstop hackathons:", len(hackathons))
    return hackathons
