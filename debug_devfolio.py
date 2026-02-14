import requests
import json

url = "https://devfolio.co/hackathons/open"

res = requests.get(url)
html = res.text

start = html.find('__NEXT_DATA__')
json_start = html.find('{', start)
json_end = html.find('</script>', json_start)

raw_json = html[json_start:json_end]

data = json.loads(raw_json)

print("\nTop keys:")
print(data.keys())

print("\nPageProps keys:")
print(data["props"]["pageProps"].keys())

print("\nFull pageProps:")
print(json.dumps(data["props"]["pageProps"], indent=2)[:3000])
