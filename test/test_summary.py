"""
Comprehensive test summary for mb_app.py
"""
import sys
import os
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mb_app import generate_image, GEMINI_3_MODEL_ID, GEMINI_25_MODEL_ID
from gradio_client import Client


def test_direct_function():
    """Test the generate_image function directly"""
    print("=" * 60)
    print("Test 1: Direct Function Test")
    print("=" * 60)
    
    try:
        # Check API key
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            print("❌ API key not found")
            return False
        
        print("✅ API key found")
        
        # Test with both models
        test_prompt = "A minimalist fashion moodboard"
        template = ""  # Use default template
        
        print(f"\nTesting with model: {GEMINI_3_MODEL_ID}")
        # generate_image now requires 3 parameters: user_input, model_id, template
        result1 = generate_image(test_prompt, GEMINI_3_MODEL_ID, template)
        if result1 and hasattr(result1, 'size'):
            print(f"✅ Model 1: Generated image with size {result1.size}")
        else:
            print("❌ Model 1: Failed")
            return False
        
        print(f"\nTesting with model: {GEMINI_25_MODEL_ID}")
        result2 = generate_image(test_prompt, GEMINI_25_MODEL_ID, template)
        if result2 and hasattr(result2, 'size'):
            print(f"✅ Model 2: Generated image with size {result2.size}")
        else:
            print("❌ Model 2: Failed")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_gradio_api():
    """Test Gradio API endpoints"""
    print("\n" + "=" * 60)
    print("Test 2: Gradio API Test")
    print("=" * 60)
    
    try:
        client = Client("http://127.0.0.1:7860")
        print("✅ Connected to Gradio server")
        
        # Test endpoint 1: /generate_image (button click)
        print("\nTesting endpoint: /generate_image (button click)")
        result1 = client.predict(
            "A modern fashion moodboard with vibrant colors",
            "gemini-3-pro-image-preview",
            "",  # template (empty string = use default)
            api_name="/generate_image"
        )
        if result1:
            # Result can be dict with path/url or PIL Image
            if isinstance(result1, dict):
                print(f"✅ Endpoint 1: Image generated successfully")
                print(f"   Path: {result1.get('path', 'N/A')}")
            else:
                print("✅ Endpoint 1: Image generated successfully")
        else:
            print("❌ Endpoint 1: Failed")
            return False
        
        # Test endpoint 2: /generate_image_1 (Enter key submission)
        print("\nTesting endpoint: /generate_image_1 (Enter key submission)")
        result2 = client.predict(
            "A vintage fashion moodboard with earth tones",
            "gemini-2.5-flash-image",
            "",  # template (empty string = use default)
            api_name="/generate_image_1"
        )
        if result2:
            # Result can be dict with path/url or PIL Image
            if isinstance(result2, dict):
                print(f"✅ Endpoint 2: Image generated successfully")
                print(f"   Path: {result2.get('path', 'N/A')}")
            else:
                print("✅ Endpoint 2: Image generated successfully")
        else:
            print("❌ Endpoint 2: Failed")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("Comprehensive Test Suite for mb_app.py")
    print("=" * 60)
    
    results = []
    
    # Test 1: Direct function
    results.append(("Direct Function Test", test_direct_function()))
    
    # Test 2: Gradio API (requires server running)
    print("\n" + "=" * 60)
    print("NOTE: Make sure mb_app.py is running for API tests")
    print("=" * 60)
    results.append(("Gradio API Test", test_gradio_api()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Final Test Summary")
    print("=" * 60)
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(result[1] for result in results)
    print("=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("\nmb_app.py is working correctly with:")
        print("  - Direct function calls")
        print("  - Gradio API endpoints")
        print("  - Both Gemini models (3 Pro and 2.5 Flash)")
        print("  - Both input methods (button click and Enter key)")
    else:
        print("❌ Some tests failed")
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

