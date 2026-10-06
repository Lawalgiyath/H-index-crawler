import json
import time
import pandas as pd
from apify_client import ApifyClient

APIFY_TOKEN = 'YOUR_APIFY_TOKEN'

def calculate_match_score(target_name, profile_name, email_info, affiliation):
    """
    Calculates a match score based on the user's advanced matching criteria:
    - MUST have unilag.edu.ng in email/affiliation (Score +100 to prioritize)
    - +10 points for each matching name part (First name, Last name)
    """
    score = 0
    
    # Check unilag.edu.ng criteria
    email_info = str(email_info).lower()
    affiliation = str(affiliation).lower()
    has_unilag = "unilag.edu.ng" in email_info or "unilag.edu.ng" in affiliation
    
    if not has_unilag:
        return 0 # Discard entirely if not verified with UNILAG
        
    score += 100 # Base score for having the UNILAG verification
    
    # Split target name into parts (e.g., ["Modupe", "Ogunlesi"])
    target_parts = [p.lower().strip() for p in target_name.split() if len(p) > 2]
    profile_name_lower = str(profile_name).lower()
    
    # Prioritize based on how many names match
    matches = 0
    for part in target_parts:
        if part in profile_name_lower:
            matches += 1
            score += 10
            
    if matches == 0:
        return 0 # Discard if no names match at all
        
    return score

print('--- Starting Advanced Smart Matching Scraper ---')

names_to_test = [
    "Modupe Ogunlesi",
    "Luqman Adams",
    "Idris Olasupo",
    "Khadijah Abdulwahab",
    "Oluwabusayo Semire"
]

client = ApifyClient(APIFY_TOKEN)
results = []

for name in names_to_test:
    print(f"\nSearching for: {name}")
    # Tell Apify to grab up to 20 items per query
    run_input = {
        "queries": [f"{name} University of Lagos"],
        "maxItems": 20
    }
    
    try:
        run = client.actor('blackfalcondata/google-scholar-scraper').call(run_input=run_input)
        dataset = list(client.dataset(run.default_dataset_id).iterate_items())
        
        best_match = None
        best_score = 0
        
        # Scheme through the first 20 profile results
        print(f"  -> Found {len(dataset)} potential profiles in SERP.")
        for res in dataset:
            prof_name = res.get("name", "Unknown")
            email = res.get("email", "")
            affil = res.get("affiliation", "")
            
            score = calculate_match_score(name, prof_name, email, affil)
            if score > 0:
                print(f"  -> [VALID] '{prof_name}' matches criteria (Score: {score})")
            
            if score > best_score:
                best_score = score
                best_match = res
                
        if best_match:
            record = {
                "Target": name,
                "Matched_As": best_match.get("name"),
                "Score": best_score,
                "Citations": best_match.get("citations"),
                "H_Index": best_match.get("hIndex"),
                "Link": f"https://scholar.google.com/citations?user={best_match.get('userId')}"
            }
            print(f"  => WINNER: {record['Matched_As']} (H-Index: {record['H_Index']})")
        else:
            record = {
                "Target": name,
                "Matched_As": "N/A",
                "Score": 0,
                "Citations": "N/A",
                "H_Index": "N/A",
                "Link": "N/A"
            }
            print(f"  => NO VALID MATCH FOUND.")
            
        results.append(record)
        
    except Exception as e:
        print(f"Error processing {name}: {e}")

df = pd.DataFrame(results)
print("\n--- FINAL RESULTS ---")
print(df.to_string(index=False))

