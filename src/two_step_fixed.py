import json
import time
import pandas as pd
from apify_client import ApifyClient

APIFY_TOKEN = 'YOUR_APIFY_TOKEN'

def calculate_match_score(target_name, profile_name):
    score = 0
    target_parts = [p.lower().strip() for p in target_name.split() if len(p) > 2]
    profile_name_lower = str(profile_name).lower()
    for part in target_parts:
        if part in profile_name_lower:
            score += 10
    return score

client = ApifyClient(APIFY_TOKEN)

name = "Luqman Adams"
print(f"\n[{name}] STEP 1: Searching SERP for Candidates...")

search_input = {
    "queries": [f"{name} University of Lagos"],
    "maxItems": 10
}

search_run = client.actor('blackfalcondata/google-scholar-scraper').call(run_input=search_input)
candidates = list(client.dataset(search_run.default_dataset_id).iterate_items())
candidate_ids = [c.get('userId') for c in candidates if c.get('userId')]

print(f"[{name}] Found {len(candidate_ids)} candidates. STEP 2: Deep-diving into their full profiles...")

profile_urls = [f"https://scholar.google.com/citations?user={uid}&hl=en" for uid in candidate_ids]
profile_input = {
    "startUrls": profile_urls,
    "maxItems": len(profile_urls)
}

profile_run = client.actor('blackfalcondata/google-scholar-scraper').call(run_input=profile_input)
profiles = list(client.dataset(profile_run.default_dataset_id).iterate_items())

best_match = None
best_score = 0

for prof in profiles:
    verified_domain = prof.get("verifiedEmailDomain", "")
    prof_name = prof.get("name", "")
    
    if "unilag.edu.ng" in verified_domain:
        score = calculate_match_score(name, prof_name)
        if score > 0:
            print(f"  -> [VALIDATED!] {prof_name} has UNILAG email AND name matches (Score: {score})")
            if score > best_score:
                best_score = score
                best_match = prof
        else:
            print(f"  -> [REJECTED] {prof_name} has UNILAG email, but name doesn't match '{name}'.")
    else:
        print(f"  -> [REJECTED] {prof_name} is not verified at UNILAG.")

if best_match:
    print(f"\n => FINAL WINNER: {best_match.get('name')} (H-Index: {best_match.get('hIndex')}, Citations: {best_match.get('citations')})")

