import os
from apify_client import ApifyClient
APIFY_TOKEN = os.environ.get('APIFY_TOKEN', 'YOUR_APIFY_TOKEN')
client = ApifyClient(APIFY_TOKEN)
run_input = {
    "queries": 'site:scholar.google.com/citations "Maureen Egenti"',
    "maxPagesPerQuery": 1,
    "resultsPerPage": 3,
}
run = client.actor('apify/google-search-scraper').call(run_input=run_input)
for item in client.dataset(run.default_dataset_id).iterate_items():
    if 'organicResults' in item:
        for res in item['organicResults']:
            print(res.get('title'), '|', res.get('url'))

