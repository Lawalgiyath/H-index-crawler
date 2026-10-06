from scholarly import scholarly, ProxyGenerator
import os

token = "YOUR_APIFY_TOKEN"
proxy_url = f"http://auto:{token}@proxy.apify.com:8000"

pg = ProxyGenerator()
pg.SingleProxy(http=proxy_url, https=proxy_url)
scholarly.use_proxy(pg)

try:
    search_query = scholarly.search_author('Luqman Adams University of Lagos')
    author = next(search_query)
    print("Found user_id:", author.get('scholar_id'))
except Exception as e:
    print("Error:", e)

