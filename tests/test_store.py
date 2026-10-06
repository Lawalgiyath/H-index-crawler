import os
import requests
token = os.environ.get('APIFY_TOKEN', 'YOUR_APIFY_TOKEN')
r = requests.get(f'https://api.apify.com/v2/store/actors?search=scholar')
for item in r.json()['data']['items'][:5]:
    print(item['name'])

