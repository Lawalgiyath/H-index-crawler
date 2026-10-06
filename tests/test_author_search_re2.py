from apify_client import ApifyClient
import re
client = ApifyClient("YOUR_APIFY_TOKEN")
url = "https://scholar.google.com/citations?view_op=search_authors&hl=en&mauthors=Luqman+Adams"
run_input = {
    "startUrls": [{"url": url}],
    "pageFunction": "async function pageFunction(context) { const $ = context.$; return { html: $('body').html() }; }",
    "proxyConfiguration": {"useApifyProxy": True}
}
run = client.actor('apify/cheerio-scraper').call(run_input=run_input)
for item in client.dataset((run.get('defaultDatasetId') if isinstance(run, dict) else run.default_dataset_id)).iterate_items():
    html = item.get("html", "")
    matches = re.findall(r'user=([^&"\'\\]+)', html)
    print("Found user IDs:", set(matches))

