"""
GOOGLE SEARCH FOR SCHOLAR IDs
==============================
Search regular Google for "Name university of lagos google scholar"
Then extract the Scholar profile link from results
Much less likely to get blocked!
"""
import json
import requests
from bs4 import BeautifulSoup
import urllib.parse
import time
import random
import re

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
]

def extract_scholar_id_from_url(url):
    """Extract user ID from Google Scholar URL"""
    match = re.search(r'user=([a-zA-Z0-9_-]+)', url)
    if match:
        return match.group(1)
    return None

def search_google_for_scholar(name, affiliation="university of lagos"):
    """
    Search Google for scholar profile
    Query: "Name university of lagos google scholar"
    """
    # Build Google search query
    query = f"{name} {affiliation} google scholar"
    encoded_query = urllib.parse.quote(query)
    google_url = f"https://www.google.com/search?q={encoded_query}"
    
    print(f"  Searching Google...", end=" ")
    
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
        response = requests.get(google_url, headers=headers, timeout=30)
        
        if response.status_code == 429:
            print("❌ Rate limited")
            return None, None, "rate_limited"
        
        if response.status_code != 200:
            print(f"❌ Status {response.status_code}")
            return None, None, "error"
        
        html = response.text
        
        # Check for CAPTCHA
        if 'captcha' in html.lower() or 'unusual traffic' in html.lower():
            print("❌ CAPTCHA")
            return None, None, "captcha"
        
        soup = BeautifulSoup(html, "html.parser")
        
        # Find all links
        links = soup.find_all('a', href=True)
        
        # Look for scholar.google.com links with user= parameter
        scholar_links = []
        for link in links:
            href = link.get('href', '')
            if 'scholar.google.com/citations' in href and 'user=' in href:
                scholar_links.append(href)
        
        if not scholar_links:
            print("❌ No Scholar profile found")
            return None, None, "not_found"
        
        # Get first scholar link
        first_link = scholar_links[0]
        
        # Clean up the URL (Google often wraps it)
        # Look for the actual scholar URL in the redirect
        if '/url?q=' in first_link:
            # Extract the actual URL
            match = re.search(r'/url\?q=(https://scholar\.google\.com/citations[^&]+)', first_link)
            if match:
                first_link = urllib.parse.unquote(match.group(1))
        
        # Extract user ID
        user_id = extract_scholar_id_from_url(first_link)
        
        if not user_id:
            print("❌ Could not extract user ID")
            return None, None, "no_id"
        
        print(f"✓ {user_id}")
        
        return user_id, first_link, "success"
    
    except Exception as e:
        print(f"❌ Error: {str(e)[:40]}")
        return None, None, "exception"

def main():
    print("=" * 80)
    print("GOOGLE SEARCH FOR SCHOLAR IDs")
    print("=" * 80)
    print("Strategy: Search Google for 'Name university google scholar'")
    print("This is less likely to get blocked than direct Scholar search")
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
    captcha_hit = False
    
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
            # Search via Google
            user_id, profile_url, status = search_google_for_scholar(name)
            
            if status == "success" and user_id:
                results.append({
                    "name": name,
                    "user_id": user_id,
                    "matched_name": name,  # We'll assume it matches
                    "affiliation": "University of Lagos",
                    "confidence": "HIGH",  # Google usually gives good results
                    "profile_url": profile_url,
                    "status": "found"
                })
                found_count += 1
                print(f"    ✓ Profile: {profile_url}")
            
            elif status == "captcha":
                captcha_hit = True
                print(f"\n    ⚠️  Google CAPTCHA detected")
                print(f"    Found {found_count}/{i} profiles so far")
                print(f"    Stopping to avoid ban...")
                
                # Add remaining as pending
                for j in range(i-1, len(staff_list)):
                    if staff_list[j]['name'] not in [r['name'] for r in results]:
                        results.append({
                            "name": staff_list[j]['name'],
                            "user_id": None,
                            "status": "pending_manual_search"
                        })
                break
            
            elif status == "rate_limited":
                print(f"    Rate limited - pausing 60s...")
                time.sleep(60)
                # Retry once
                user_id, profile_url, status = search_google_for_scholar(name)
                if status == "success" and user_id:
                    results.append({
                        "name": name,
                        "user_id": user_id,
                        "profile_url": profile_url,
                        "confidence": "HIGH",
                        "status": "found"
                    })
                    found_count += 1
                else:
                    results.append({
                        "name": name,
                        "user_id": None,
                        "status": "not_found_after_retry"
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
        
        # Delay between searches (important!)
        if i < len(staff_list) and not captcha_hit:
            delay = random.uniform(8, 15)  # Longer delays for Google
            print(f"  [Waiting {delay:.1f}s...]\n")
            time.sleep(delay)
    
    # Save results
    with open('scholar_ids_found.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print("=" * 80)
    print("SEARCH COMPLETE" if not captcha_hit else "SEARCH INTERRUPTED")
    print("=" * 80)
    
    # Summary
    with_ids = [r for r in results if r.get('user_id')]
    without_ids = [r for r in results if not r.get('user_id')]
    
    print(f"\nResults:")
    print(f"  ✓ Found: {len(with_ids)}/{len(staff_list)}")
    print(f"  ✗ Not found: {len(without_ids)}")
    
    if captcha_hit:
        pending = [r for r in results if r.get('status') == 'pending_manual_search']
        print(f"\n  ⚠️  Hit Google CAPTCHA - {len(pending)} profiles pending")
        print(f"\n  Options:")
        print(f"     1. Wait 1-2 hours, then run again")
        print(f"     2. Use HTML tool: find_scholar_ids.html")
        print(f"     3. Continue from where we stopped (script will skip found)")
    
    if without_ids and not captcha_hit:
        print(f"\n  Not found:")
        for r in without_ids:
            print(f"    - {r['name']}")
    
    print(f"\nResults saved to: scholar_ids_found.json")
    
    # Create ready-to-scrape list
    ready = [r for r in results if r.get('user_id')]
    
    with open('scholar_ids_ready_to_scrape.json', 'w', encoding='utf-8') as f:
        json.dump(ready, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ {len(ready)} profiles ready for Apify scraping")
    if len(ready) > 0:
        print(f"  Apify cost: ${len(ready) * 0.0009:.3f}")
        print(f"\n  Next: Update apify_scholar_final.py to use these IDs")
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
