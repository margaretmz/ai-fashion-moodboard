"""
Comprehensive test for Gradio API endpoints
"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:7860"


def test_main_page():
    """Test if main page is accessible"""
    print("Testing main page...")
    try:
        response = requests.get(BASE_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Main page accessible")
            return True
        else:
            print(f"❌ Main page returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accessing main page: {e}")
        return False


def test_api_info():
    """Test API info endpoint"""
    print("\nTesting /api/info endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/info", timeout=5)
        if response.status_code == 200:
            info = response.json()
            endpoints = info.get('named_endpoints', {})
            print(f"✅ API info retrieved: {len(endpoints)} endpoints found")
            for endpoint in list(endpoints.keys())[:5]:  # Show first 5
                print(f"   - {endpoint}")
            return True
        else:
            print(f"⚠️  /api/info returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"⚠️  Could not test /api/info: {e}")
        return False


def test_api_predict():
    """Test the predict endpoint for image generation"""
    print("\nTesting /api/predict endpoint (image generation)...")
    
    # Get API info first to find the correct endpoint
    try:
        info_response = requests.get(f"{BASE_URL}/api/info", timeout=5)
        if info_response.status_code == 200:
            info = info_response.json()
            endpoints = info.get('named_endpoints', {})
            
            # Find the generate_image endpoint
            generate_endpoint = None
            for endpoint_name, endpoint_info in endpoints.items():
                if 'generate_image' in endpoint_name.lower() or 'predict' in endpoint_name.lower():
                    generate_endpoint = endpoint_name
                    break
            
            if not generate_endpoint:
                # Try to find any predict endpoint
                generate_endpoint = list(endpoints.keys())[0] if endpoints else None
            
            if generate_endpoint:
                print(f"Found endpoint: {generate_endpoint}")
                
                # Prepare test data (now requires 3 parameters: subject, model, template)
                test_data = {
                    "data": [
                        "A simple fashion moodboard with neutral colors and minimalist design",
                        "gemini-3-pro-image-preview",
                        ""  # template (empty string = use default)
                    ],
                    "event_data": None,
                    "fn_index": 0,
                    "trigger_id": 0,
                    "session_hash": None
                }
                
                print("Sending request to generate image...")
                response = requests.post(
                    f"{BASE_URL}/api/predict",
                    json=test_data,
                    timeout=120  # Image generation can take time
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print("✅ Image generation request successful")
                    print(f"   Response keys: {list(result.keys())}")
                    if 'data' in result:
                        print(f"   Data type: {type(result['data'])}")
                    return True
                else:
                    print(f"❌ Request failed with status {response.status_code}")
                    print(f"   Response: {response.text[:200]}")
                    return False
            else:
                print("⚠️  Could not find generate_image endpoint")
                return False
        else:
            print("⚠️  Could not get API info")
            return False
    except Exception as e:
        print(f"❌ Error testing predict endpoint: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_static_files():
    """Test if static files are accessible"""
    print("\nTesting static files...")
    try:
        # Test favicon or other static assets
        response = requests.get(f"{BASE_URL}/favicon.ico", timeout=5)
        # 404 is OK, we just want to make sure the server responds
        print(f"✅ Static file endpoint responds (status: {response.status_code})")
        return True
    except Exception as e:
        print(f"⚠️  Static file test: {e}")
        return False


def run_all_tests():
    """Run all API tests"""
    print("=" * 60)
    print("Testing Gradio API Endpoints")
    print("=" * 60)
    
    results = []
    
    results.append(("Main Page", test_main_page()))
    results.append(("API Info", test_api_info()))
    results.append(("Static Files", test_static_files()))
    results.append(("Image Generation API", test_api_predict()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(result[1] for result in results)
    print("=" * 60)
    if all_passed:
        print("✅ All API tests passed!")
    else:
        print("⚠️  Some tests had issues (this may be normal)")
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    run_all_tests()

