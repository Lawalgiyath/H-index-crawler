from apify_client import ApifyClient
client = ApifyClient("YOUR_APIFY_TOKEN")
items = client.store().iterate_items()
for item in items:
    if "scholar" in item.get("title", "").lower() or "scholar" in item.get("name", "").lower():
        print(item.get("name"), item.get("title"))

