"""
SERPAPI GOOGLE SCHOLAR SCRAPER
===============================
SerpAPI specializes in Google Scholar!
Free: 100 searches/month
"""
import json
import requests
import pandas as pd
import time
import random

print("SERPAPI GOOGLE SCHOLAR SCRAPER")
print("=" * 70)
print("Free tier: 100 searches/month")
print("=" * 70 + "\n")

SERPAPI_KEY = ""  # Add your SerpAPI key

class SerpAPIScraper:
    """Use SerpAPI - built for Google Scholar"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.success_count = 0
        
        if not api_key:
            print("ERROR: No API key!")
            print("Get your key:")
            print("  1. Sign up: https://serpapi.com/")
            print("  2. Free: 100 searches/month")
            print("  3. Copy API key\n")
            raise ValueError("API key required")
        
        print(f"OK API Key: {api_key[:10]}...{api_key[-4:]}\n")
    
    def get_author_metrics(self, author_id, name):
        """Get author metrics directly from SerpAPI"""
        print(f"  [FETCH] {name} (ID: {author_id})")
        
        params = {
            'engine': 'google_scholar_author',
            'author_id': author_id,
            'api_key': self.api_key
        }
        
        try:
            response = requests.get('https://serpapi.com/search', params=params, timeout=30)
            
            if response.status_code != 200:
                print(f"  [ERROR] Status {response.status_code}")
                return None
            
            data = response.json()
            
            # Extract from cited_by table
            metrics = {
                "Citations_All": "0",
                "Citations_Since_2021": "0",
                "H_Index_All": "0",
                "H_Index_Since_2021": "0",
                "I10_Index_All": "0",
                "I10_Index_Since_2021": "0"
            }
            
            if 'cited_by' in data and 'table' in data['cited_by']:
                table = data['cited_by']['table']
                
                for row in table:
                    label = row.get('citations', {}).get('label', '')
                    
                    if 'Citations' in label:
                        metrics["Citations_All"] = str(row['citations'].get('all', '0'))
                        metrics["Citations_Since_2021"] = str(row['citations'].get('since', '0'))
                    elif 'h-index' in label:
                        metrics["H_Index_All"] = str(row['citations'].get('all', '0'))
                        metrics["H_Index_Since_2021"] = str(row['citations'].get('since', '0'))
                    elif 'i10-index' in label:
                        metrics["I10_Index_All"] = str(row['citations'].get('all', '0'))
                        metrics["I10_Index_Since_2021"] = str(row['citations'].get('since', '0'))
            
            print(f"  [SUCCESS] Cites: {metrics['Citations_All']}, H: {metrics['H_Index_All']}")
            self.success_count += 1
            return metrics
        
        except Exception as e:
            print(f"  [ERROR] {str(e)[:80]}")
            return None

def main():
    print("\nStarting SerpAPI scraper...\n")
    
    # API key
    api_key = SERPAPI_KEY
    
    if not api_key:
        print("SETUP REQUIRED")
        print("="*70)
        print("\n1. Sign up: https://serpapi.com/")
        print("2. Get API key")
        print("3. Paste here:")
        api_key = input("\nAPI Key: ").strip()
        
        if not api_key:
            print("\nNo key. Exiting.")
            return
    
    # We already have the user IDs from previous search
    # Let's use them directly!
    staff_data = [
        {"name": "Lawrence Ekebafe", "user_id": "s9d437QAAAAJ"},
        {"name": "Wesley Okiei", "user_id": "tQgb_bgAAAAJ"},
        {"name": "Babajide Alo", "user_id": "gklRvzMAAAAJ"},
    ]
    
    print(f"Test mode: {len(staff_data)} staff with known IDs\n")
    
    # Initialize
    try:
        scraper = SerpAPIScraper(api_key)
    except ValueError:
        return
    
    results = []
    
    for i, staff in enumerate(staff_data, 1):
        name = staff["name"]
        user_id = staff["user_id"]
        
        print(f"\n[{i}/{len(staff_data)}] {name}")
        print("-" * 70)
        
        metrics = scraper.get_author_metrics(user_id, name)
        
        record = {"Name": name, "Department": "Chemistry"}
        
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
        
        if i < len(staff_data):
            delay = random.uniform(2, 4)
            print(f"  [DELAY] {delay:.1f}s")
            time.sleep(delay)
    
    # Save
    df = pd.DataFrame(results)
    output = 'chemistry_scholar_metrics_SERPAPI_TEST.csv'
    df.to_csv(output, index=False, encoding='utf-8')
    
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    print(f"Success: {scraper.success_count}/{len(results)}")
    print(f"Rate: {scraper.success_count/len(results)*100:.1f}%")
    print(f"File: {output}\n")
    print(df.to_string(index=False))
    print("\n" + "="*70)
    print("Expected for Wesley Okiei:")
    print("  Citations: 1079 / 370")
    print("  H-index: 17 / 9")
    print("  i10-index: 19 / 9")
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
