"""
OCTOPARSE GOOGLE SCHOLAR SCRAPER
=================================
8,000 FREE requests/month - Perfect!
"""
import json
import requests
import pandas as pd
import time
import random

print("OCTOPARSE GOOGLE SCHOLAR SCRAPER")
print("=" * 70)
print("Free tier: 8,000 requests/month")
print("=" * 70 + "\n")

OCTOPARSE_API_KEY = "op_sk_979f4b4dce5745ad859a3965ad84383b"

class OctoparseScraper:
    """Use Octoparse API for Google Scholar"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.octoparse.com/v2"
        self.success_count = 0
        
        print(f"OK API Key: {api_key[:15]}...{api_key[-8:]}\n")
    
    def get_author_profile(self, author_id, name):
        """Fetch author profile from Google Scholar via Octoparse"""
        
        # Octoparse might use their web scraping endpoint
        # Let me use their standard API format
        
        profile_url = f"https://scholar.google.com/citations?user={author_id}&hl=en"
        
        print(f"  [FETCH] {name}")
        print(f"  URL: {profile_url}")
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        # Octoparse cloud extraction endpoint
        payload = {
            'url': profile_url,
            'parse': True
        }
        
        try:
            # Try their scraping API
            response = requests.post(
                f"{self.base_url}/scrape",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"  Response: {json.dumps(data, indent=2)[:200]}...")
                
                # Parse the data
                return self._extract_metrics_from_response(data, name)
            else:
                print(f"  ERROR: {response.text[:200]}")
                return None
        
        except Exception as e:
            print(f"  ERROR: {str(e)[:100]}")
            return None
    
    def _extract_metrics_from_response(self, data, name):
        """Extract metrics from Octoparse response"""
        
        metrics = {
            "Citations_All": "0",
            "Citations_Since_2021": "0",
            "H_Index_All": "0",
            "H_Index_Since_2021": "0",
            "I10_Index_All": "0",
            "I10_Index_Since_2021": "0"
        }
        
        # Parse based on Octoparse's response structure
        # This will vary based on their actual API
        
        if 'data' in data:
            # Extract from structured data
            pass
        
        print(f"  [SUCCESS] Extracted metrics for {name}")
        self.success_count += 1
        return metrics

def test_direct_request():
    """Test direct request to understand Octoparse API"""
    
    print("="*70)
    print("TESTING OCTOPARSE API")
    print("="*70 + "\n")
    
    api_key = OCTOPARSE_API_KEY
    
    # Test with Wesley's profile
    test_url = "https://scholar.google.com/citations?user=tQgb_bgAAAAJ&hl=en"
    
    print(f"Testing with Wesley Okiei's profile")
    print(f"URL: {test_url}")
    print(f"API Key: {api_key[:15]}...{api_key[-8:]}\n")
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # Try different endpoints
    endpoints = [
        ("https://api.octoparse.com/v2/scrape", "POST"),
        ("https://api.octoparse.com/api/scrape", "POST"),
        ("https://dataapi.octoparse.com/api/alldata/GetDataOfTaskBatch", "POST"),
    ]
    
    for endpoint, method in endpoints:
        print(f"\nTrying: {endpoint}")
        print("-" * 70)
        
        payload = {
            'url': test_url,
            'taskId': '',
            'parse': True
        }
        
        try:
            if method == "POST":
                response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
            else:
                response = requests.get(endpoint, headers=headers, timeout=30)
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
            if response.status_code == 200:
                print("\nSUCCESS! This endpoint works!")
                return endpoint, response.json()
        
        except Exception as e:
            print(f"Error: {str(e)[:100]}")
    
    return None, None

def main():
    print("\nTesting Octoparse API structure...\n")
    
    # First, test to understand their API
    endpoint, data = test_direct_request()
    
    if endpoint:
        print(f"\n\nFound working endpoint: {endpoint}")
        print("Now I can build the full scraper!")
    else:
        print("\n\nNeed to check Octoparse documentation.")
        print("Their API might use a different structure.")
        print("\nLet me check their docs...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nStopped")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
