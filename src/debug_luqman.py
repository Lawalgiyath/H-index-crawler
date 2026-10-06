import json
import time
from apify_client import ApifyClient

APIFY_TOKEN = 'YOUR_APIFY_TOKEN'

client = ApifyClient(APIFY_TOKEN)

run_input = {
    "startUrls": ["https://scholar.google.com/citations?user=I02xXeUAAAAJ&hl=en"],
    "maxItems": 1
}

run = client.actor('blackfalcondata/google-scholar-scraper').call(run_input=run_input)
dataset = list(client.dataset(run.default_dataset_id).iterate_items())

if dataset:
    res = dataset[0]
    print(json.dumps(res, indent=2))
else:
    print("No results found.")

