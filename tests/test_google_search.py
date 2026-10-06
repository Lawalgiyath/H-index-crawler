"""
Test Google search to see what we actually get
"""
import requests
from bs4 import BeautifulSoup
import urllib.parse
import re

name = "Lawrence Ekebafe"
query = f"{name} university of lagos google scholar"
encoded = urllib.parse.quote(query)
url = f"https://www.google.com/search?q={encoded}"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

print(f"Query: {query}")
print(f"URL: {url}\n")

response = requests.get(url, headers=headers, timeout=30)

print(f"Status: {response.status_code}")

if response.status_code == 200:
    html = response.text
    
    # Save HTML for inspection
    with open('google_search_result.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Saved HTML to: google_search_result.html")
    print(f"HTML length: {len(html)} chars\n")
    
    # Check for blocks
    if 'captcha' in html.lower():
        print("WARNING: CAPTCHA detected!")
    if 'unusual traffic' in html.lower():
        print("WARNING: Rate limit detected!")
    
    # Look for scholar URLs
    soup = BeautifulSoup(html, "html.parser")
    
    print("\n--- Looking for scholar.google.com links ---")
    
    # Method 1: All links
    links = soup.find_all('a', href=True)
    scholar_count = 0
    
    for link in links:
        href = link.get('href', '')
        if 'scholar.google.com' in href:
            scholar_count += 1
            print(f"\nScholar link #{scholar_count}:")
            print(f"  {href[:200]}")
            
            # Extract user ID
            if 'user=' in href:
                match = re.search(r'user=([a-zA-Z0-9_-]+)', href)
                if match:
                    print(f"  USER ID: {match.group(1)}")
    
    # Method 2: Search raw HTML
    print("\n--- Searching raw HTML ---")
    scholar_matches = re.findall(r'scholar\.google\.com[^"<>]*?user=([a-zA-Z0-9_-]+)', html)
    if scholar_matches:
        print(f"Found {len(scholar_matches)} user IDs in raw HTML:")
        for uid in set(scholar_matches):
            print(f"  {uid}")
    else:
        print("No user IDs found in raw HTML")
    
    # Method 3: Look for any scholar.google.com mention
    if 'scholar.google.com' in html:
        print(f"\n'scholar.google.com' appears {html.count('scholar.google.com')} times in HTML")
        # Show context around first occurrence
        idx = html.find('scholar.google.com')
        if idx >= 0:
            context = html[max(0, idx-100):min(len(html), idx+300)]
            print(f"\nContext around first occurrence:")
            print(context)
    else:
        print("\n'scholar.google.com' NOT found in HTML at all!")
        print("\nThis means Google might be blocking or not showing Scholar results.")

else:
    print(f"Error: Status {response.status_code}")
