import requests

def test_google():
    profile_url = "https://scholar.google.com/citations?user=I02xXeUAAAAJ&hl=en"
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    try:
        response = requests.get(profile_url, headers=HEADERS, timeout=15)
        print(f"Status Code: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

test_google()
