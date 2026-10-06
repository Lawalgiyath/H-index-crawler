import os
from apify_client import ApifyClient
client = ApifyClient(os.environ.get('APIFY_TOKEN', 'YOUR_APIFY_TOKEN'))
query = 'folasade ogunsola "University of Lagos" Google Scholar citations'
print("Running query:", query)
run = client.actor('apify/google-search-scraper').call(run_input={"queries": query, "maxPagesPerQuery": 1, "resultsPerPage": 10})
for item in client.dataset(run.default_dataset_id).iterate_items():
    if 'organicResults' in item:
        for res in item['organicResults']:
            print(res.get('url', ''), "-->", res.get('title', ''))

