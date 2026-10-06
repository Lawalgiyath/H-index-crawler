import requests
resp = requests.get("https://api.apify.com/v2/store/actors?search=scholar")
data = resp.json()
for item in data.get("data", {}).get("items", []):
    print(item.get("name"), item.get("title"))
