import requests

SERP_API_KEY = "2ed52345511b01799298bc6f86b4d451717f9b8c0df4e2860d5b5d38ce62f790"
url = f"https://serpapi.com/search.json?engine=google_scholar_author&author_id=I02xXeUAAAAJ&api_key={SERP_API_KEY}"

try:
    response = requests.get(url, timeout=30)
    print("Status:", response.status_code)
    if response.status_code == 200:
        data = response.json()
        print("Citations:", data.get("cited_by", {}).get("table"))
except Exception as e:
    print("Error:", e)
