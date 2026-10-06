from apify_client import ApifyClient
client = ApifyClient("YOUR_APIFY_TOKEN")
query = 'Luqman Adams "University of Lagos" Google Scholar citations'
run_input = {
    "queries": query,
    "maxPagesPerQuery": 1,
    "resultsPerPage": 10,
}
run = client.actor('apify/google-search-scraper').call(run_input=run_input)
dataset_id = run.get("defaultDatasetId") if isinstance(run, dict) else run.default_dataset_id
for item in client.dataset(dataset_id).iterate_items():
    if "organicResults" in item:
        for res in item["organicResults"]:
            url = res.get("url", "")
            if 'user=' in url:
                print("Title:", res.get("title"))
                print("Desc:", res.get("description"))

