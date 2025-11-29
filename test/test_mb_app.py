"""
Test script for mb_app.py Gradio API functionality
"""
import os
import sys
import time
import requests
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the app components
from mb_app import generate_image, GEMINI_3_MODEL_ID, GEMINI_25_MODEL_ID, DEFAULT_MODEL_ID


def test_api_key_available():
    """Test if API key is available"""
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("❌ ERROR: GEMINI_API_KEY or GOOGLE_API_KEY not set")
        return False
    print("✅ API key found")
    return True


def test_generate_image_function():
    """Test the generate_image function directly"""
    print("\n=== Testing generate_image function ===")
    
    # Check API key
    if not test_api_key_available():
        return False
    
    try:
        # Test with a simple prompt
        test_prompt = "A simple fashion moodboard with neutral colors"
        print(f"Testing with prompt: '{test_prompt}'")
        print(f"Using model: {DEFAULT_MODEL_ID}")
        print(f"Using default template (empty string)")
        
        # generate_image now requires 3 parameters: user_input, model_id, template
        result = generate_image(test_prompt, DEFAULT_MODEL_ID, "")
        
        if result is None:
            print("❌ ERROR: generate_image returned None")
            return False
        
        # Check if it's a PIL Image
        if not hasattr(result, 'size'):
            print("❌ ERROR: Result is not a PIL Image")
            return False
        
        print(f"✅ generate_image returned a PIL Image with size: {result.size}")
        return True
        
    except Exception as e:
        print(f"❌ ERROR in generate_image: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_gradio_api(port=7860, timeout=30):
    """Test Gradio API endpoints"""
    print("\n=== Testing Gradio API endpoints ===")
    
    base_url = f"http://127.0.0.1:{port}"
    
    # Wait for server to be ready
    print(f"Waiting for Gradio server to start on port {port}...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{base_url}/", timeout=2)
            if response.status_code == 200:
                print("✅ Gradio server is running")
                break
        except requests.exceptions.RequestException:
            time.sleep(1)
    else:
        print(f"❌ ERROR: Gradio server did not start within {timeout} seconds")
        return False
    
    # Test API info endpoint
    try:
        print("Testing /api/info endpoint...")
        response = requests.get(f"{base_url}/api/info", timeout=5)
        if response.status_code == 200:
            info = response.json()
            print(f"✅ API info retrieved: {len(info.get('named_endpoints', []))} endpoints found")
        else:
            print(f"⚠️  Warning: /api/info returned status {response.status_code}")
    except Exception as e:
        print(f"⚠️  Warning: Could not test /api/info: {str(e)}")
    
    # Test if we can access the main page
    try:
        print("Testing main page access...")
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Main page accessible")
        else:
            print(f"❌ ERROR: Main page returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ ERROR: Could not access main page: {str(e)}")
        return False
    
    return True


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Testing mb_app.py Functionality")
    print("=" * 60)
    
    results = []
    
    # Test 1: API key availability
    results.append(("API Key Check", test_api_key_available()))
    
    # Test 2: Direct function test (only if API key is available)
    if results[0][1]:
        results.append(("generate_image Function", test_generate_image_function()))
    
    # Test 3: Gradio API (requires server to be running)
    print("\n" + "=" * 60)
    print("NOTE: For Gradio API tests, make sure mb_app.py is running")
    print("Start it with: python mb_app.py")
    print("=" * 60)
    
    # Try to test Gradio API
    results.append(("Gradio API", test_gradio_api()))
    
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
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed")
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

