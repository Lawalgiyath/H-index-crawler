import requests
from bs4 import BeautifulSoup

url = "https://scholar.google.com/citations?user=I02xXeUAAAAJ&hl=en"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
resp = requests.get(url, headers=headers)
soup = BeautifulSoup(resp.text, "html.parser")
name = soup.find("div", {"id": "gsc_prf_in"})
affil = soup.find("div", {"class": "gsc_prf_il"})
print("Name:", name.text if name else "None")
print("Affil:", affil.text if affil else "None")
