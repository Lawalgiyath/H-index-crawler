"""
APIFY GOOGLE SCHOLAR SCRAPER - FINAL WORKING VERSION
=====================================================
$5 FREE credits = 5,555+ profiles!
Uses: blackfalcondata/google-scholar-scraper
Price: $0.90 per 1,000 profiles
"""
import json
from apify_client import ApifyClient
import pandas as pd
import time

print("APIFY GOOGLE SCHOLAR SCRAPER")
print("=" * 70)
print("Free: $5 credits = 5,555+ author profiles")
print("Cost: $0.90 per 1,000 profiles")
print("For 27 staff: $0.02 total!")
print("=" * 70 + "\n")

APIFY_TOKEN = "YOUR_APIFY_TOKEN"

def scrape_author_profiles(api_token, author_ids):
    """Scrape multiple author profiles using Apify"""
    
    client = ApifyClient(api_token)
    
    # The actor needs individual URLs or a search query
    # Let's build profile URLs
    profile_urls = [f"https://scholar.google.com/citations?user={aid}&hl=en" for aid in author_ids]
    
    # Using: blackfalcondata/google-scholar-scraper
    # They need simple string URLs
    run_input = {
        "startUrls": profile_urls,  # Just the URL strings
        "maxItems": len(author_ids)
    }
    
    print(f"Starting Apify Actor...")
    print(f"Profile URLs: {len(profile_urls)}\n")
    
    # Run the actor
    run = client.actor("blackfalcondata/google-scholar-scraper").call(run_input=run_input)
    
    print(f"Actor completed!")
    print(f"Status: {run.status}\n")
    
    # Fetch results
    results = []
    for item in client.dataset(run.default_dataset_id).iterate_items():
        results.append(item)
    
    return results

def extract_metrics(apify_result):
    """Extract metrics from Apify result"""
    
    # FIXED: The actor returns: citations, citationsSinceYear, hIndex, hIndexSinceYear, i10Index, i10IndexSinceYear
    # NOT citationsSince, hIndexSince, etc.
    metrics = {
        "Citations_All": str(apify_result.get('citations', 0)),
        "Citations_Since_2021": str(apify_result.get('citationsSinceYear', 0)),
        "H_Index_All": str(apify_result.get('hIndex', 0)),
        "H_Index_Since_2021": str(apify_result.get('hIndexSinceYear', 0)),
        "I10_Index_All": str(apify_result.get('i10Index', 0)),
        "I10_Index_Since_2021": str(apify_result.get('i10IndexSinceYear', 0))
    }
    
    return metrics

def main():
    print("Starting Apify Google Scholar scraper...\n")
    
    # Get API token
    api_token = APIFY_TOKEN
    
    if not api_token:
        print("=" * 70)
        print("SETUP REQUIRED")
        print("=" * 70)
        print("\n1. Sign up: https://apify.com/")
        print("2. Get $5 FREE credits (no card needed!)")
        print("3. Get API token from: https://console.apify.com/account/integrations")
        print("4. Paste it here:")
        api_token = input("\nApify API Token: ").strip()
        
        if not api_token:
            print("\nNo token provided. Exiting.")
            return
    
    # Test with 3 known author IDs
    test_authors = [
        {"name": "Lawrence Ekebafe", "user_id": "s9d437QAAAAJ"},
        {"name": "Wesley Okiei", "user_id": "tQgb_bgAAAAJ"},
        {"name": "Babajide Alo", "user_id": "gklRvzMAAAAJ"},
    ]
    
    author_ids = [author["user_id"] for author in test_authors]
    
    print(f"\nTest mode: {len(test_authors)} authors\n")
    print("Running Apify Actor...\n")
    
    try:
        # Scrape all profiles
        apify_results = scrape_author_profiles(api_token, author_ids)
        
        print(f"\nGot {len(apify_results)} results\n")
        
        # Debug: print first result structure
        if apify_results:
            print("DEBUG: First result structure:")
            print(json.dumps(apify_results[0], indent=2)[:500])
            print("\n")
        
        # Process results
        results = []
        
        for i, apify_result in enumerate(apify_results):
            # Get user ID from result
            user_id = apify_result.get('userId', '')
            name = apify_result.get('name', '')
            
            print(f"[{i+1}/{len(apify_results)}] {name}")
            
            metrics = extract_metrics(apify_result)
            
            record = {
                "Name": name,
                "Department": "Chemistry",
                "Profile_Link": f"https://scholar.google.com/citations?user={user_id}" if user_id else "N/A"
            }
            record.update(metrics)
            
            print(f"  Citations: {metrics['Citations_All']} / {metrics['Citations_Since_2021']}")
            print(f"  H-index: {metrics['H_Index_All']} / {metrics['H_Index_Since_2021']}")
            print(f"  i10-index: {metrics['I10_Index_All']} / {metrics['I10_Index_Since_2021']}\n")
            
            results.append(record)
        
        # Save results
        df = pd.DataFrame(results)
        output = 'chemistry_scholar_metrics_APIFY.csv'
        df.to_csv(output, index=False, encoding='utf-8')
        
        print("=" * 70)
        print("FINAL RESULTS")
        print("=" * 70)
        print(f"Success: {len(results)}/{len(test_authors)}")
        print(f"Saved to: {output}\n")
        print(df.to_string(index=False))
        
        print("\n" + "=" * 70)
        print("VERIFICATION (Wesley Okiei)")
        print("=" * 70)
        print("Expected: Citations: 1079/370, H: 17/9, i10: 19/9")
        wesley = df[df['Name'] == 'Wesley Okiei']
        if not wesley.empty:
            w = wesley.iloc[0]
            print(f"Actual:   Citations: {w['Citations_All']}/{w['Citations_Since_2021']}, H: {w['H_Index_All']}/{w['H_Index_Since_2021']}, i10: {w['I10_Index_All']}/{w['I10_Index_Since_2021']}")
        print("=" * 70 + "\n")
    
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nStopped by user")
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()

