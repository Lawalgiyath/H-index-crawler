"""
APIFY SEARCH + SCRAPE - FULLY AUTOMATIC
========================================
Use Apify to SEARCH for each person by name
Then scrape their metrics
All in one go!
"""
import json
from apify_client import ApifyClient
import pandas as pd
import time

APIFY_TOKEN = "YOUR_APIFY_TOKEN"

def main():
    print("=" * 80)
    print("APIFY SEARCH + SCRAPE - FULLY AUTOMATIC")
    print("=" * 80)
    print("Uses Apify to search by name AND scrape metrics")
    print("Cost: ~$0.12 for 27 people (search + scrape)")
    print("=" * 80)
    
    # Load staff
    with open('chemistry_staff_cleaned.json', 'r', encoding='utf-8') as f:
        staff_list = json.load(f)
    
    print(f"\nTotal staff: {len(staff_list)}\n")
    
    input("Press Enter to start...")
    print()
    
    client = ApifyClient(APIFY_TOKEN)
    
    print(f"Searching for {len(staff_list)} profiles (one at a time)...\n")
    
    # Search for each person individually
    apify_results = []
    
    for i, staff in enumerate(staff_list, 1):
        name = staff['name']
        query = f"{name} University of Lagos"
        
        print(f"[{i}/{len(staff_list)}] Searching: {name}...", end=" ")
        
        run_input = {
            "query": query,
            "maxResults": 3,  # Get top 3 results
            "includeDetails": True,
            "compact": False
        }
        
        try:
            run = client.actor("blackfalcondata/google-scholar-scraper").call(run_input=run_input)
            
            # Get results for this search
            count = 0
            for item in client.dataset(run.default_dataset_id).iterate_items():
                apify_results.append(item)
                count += 1
            
            print(f"OK ({count} results)")
            
        except Exception as e:
            print(f"ERROR: {str(e)[:50]}")
        
        # Small delay between searches
        if i < len(staff_list):
            time.sleep(1)
    
    print(f"\nGot {len(apify_results)} total results\n")
    
    # Match results to staff names
    # Create a map of results by name similarity
    results_map = {}
    
    for apify_result in apify_results:
        result_name = apify_result.get('name', '').lower()
        result_affiliation = apify_result.get('affiliation', '').lower()
        
        # Try to match to a staff member
        for staff in staff_list:
            staff_name = staff['name'].lower()
            
            # Check if names match (even partially)
            if any(word in result_name for word in staff_name.split() if len(word) > 3):
                # Additional check: affiliation should contain "lagos"
                if 'lagos' in result_affiliation or 'unilag' in result_affiliation:
                    # Store best match (first one with lagos affiliation)
                    if staff['name'] not in results_map:
                        results_map[staff['name']] = apify_result
                        break
    
    print(f"Matched {len(results_map)}/{len(staff_list)} profiles\n")
    
    # Process matched results
    results = []
    
    for staff in staff_list:
        name = staff['name']
        
        if name in results_map:
            apify_result = results_map[name]
            
            print(f"[OK] {name}")
            
            metrics = {
                "Name": apify_result.get('name', name),
                "Original_Name": name,
                "Department": "Chemistry",
                "User_ID": apify_result.get('userId', ''),
                "Citations_All": str(apify_result.get('citations', 0)),
                "Citations_Since_2021": str(apify_result.get('citationsSinceYear', 0)),
                "H_Index_All": str(apify_result.get('hIndex', 0)),
                "H_Index_Since_2021": str(apify_result.get('hIndexSinceYear', 0)),
                "I10_Index_All": str(apify_result.get('i10Index', 0)),
                "I10_Index_Since_2021": str(apify_result.get('i10IndexSinceYear', 0)),
                "Affiliation": apify_result.get('affiliation', ''),
                "Profile_URL": f"https://scholar.google.com/citations?user={apify_result.get('userId', '')}&hl=en"
            }
            
            print(f"  Citations: {metrics['Citations_All']} / {metrics['Citations_Since_2021']}")
            print(f"  H-index: {metrics['H_Index_All']} / {metrics['H_Index_Since_2021']}\n")
            
            results.append(metrics)
        else:
            print(f"[NOT FOUND] {name}")
            results.append({
                "Name": name,
                "Original_Name": name,
                "Department": "Chemistry",
                "User_ID": "",
                "Citations_All": "N/A",
                "Citations_Since_2021": "N/A",
                "H_Index_All": "N/A",
                "H_Index_Since_2021": "N/A",
                "I10_Index_All": "N/A",
                "I10_Index_Since_2021": "N/A",
                "Affiliation": "",
                "Profile_URL": ""
            })
    
    # Save results
    df = pd.DataFrame(results)
    output_csv = 'chemistry_scholar_metrics_COMPLETE.csv'
    output_json = 'chemistry_scholar_metrics_COMPLETE.json'
    
    df.to_csv(output_csv, index=False, encoding='utf-8')
    
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print("=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)
    print(f"Found: {len(results_map)}/{len(staff_list)}")
    print(f"Not found: {len(staff_list) - len(results_map)}")
    print(f"\nFiles created:")
    print(f"  - {output_csv}")
    print(f"  - {output_json}")
    print("\n" + df[['Original_Name', 'Citations_All', 'H_Index_All', 'I10_Index_All']].to_string(index=False))
    print("\n" + "=" * 80)
    print("DONE!")
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

