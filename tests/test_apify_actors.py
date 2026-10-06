from apify_client import ApifyClient
client = ApifyClient("YOUR_APIFY_TOKEN")
try:
    for actor in client.actors().list().items:
        print(actor.get("name"))
except Exception as e:
    print(e)

