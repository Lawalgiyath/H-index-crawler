"""
AUTOMATIC GOOGLE SCHOLAR ID FINDER
===================================
Searches for each staff member and automatically extracts their Scholar ID
Uses fuzzy matching to find the best profile match
"""
import json
from apify_client import ApifyClient
from difflib import SequenceMatcher
import time

APIFY_TOKEN = "YOUR_APIFY_TOKEN"

def similarity(a, b):
    """Calculate similarity ratio between two strings"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def find_scholar_id(api_token, name, department="University of Lagos"):
    """
    Search for a scholar and return their user ID
    Returns: (user_id, confidence, matched_name, affiliation)
    """
    
    client = ApifyClient(api_token)
    
    # Search query - just the name and university
    search_query = f"{name} {department}"
    
    run_input = {
        "query": search_query,
        "maxResults": 5,  # Get top 5 to find best match
        "includeDetails": False,
        "compact": True
    }
    
    print(f"  Searching: '{search_query}'...", end=" ")
    
    try:
        # Run the actor
        run = client.actor("blackfalcondata/google-scholar-scraper").call(run_input=run_input)
        
        # Fetch results
        results = []
        for item in client.dataset(run.default_dataset_id).iterate_items():
            results.append(item)
        
        if not results:
            print("❌ No results")
            return None, 0, None, None
        
        # Find best match by name similarity
        best_match = None
        best_score = 0
        
        for result in results:
            result_name = result.get('name', '')
            result_affiliation = result.get('affiliation', '')
            result_user_id = result.get('userId', '')
            
            # Calculate similarity score
            name_sim = similarity(name, result_name)
            
            # Bonus points if "Lagos" or "UNILAG" in affiliation
            affiliation_bonus = 0
            if result_affiliation:
                affiliation_lower = result_affiliation.lower()
                if 'lagos' in affiliation_lower or 'unilag' in affiliation_lower:
                    affiliation_bonus = 0.2
            
            total_score = name_sim + affiliation_bonus
            
            if total_score > best_score and result_user_id:
                best_score = total_score
                best_match = {
                    'userId': result_user_id,
                    'name': result_name,
                    'affiliation': result_affiliation,
                    'citations': result.get('citations', 0),
                    'score': total_score
                }
        
        if best_match:
            confidence = "HIGH" if best_score >= 0.8 else "MEDIUM" if best_score >= 0.6 else "LOW"
            print(f"✓ {confidence} ({best_score:.2f})")
            return best_match['userId'], best_score, best_match['name'], best_match['affiliation']
        else:
            print("❌ No valid match")
            return None, 0, None, None
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, 0, None, None

def main():
    print("=" * 80)
    print("AUTOMATIC GOOGLE SCHOLAR ID FINDER")
    print("=" * 80)
    print("This will search for each staff member and find their Scholar profile")
    print("Cost: ~$0.10-0.15 for 27 staff (searching 5 results per person)")
    print("=" * 80)
    
    input("\nPress Enter to start...")
    print()
    
    # Load staff names
    with open('chemistry_staff_cleaned.json', 'r', encoding='utf-8') as f:
        staff_list = json.load(f)
    
    print(f"Total staff to search: {len(staff_list)}\n")
    
    # Already confirmed (to avoid re-searching)
    confirmed = {
        "Lawrence Ekebafe": "s9d437QAAAAJ",
        "Wesley Okiei": "tQgb_bgAAAAJ"
    }
    
    results = []
    
    for i, staff in enumerate(staff_list, 1):
        name = staff['name']
        
        print(f"[{i}/{len(staff_list)}] {name}")
        
        # Check if already confirmed
        if name in confirmed:
            user_id = confirmed[name]
            print(f"  ✓ Already confirmed: {user_id}")
            results.append({
                "name": name,
                "user_id": user_id,
                "matched_name": name,
                "affiliation": "University of Lagos",
                "confidence": 1.0,
                "confidence_level": "CONFIRMED",
                "profile_url": f"https://scholar.google.com/citations?user={user_id}&hl=en",
                "status": "confirmed"
            })
        else:
            # Search for profile
            user_id, score, matched_name, affiliation = find_scholar_id(APIFY_TOKEN, name)
            
            if user_id:
                confidence_level = "HIGH" if score >= 0.8 else "MEDIUM" if score >= 0.6 else "LOW"
                
                result = {
                    "name": name,
                    "user_id": user_id,
                    "matched_name": matched_name,
                    "affiliation": affiliation,
                    "confidence": round(score, 3),
                    "confidence_level": confidence_level,
                    "profile_url": f"https://scholar.google.com/citations?user={user_id}&hl=en",
                    "status": "found"
                }
                
                results.append(result)
                
                # Show details
                if matched_name != name:
                    print(f"    Matched: {matched_name}")
                if affiliation:
                    print(f"    Affiliation: {affiliation}")
            else:
                print(f"    ⚠️  No profile found")
                results.append({
                    "name": name,
                    "user_id": None,
                    "matched_name": None,
                    "affiliation": None,
                    "confidence": 0,
                    "confidence_level": "NOT_FOUND",
                    "profile_url": None,
                    "status": "not_found"
                })
        
        print()
        
        # Small delay to avoid overwhelming the API
        if i < len(staff_list):
            time.sleep(0.5)
    
    # Save results
    with open('scholar_ids_found.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print("=" * 80)
    print("SEARCH COMPLETE!")
    print("=" * 80)
    
    # Summary
    found = [r for r in results if r['user_id']]
    high_conf = [r for r in results if r['confidence_level'] in ['CONFIRMED', 'HIGH']]
    medium_conf = [r for r in results if r['confidence_level'] == 'MEDIUM']
    low_conf = [r for r in results if r['confidence_level'] == 'LOW']
    not_found = [r for r in results if not r['user_id']]
    
    print(f"\nSummary:")
    print(f"  ✓ Found: {len(found)}/{len(staff_list)}")
    print(f"    - High confidence: {len(high_conf)}")
    print(f"    - Medium confidence: {len(medium_conf)}")
    print(f"    - Low confidence: {len(low_conf)}")
    print(f"  ✗ Not found: {len(not_found)}")
    
    if not_found:
        print(f"\n  Staff not found:")
        for r in not_found:
            print(f"    - {r['name']}")
    
    print(f"\nResults saved to: scholar_ids_found.json")
    
    if medium_conf or low_conf:
        print("\n⚠️  WARNING: Some matches have medium/low confidence.")
        print("   Review scholar_ids_found.json and verify these profiles manually:")
        for r in medium_conf + low_conf:
            print(f"   - {r['name']} → {r['matched_name']} ({r['confidence_level']})")
            print(f"     {r['profile_url']}")
    
    # Create the final list for scraping (only high confidence)
    scrape_ready = [r for r in results if r['user_id'] and r['confidence_level'] in ['CONFIRMED', 'HIGH']]
    
    with open('scholar_ids_ready_to_scrape.json', 'w', encoding='utf-8') as f:
        json.dump(scrape_ready, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ {len(scrape_ready)} profiles ready for scraping")
    print(f"  Saved to: scholar_ids_ready_to_scrape.json")
    print("\nNext step: Run scrape_all_staff.py to get their metrics!")
    print("=" * 80)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nStopped by user")
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()

