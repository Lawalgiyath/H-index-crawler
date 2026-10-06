import json
import pandas as pd
import os
import sys
import time
from apify_client import ApifyClient

# Use your Apify API token
client = ApifyClient(os.environ.get('APIFY_TOKEN', 'YOUR_APIFY_TOKEN'))

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
        print(f"Error: {e}")
        return None

def extract_metrics_with_apify(profile_url):
    print(f"  Scraping metrics from profile...", end=" ")
    try:
        run_input = {
            "startUrls": [{"url": profile_url}],
            "pageFunction": """
            async function pageFunction(context) {
                const { $, request, log } = context;
                const metrics = { url: request.url };
                
                $('#gsc_rsb_st tbody tr').each((i, el) => {
                    const rowName = $(el).find('.gsc_rsb_f').text().trim();
                    const valAll = $(el).find('.gsc_rsb_std').eq(0).text().trim();
                    const valSince2021 = $(el).find('.gsc_rsb_std').eq(1).text().trim();
                    
                    if (rowName === 'Citations') {
                        metrics.citations_all = valAll;
                        metrics.citations_since_2021 = valSince2021;
                    } else if (rowName === 'h-index') {
                        metrics.h_index_all = valAll;
                        metrics.h_index_since_2021 = valSince2021;
                    } else if (rowName === 'i10-index') {
                        metrics.i10_index_all = valAll;
                        metrics.i10_index_since_2021 = valSince2021;
                    }
                });
                return metrics;
            }
            """
        }
        
        run = client.actor('apify/cheerio-scraper').call(run_input=run_input)
        dataset_id = run.get("defaultDatasetId") if isinstance(run, dict) else run.default_dataset_id
        
        items = list(client.dataset(dataset_id).iterate_items())
        if items:
            item = items[0]
            cites = item.get('citations_all', 'N/A')
            h = item.get('h_index_all', 'N/A')
            print(f"(Cites: {cites}, H: {h})")
            return item
        print("Failed to extract")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    print("=" * 70)
    print("APIFY SCRAPER FOR MISSED PROFILES")
    print("=" * 70)
    
    baseline_df = pd.read_csv('baseline.csv')
    
    missed_names = ["Kehinde Olayinka", "Taofeeq Ogunbayo", "Oluwakemi Whenu", "Ayorinde Nejo"]
    
    for idx, row in baseline_df.iterrows():
        name = row['Name']
        if name in missed_names:
            print("\n" + "=" * 70)
            print(f"Re-scraping {name}")
            print("=" * 70)
            url = get_profile_url_with_apify(name)
            if url:
                metrics = extract_metrics_with_apify(url)
                if metrics:
                    try:
                        cites = float(metrics.get('citations_all', 0))
                        h = float(metrics.get('h_index_all', 0))
                    except ValueError:
                        cites, h = 'N/A', 'N/A'
                    baseline_df.at[idx, 'Citations_All'] = cites
                    baseline_df.at[idx, 'H_Index_All'] = h
    
    baseline_df.to_csv('chemistry_scholar_metrics_APIFY.csv', index=False)
    print("\n" + "=" * 70)
    print("RESULTS SAVED TO chemistry_scholar_metrics_APIFY.csv")

if __name__ == "__main__":
    main()

