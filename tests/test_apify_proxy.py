import requests
import os
import urllib3
urllib3.disable_warnings()

APIFY_TOKEN = "YOUR_APIFY_TOKEN"
proxy_url = f"http://auto:{APIFY_TOKEN}@proxy.apify.com:8000"
proxies = {"http": proxy_url, "https": proxy_url}
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
profile_url = "https://scholar.google.com/citations?user=I02xXeUAAAAJ&hl=en"
try:
    response = requests.get(profile_url, headers=HEADERS, proxies=proxies, timeout=15, verify=False)
    print("Status:", response.status_code)
    if response.status_code == 200:
        print("Success! len:", len(response.text))
except Exception as e:
    print("Error:", e)

