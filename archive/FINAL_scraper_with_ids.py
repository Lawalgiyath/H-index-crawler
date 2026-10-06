"""
FINAL GOOGLE SCHOLAR SCRAPER
=============================
You provide the user IDs, this scrapes all metrics
Simple and reliable!
"""
import json
from apify_client import ApifyClient
import pandas as pd

APIFY_TOKEN = "YOUR_APIFY_TOKEN"

# ADD YOUR SCHOLAR USER IDs HERE
# Format: {"Name": "user_id"}
SCHOLAR_IDS = {
    "Lawrence Ekebafe": "s9d437QAAAAJ",
    "Wesley Okiei": "tQgb_bgAAAAJ",
    "Babajide Alo": "gklRvzMAAAAJ",
    # Add more here...
    # "Name": "user_id",
}

def scrape_all_profiles(api_token, scholar_ids):
    """Scrape all profiles at once"""
    
    client = ApifyClient(api_token)
    
    # Build profile URLs
    profile_urls = []
    for name, user_id in scholar_ids.items():
        url = f"https://scholar.google.com/citations?user={user_id}&hl=en"
        profile_urls.append(url)
    
    print(f"Scraping {len(profile_urls)} profiles...")
    print(f"Cost: ${len(profile_urls) * 0.0009:.4f}\n")
    
    run_input = {
        "startUrls": profile_urls,
        "maxItems": len(profile_urls),
        "includeDetails": True
    }
    
    print("Starting Apify actor...\n")
    
    # Run the actor
    run = client.actor("blackfalcondata/google-scholar-scraper").call(run_input=run_input)
    
    print(f"Actor completed! Status: {run.status}\n")
    
    # Fetch results
    results = []
    for item in client.dataset(run.default_dataset_id).iterate_items():
        results.append(item)
    
    return results

def main():
    print("=" * 80)
    print("FINAL GOOGLE SCHOLAR SCRAPER")
    print("=" * 80)
    print(f"Profiles configured: {len(SCHOLAR_IDS)}")
    print("\nConfigured profiles:")
    for i, name in enumerate(SCHOLAR_IDS.keys(), 1):
        print(f"  {i}. {name}")
    print("=" * 80)
    
    if len(SCHOLAR_IDS) < 3:
        print("\n⚠️  Only 3 profiles configured. Add more IDs to SCHOLAR_IDS dictionary.")
        print("   Format: 'Name': 'user_id',")
    
    input("\nPress Enter to start scraping...")
    print()
    
    # Scrape
    apify_results = scrape_all_profiles(APIFY_TOKEN, SCHOLAR_IDS)
    
    print(f"Got {len(apify_results)} results\n")
    
    # Process results
    results = []
    
    for i, apify_result in enumerate(apify_results, 1):
        name = apify_result.get('name', 'Unknown')
        user_id = apify_result.get('userId', '')
        
        print(f"[{i}/{len(apify_results)}] {name}")
        
        metrics = {
            "Name": name,
            "Department": "Chemistry",
            "User_ID": user_id,
            "Citations_All": str(apify_result.get('citations', 0)),
            "Citations_Since_2021": str(apify_result.get('citationsSinceYear', 0)),
            "H_Index_All": str(apify_result.get('hIndex', 0)),
            "H_Index_Since_2021": str(apify_result.get('hIndexSinceYear', 0)),
            "I10_Index_All": str(apify_result.get('i10Index', 0)),
            "I10_Index_Since_2021": str(apify_result.get('i10IndexSinceYear', 0)),
            "Profile_URL": f"https://scholar.google.com/citations?user={user_id}&hl=en"
        }
        
        print(f"  Citations: {metrics['Citations_All']} / {metrics['Citations_Since_2021']}")
        print(f"  H-index: {metrics['H_Index_All']} / {metrics['H_Index_Since_2021']}")
        print(f"  i10-index: {metrics['I10_Index_All']} / {metrics['I10_Index_Since_2021']}\n")
        
        results.append(metrics)
    
    # Save results
    df = pd.DataFrame(results)
    output = 'chemistry_scholar_metrics_FINAL.csv'
    df.to_csv(output, index=False, encoding='utf-8')
    
    print("=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)
    print(f"Success: {len(results)}/{len(SCHOLAR_IDS)}")
    print(f"Saved to: {output}\n")
    print(df[['Name', 'Citations_All', 'Citations_Since_2021', 'H_Index_All', 'H_Index_Since_2021']].to_string(index=False))
    print("\n" + "=" * 80)
    
    # Also save as JSON
    json_output = 'chemistry_scholar_metrics_FINAL.json'
    with open(json_output, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"Also saved as JSON: {json_output}")
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

