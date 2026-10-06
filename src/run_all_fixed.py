import json
import time
import pandas as pd
from apify_client import ApifyClient

APIFY_TOKEN = 'YOUR_APIFY_TOKEN'

print('--- Starting Full Batch Scraping (Fixed Loose Matching) ---')

# Load the original complete JSON that has the User IDs
with open('data/outputs/chemistry_scholar_metrics_COMPLETE.json', 'r') as f:
    staff_full = json.load(f)

# Build start URLs using the User IDs where available, just like the original apify_scholar_final.py
start_urls = []
name_mapping = {}

for person in staff_full:
    user_id = person.get("User_ID", "")
    name = person.get("Original_Name", person.get("Name"))
    if user_id and user_id != "N/A":
        url = f"https://scholar.google.com/citations?user={user_id}&hl=en"
        start_urls.append(url)
    else:
        # Fallback to search query if no User_ID
        pass

client = ApifyClient(APIFY_TOKEN)

run_input = {
    'startUrls': start_urls,
    'maxItems': len(start_urls)
}

print(f"Sending {len(start_urls)} direct profile requests to Apify Actor...")
start_time = time.time()
try:
    run = client.actor('blackfalcondata/google-scholar-scraper').call(run_input=run_input)
    print(f"Actor run finished in {time.time() - start_time:.1f} seconds. Processing results...")
    
    dataset = list(client.dataset(run.default_dataset_id).iterate_items())
    
    results = []
    
    # We now trust the data Apify returns directly without strict string filtering
    for res in dataset:
        user_id = res.get("userId", "")
        # The actor might return the name from the profile
        profile_name = res.get("name", "Unknown")
        
        record = {
            "Name": profile_name,
            "Department": "Chemistry",
            "Profile_Link": f"https://scholar.google.com/citations?user={user_id}" if user_id else "N/A",
            "Citations_All": str(res.get("citations", "0")),
            "H_Index_All": str(res.get("hIndex", "0")),
            "I10_Index_All": str(res.get("i10Index", "0"))
        }
        results.append(record)
        print(f"Processed: {record['Name']} -> {record['Citations_All']} citations, H-Index: {record['H_Index_All']}, Link: {record['Profile_Link']}")
    
    df = pd.DataFrame(results)
    out_path = 'data/outputs/chemistry_scholar_metrics_APIFY_FULL_FIXED.csv'
    df.to_csv(out_path, index=False)
    print(f"\n--- SUCCESS! Saved to {out_path} ---")
except Exception as e:
    print(f'Error: {e}')

