from scholarly import scholarly, ProxyGenerator
import os

token = "YOUR_APIFY_TOKEN"
proxy_url = f"http://auto:{token}@proxy.apify.com:8000"

pg = ProxyGenerator()
pg.SingleProxy(http=proxy_url, https=proxy_url)
scholarly.use_proxy(pg)

try:
    search_query = scholarly.search_author('Luqman Adams')
    for i in range(2):
        author = next(search_query)
        print("Found user:", author.get('name'), "Affiliation:", author.get("affiliation"), "ID:", author.get("scholar_id"))
except Exception as e:
    print("Error:", e)

