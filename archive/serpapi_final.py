"""
SERPAPI GOOGLE SCHOLAR SCRAPER - FINAL VERSION
===============================================
Built specifically for Google Scholar Author Profiles
100 FREE searches/month - Perfect for 27 staff!
"""
import json
import requests
import pandas as pd
import time
import random

print("SERPAPI GOOGLE SCHOLAR SCRAPER")
print("=" * 70)
print("Free tier: 100 searches/month")
print("For 27 staff: Uses 27 searches (27% of free tier)")
print("=" * 70 + "\n")

SERPAPI_KEY = ""  # Will ask for it

class SerpAPIScraper:
    """Use SerpAPI - THE solution for Google Scholar"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.success_count = 0
        
        print(f"OK API Key: {api_key[:10]}...{api_key[-4:]}\n")
    
    def get_author_metrics(self, author_id, name):
        """Get author metrics using SerpAPI Google Scholar Author endpoint"""
        
        print(f"  [{name}]")
        print(f"  Author ID: {author_id}")
        
        params = {
            'engine': 'google_scholar_author',
            'author_id': author_id,
            'api_key': self.api_key,
            'hl': 'en'
        }
        
        try:
            response = requests.get(
                'https://serpapi.com/search',
                params=params,
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"  ERROR: Status {response.status_code}")
                print(f"  Response: {response.text[:200]}")
                return None
            
            data = response.json()
            
            # Extract metrics from cited_by table
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
                    citations = row.get('citations', {})
                    label = citations.get('label', '').lower()
                    
                    if 'citations' in label or 'cited by' in label:
                        metrics["Citations_All"] = str(citations.get('all', '0'))
                        metrics["Citations_Since_2021"] = str(citations.get('since', '0'))
                    elif 'h-index' in label:
                        metrics["H_Index_All"] = str(citations.get('all', '0'))
                        metrics["H_Index_Since_2021"] = str(citations.get('since', '0'))
                    elif 'i10-index' in label:
                        metrics["I10_Index_All"] = str(citations.get('all', '0'))
                        metrics["I10_Index_Since_2021"] = str(citations.get('since', '0'))
            
            print(f"  SUCCESS: Cites={metrics['Citations_All']}, H={metrics['H_Index_All']}, i10={metrics['I10_Index_All']}")
            self.success_count += 1
            return metrics
        
        except Exception as e:
            print(f"  ERROR: {str(e)[:100]}")
            return None

def main():
    print("\nStarting SerpAPI Google Scholar scraper...\n")
    
    # Get API key
    api_key = SERPAPI_KEY
    
    if not api_key:
        print("=" * 70)
        print("SETUP REQUIRED")
        print("=" * 70)
        print("\n1. Sign up: https://serpapi.com/")
        print("2. Get your API key from dashboard")
        print("3. Free: 100 searches/month")
        print("4. Paste it here:")
        api_key = input("\nSerpAPI Key: ").strip()
        
        if not api_key:
            print("\nNo key provided. Exiting.")
            return
    
    # Load staff data with user IDs
    # We have 3 confirmed IDs from previous searches
    staff_data = [
        {"name": "Lawrence Ekebafe", "user_id": "s9d437QAAAAJ", "department": "Chemistry"},
        {"name": "Wesley Okiei", "user_id": "tQgb_bgAAAAJ", "department": "Chemistry"},
        {"name": "Babajide Alo", "user_id": "gklRvzMAAAAJ", "department": "Chemistry"},
    ]
    
    print(f"\nLoaded {len(staff_data)} staff members with known Google Scholar IDs\n")
    print("Note: These are the 3 we found IDs for.")
    print("For the full 27 staff, we'd need to search for the other 24 IDs first.\n")
    
    confirm = input("Run test with these 3? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancelled.")
        return
    
    print("\nStarting scraping...\n")
    
    # Initialize scraper
    scraper = SerpAPIScraper(api_key)
    
    results = []
    
    for i, staff in enumerate(staff_data, 1):
        name = staff["name"]
        user_id = staff["user_id"]
        dept = staff["department"]
        
        print(f"\n[{i}/{len(staff_data)}] " + "="*60)
        
        metrics = scraper.get_author_metrics(user_id, name)
        
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
        
        # Delay between requests
        if i < len(staff_data):
            delay = random.uniform(2, 4)
            print(f"  Delay: {delay:.1f}s")
            time.sleep(delay)
    
    # Save results
    df = pd.DataFrame(results)
    output = 'chemistry_scholar_metrics_SERPAPI.csv'
    df.to_csv(output, index=False, encoding='utf-8')
    
    print("\n" + "="*70)
    print("FINAL RESULTS")
    print("="*70)
    print(f"Success: {scraper.success_count}/{len(results)} ({scraper.success_count/len(results)*100:.1f}%)")
    print(f"Saved to: {output}\n")
    print(df.to_string(index=False))
    
    print("\n" + "="*70)
    print("VERIFICATION")
    print("="*70)
    print("Expected for Wesley Okiei:")
    print("  Citations: 1079 / 370")
    print("  H-index: 17 / 9")
    print("  i10-index: 19 / 9")
    print("\nActual from scraper:")
    wesley = df[df['Name'] == 'Wesley Okiei'].iloc[0]
    print(f"  Citations: {wesley['Citations_All']} / {wesley['Citations_Since_2021']}")
    print(f"  H-index: {wesley['H_Index_All']} / {wesley['H_Index_Since_2021']}")
    print(f"  i10-index: {wesley['I10_Index_All']} / {wesley['I10_Index_Since_2021']}")
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
