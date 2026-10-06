"""
FIND GOOGLE SCHOLAR IDs FOR STAFF
==================================
Uses Apify to search for each staff member by name
Returns candidate profiles for manual verification
"""
import json
from apify_client import ApifyClient

APIFY_TOKEN = "YOUR_APIFY_TOKEN"

def search_scholar_profile(api_token, name, affiliation="University of Lagos"):
    """Search for a scholar by name"""
    
    client = ApifyClient(api_token)
    
    # Search query: name + affiliation
    search_query = f"{name} {affiliation}"
    
    run_input = {
        "query": search_query,
        "maxResults": 5,  # Get top 5 matches
        "includeDetails": False,  # Faster, we just need basic info
        "compact": True
    }
    
    print(f"Searching: {search_query}...")
    
    try:
        # Run the actor
        run = client.actor("blackfalcondata/google-scholar-scraper").call(run_input=run_input)
        
        # Fetch results
        results = []
        for item in client.dataset(run.default_dataset_id).iterate_items():
            results.append(item)
        
        return results
    
    except Exception as e:
        print(f"  ERROR: {e}")
        return []

def main():
    print("FINDING GOOGLE SCHOLAR IDs")
    print("=" * 70)
    
    # Load staff names
    with open('chemistry_staff_cleaned.json', 'r', encoding='utf-8') as f:
        staff_list = json.load(f)
    
    print(f"Total staff: {len(staff_list)}\n")
    
    # Already confirmed IDs
    confirmed = {
        "Lawrence Ekebafe": "s9d437QAAAAJ",
        "Wesley Okiei": "tQgb_bgAAAAJ"
    }
    
    results_map = {}
    
    for i, staff in enumerate(staff_list, 1):
        name = staff['name']
        
        print(f"\n[{i}/{len(staff_list)}] {name}")
        print("-" * 70)
        
        # Check if already confirmed
        if name in confirmed:
            print(f"  ✓ Already confirmed: {confirmed[name]}")
            results_map[name] = {
                "user_id": confirmed[name],
                "status": "confirmed"
            }
            continue
        
        # Search for profile
        candidates = search_scholar_profile(APIFY_TOKEN, name)
        
        if not candidates:
            print("  ✗ No profiles found")
            results_map[name] = {
                "user_id": None,
                "status": "not_found",
                "candidates": []
            }
        else:
            print(f"  Found {len(candidates)} candidate(s):")
            candidate_info = []
            
            for j, candidate in enumerate(candidates, 1):
                user_id = candidate.get('userId', 'N/A')
                cand_name = candidate.get('name', 'N/A')
                affiliation = candidate.get('affiliation', 'N/A')
                citations = candidate.get('citations', 0)
                
                print(f"    {j}. {cand_name}")
                print(f"       ID: {user_id}")
                print(f"       Affiliation: {affiliation}")
                print(f"       Citations: {citations}")
                
                candidate_info.append({
                    "userId": user_id,
                    "name": cand_name,
                    "affiliation": affiliation,
                    "citations": citations
                })
            
            results_map[name] = {
                "user_id": None,  # To be manually verified
                "status": "needs_verification",
                "candidates": candidate_info
            }
    
    # Save results for manual verification
    with open('scholar_id_candidates.json', 'w', encoding='utf-8') as f:
        json.dump(results_map, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 70)
    print("SEARCH COMPLETE")
    print("=" * 70)
    print(f"Results saved to: scholar_id_candidates.json")
    print("\nNext steps:")
    print("1. Review scholar_id_candidates.json")
    print("2. Manually verify each candidate")
    print("3. Update the 'user_id' field with the correct ID")
    print("4. Set 'status' to 'confirmed' for verified profiles")
    print("=" * 70)
    
    # Summary
    confirmed_count = sum(1 for v in results_map.values() if v['status'] == 'confirmed')
    needs_verification = sum(1 for v in results_map.values() if v['status'] == 'needs_verification')
    not_found = sum(1 for v in results_map.values() if v['status'] == 'not_found')
    
    print(f"\nSummary:")
    print(f"  Confirmed: {confirmed_count}")
    print(f"  Needs verification: {needs_verification}")
    print(f"  Not found: {not_found}")
    print(f"  Total: {len(staff_list)}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nStopped by user")
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()

