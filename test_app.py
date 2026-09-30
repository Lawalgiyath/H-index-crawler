"""
Test script for the Scholar Metrics Scraper
"""
import requests
import json
import time

def test_flask_app():
    """Test if the Flask app is running and responsive"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing University of Lagos Scholar Metrics Scraper\n")
    print("=" * 60)
    
    # Test 1: Check if server is running
    print("\n1. Testing server connectivity...")
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200:
            print("   ✓ Server is running and accessible")
        else:
            print(f"   ✗ Server returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ✗ Cannot connect to server. Is it running?")
        print("   💡 Run: python Crawlee.py")
        return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test 2: Check if HTML content is served
    print("\n2. Checking web interface...")
    if "University of Lagos" in response.text:
        print("   ✓ Web interface loaded successfully")
    else:
        print("   ✗ Web interface content not found")
        return False
    
    # Test 3: Test file upload endpoint with sample data
    print("\n3. Testing scraper endpoint...")
    try:
        # Read test sample
        with open('test_sample.json', 'r') as f:
            test_data = f.read()
        
        # Prepare file upload
        files = {
            'file': ('test_sample.json', test_data, 'application/json')
        }
        
        print("   ⏳ Uploading test file (this may take a minute)...")
        response = requests.post(
            f"{base_url}/crawl",
            files=files,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("   ✓ Scraper endpoint working")
                print(f"   ✓ Processed {len(result.get('results', []))} records")
                
                # Display sample results
                if result.get('results'):
                    print("\n   Sample result:")
                    first_result = result['results'][0]
                    print(f"     Name: {first_result.get('Name', 'N/A')}")
                    print(f"     Citations (All): {first_result.get('Citations_All', 'N/A')}")
                    print(f"     H-Index (All): {first_result.get('H_Index_All', 'N/A')}")
            else:
                print(f"   ✗ Scraper returned error: {result.get('error', 'Unknown')}")
                return False
        else:
            print(f"   ✗ Request failed with status code: {response.status_code}")
            return False
    
    except FileNotFoundError:
        print("   ⚠️  test_sample.json not found - skipping scraper test")
    except Exception as e:
        print(f"   ✗ Error testing scraper: {e}")
        return False
    
    # Final summary
    print("\n" + "=" * 60)
    print("✓ All tests passed successfully!")
    print("\n📊 Your application is ready to use!")
    print(f"\n🌐 Open your browser and visit: {base_url}")
    print("\n💡 To test with real data:")
    print("   1. Open the web interface")
    print("   2. Upload test_sample.json or chemistry_staff.json")
    print("   3. Click 'Start Scholar Crawler'")
    print("   4. Download results as CSV")
    
    return True

if __name__ == "__main__":
    print("\n" + "🎓" * 30 + "\n")
    success = test_flask_app()
    print("\n" + "🎓" * 30 + "\n")
    
    if not success:
        print("⚠️  Some tests failed. Please check the errors above.")
        exit(1)
