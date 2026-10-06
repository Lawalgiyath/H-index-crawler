"""
HYBRID GOOGLE SCHOLAR ID FINDER
================================
Uses ScraperAPI (free trial) to SEARCH for profiles
Then extracts user IDs without using Apify credits
"""
import json
import requests
from bs4 import BeautifulSoup
import urllib.parse
import time
import random

# Your ScraperAPI key (free 5000 requests)
SCRAPERAPI_KEY = "4052c653946f503496a6df02ed39f9d9"

def search_scholar_profile(api_key, name, affiliation="University of Lagos"):
    """
    Search Google Scholar and extract user ID
    Uses ScraperAPI to bypass blocks
    """
    # Build search URL
    query = f"{name} {affiliation}"
    encoded_query = urllib.parse.quote(query)
    search_url = f"https://scholar.google.com/citations?view_op=search_authors&mauthors={encoded_query}&hl=en"
    
    print(f"  Searching: {name}...", end=" ")
    
    # Request through ScraperAPI
    scraper_url = f"http://api.scraperapi.com?api_key={api_key}&url={search_url}"
    
    try:
        response = requests.get(scraper_url, timeout=60)
        
        if response.status_code != 200:
            print(f"❌ Status {response.status_code}")
            return None, None, None
        
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        
        # Find first profile result
        # Google Scholar author search results have class "gs_ai_t"
        profile_link = soup.select_one(".gsc_1usr a")
        
        if not profile_link:
            # Try alternate selector
            profile_link = soup.select_one("a[href*='user=']")
        
        if not profile_link:
            print("❌ No profile found")
            return None, None, None
        
        # Extract user ID from href
        href = profile_link.get("href", "")
        parsed = urllib.parse.urlparse(href)
        params = urllib.parse.parse_qs(parsed.query)
        
        if "user" not in params:
            print("❌ No user ID in link")
            return None, None, None
        
        user_id = params["user"][0]
        
        # Get name and affiliation from result
        name_elem = soup.select_one(".gs_ai_name a")
        affil_elem = soup.select_one(".gs_ai_aff")
        
        found_name = name_elem.text.strip() if name_elem else name
        found_affil = affil_elem.text.strip() if affil_elem else ""
        
        # Check if Lagos/UNILAG is in affiliation
        is_lagos = False
        if found_affil:
            affil_lower = found_affil.lower()
            is_lagos = 'lagos' in affil_lower or 'unilag' in affil_lower
        
        confidence = "HIGH" if is_lagos else "MEDIUM"
        
        print(f"✓ {confidence} ({user_id})")
        
        return user_id, found_name, found_affil
    
    except Exception as e:
        print(f"❌ Error: {str(e)[:50]}")
        return None, None, None

def main():
    print("=" * 80)
    print("HYBRID GOOGLE SCHOLAR ID FINDER")
    print("=" * 80)
    print("Uses: ScraperAPI (free 5000 requests) to find profile IDs")
    print("Cost: ~27 requests = FREE (uses your ScraperAPI trial)")
    print("=" * 80)
    
    input("\nPress Enter to start...")
    print()
    
    # Load staff names
    with open('chemistry_staff_cleaned.json', 'r', encoding='utf-8') as f:
        staff_list = json.load(f)
    
    print(f"Total staff to search: {len(staff_list)}\n")
    
    # Already confirmed IDs (don't search these)
    confirmed = {
        "Lawrence Ekebafe": "s9d437QAAAAJ",
        "Wesley Okiei": "tQgb_bgAAAAJ"
    }
    
    results = []
    found_count = 0
    
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
                "confidence": "CONFIRMED",
                "profile_url": f"https://scholar.google.com/citations?user={user_id}&hl=en",
                "status": "confirmed"
            })
            found_count += 1
        else:
            # Search for profile
            user_id, matched_name, affiliation = search_scholar_profile(SCRAPERAPI_KEY, name)
            
            if user_id:
                # Determine confidence
                confidence = "HIGH"
                if affiliation:
                    affil_lower = affiliation.lower()
                    if 'lagos' not in affil_lower and 'unilag' not in affil_lower:
                        confidence = "MEDIUM"
                
                results.append({
                    "name": name,
                    "user_id": user_id,
                    "matched_name": matched_name or name,
                    "affiliation": affiliation or "Unknown",
                    "confidence": confidence,
                    "profile_url": f"https://scholar.google.com/citations?user={user_id}&hl=en",
                    "status": "found"
                })
                found_count += 1
                
                # Show match details if different
                if matched_name and matched_name != name:
                    print(f"    Matched to: {matched_name}")
                if affiliation:
                    print(f"    Affiliation: {affiliation[:60]}")
            else:
                print(f"    ⚠️  Profile not found")
                results.append({
                    "name": name,
                    "user_id": None,
                    "matched_name": None,
                    "affiliation": None,
                    "confidence": "NOT_FOUND",
                    "profile_url": None,
                    "status": "not_found"
                })
        
        print()
        
        # Delay between requests (be nice to ScraperAPI)
        if i < len(staff_list):
            delay = random.uniform(1.5, 3)
            time.sleep(delay)
    
    # Save results
    with open('scholar_ids_found.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print("=" * 80)
    print("SEARCH COMPLETE!")
    print("=" * 80)
    
    # Summary
    high_conf = [r for r in results if r['confidence'] in ['CONFIRMED', 'HIGH']]
    medium_conf = [r for r in results if r['confidence'] == 'MEDIUM']
    not_found = [r for r in results if r['status'] == 'not_found']
    
    print(f"\nResults:")
    print(f"  ✓ Found: {found_count}/{len(staff_list)}")
    print(f"    - High confidence: {len(high_conf)}")
    print(f"    - Medium confidence: {len(medium_conf)}")
    print(f"  ✗ Not found: {len(not_found)}")
    
    if not_found:
        print(f"\n  Staff not found:")
        for r in not_found:
            print(f"    - {r['name']}")
    
    if medium_conf:
        print(f"\n  ⚠️  Medium confidence (verify affiliation):")
        for r in medium_conf:
            print(f"    - {r['name']} → {r['matched_name']}")
            print(f"      Affiliation: {r['affiliation']}")
            print(f"      URL: {r['profile_url']}")
    
    print(f"\nResults saved to: scholar_ids_found.json")
    
    # Create ready-to-scrape list (high confidence only)
    ready_to_scrape = [r for r in results if r['user_id'] and r['confidence'] in ['CONFIRMED', 'HIGH']]
    
    with open('scholar_ids_ready_to_scrape.json', 'w', encoding='utf-8') as f:
        json.dump(ready_to_scrape, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ {len(ready_to_scrape)} profiles ready for scraping")
    print(f"  Saved to: scholar_ids_ready_to_scrape.json")
    
    print("\n" + "=" * 80)
    print("NEXT STEP:")
    print("=" * 80)
    print("Run: python apify_scholar_final.py")
    print("(It will use the IDs from scholar_ids_ready_to_scrape.json)")
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
