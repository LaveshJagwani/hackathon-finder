import os
import json
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
You are a filter extraction engine for a hackathon search system.

Extract structured filters from the user's query.

Return ONLY valid JSON.

Possible fields:
- location (string)
- is_online (boolean)
- theme (string)
- participants_min (number)
- participants_max (number)
- registration_deadline_before_days (number)
- sort_by ("deadline" or "start_date")
- source ("devpost", "mlh", "unstop", "devfolio", "hackerearth")

If not mentioned, omit the field.
"""


# ---------------------------------------
# Validate + Normalize Output
# ---------------------------------------

def validate_filters(data: dict):

    clean = {}

    if not isinstance(data, dict):
        return {}

    if "location" in data and isinstance(data["location"], str):
        clean["location"] = data["location"].strip()

    if "is_online" in data and isinstance(data["is_online"], bool):
        clean["is_online"] = data["is_online"]

    if "theme" in data and isinstance(data["theme"], str):
        clean["theme"] = data["theme"].strip()

    if "participants_min" in data and isinstance(data["participants_min"], (int, float)):
        clean["participants_min"] = int(data["participants_min"])

    if "participants_max" in data and isinstance(data["participants_max"], (int, float)):
        clean["participants_max"] = int(data["participants_max"])

    if "registration_deadline_before_days" in data and isinstance(data["registration_deadline_before_days"], (int, float)):
        clean["registration_deadline_before_days"] = int(data["registration_deadline_before_days"])

    if "sort_by" in data and data["sort_by"] in ["deadline", "start_date"]:
        clean["sort_by"] = data["sort_by"]

    if "source" in data and isinstance(data["source"], str):
        clean["source"] = data["source"].lower().strip()

    return clean


# ---------------------------------------
# Main Parse Function
# ---------------------------------------

def parse_query(user_query: str):

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_query}
        ],
        temperature=0
    )

    content = response.choices[0].message.content.strip()

    try:
        raw_filters = json.loads(content)
        return validate_filters(raw_filters)
    except:
        print("LLM returned invalid JSON:", content)
        return {}
