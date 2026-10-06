import json
import time
import pandas as pd
from apify_client import ApifyClient

APIFY_TOKEN = 'YOUR_APIFY_TOKEN'

def calculate_match_score(target_name, profile_name):
    score = 0
    target_parts = [p.lower().strip() for p in target_name.split() if len(p) > 2]
    profile_name_lower = str(profile_name).lower() if profile_name else ""
    for part in target_parts:
        if part in profile_name_lower:
            score += 10
    return score

print('--- Starting Batch Two-Step Architecture ---')

with open('data/outputs/chemistry_staff_cleaned.json', 'r') as f:
    staff_base = json.load(f)

client = ApifyClient(APIFY_TOKEN)
results = []

# STEP 1: Batch all SERP queries into a single API call to avoid rate limits
print("STEP 1: Batching SERP searches for all 27 names...")
queries = [f"{person['name']} University of Lagos" for person in staff_base]
search_input = {
    "queries": queries,
    "maxItems": len(queries) * 5 # Get a few candidates per query
}

search_run = client.actor('blackfalcondata/google-scholar-scraper').call(run_input=search_input)
candidates = list(client.dataset(search_run.default_dataset_id).iterate_items())
candidate_ids = list(set([c.get('userId') for c in candidates if c.get('userId')]))

print(f"-> Found {len(candidate_ids)} unique candidate profiles across all searches.")

# STEP 2: Batch all Profile queries into a single API call
print("\nSTEP 2: Deep-diving into all candidate profiles concurrently...")
profile_urls = [f"https://scholar.google.com/citations?user={uid}&hl=en" for uid in candidate_ids]
profile_input = {
    "startUrls": profile_urls,
    "maxItems": len(profile_urls)
}
profile_run = client.actor('blackfalcondata/google-scholar-scraper').call(run_input=profile_input)
profiles = list(client.dataset(profile_run.default_dataset_id).iterate_items())

# STEP 3: Match the profiles back to the original names
print("\nSTEP 3: Applying strict Unilag verification and Name Matching...")

for person in staff_base:
    name = person["name"]
    best_match = None
    best_score = 0
    
    for prof in profiles:
        verified_domain = prof.get("verifiedEmailDomain", "") or ""
        prof_name = prof.get("name", "") or ""
        
        if "unilag.edu.ng" in verified_domain.lower():
            score = calculate_match_score(name, prof_name)
            if score > 0 and score > best_score:
                best_score = score
                best_match = prof
                
    if best_match:
        record = {
            "Target": name,
            "Matched_As": best_match.get("name"),
            "Verified_Domain": best_match.get("verifiedEmailDomain"),
            "Citations": best_match.get("citations", "0"),
            "H_Index": best_match.get("hIndex", "0"),
            "I10_Index": best_match.get("i10Index", "0"),
            "Link": f"https://scholar.google.com/citations?user={best_match.get('userId')}"
        }
        print(f"  => SUCCESS [{name}]: {record['Matched_As']} (H-Index: {record['H_Index']})")
    else:
        record = {
            "Target": name, "Matched_As": "N/A", "Verified_Domain": "N/A",
            "Citations": "N/A", "H_Index": "N/A", "I10_Index": "N/A", "Link": "N/A"
        }
        print(f"  => NO MATCH [{name}]")
        
    results.append(record)

df = pd.DataFrame(results)
out_path = 'data/outputs/chemistry_scholar_metrics_ULTIMATE.csv'
df.to_csv(out_path, index=False)
print(f"\n--- SUCCESS! Saved to {out_path} ---")

