"""
Test mb_app.py using Gradio's client API
"""
import sys
from pathlib import Path

try:
    from gradio_client import Client
except ImportError:
    print("Installing gradio_client...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "gradio_client"])
    from gradio_client import Client


def test_gradio_client():
    """Test the Gradio app using the client API"""
    print("=" * 60)
    print("Testing mb_app.py with Gradio Client API")
    print("=" * 60)
    
    try:
        # Connect to the running Gradio app
        print("\nConnecting to Gradio app at http://127.0.0.1:7860...")
        client = Client("http://127.0.0.1:7860")
        
        print("✅ Connected successfully")
        print(f"   API endpoint: {client.api_url}")
        
        # Test the endpoint directly
        print("\nTesting image generation endpoint...")
        print("   Prompt: 'A simple fashion moodboard with neutral colors'")
        print("   Model: gemini-3-pro-image-preview")
        print("   Using endpoint: /generate_image")
        
        # Call the endpoint (now requires 3 parameters: subject, model, template)
        result = client.predict(
            "A simple fashion moodboard with neutral colors and minimalist design",
            "gemini-3-pro-image-preview",
            "",  # template (empty string = use default)
            api_name="/generate_image"
        )
        
        print("✅ Image generation successful!")
        print(f"   Result type: {type(result)}")
        if result:
            if isinstance(result, dict):
                print(f"   Image path: {result.get('path', 'N/A')}")
                print(f"   Image URL: {result.get('url', 'N/A')[:80] if result.get('url') else 'N/A'}...")
                print(f"   Image size: {result.get('size', 'N/A')} bytes")
                print(f"   Original name: {result.get('orig_name', 'N/A')}")
            elif isinstance(result, str):
                print(f"   Image path: {result}")
            else:
                print(f"   Result: {str(result)[:100]}...")
        
        return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_gradio_client()
    sys.exit(0 if success else 1)

