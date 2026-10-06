import os
import pandas as pd
from apify_client import ApifyClient
from bs4 import BeautifulSoup
import requests
import random
import time

APIFY_TOKEN = 'YOUR_APIFY_TOKEN'
client = ApifyClient(APIFY_TOKEN)

def scrape_scholar_metrics(user_id):
    profile_url = f"https://scholar.google.com/citations?user={user_id}&hl=en"
    for attempt in range(3):
        try:
            session = requests.Session()
            session.headers.update({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            })
            response = session.get(profile_url, timeout=15)
            
            html_content = ""
            if response.status_code in (429, 503) or (response.status_code == 200 and ("g-recaptcha" in response.text.lower() or "sorry" in response.text.lower() or "did not match any articles" in response.text.lower())):
                # Fallback to Apify
                run_input = {
                    "startUrls": [{"url": profile_url}],
                    "pageFunction": "async function pageFunction(context) { const $ = context.$; return { html: $('body').html() }; }",
                    "proxyConfiguration": {"useApifyProxy": True}
                }
                run = client.actor('apify/cheerio-scraper').call(run_input=run_input)
                dataset_id = run.get('defaultDatasetId') if isinstance(run, dict) else run.default_dataset_id
                for item in client.dataset(dataset_id).iterate_items():
                    html_content = item.get("html", "")
                    break
                if not html_content:
                    time.sleep(random.uniform(5, 10))
                    continue
            elif response.status_code != 200:
                time.sleep(random.uniform(3, 5))
                continue
            else:
                html_content = response.text

            if not html_content:
                continue

            soup = BeautifulSoup(html_content, "html.parser")
            table_rows = soup.select("#gsc_rsb_st tr")
            metrics = {
                "Citations_All": "0", "Citations_Since_2021": "0",
                "H_Index_All": "0", "H_Index_Since_2021": "0",
                "I10_Index_All": "0", "I10_Index_Since_2021": "0"
            }
            
            name_elem = soup.select_one("#gsc_prf_in")
            if name_elem:
                metrics["Exact_Name"] = name_elem.text.strip()
            
            affil_elem = soup.select_one(".gsc_prf_il")
            if affil_elem:
                metrics["Exact_Affiliation"] = affil_elem.text.strip()
                
            email_elem = soup.select_one("#gsc_prf_ivh")
            if email_elem:
                metrics["Verified_Email"] = email_elem.text.strip()
            else:
                metrics["Verified_Email"] = ""

            for row in table_rows:
                header = row.select_one(".gsc_rsb_sc1")
                values = row.select(".gsc_rsb_std")
                if header and len(values) >= 2:
                    t = header.text.strip().lower()
                    if "citations" in t:
                        metrics["Citations_All"]        = values[0].text.strip()
                        metrics["Citations_Since_2021"] = values[1].text.strip()
                    elif "h-index" in t:
                        metrics["H_Index_All"]          = values[0].text.strip()
                        metrics["H_Index_Since_2021"]   = values[1].text.strip()
                    elif "i10" in t:
                        metrics["I10_Index_All"]        = values[0].text.strip()
                        metrics["I10_Index_Since_2021"] = values[1].text.strip()
            return metrics
        except Exception as e:
            time.sleep(3)
    return None

df = pd.read_csv('chemistry_scholar_metrics_APIFY.csv')

results = []

print("Starting batch crawl...")
for idx, row in df.iterrows():
    csv_name = row['Name']
    dept = row['Department']
    print(f"[{idx+1}/{len(df)}] Searching for {csv_name}...")
    
    names = csv_name.split(' ')
    first = names[0]
    last = ' '.join(names[1:]) if len(names) > 1 else ''
    full_name = f"{first} {last}".strip()
    
    query = f'{full_name}'
    
    user_id = None
    try:
        run_input = {
            "query": query,
            "maxResults": 20,
            "includeDetails": False,
            "compact": False
        }
        run = client.actor('blackfalcondata/google-scholar-scraper').call(run_input=run_input)
        dataset_id = run.get('defaultDatasetId') if isinstance(run, dict) else run.default_dataset_id
        
        for item in client.dataset(dataset_id).iterate_items():
            res_name = (item.get('name') or '').lower()
            res_id = item.get('userId')
            if not res_id: continue
            
            last_lower = last.lower()
            
            last_parts = [p for p in last_lower.replace('-', ' ').split() if len(p) > 2]
            first_parts = [p for p in first.lower().replace('-', ' ').split() if len(p) > 2]
            all_parts = last_parts + first_parts
            name_match = any(p in res_name for p in all_parts) if all_parts else (last_lower in res_name)
            
            if name_match:
                # We have a name match, now check the profile directly for email
                temp_metrics = scrape_scholar_metrics(res_id)
                if temp_metrics:
                    email_domain_apify = (item.get('verifiedEmailDomain') or '').lower()
                    email_profile = (temp_metrics.get('Verified_Email') or '').lower()
                    
                    if 'unilag' in email_domain_apify or 'unilag' in email_profile:
                        user_id = res_id
                        metrics = temp_metrics
                        break
    except Exception as e:
        print("  Error searching:", e)
        
    if user_id and metrics:
        print(f"  Found ID: {user_id}. Scraping metrics...")
        if metrics:
            profile_name = metrics.get('Exact_Name', full_name)
            title = ""
            prefixes = ["prof. ", "prof ", "professor ", "dr. ", "dr ", "mr. ", "mr ", "mrs. ", "mrs ", "engr. ", "engr ", "arc. ", "arc ", "pharm. ", "pharm "]
            lname = profile_name.lower()
            for p in prefixes:
                if lname.startswith(p):
                    title = p.strip().capitalize()
                    if title == "Prof": title = "Prof."
                    elif title == "Dr": title = "Dr."
                    elif title == "Mr": title = "Mr."
                    elif title == "Mrs": title = "Mrs."
                    elif title == "Engr": title = "Engr."
                    elif title == "Arc": title = "Arc."
                    elif title == "Pharm": title = "Pharm."
                    profile_name = profile_name[len(p):].strip()
                    break
                    
            results.append({
                "Title": title,
                "Name": profile_name,
                "Department": dept,
                "Profile_URL": f"https://scholar.google.com/citations?user={user_id}",
                "Citations_All": metrics.get("Citations_All", "0"),
                "Citations_Since_2021": metrics.get("Citations_Since_2021", "0"),
                "H_Index_All": metrics.get("H_Index_All", "0"),
                "H_Index_Since_2021": metrics.get("H_Index_Since_2021", "0"),
                "I10_Index_All": metrics.get("I10_Index_All", "0"),
                "I10_Index_Since_2021": metrics.get("I10_Index_Since_2021", "0")
            })
            print("  Success!")
            continue

    print("  Failed to match profile.")
    results.append({
        "Title": "", "Name": csv_name, "Department": dept, "Profile_URL": "",
        "Citations_All": "N/A", "Citations_Since_2021": "N/A",
        "H_Index_All": "N/A", "H_Index_Since_2021": "N/A",
        "I10_Index_All": "N/A", "I10_Index_Since_2021": "N/A"
    })

df_new = pd.DataFrame(results)
df_new.to_csv('chemistry_scholar_metrics_APIFY_Updated.csv', index=False)
print("Saved to chemistry_scholar_metrics_APIFY_Updated.csv")

