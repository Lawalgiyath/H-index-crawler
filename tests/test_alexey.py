from apify_client import ApifyClient
client = ApifyClient("YOUR_APIFY_TOKEN")
run_input = {
    "queries": "Luqman Adams University of Lagos",
    "language": "en"
}
run = client.actor('alexey/google-scholar-scraper').call(run_input=run_input)
for item in client.dataset((run.get('defaultDatasetId') if isinstance(run, dict) else run.default_dataset_id)).iterate_items():
    print(item)

