import requests

SCRAPER_API_KEY = "5a2b16d3fbbbd6fc82e6d63428d022df"
url = "https://scholar.google.com/citations?user=I02xXeUAAAAJ&hl=en"
scraper_url = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={url}"

try:
    response = requests.get(scraper_url, timeout=30)
    print("Status:", response.status_code)
    if response.status_code == 200:
        print("Success! len:", len(response.text))
except Exception as e:
    print("Error:", e)
