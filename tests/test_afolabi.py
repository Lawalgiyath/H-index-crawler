import os
from apify_client import ApifyClient
client = ApifyClient(os.environ.get('APIFY_TOKEN', 'YOUR_APIFY_TOKEN'))
run = client.actor('apify/google-search-scraper').call(run_input={
    'queries': 'site:scholar.google.com/citations Foluso Afolabi\nsite:scholar.google.com/citations Foluso Afolabi "Lagos"',
    'maxPagesPerQuery': 1,
    'resultsPerPage': 3
})
for item in client.dataset(run['defaultDatasetId']).iterate_items():
    if 'organicResults' in item:
        for res in item['organicResults']:
            print('Title:', res.get('title'))
            print('Desc:', res.get('description'))
            print('URL:', res.get('url'))

