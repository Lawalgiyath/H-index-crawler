from apify_client import ApifyClient
client = ApifyClient("YOUR_APIFY_TOKEN")
run_input = {
    "startUrls": [{"url": "https://scholar.google.com/citations?user=I02xXeUAAAAJ&hl=en"}],
    "pageFunction": "async function pageFunction(context) { const $ = context.$; return { html: $('body').html() }; }",
    "proxyConfiguration": {"useApifyProxy": True}
}
run = client.actor('apify/cheerio-scraper').call(run_input=run_input)
for item in client.dataset(run.default_dataset_id).iterate_items():
    print(len(item.get("html", "")))

