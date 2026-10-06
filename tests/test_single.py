import requests
from bs4 import BeautifulSoup

# Test fetching Wesley Okiei's profile
url = 'https://scholar.google.com/citations?user=tQgb_bgAAAAJ&hl=en'
api_key = '4052c653946f503496a6df02ed39f9d9'

print("Testing ScraperAPI with Wesley Okiei's profile...")
print(f"URL: {url}\n")

response = requests.get(
    'http://api.scraperapi.com',
    params={
        'api_key': api_key, 
        'url': url,
        'premium': 'true'  # Required for Google Scholar!
    },
    timeout=60
)

print(f"Status Code: {response.status_code}\n")

if response.status_code == 200:
    # Save for inspection
    with open('wesley_profile.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    print("Saved HTML to wesley_profile.html")
    
    # Parse and extract metrics
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the citation stats table
    table_rows = soup.select('#gsc_rsb_st tr')
    
    print(f"\nFound {len(table_rows)} table rows\n")
    
    if table_rows:
        print("Extracted Metrics:")
        print("-" * 60)
        for row in table_rows:
            header = row.select_one('.gsc_rsb_sc1')
            values = row.select('.gsc_rsb_std')
            
            if header and len(values) >= 2:
                label = header.text.strip()
                all_val = values[0].text.strip()
                since_2021 = values[1].text.strip()
                print(f"{label:20} All: {all_val:10} Since 2021: {since_2021}")
        
        print("\nEXPECTED:")
        print("-" * 60)
        print("Citations            All: 1079       Since 2021: 370")
        print("h-index              All: 17         Since 2021: 9")
        print("i10-index            All: 19         Since 2021: 9")
    else:
        print("ERROR: No table found!")
        print("This might mean:")
        print("1. Wrong CSS selector")
        print("2. Page structure different")
        print("3. Need to render JavaScript")
        print("\nSaving HTML for manual inspection...")
else:
    print(f"ERROR: {response.text[:500]}")
