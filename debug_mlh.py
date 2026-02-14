import requests
from bs4 import BeautifulSoup

url = "https://mlh.io/seasons/2026/events"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)

print("Status:", response.status_code)

soup = BeautifulSoup(response.text, "html.parser")

# Print first 2000 characters of HTML
print(response.text[:2000])
