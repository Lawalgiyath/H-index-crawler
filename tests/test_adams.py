import os
import urllib.parse
from apify_client import ApifyClient
client = ApifyClient("YOUR_APIFY_TOKEN")

first_name = "luqman"
last_name = "adams"
affiliation = "University of Lagos"
full_name = f"{first_name} {last_name}".strip()
query = f'{full_name} "{affiliation}" Google Scholar citations'

print("Query:", query)
run_input = {"queries": query, "maxPagesPerQuery": 1, "resultsPerPage": 10}
run = client.actor('apify/google-search-scraper').call(run_input=run_input)

for item in client.dataset(run.default_dataset_id).iterate_items():
    if 'organicResults' in item:
        for res in item['organicResults']:
            url = res.get('url', '')
            title = res.get('title', '').lower()
            snippet = res.get('description', '').lower()
            
            print(f"URL: {url}")
            try:
                print(f"TITLE: {title}")
                print(f"SNIPPET: {snippet}")
            except:
                pass
            
            if 'user=' not in url:
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

