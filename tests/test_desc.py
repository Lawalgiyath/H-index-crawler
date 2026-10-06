import os
from apify_client import ApifyClient
client = ApifyClient('YOUR_APIFY_TOKEN')
run = client.actor('apify/google-search-scraper').call(run_input={'queries': 'site:scholar.google.com/citations "Maureen Egenti"', 'maxPagesPerQuery': 1})
print([r.get('description') for i in client.dataset(run['defaultDatasetId']).iterate_items() for r in i.get('organicResults', [])])

