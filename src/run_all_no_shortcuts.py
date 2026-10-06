import json
import time
import pandas as pd
from apify_client import ApifyClient

APIFY_TOKEN = 'YOUR_APIFY_TOKEN'

print('--- Starting Full Batch Scraping (NO SHORTCUTS) ---')

with open('data/outputs/chemistry_staff_cleaned.json', 'r') as f:
    staff_base = json.load(f)
    
with open('data/outputs/chemistry_scholar_metrics_COMPLETE.json', 'r') as f:
    staff_full = json.load(f)

# Create a lookup mapping from Name -> User ID from the previously known dataset
known_ids = {}
for p in staff_full:
    uid = p.get("User_ID", "")
    if uid and uid != "N/A":
        known_ids[p.get("Original_Name", p.get("Name"))] = uid

client = ApifyClient(APIFY_TOKEN)
results = []

print(f"Processing all {len(staff_base)} names...")

for person in staff_base:
    name = person["name"]
    user_id = known_ids.get(name)
    
    if user_id:
        # We know their exact profile URL
        url = f"https://scholar.google.com/citations?user={user_id}&hl=en"
        run_input = {"startUrls": [url], "maxItems": 1}
    else:
        # We MUST perform a raw search, no shortcuts!
        run_input = {"queries": [f"{name} University of Lagos"], "maxItems": 1}
        
    try:
        run = client.actor('blackfalcondata/google-scholar-scraper').call(run_input=run_input)
        dataset = list(client.dataset(run.default_dataset_id).iterate_items())
        
        if dataset:
            res = dataset[0] # Grab the top result Apify finds
            found_uid = res.get("userId", "")
            record = {
                "Name": res.get("name", name),
                "Department": "Chemistry",
                "Profile_Link": f"https://scholar.google.com/citations?user={found_uid}" if found_uid else "N/A",
                "Citations_All": str(res.get("citations", "0")),
                "H_Index_All": str(res.get("hIndex", "0")),
                "I10_Index_All": str(res.get("i10Index", "0"))
            }
        else:
            # Apify searched but literally nothing exists
            record = {
                "Name": name,
                "Department": "Chemistry",
                "Profile_Link": "N/A",
                "Citations_All": "N/A",
                "H_Index_All": "N/A",
                "I10_Index_All": "N/A"
            }
        results.append(record)
        print(f"Processed: {name} -> Found as: {record['Name']} | Citations: {record['Citations_All']} | H-Index: {record['H_Index_All']}")
        
    except Exception as e:
        print(f"Error processing {name}: {e}")

df = pd.DataFrame(results)
out_path = 'data/outputs/chemistry_scholar_metrics_APIFY_FULL_NO_SHORTCUTS.csv'
df.to_csv(out_path, index=False)
print(f"\n--- SUCCESS! All {len(results)} names processed! Saved to {out_path} ---")

