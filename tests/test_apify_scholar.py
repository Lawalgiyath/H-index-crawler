from apify_client import ApifyClient
client = ApifyClient("YOUR_APIFY_TOKEN")
try:
    run = client.actor('steves/google-scholar-profile-scraper').call(run_input={"startUrls": [{"url": "https://scholar.google.com/citations?user=I02xXeUAAAAJ&hl=en"}]})
    print("steves/google-scholar-profile-scraper success!")
except Exception as e:
    print(e)

