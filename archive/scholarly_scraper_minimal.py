import json
import time
import pandas as pd
from scholarly import scholarly

print("Running Scholarly Scraper...")

with open('chemistry_staff_cleaned.json', 'r', encoding='utf-8') as f:
    staff_list = json.load(f)

results = []

for staff in staff_list:
    name = staff['name']
    department = staff.get('department', 'Chemistry')
    print(f"Processing: {name}")
    
    record = {
        "Name": name, "Department": department,
        "Citations_All": "N/A", "Citations_Since_2021": "N/A",
        "H_Index_All": "N/A", "H_Index_Since_2021": "N/A",
        "I10_Index_All": "N/A", "I10_Index_Since_2021": "N/A"
    }
    
    try:
        search_query = scholarly.search_author(name + " University of Lagos")
        author = next(search_query, None)
        
        if author:
            print(f"Found author: {author['name']}")
            author = scholarly.fill(author, sections=['indices'])
            
            record["Citations_All"] = author.get('citedby', "0")
            record["Citations_Since_2021"] = author.get('citedby5y', "0")
            record["H_Index_All"] = author.get('hindex', "0")
            record["H_Index_Since_2021"] = author.get('hindex5y', "0")
            record["I10_Index_All"] = author.get('i10index', "0")
            record["I10_Index_Since_2021"] = author.get('i10index5y', "0")
        else:
            print("Not found.")
    except Exception as e:
        print(f"Error for {name}: {e}")
        
    results.append(record)
    time.sleep(2)

df = pd.DataFrame(results)
output_file = 'chemistry_scholar_metrics_SCHOLARLY.csv'
df.to_csv(output_file, index=False)
print(f"Done! Saved to {output_file}")
