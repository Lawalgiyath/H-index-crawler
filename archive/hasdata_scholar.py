"""
HASDATA GOOGLE SCHOLAR SCRAPER
===============================
Uses HasData API - 1000 FREE credits/month forever!
No trial, no credit card, truly free!
"""
import json
import requests
import pandas as pd
import time
import random

print("HASDATA GOOGLE SCHOLAR SCRAPER")
print("=" * 70)
print("Free forever: 1,000 credits/month")
print("Cost per call: ~10 credits")
print("You can scrape: ~100 profiles/month")
print("=" * 70 + "\n")

# HASDATA CONFIGURATION
HASDATA_API_KEY = ""  # Add after signup

class HasDataScraper:
    """Use HasData API for Google Scholar"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.hasdata.com/scrape/google/scholar"
        self.author_url = "https://api.hasdata.com/scrape/google/scholar/author"
        self.success_count = 0
        
        if not api_key:
            print("ERROR: No API key provided!")
            print("Get your key:")
            print("  1. Sign up: https://hasdata.com/")
            print("  2. No credit card needed!")
            print("  3. Get 1,000 FREE credits/month")
            print("  4. Copy API key from dashboard\n")
            raise ValueError("API key required")
        
        print(f"OK API Key: {api_key[:10]}...{api_key[-4:]}\n")
    
    def search_author(self, name):
        """Search for author profile"""
        headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json'
        }
        
        payload = {
            'q': f"{name} University of Lagos"
        }
        
        print(f"  [SEARCH] {name}")
        
        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"  [ERROR] Status {response.status_code}: {response.text[:100]}")
                return None
            
            data = response.json()
            
            # Find author profile in results
            if 'organic_results' in data:
                for result in data['organic_results']:
                    if 'author' in result and result['author']:
                        author_id = result['author'].get('id')
                        if author_id:
                            print(f"  [FOUND] Author ID: {author_id}")
                            return author_id
            
            # Alternative: check profiles
            if 'profiles' in data and data['profiles']:
                author_id = data['profiles'][0].get('author_id')
                if author_id:
                    print(f"  [FOUND] Author ID: {author_id}")
                    return author_id
            
            print(f"  [NOT FOUND] No profile in results")
            return None
        
        except Exception as e:
            print(f"  [ERROR] {str(e)[:80]}")
            return None
    
    def get_author_metrics(self, author_id, name):
        """Get author profile metrics"""
        headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json'
        }
        
        payload = {
            'author_id': author_id
        }
        
        print(f"  [METRICS] Fetching...")
        
        try:
            response = requests.post(
                self.author_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"  [ERROR] Status {response.status_code}")
                return None
            
            data = response.json()
            
            # Extract metrics
            metrics = {
                "Citations_All": "0",
                "Citations_Since_2021": "0",
                "H_Index_All": "0",
                "H_Index_Since_2021": "0",
                "I10_Index_All": "0",
                "I10_Index_Since_2021": "0"
            }
            
            if 'cited_by' in data:
                cited = data['cited_by']
                if 'table' in cited:
                    table = cited['table']
                    for row in table:
                        if 'Citations' in row.get('label', ''):
                            metrics["Citations_All"] = str(row.get('all', '0'))
                            metrics["Citations_Since_2021"] = str(row.get('since_2019', '0'))  # Close enough
                        elif 'h-index' in row.get('label', ''):
                            metrics["H_Index_All"] = str(row.get('all', '0'))
                            metrics["H_Index_Since_2021"] = str(row.get('since_2019', '0'))
                        elif 'i10-index' in row.get('label', ''):
                            metrics["I10_Index_All"] = str(row.get('all', '0'))
                            metrics["I10_Index_Since_2021"] = str(row.get('since_2019', '0'))
            
            print(f"  [SUCCESS] Citations: {metrics['Citations_All']}, H-index: {metrics['H_Index_All']}")
            self.success_count += 1
            return metrics
        
        except Exception as e:
            print(f"  [ERROR] {str(e)[:80]}")
            return None
    
    def scrape_profile(self, name):
        """Full pipeline"""
        # Search
        author_id = self.search_author(name)
        
        if not author_id:
            return None
        
        # Delay
        time.sleep(random.uniform(2, 4))
        
        # Get metrics
        metrics = self.get_author_metrics(author_id, name)
        
        return metrics

def main():
    print("\nStarting HasData Scholar scraper...\n")
    
    # API key
    api_key = HASDATA_API_KEY
    
    if not api_key:
        print("=" * 70)
        print("SETUP REQUIRED")
        print("=" * 70)
        print("\n1. Sign up: https://hasdata.com/")
        print("2. No credit card required!")
        print("3. Get your API key")
        print("4. Paste it here:")
        api_key = input("\nAPI Key: ").strip()
        
        if not api_key:
            print("\nNo API key. Exiting.")
            return
    
    # Load staff
    with open('chemistry_staff_cleaned.json', 'r', encoding='utf-8') as f:
        staff_list = json.load(f)
    
    print(f"\nTotal staff: {len(staff_list)}")
    
    # Mode
    mode = input("\nMode:\n  1 = Test (3 people)\n  2 = All (27 people)\nChoice: ").strip()
    
    if mode == "2":
        print(f"\nProcessing all {len(staff_list)}...")
        print("Note: With 1000 credits, you can do ~50 profiles")
        confirm = input("Continue? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Cancelled.")
            return
    else:
        print("\nTest mode: 3 staff...")
        staff_list = staff_list[:3]
    
    print("\nStarting...\n")
    
    # Initialize
    try:
        scraper = HasDataScraper(api_key)
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
        
        if i < len(staff_list):
            delay = random.uniform(3, 6)
            print(f"  [DELAY] {delay:.1f}s")
            time.sleep(delay)
    
    # Save
    df = pd.DataFrame(results)
    output = 'chemistry_scholar_metrics_HASDATA.csv'
    df.to_csv(output, index=False, encoding='utf-8')
    
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    print(f"Success: {scraper.success_count}/{len(results)}")
    print(f"Rate: {scraper.success_count/len(results)*100:.1f}%")
    print(f"File: {output}\n")
    print(df.to_string(index=False))
    print("\n" + "="*70)
    print("DONE!")
    print("="*70 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nStopped")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
