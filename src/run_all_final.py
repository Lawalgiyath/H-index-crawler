import json
import time
import pandas as pd
from apify_client import ApifyClient

APIFY_TOKEN = 'YOUR_APIFY_TOKEN'

def calculate_match_score(target_name, profile_name, affiliation):
    """
    Score the profile:
    - Affiliation must contain 'lagos' or 'unilag'
    - +10 points for each matching name part
    """
    affiliation = str(affiliation).lower()
    if "lagos" not in affiliation and "unilag" not in affiliation:
        return 0 # Discard entirely if not affiliated with Lagos
        
    score = 100 # Base score for having the right affiliation
    
    target_parts = [p.lower().strip() for p in target_name.split() if len(p) > 2]
    profile_name_lower = str(profile_name).lower()
    
    matches = 0
    for part in target_parts:
        if part in profile_name_lower:
            matches += 1
            score += 10
            
    if matches == 0:
        return 0 # Discard if no names match at all
        
    return score

print('--- Starting Robust 27-Name Scraper (No Shortcuts) ---')

with open('data/outputs/chemistry_staff_cleaned.json', 'r') as f:
    staff_base = json.load(f)

client = ApifyClient(APIFY_TOKEN)
results = []

for i, person in enumerate(staff_base):
    name = person["name"]
    print(f"\n[{i+1}/27] Searching for: {name}")
    
    run_input = {
        "queries": [f"{name} University of Lagos"],
        "maxItems": 15
    }
    
    try:
        run = client.actor('blackfalcondata/google-scholar-scraper').call(run_input=run_input)
        dataset = list(client.dataset(run.default_dataset_id).iterate_items())
        
        best_match = None
        best_score = 0
        
        for res in dataset:
            prof_name = res.get("name", "Unknown")
            affil = res.get("affiliation", "")
            
            score = calculate_match_score(name, prof_name, affil)
            
            if score > best_score:
                best_score = score
                best_match = res
                
        if best_match:
            record = {
                "Target": name,
                "Matched_As": best_match.get("name"),
                "Affiliation": best_match.get("affiliation"),
                "Citations": best_match.get("citations", "0"),
                "H_Index": best_match.get("hIndex", "0"),
                "I10_Index": best_match.get("i10Index", "0"),
                "Link": f"https://scholar.google.com/citations?user={best_match.get('userId')}"
            }
            print(f"  => SUCCESS: {record['Matched_As']} (H-Index: {record['H_Index']})")
        else:
            record = {
                "Target": name,
                "Matched_As": "N/A",
                "Affiliation": "N/A",
                "Citations": "N/A",
                "H_Index": "N/A",
                "I10_Index": "N/A",
                "Link": "N/A"
            }
            print(f"  => NO VALID MATCH FOUND.")
            
        results.append(record)
        
    except Exception as e:
        print(f"Error processing {name}: {e}")

df = pd.DataFrame(results)
out_path = 'data/outputs/chemistry_scholar_metrics_APIFY_PERFECT.csv'
df.to_csv(out_path, index=False)
print(f"\n--- SUCCESS! Saved to {out_path} ---")

