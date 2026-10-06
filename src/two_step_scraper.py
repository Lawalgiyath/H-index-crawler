import json
import time
import pandas as pd
from apify_client import ApifyClient

APIFY_TOKEN = 'YOUR_APIFY_TOKEN'

print('--- Starting Two-Step Smart Scraper ---')

names_to_test = [
    "Modupe Ogunlesi",
    "Luqman Adams",
    "Rose Alani" # testing a known one that failed in SERP
]

client = ApifyClient(APIFY_TOKEN)
results = []

for name in names_to_test:
    print(f"\n[{name}] STEP 1: Searching SERP for Candidates...")
    
    # 1. Search for candidates
    search_input = {
        "queries": [f"{name} University of Lagos"],
        "maxItems": 3 # get the top 3 potential candidates
    }
    
    try:
        search_run = client.actor('blackfalcondata/google-scholar-scraper').call(run_input=search_input)
        candidates = list(client.dataset(search_run.default_dataset_id).iterate_items())
        
        candidate_ids = [c.get('userId') for c in candidates if c.get('userId')]
        
        if not candidate_ids:
            print(f"[{name}] No candidates found in search.")
            continue
            
        print(f"[{name}] Found {len(candidate_ids)} candidates. STEP 2: Deep-diving into their full profiles...")
        
        # 2. Fetch the FULL profiles for these candidates
        profile_urls = [f"https://scholar.google.com/citations?user={uid}&hl=en" for uid in candidate_ids]
        profile_input = {
            "startUrls": profile_urls,
            "maxItems": len(profile_urls)
        }
        
        profile_run = client.actor('blackfalcondata/google-scholar-scraper').call(run_input=profile_input)
        profiles = list(client.dataset(profile_run.default_dataset_id).iterate_items())
        
        # 3. Apply the strict Unilag verification!
        best_match = None
        for prof in profiles:
            verified_domain = prof.get("verifiedEmailDomain", "")
            prof_name = prof.get("name", "")
            
            # The ultimate check: Is it officially verified by UNILAG?
            if "unilag.edu.ng" in verified_domain:
                print(f"  -> [BINGO!] Found UNILAG Verified Profile: {prof_name}")
                best_match = prof
                break # We found the verified academic, stop looking!
            else:
                print(f"  -> [REJECTED] {prof_name} is verified at '{verified_domain}' (Not UNILAG).")
                
        if best_match:
            record = {
                "Target": name,
                "Matched_As": best_match.get("name"),
                "Verified_Domain": best_match.get("verifiedEmailDomain"),
                "Citations": best_match.get("citations", best_match.get("publicationCount", "0")), # Fallback if citations field varies
                "Link": f"https://scholar.google.com/citations?user={best_match.get('userId')}"
            }
            results.append(record)
        else:
            print(f"[{name}] None of the candidates were verified at UNILAG.")
            
    except Exception as e:
        print(f"Error processing {name}: {e}")

print("\n--- FINAL RESULTS ---")
print(pd.DataFrame(results).to_string(index=False))

