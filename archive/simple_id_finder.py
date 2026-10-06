"""
SIMPLE GOOGLE SCHOLAR ID FINDER
================================
Uses basic requests + rotating user agents
Just searches and extracts user IDs
Free and simple!
"""
import json
import requests
from bs4 import BeautifulSoup
import urllib.parse
import time
import random

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
]

def search_scholar_profile(name, affiliation="University of Lagos"):
    """
    Search Google Scholar and extract user ID
    Simple approach - no API needed
    """
    # Build search URL
    query = f"{name} {affiliation}"
    encoded_query = urllib.parse.quote(query)
    search_url = f"https://scholar.google.com/citations?view_op=search_authors&mauthors={encoded_query}&hl=en"
    
    print(f"  Searching...", end=" ")
    
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    try:
        response = requests.get(search_url, headers=headers, timeout=30)
        
        if response.status_code == 429:
            print("❌ Rate limited (wait longer)")
            return None, None, None, "rate_limited"
        
        if response.status_code != 200:
            print(f"❌ Status {response.status_code}")
            return None, None, None, "error"
        
        html = response.text
        
        # Check for CAPTCHA
        if 'captcha' in html.lower() or 'unusual traffic' in html.lower():
            print("❌ CAPTCHA detected")
            return None, None, None, "captcha"
        
        soup = BeautifulSoup(html, "html.parser")
        
        # Find first profile result
        # Method 1: Modern layout
        profile_div = soup.select_one(".gsc_1usr")
        
        if not profile_div:
            print("❌ No results found")
            return None, None, None, "not_found"
        
        # Get the profile link
        profile_link = profile_div.select_one("a[href*='user=']")
        
        if not profile_link:
            print("❌ No user link")
            return None, None, None, "no_link"
        
        # Extract user ID
        href = profile_link.get("href", "")
        parsed = urllib.parse.urlparse(href)
        params = urllib.parse.parse_qs(parsed.query)
        
        if "user" not in params:
            print("❌ No user ID")
            return None, None, None, "no_id"
        
        user_id = params["user"][0]
        
        # Get name and affiliation
        name_elem = profile_div.select_one(".gs_ai_name a")
        affil_elem = profile_div.select_one(".gs_ai_aff")
        
        found_name = name_elem.text.strip() if name_elem else name
        found_affil = affil_elem.text.strip() if affil_elem else ""
        
        # Check confidence
        confidence = "MEDIUM"
        if found_affil:
            affil_lower = found_affil.lower()
            if 'lagos' in affil_lower or 'unilag' in affil_lower:
                confidence = "HIGH"
        
        print(f"✓ {user_id} ({confidence})")
        
        return user_id, found_name, found_affil, "success"
    
    except Exception as e:
        print(f"❌ Error: {str(e)[:40]}")
        return None, None, None, "exception"

def main():
    print("=" * 80)
    print("SIMPLE GOOGLE SCHOLAR ID FINDER")
    print("=" * 80)
    print("Direct search - NO API needed")
    print("Note: May hit rate limits - will pause if needed")
    print("=" * 80)
    
    input("\nPress Enter to start...")
    print()
    
    # Load staff names
    with open('chemistry_staff_cleaned.json', 'r', encoding='utf-8') as f:
        staff_list = json.load(f)
    
    print(f"Total staff to search: {len(staff_list)}\n")
    
    # Already confirmed
    confirmed = {
        "Lawrence Ekebafe": "s9d437QAAAAJ",
        "Wesley Okiei": "tQgb_bgAAAAJ"
    }
    
    results = []
    found_count = 0
    captcha_count = 0
    
    for i, staff in enumerate(staff_list, 1):
        name = staff['name']
        
        print(f"[{i}/{len(staff_list)}] {name}")
        
        # Check if already confirmed
        if name in confirmed:
            user_id = confirmed[name]
            print(f"  ✓ Confirmed: {user_id}")
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
            # Search
            user_id, matched_name, affiliation, status = search_scholar_profile(name)
            
            if status == "success" and user_id:
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
                
                if matched_name and matched_name != name:
                    print(f"    → {matched_name}")
                if affiliation:
                    print(f"    {affiliation[:70]}")
            
            elif status == "captcha":
                captcha_count += 1
                print(f"    ⚠️  CAPTCHA detected - stopping to avoid ban")
                print(f"\n    Found {found_count}/{i} so far")
                print(f"    Remaining: {len(staff_list) - i}")
                
                # Save partial results
                partial = {
                    "name": name,
                    "user_id": None,
                    "status": "interrupted_by_captcha"
                }
                results.append(partial)
                
                # Stop here
                break
            
            elif status == "rate_limited":
                print(f"    Pausing for 60 seconds...")
                time.sleep(60)
                # Retry once
                user_id, matched_name, affiliation, status = search_scholar_profile(name)
                if status == "success" and user_id:
                    results.append({
                        "name": name,
                        "user_id": user_id,
                        "matched_name": matched_name or name,
                        "affiliation": affiliation or "Unknown",
                        "confidence": "MEDIUM",
                        "profile_url": f"https://scholar.google.com/citations?user={user_id}&hl=en",
                        "status": "found"
                    })
                    found_count += 1
                else:
                    results.append({
                        "name": name,
                        "user_id": None,
                        "status": "failed_after_retry"
                    })
            
            else:
                results.append({
                    "name": name,
                    "user_id": None,
                    "matched_name": None,
                    "affiliation": None,
                    "confidence": "NOT_FOUND",
                    "profile_url": None,
                    "status": status
                })
        
        print()
        
        # Random delay (important!)
        if i < len(staff_list) and captcha_count == 0:
            delay = random.uniform(5, 10)  # Longer delays
            print(f"  [Waiting {delay:.1f}s...]\n")
            time.sleep(delay)
    
    # Save results
    with open('scholar_ids_found.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print("=" * 80)
    print("SEARCH COMPLETE" if captcha_count == 0 else "SEARCH INTERRUPTED")
    print("=" * 80)
    
    # Summary
    high_conf = [r for r in results if r.get('confidence') in ['CONFIRMED', 'HIGH']]
    medium_conf = [r for r in results if r.get('confidence') == 'MEDIUM']
    not_found = [r for r in results if r.get('status') in ['not_found', 'failed_after_retry', 'no_link', 'no_id']]
    
    print(f"\nResults:")
    print(f"  ✓ Found: {found_count}/{len(results)}")
    print(f"    - High confidence: {len(high_conf)}")
    print(f"    - Medium confidence: {len(medium_conf)}")
    print(f"  ✗ Not found: {len(not_found)}")
    
    if captcha_count > 0:
        print(f"\n  ⚠️  Hit CAPTCHA - could not complete all searches")
        print(f"     Options:")
        print(f"     1. Wait 1 hour and run again (it will skip already found)")
        print(f"     2. Use the HTML tool (find_scholar_ids.html)")
        print(f"     3. Manually search remaining profiles")
    
    print(f"\nResults saved to: scholar_ids_found.json")
    
    # Create ready-to-scrape list
    ready = [r for r in results if r.get('user_id') and r.get('confidence') in ['CONFIRMED', 'HIGH']]
    
    with open('scholar_ids_ready_to_scrape.json', 'w', encoding='utf-8') as f:
        json.dump(ready, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ {len(ready)} profiles ready for Apify scraping")
    print(f"  Cost: ${len(ready) * 0.0009:.3f}")
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
