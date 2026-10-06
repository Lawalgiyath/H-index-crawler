"""
SCRAPERAPI GOOGLE SCHOLAR SCRAPER
==================================
Uses ScraperAPI - 5000 FREE requests in trial!
No CAPTCHA, no blocking, just works!
"""
import json
import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
import random
import urllib.parse

print("SCRAPERAPI GOOGLE SCHOLAR SCRAPER")
print("=" * 70)
print("Free tier: 5,000 requests (7-day trial)")
print("=" * 70 + "\n")

# SCRAPERAPI CONFIGURATION
SCRAPERAPI_KEY = "4052c653946f503496a6df02ed39f9d9"

class ScraperAPIScraper:
    """Use ScraperAPI to bypass all blocking"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "http://api.scraperapi.com"
        self.success_count = 0
        
        if not api_key:
            print("ERROR: No API key provided!")
            print("Get your key:")
            print("  1. Sign up: https://www.scraperapi.com/")
            print("  2. Get 5,000 FREE requests")
            print("  3. Copy your API key")
            print("  4. Set SCRAPERAPI_KEY in this file\n")
            raise ValueError("API key required")
        
        print(f"OK API Key: {api_key[:10]}...{api_key[-4:]}\n")
    
    def _make_request(self, url, render_js=False):
        """Make request through ScraperAPI"""
        params = {
            'api_key': self.api_key,
            'url': url,
            'country_code': 'us'  # Use US servers
        }
        
        # Only add render for complex pages
        if render_js:
            params['render'] = 'true'
        
        try:
            response = requests.get(self.base_url, params=params, timeout=60)
            
            if response.status_code == 200:
                return response.text
            else:
                print(f"  [ERROR] Status {response.status_code}: {response.text[:100]}")
                return None
        
        except Exception as e:
            print(f"  [ERROR] Request failed: {str(e)[:80]}")
            return None
    
    def search_scholar_profile(self, name):
        """Search for profile on Google Scholar"""
        query = urllib.parse.quote(f"{name} University of Lagos")
        search_url = f"https://scholar.google.com/scholar?hl=en&q={query}"
        
        print(f"  [SEARCH] {name}")
        
        html = self._make_request(search_url)
        
        if not html:
            print(f"  [FAILED] No response")
            return None
        
        # Parse HTML
        soup = BeautifulSoup(html, "html.parser")
        
        # Find profile link
        profile_link = None
        
        # Method 1: Profile photo link
        profile_link = soup.select_one(".gs_ai_pho a")
        
        # Method 2: Any citations link
        if not profile_link:
            for link in soup.select("a[href*='citations?user=']"):
                profile_link = link
                break
        
        # Method 3: Check all links
        if not profile_link:
            for link in soup.select("a"):
                href = link.get("href", "")
                if "user=" in href and "citations" in href:
                    profile_link = link
                    break
        
        if not profile_link:
            print(f"  [NOT FOUND] No profile in results")
            return None
        
        # Extract user ID
        href = profile_link.get("href", "")
        if not href.startswith("http"):
            href = "https://scholar.google.com" + href
        
        parsed = urllib.parse.urlparse(href)
        params = urllib.parse.parse_qs(parsed.query)
        
        if "user" not in params:
            print(f"  [ERROR] No user ID")
            return None
        
        user_id = params["user"][0]
        print(f"  [FOUND] ID: {user_id}")
        
        return user_id
    
    def get_scholar_metrics(self, user_id, name):
        """Get metrics from profile page"""
        profile_url = f"https://scholar.google.com/citations?user={user_id}&hl=en&view_op=list_works"
        
        print(f"  [METRICS] Fetching...")
        
        # Try direct approach first
        try:
            full_url = f"{self.base_url}?api_key={self.api_key}&url={profile_url}"
            response = requests.get(full_url, timeout=60)
            
            if response.status_code == 200:
                html = response.text
            else:
                print(f"  [RETRY] Status {response.status_code}, trying alternate method...")
                # Try without view_op
                profile_url = f"https://scholar.google.com/citations?user={user_id}&hl=en"
                html = self._make_request(profile_url)
                
                if not html:
                    print(f"  [FAILED] Could not fetch profile")
                    return None
        
        except Exception as e:
            print(f"  [ERROR] {str(e)[:60]}")
            return None
        
        # Parse HTML
        soup = BeautifulSoup(html, "html.parser")
        
        # Find metrics table
        rows = soup.select("#gsc_rsb_st tr")
        
        if not rows:
            print(f"  [WARNING] No metrics table")
            return None
        
        metrics = {
            "Citations_All": "0",
            "Citations_Since_2021": "0",
            "H_Index_All": "0",
            "H_Index_Since_2021": "0",
            "I10_Index_All": "0",
            "I10_Index_Since_2021": "0"
        }
        
        for row in rows:
            header = row.select_one(".gsc_rsb_sc1")
            values = row.select(".gsc_rsb_std")
            
            if header and len(values) >= 2:
                title = header.text.strip().lower()
                all_val = values[0].text.strip()
                recent_val = values[1].text.strip()
                
                if "citations" in title or "cited" in title:
                    metrics["Citations_All"] = all_val
                    metrics["Citations_Since_2021"] = recent_val
                elif "h-index" in title:
                    metrics["H_Index_All"] = all_val
                    metrics["H_Index_Since_2021"] = recent_val
                elif "i10" in title:
                    metrics["I10_Index_All"] = all_val
                    metrics["I10_Index_Since_2021"] = recent_val
        
        print(f"  [SUCCESS] Citations: {metrics['Citations_All']}, H-index: {metrics['H_Index_All']}")
        self.success_count += 1
        return metrics
    
    def scrape_profile(self, name):
        """Full pipeline: search + get metrics"""
        # Search for profile
        user_id = self.search_scholar_profile(name)
        
        if not user_id:
            return None
        
        # Small delay
        time.sleep(random.uniform(2, 4))
        
        # Get metrics
        metrics = self.get_scholar_metrics(user_id, name)
        
        return metrics

def main():
    print("\nStarting ScraperAPI Scholar scraper...\n")
    
    # Check for API key
    api_key = SCRAPERAPI_KEY
    
    if not api_key:
        print("=" * 70)
        print("SETUP REQUIRED")
        print("=" * 70)
        print("\n1. Sign up: https://www.scraperapi.com/")
        print("2. Get your API key from dashboard")
        print("3. Paste it here:")
        api_key = input("\nAPI Key: ").strip()
        
        if not api_key:
            print("\nNo API key provided. Exiting.")
            return
    
    # Load staff
    with open('chemistry_staff_cleaned.json', 'r', encoding='utf-8') as f:
        staff_list = json.load(f)
    
    print(f"\nTotal staff: {len(staff_list)}")
    
    print(f"\nProcessing all {len(staff_list)} staff...")
    
    print("\nStarting...\n")
    
    # Initialize scraper
    try:
        scraper = ScraperAPIScraper(api_key)
    except ValueError:
        return
    
    results = []
    
    for i, staff in enumerate(staff_list, 1):
        name = staff.get("name")
        dept = staff.get("department", "Chemistry")
        
        print(f"\n{'='*70}")
        print(f"[{i}/{len(staff_list)}] {name}")
        print('='*70)
        
        metrics = scraper.scrape_profile(name)
        
        record = {"Name": name, "Department": dept}
        
        if metrics:
            record.update(metrics)
        else:
            record.update({
                "Citations_All": "N/A",
                "Citations_Since_2021": "N/A",
                "H_Index_All": "N/A",
                "H_Index_Since_2021": "N/A",
                "I10_Index_All": "N/A",
                "I10_Index_Since_2021": "N/A"
            })
        
        results.append(record)
        
        # Delay between profiles
        if i < len(staff_list):
            delay = random.uniform(3, 6)
            print(f"  [DELAY] {delay:.1f}s")
            time.sleep(delay)
    
    # Save results
    df = pd.DataFrame(results)
    output = 'chemistry_scholar_metrics_SCRAPERAPI.csv'
    df.to_csv(output, index=False, encoding='utf-8')
    
    print("\n" + "="*70)
    print("FINAL RESULTS")
    print("="*70)
    print(f"Successful: {scraper.success_count}/{len(results)}")
    print(f"Success rate: {scraper.success_count/len(results)*100:.1f}%")
    print(f"Saved to: {output}\n")
    print(df.to_string(index=False))
    print("\n" + "="*70)
    print("DONE!")
    print("="*70 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nStopped by user")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
