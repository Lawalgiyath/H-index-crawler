import requests, bs4, urllib.parse
query = urllib.parse.quote('Maureen Egenti')
url = f'https://scholar.google.com/citations?view_op=search_authors&hl=en&mauthors={query}'
print(url)
r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
s = bs4.BeautifulSoup(r.text, 'html.parser')
link = s.select_one('.gs_ai_pho a')
print('Found link:', link.get('href') if link else 'None')
