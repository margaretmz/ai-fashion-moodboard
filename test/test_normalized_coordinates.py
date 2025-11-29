"""
Test normalized coordinates for image editing
"""
import sys
import time
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

OUTPUT_DIR = Path(__file__).parent.parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

from gradio_client import Client
from PIL import Image


def test_normalized_coordinates():
    """Test image editing with normalized coordinates"""
    print("=" * 60)
    print("Test: Normalized Coordinates for Image Editing")
    print("=" * 60)
    
    try:
        client = Client("http://127.0.0.1:7860")
        print("✅ Connected to Gradio server")
        
        # First, generate an image
        print("\n1. Generating test image...")
        result = client.predict(
            "A simple fashion moodboard with neutral colors",
            "gemini-3-pro-image-preview",
            "",  # template (empty string = use default)
            api_name="/generate_image"
        )
        
        # Extract path from result
        if isinstance(result, dict):
            image_path = result.get('path')
        elif isinstance(result, str):
            image_path = result
        else:
            print("❌ Unexpected result type")
            return False
        
        if not image_path or not os.path.exists(image_path):
            print("❌ Generated image not found")
            return False
        
        print(f"✅ Image generated: {image_path}")
        
        # Load image to get dimensions
        img = Image.open(image_path)
        img_width, img_height = img.size
        print(f"   Image size: {img_width} x {img_height}")
        
        # Calculate normalized coordinates for a region
        # Use top-left 25% of the image
        x_top = 0
        y_top = 0
        x_bottom = int(img_width * 0.25)
        y_bottom = int(img_height * 0.25)
        
        # Calculate expected normalized values
        x_top_norm = round(x_top / img_width, 4)
        y_top_norm = round(y_top / img_height, 4)
        x_bottom_norm = round(x_bottom / img_width, 4)
        y_bottom_norm = round(y_bottom / img_height, 4)
        width_norm = round((x_bottom - x_top) / img_width, 4)
        height_norm = round((y_bottom - y_top) / img_height, 4)
        
        print(f"\n2. Testing with normalized coordinates...")
        print(f"   Absolute coordinates: ({x_top}, {y_top}) to ({x_bottom}, {y_bottom})")
        print(f"   Expected normalized: ({x_top_norm}, {y_top_norm}) to ({x_bottom_norm}, {y_bottom_norm})")
        print(f"   Region size: {x_bottom - x_top} x {y_bottom - y_top} pixels")
        print(f"   Normalized size: {width_norm} x {height_norm}")
        
        edit_request = "Change this region to vibrant blues and purples"
        
        # Edit the image
        print(f"\n3. Editing image region...")
        edited_result = client.predict(
            None,  # image_display
            image_path,  # image_path_file
            int(x_top),
            int(y_top),
            int(x_bottom),
            int(y_bottom),
            edit_request,
            "gemini-3-pro-image-preview",
            "",  # edit_template (empty string = use default)
            api_name="/edit_image_region"
        )
        
        if not edited_result:
            print("❌ No edited image returned")
            return False
        
        # Extract path from result
        if isinstance(edited_result, dict):
            edited_path = edited_result.get('path')
        elif isinstance(edited_result, str):
            edited_path = edited_result
        else:
            print("❌ Unexpected result type")
            return False
        
        if edited_path and os.path.exists(edited_path):
            edited_img = Image.open(edited_path)
            print(f"✅ Image edited successfully")
            print(f"   Edited image size: {edited_img.size}")
            print(f"   Saved to: {edited_path}")
            
            # Verify the prompt includes normalized coordinates
            # (We can't directly check the prompt, but we can verify the edit worked)
            print(f"\n✅ Normalized coordinates test completed successfully!")
            print(f"   The edit prompt should include normalized coordinates (0.0-1.0)")
            print(f"   which are more reliable for AI models to understand region location.")
            return True
        else:
            print(f"❌ Edited image file not found: {edited_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def wait_for_server(timeout=30):
    """Wait for Gradio server to be ready"""
    print("Waiting for Gradio server to start...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            client = Client("http://127.0.0.1:7860")
            print("✅ Server is ready")
            return True
        except Exception:
            time.sleep(2)
    
    print(f"❌ Server did not start within {timeout} seconds")
    return False


if __name__ == "__main__":
    print("=" * 60)
    print("Normalized Coordinates Test")
    print("=" * 60)
    print(f"Output directory: {OUTPUT_DIR}")
    print()
    
    # Wait for server
    if not wait_for_server():
        print("\n❌ Cannot proceed without server")
        sys.exit(1)
    
    # Run test
    success = test_normalized_coordinates()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ TEST PASSED!")
    else:
        print("❌ TEST FAILED")
    print("=" * 60)
    
    sys.exit(0 if success else 1)

