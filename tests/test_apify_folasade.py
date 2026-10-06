import os
from apify_client import ApifyClient
import urllib.parse
client = ApifyClient(os.environ.get('APIFY_TOKEN', 'YOUR_APIFY_TOKEN'))
run = client.actor('apify/google-search-scraper').call(run_input={"queries": "site:scholar.google.com/citations folasade ogunsola University of Lagos", "maxPagesPerQuery": 1, "resultsPerPage": 5})
for item in client.dataset(run.default_dataset_id).iterate_items():
    if 'organicResults' in item:
        for res in item['organicResults']:
            print(res)

