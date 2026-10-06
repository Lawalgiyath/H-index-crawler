import json
import time
from apify_client import ApifyClient

APIFY_TOKEN = 'YOUR_APIFY_TOKEN'

with open('data/outputs/chemistry_staff_cleaned.json', 'r') as f:
    staff = json.load(f)

client = ApifyClient(APIFY_TOKEN)

print('--- Starting Live Scraping ---')
for i, person in enumerate(staff[:3], 1): # Just first 3 for immediate live test
    name = person['name']
    print(f'[{i}/{len(staff)}] Searching for: {name} (Chemistry, University of Lagos)...')
    
    run_input = {
        'queries': [f'{name} University of Lagos'],
        'maxItems': 1
    }
    try:
        run = client.actor('blackfalcondata/google-scholar-scraper').call(run_input=run_input)
        dataset = list(client.dataset(run.default_dataset_id).iterate_items())
        if dataset:
            res = dataset[0]
            print(f'   -> FOUND: Citations={res.get("citations", 0)}, H-Index={res.get("hIndex", 0)}, i10-Index={res.get("i10Index", 0)}, Link=https://scholar.google.com/citations?user={res.get("userId", "")}')
        else:
            print('   -> No profile found.')
    except Exception as e:
        print(f'   -> Error: {e}')
    
    time.sleep(1)
print('--- End of Batch ---')

