import os
import urllib.parse
from apify_client import ApifyClient
client = ApifyClient(os.environ.get('APIFY_TOKEN', 'YOUR_APIFY_TOKEN'))

first_name = "folasade"
last_name = "ogunsola"
affiliation = "University of Lagos"
full_name = f"{first_name} {last_name}".strip()
query = f'{full_name} "{affiliation}" Google Scholar citations'

print("Query:", query)
run_input = {"queries": query, "maxPagesPerQuery": 1, "resultsPerPage": 10}
run = client.actor('apify/google-search-scraper').call(run_input=run_input)

user_id = None
for item in client.dataset(run.default_dataset_id).iterate_items():
    if 'organicResults' in item:
        for res in item['organicResults']:
            url = res.get('url', '')
            title = res.get('title', '').lower()
            snippet = res.get('description', '').lower()
            
            print(f"URL: {url}")
            print(f"TITLE: {title}")
            print(f"SNIPPET: {snippet}")
            
            if 'user=' not in url:
                print("Skipping - no user=")
                continue
                
            last_lower = last_name.lower()
            first_lower = first_name.lower()
            affil_lower = affiliation.lower()
            
            name_match = last_lower in title or last_lower in snippet
            affil_match = (
                affil_lower in title or affil_lower in snippet
                or 'lagos' in title or 'lagos' in snippet
                or 'unilag' in title or 'unilag' in snippet
            )
            print(f"name_match: {name_match}, affil_match: {affil_match}")
            
            if name_match and affil_match:
                parsed = urllib.parse.urlparse(url)
                qs = urllib.parse.parse_qs(parsed.query)
                if 'user' in qs:
                    user_id = qs['user'][0]
                    print(f"STRONG MATCH: {user_id}")
                    break
            elif name_match:
                parsed = urllib.parse.urlparse(url)
                qs = urllib.parse.parse_qs(parsed.query)
                if 'user' in qs and not user_id:
                    user_id = qs['user'][0]
                    print(f"WEAK MATCH: {user_id}")
        if user_id: break
print("Final user_id:", user_id)

