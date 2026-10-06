import requests
from bs4 import BeautifulSoup
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
resp = requests.get("https://scholar.google.com/citations?user=HemfnRwAAAAJ&hl=en", headers=HEADERS)
soup = BeautifulSoup(resp.text, "html.parser")
affil = soup.select(".gsc_prf_il")
for idx, el in enumerate(affil):
    print(f"[{idx}] {el.text}")
