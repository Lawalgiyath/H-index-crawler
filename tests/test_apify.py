import os
from apify_client import ApifyClient
APIFY_TOKEN = os.environ.get('APIFY_TOKEN', 'YOUR_APIFY_TOKEN')
client = ApifyClient(APIFY_TOKEN)
run_input = {'query': 'author:"Maureen Egenti"', 'maxResults': 5, 'includeDetails': True, 'compact': False}
run = client.actor('blackfalcondata/google-scholar-scraper').call(run_input=run_input)
for item in client.dataset(run.default_dataset_id).iterate_items():
    print(item.get('name'), '|', item.get('affiliation'))

