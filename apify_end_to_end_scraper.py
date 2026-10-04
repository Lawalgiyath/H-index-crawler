import json
import os
import urllib.parse
import pandas as pd
from apify_client import ApifyClient

# Using the provided Apify Token from environment
APIFY_TOKEN = os.environ.get('APIFY_TOKEN', '')
if not APIFY_TOKEN:
    raise ValueError("APIFY_TOKEN environment variable is not set")
client = ApifyClient(APIFY_TOKEN)

print("=" * 70)
print("APIFY END-TO-END GOOGLE SCHOLAR SCRAPER")
print("=" * 70 + "\n")

def get_profile_url_with_apify(name):
    print(f"  Finding profile URL for '{name}'...", end=" ")
    try:
        queries = f'site:scholar.google.com/citations {name}\nsite:scholar.google.com/citations {name} "Lagos"'
        run_input = {
            "queries": queries,
            "maxPagesPerQuery": 1,
            "resultsPerPage": 3,
        }
        
        run = client.actor('apify/google-search-scraper').call(run_input=run_input)
        dataset_id = run.get("defaultDatasetId") if isinstance(run, dict) else run.default_dataset_id
        
        for item in client.dataset(dataset_id).iterate_items():
            if 'organicResults' in item:
                for res in item['organicResults']:
                    url = res.get('url', '')
                    if 'scholar.google.com/citations' in url and 'user=' in url:
                        print(f"Found!")
                        return url
                        
        print("Profile not found")
        return None
    except Exception as e:
        print(f"Apify search error: {str(e)[:50]}")
        return None

def scrape_metrics_with_apify(profile_url, queried_name):
    print(f"  Scraping metrics from profile...", end=" ")
    try:
        page_function = '''
        async function pageFunction(context) {
            const { $ } = context;
            let metrics = {
                Citations_All: "0", Citations_Since_2021: "0",
                H_Index_All: "0", H_Index_Since_2021: "0",
                I10_Index_All: "0", I10_Index_Since_2021: "0",
                Profile_Name: $("#gsc_prf_in").text().trim(),
                Affiliation: $(".gsc_prf_il").first().text().trim(),
                Email: $("#gsc_prf_ivh").text().trim()
            };
            $("#gsc_rsb_st tr").each((i, row) => {
                const header = $(row).find(".gsc_rsb_sc1").text().trim().toLowerCase();
                const values = $(row).find(".gsc_rsb_std");
                if(header && values.length >= 2) {
                    const val_all = $(values[0]).text().trim();
                    const val_recent = $(values[1]).text().trim();
                    if (header.includes("citations") || header.includes("cited by")) {
                        metrics.Citations_All = val_all;
                        metrics.Citations_Since_2021 = val_recent;
                    } else if (header.includes("h-index")) {
                        metrics.H_Index_All = val_all;
                        metrics.H_Index_Since_2021 = val_recent;
                    } else if (header.includes("i10-index")) {
                        metrics.I10_Index_All = val_all;
                        metrics.I10_Index_Since_2021 = val_recent;
                    }
                }
            });
            return metrics;
        }
        '''
        
        run = client.actor('apify/cheerio-scraper').call(run_input={
            'startUrls': [{'url': profile_url}],
            'pageFunction': page_function
        })
        
        dataset_id = run.get("defaultDatasetId") if isinstance(run, dict) else run.default_dataset_id
        
        items = list(client.dataset(dataset_id).iterate_items())
        if items and len(items) > 0:
            metrics = items[0]
            if metrics.get('#error'):
                print("Error scraping metrics")
                return None
            
            # Clean up Apify debug info
            metrics.pop('#error', None)
            metrics.pop('#debug', None)
            
            # --- STRICT VALIDATION ---
            prof_name = metrics.get('Profile_Name', '').lower()
            affil = metrics.get('Affiliation', '').lower()
            email_txt = metrics.get('Email', '').lower()
            q_parts = queried_name.lower().split()
            first_name = q_parts[0]
            last_name = q_parts[-1]
            
            # If the last name isn't even in the profile name, reject it
            if last_name not in prof_name:
                print(f"Rejected: Name mismatch (Expected last name '{last_name}' in '{prof_name}')")
                return None
                
            # If the first name isn't in the profile, we MUST verify they are from Lagos
            if first_name not in prof_name:
                has_lagos = "lagos" in affil or "unilag" in affil or "unilag" in email_txt or "lagos" in email_txt
                if not has_lagos:
                    print(f"Rejected: Profile is '{prof_name}' at '{affil}', not matching '{queried_name}' at UNILAG")
                    return None
            
            print(f"(Cites: {metrics.get('Citations_All')}, H: {metrics.get('H_Index_All')})")
            return metrics
            
        print("No metrics returned")
        return None
    except Exception as e:
        print(f"Apify scrape error: {str(e)[:50]}")
        return None

import sys

def main():
    # Use provided filename or default to chemistry_staff_cleaned.json
    input_file = sys.argv[1] if len(sys.argv) > 1 else 'chemistry_staff_cleaned.json'
    
    # Load staff
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            staff_list = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find input file '{input_file}'")
        return
        
    print(f"Loaded {len(staff_list)} staff members from {input_file} to process.")
    
    # Create output filename based on input filename
    base_name = os.path.splitext(input_file)[0]
    output_file = f"{base_name}_scholar_metrics.csv"
    
    results = []
    success_count = 0
    
    for i, staff in enumerate(staff_list, 1):
        name = staff.get("name")
        department = staff.get("department", "Chemistry")
        
        print(f"\n{'='*70}")
        print(f"[{i}/{len(staff_list)}] {name}")
        print('='*70)
        
        record = {"Name": name, "Department": department}
        
        # 1. Get profile URL
        profile_url = get_profile_url_with_apify(name)
        
        if profile_url:
            # 2. Get Metrics
            metrics = scrape_metrics_with_apify(profile_url, name)
            if metrics:
                record.update(metrics)
                success_count += 1
            else:
                record.update({
                    "Citations_All": "N/A", "Citations_Since_2021": "N/A",
                    "H_Index_All": "N/A", "H_Index_Since_2021": "N/A",
                    "I10_Index_All": "N/A", "I10_Index_Since_2021": "N/A"
                })
        else:
            record.update({
                "Citations_All": "N/A", "Citations_Since_2021": "N/A",
                "H_Index_All": "N/A", "H_Index_Since_2021": "N/A",
                "I10_Index_All": "N/A", "I10_Index_Since_2021": "N/A"
            })
            
        results.append(record)
        
        # Save incrementally
        df = pd.DataFrame(results)
        df.to_csv(output_file, index=False, encoding='utf-8')
        
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    print(f"Success: {success_count}/{len(results)}")
    print(f"Saved to: {output_file}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nStopped by user")
    except Exception as e:
        print(f"\n\nFatal Error: {e}")
