import json
import time
import pandas as pd
from apify_client import ApifyClient

APIFY_TOKEN = 'YOUR_APIFY_TOKEN'

def calculate_match_score(target_name, profile_name):
    """
    Score the profile: +10 points for each matching name part
    """
    score = 0
    target_parts = [p.lower().strip() for p in target_name.split() if len(p) > 2]
    profile_name_lower = str(profile_name).lower()
    
    for part in target_parts:
        if part in profile_name_lower:
            score += 10
            
    return score

print('--- Starting Ultimate Two-Step Architecture ---')

with open('data/outputs/chemistry_staff_cleaned.json', 'r') as f:
    staff_base = json.load(f)

client = ApifyClient(APIFY_TOKEN)
results = []

for i, person in enumerate(staff_base):
    name = person["name"]
    print(f"\n[{i+1}/27] Searching for: {name}")
    
    # 1. SERP Search
    search_input = {
        "queries": [f"{name} University of Lagos"],
        "maxItems": 10
    }
    
    try:
        search_run = client.actor('blackfalcondata/google-scholar-scraper').call(run_input=search_input)
        candidates = list(client.dataset(search_run.default_dataset_id).iterate_items())
        
        candidate_ids = [c.get('userId') for c in candidates if c.get('userId')]
        
        if not candidate_ids:
            print(f"  -> No candidates found in SERP.")
            record = {
                "Target": name, "Matched_As": "N/A", "Verified_Domain": "N/A",
                "Citations": "N/A", "H_Index": "N/A", "I10_Index": "N/A", "Link": "N/A"
            }
            results.append(record)
            continue
            
        print(f"  -> Found {len(candidate_ids)} candidates. Fetching full profiles...")
        
        # 2. Deep Dive Profile Scraping
        profile_urls = [f"https://scholar.google.com/citations?user={uid}&hl=en" for uid in candidate_ids]
        profile_input = {
            "startUrls": profile_urls,
            "maxItems": len(profile_urls)
        }
        
        profile_run = client.actor('blackfalcondata/google-scholar-scraper').call(run_input=profile_input)
        profiles = list(client.dataset(profile_run.default_dataset_id).iterate_items())
        
        best_match = None
        best_score = 0
        
        # 3. Smart Validation
        for prof in profiles:
            verified_domain = prof.get("verifiedEmailDomain", "")
            prof_name = prof.get("name", "")
            
            # Allow unilag.edu.ng OR lagos in affiliation if verification is somehow hidden
            # But heavily prioritize explicit UNILAG email verification
            is_verified = "unilag.edu.ng" in verified_domain
            
            if is_verified:
                score = calculate_match_score(name, prof_name)
                if score > 0:
                    if score > best_score:
                        best_score = score
                        best_match = prof
        
        if best_match:
            record = {
                "Target": name,
                "Matched_As": best_match.get("name"),
                "Verified_Domain": best_match.get("verifiedEmailDomain", "unilag.edu.ng"),
                "Citations": best_match.get("citations", "0"),
                "H_Index": best_match.get("hIndex", "0"),
                "I10_Index": best_match.get("i10Index", "0"),
                "Link": f"https://scholar.google.com/citations?user={best_match.get('userId')}"
            }
            print(f"  => SUCCESS: {record['Matched_As']} (H-Index: {record['H_Index']})")
        else:
            record = {
                "Target": name, "Matched_As": "N/A", "Verified_Domain": "N/A",
                "Citations": "N/A", "H_Index": "N/A", "I10_Index": "N/A", "Link": "N/A"
            }
            print(f"  => NO VALID MATCH FOUND (No Unilag match found).")
            
        results.append(record)
        
    except Exception as e:
        print(f"Error processing {name}: {e}")

df = pd.DataFrame(results)
out_path = 'data/outputs/chemistry_scholar_metrics_ULTIMATE.csv'
df.to_csv(out_path, index=False)
print(f"\n--- SUCCESS! Saved to {out_path} ---")

