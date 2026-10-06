import os
from apify_client import ApifyClient
client = ApifyClient(os.environ.get('APIFY_TOKEN', 'YOUR_APIFY_TOKEN'))

def test_query(query):
    print(f"\nQuery: {query}")
    run = client.actor('apify/google-search-scraper').call(run_input={
        'queries': query,
        'maxPagesPerQuery': 1,
        'resultsPerPage': 3
    })
    for item in client.dataset(run['defaultDatasetId']).iterate_items():
        if 'organicResults' in item:
            for res in item['organicResults']:
                print(res.get('title'), res.get('url'))

test_query('site:scholar.google.com/citations "Ogunbayo" "Lagos"')
test_query('site:scholar.google.com/citations Taofeeq Ogunbayo University of Lagos')
test_query('site:scholar.google.com/citations Oluwakemi Whenu University of Lagos')
test_query('site:scholar.google.com/citations Kehinde Olayinka University of Lagos')
test_query('site:scholar.google.com/citations Ayorinde Nejo University of Lagos')

