import json
import time
import pandas as pd
from apify_client import ApifyClient

APIFY_TOKEN = 'YOUR_APIFY_TOKEN'

print('--- Starting Full Batch Scraping ---')
with open('data/outputs/chemistry_staff_cleaned.json', 'r') as f:
    staff = json.load(f)

queries = [f"{person['name']} University of Lagos" for person in staff]

client = ApifyClient(APIFY_TOKEN)

run_input = {
    'queries': queries,
    'maxItems': len(queries)
}

print(f"Sending {len(queries)} queries to Apify Actor...")
start_time = time.time()
try:
    run = client.actor('blackfalcondata/google-scholar-scraper').call(run_input=run_input)
    print(f"Actor run finished in {time.time() - start_time:.1f} seconds. Processing results...")
    
    dataset = list(client.dataset(run.default_dataset_id).iterate_items())
    
    results = []
    # Deduplicate results by keeping the best match per query
    for person in staff:
        name = person['name']
        
        # find matching result for this query
        match = None
        for res in dataset:
            if name.lower() in res.get("name", "").lower():
                match = res
                break
                
        if not match:
            # fallback loose match
            for res in dataset:
                if name.split()[-1].lower() in res.get("name", "").lower():
                    match = res
                    break
        
        if match:
            user_id = match.get("userId", "")
            record = {
                "Name": match.get("name", name),
                "Department": "Chemistry",
                "Profile_Link": f"https://scholar.google.com/citations?user={user_id}" if user_id else "N/A",
                "Citations_All": match.get("citations", "0"),
                "H_Index_All": match.get("hIndex", "0"),
                "I10_Index_All": match.get("i10Index", "0")
            }
        else:
            record = {
                "Name": name,
                "Department": "Chemistry",
                "Profile_Link": "N/A",
                "Citations_All": "N/A",
                "H_Index_All": "N/A",
                "I10_Index_All": "N/A"
            }
            
        results.append(record)
        print(f"Processed: {record['Name']} -> {record['Citations_All']} citations, H-Index: {record['H_Index_All']}, Link: {record['Profile_Link']}")
    
    df = pd.DataFrame(results)
    out_path = 'data/outputs/chemistry_scholar_metrics_APIFY_FULL.csv'
    df.to_csv(out_path, index=False)
    print(f"\n--- SUCCESS! Saved to {out_path} ---")
except Exception as e:
    print(f'Error: {e}')

