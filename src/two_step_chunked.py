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

def chunk_list(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

print('--- Starting Chunked Two-Step Architecture (No Cheating!) ---')

with open('data/outputs/chemistry_staff_cleaned.json', 'r') as f:
    staff_base = json.load(f)

client = ApifyClient(APIFY_TOKEN)
results = []

# Process in chunks of 5 names to bypass Apify's truncation limits
chunks = list(chunk_list(staff_base, 5))
print(f"Total names to process: {len(staff_base)}")
print(f"Divided into {len(chunks)} batches of 5 to avoid data truncation.\n")

for batch_idx, batch in enumerate(chunks, 1):
    print(f"=== Processing Batch {batch_idx}/{len(chunks)} ===")
    
    # STEP 1: SERP searches for this batch
    queries = [f"{person['name']} University of Lagos" for person in batch]
    search_input = {
        "queries": queries,
        "maxItems": len(queries) * 10 # Request 10 candidates per name in this batch
    }
    
    print(f"  -> Fetching SERP candidates for {len(batch)} names...")
    try:
        search_run = client.actor('blackfalcondata/google-scholar-scraper').call(run_input=search_input)
        candidates = list(client.dataset(search_run.default_dataset_id).iterate_items())
        candidate_ids = list(set([c.get('userId') for c in candidates if c.get('userId')]))
        
        if not candidate_ids:
            print("  -> No candidates found in this batch.")
            for person in batch:
                results.append({
                    "Target": person['name'], "Matched_As": "N/A", "Verified_Domain": "N/A",
                    "Citations": "N/A", "H_Index": "N/A", "I10_Index": "N/A", "Link": "N/A"
                })
            continue
            
        print(f"  -> Found {len(candidate_ids)} unique candidates. Deep-diving into full profiles...")
        
        # STEP 2: Deep-dive into candidates
        profile_urls = [f"https://scholar.google.com/citations?user={uid}&hl=en" for uid in candidate_ids]
        profile_input = {
            "startUrls": profile_urls,
            "maxItems": len(profile_urls)
        }
        profile_run = client.actor('blackfalcondata/google-scholar-scraper').call(run_input=profile_input)
        profiles = list(client.dataset(profile_run.default_dataset_id).iterate_items())
        
        # STEP 3: Match the profiles back to the original names
        print("  -> Applying strict Unilag verification and Name Matching...")
        for person in batch:
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
                print(f"     [SUCCESS] {name} => {record['Matched_As']} (H-Index: {record['H_Index']})")
            else:
                record = {
                    "Target": name, "Matched_As": "N/A", "Verified_Domain": "N/A",
                    "Citations": "N/A", "H_Index": "N/A", "I10_Index": "N/A", "Link": "N/A"
                }
                print(f"     [NO MATCH] {name}")
                
            results.append(record)
            
    except Exception as e:
        print(f"  -> Error processing batch: {e}")
        for person in batch:
            results.append({
                "Target": person['name'], "Matched_As": "ERROR", "Verified_Domain": "ERROR",
                "Citations": "ERROR", "H_Index": "ERROR", "I10_Index": "ERROR", "Link": "ERROR"
            })
            
    # Sleep to respect rate limits between batches
    time.sleep(2)

df = pd.DataFrame(results)
out_path = 'data/outputs/chemistry_scholar_metrics_ULTIMATE.csv'
df.to_csv(out_path, index=False)
print(f"\n--- SUCCESS! Saved all to {out_path} ---")

