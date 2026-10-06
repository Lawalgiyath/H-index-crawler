from apify_client import ApifyClient
client = ApifyClient("YOUR_APIFY_TOKEN")
run_input = {
    "query": "Luqman Adams University of Lagos",
    "maxResults": 3,
    "includeDetails": True,
    "compact": False
}
run = client.actor("blackfalcondata/google-scholar-scraper").call(run_input=run_input)
for item in client.dataset(run.get("defaultDatasetId") if isinstance(run, dict) else run.default_dataset_id).iterate_items():
    print(item.get("name"), item.get("affiliation"), item.get("userId"))

