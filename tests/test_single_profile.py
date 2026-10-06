"""
Test single profile - Babajide Alo
"""
from apify_client import ApifyClient

APIFY_TOKEN = "YOUR_APIFY_TOKEN"

client = ApifyClient(APIFY_TOKEN)

# Test Babajide Alo's profile
profile_url = "https://scholar.google.com/citations?user=gklRvzMAAAAJ&hl=en"

print("Testing Babajide Alo's profile...")
print(f"URL: {profile_url}\n")

run_input = {
    "startUrls": [profile_url],
    "maxItems": 1,
    "includeDetails": True
}

print("Running Apify actor...")
run = client.actor("blackfalcondata/google-scholar-scraper").call(run_input=run_input)

print(f"Status: {run.status}\n")

# Get results
print("Results:")
for item in client.dataset(run.default_dataset_id).iterate_items():
    print(f"Name: {item.get('name')}")
    print(f"User ID: {item.get('userId')}")
    print(f"Affiliation: {item.get('affiliation')}")
    print(f"Citations: {item.get('citations')}")
    print(f"Citations Since Year: {item.get('citationsSinceYear')}")
    print(f"H-index: {item.get('hIndex')}")
    print(f"H-index Since Year: {item.get('hIndexSinceYear')}")
    print(f"\nFull data:")
    import json
    print(json.dumps(item, indent=2))

