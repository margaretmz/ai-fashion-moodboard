"""
Test image generation and editing APIs, saving outputs to files
"""
import sys
import time
import os
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Update OUTPUT_DIR to point to parent's outputs directory
OUTPUT_DIR = Path(__file__).parent.parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

from gradio_client import Client
from PIL import Image


def test_image_generation():
    """Test image generation API"""
    print("=" * 60)
    print("Test 1: Image Generation")
    print("=" * 60)
    
    try:
        client = Client("http://127.0.0.1:7860")
        print("✅ Connected to Gradio server")
        
        # Test parameters
        subject = "sustainable luxury dress collection"
        model = "gemini-3-pro-image-preview"
        
        print(f"\nGenerating image...")
        print(f"  Subject: {subject}")
        print(f"  Model: {model}")
        
        # Generate image - returns object with url and path properties
        result = client.predict(
            subject,
            model,
            "",  # template (empty string = use default)
            api_name="/generate_image"
        )
        
        if not result:
            print("❌ No image result returned")
            return None
        
        # Extract path from result (could be object with path/url or direct path)
        if isinstance(result, dict):
            image_path = result.get('path')
            image_url = result.get('url')
            print(f"✅ Image generated")
            print(f"   Path: {image_path}")
            print(f"   URL: {image_url[:80] if image_url else 'N/A'}...")
        elif isinstance(result, str):
            image_path = result
            print(f"✅ Image generated: {image_path}")
        else:
            print(f"❌ Unexpected result type: {type(result)}")
            return None
        
        # Verify the image exists and get its info
        if image_path and os.path.exists(image_path):
            img = Image.open(image_path)
            print(f"✅ Image saved to: {image_path}")
            print(f"   Image size: {img.size}")
            # Return the file path (already saved by generate_image function)
            return image_path
        else:
            print(f"❌ Image file not found at: {image_path}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_image_editing(image_path):
    """Test image editing API"""
    print("\n" + "=" * 60)
    print("Test 2: Image Editing")
    print("=" * 60)
    
    if image_path is None or not os.path.exists(image_path):
        print("❌ No image available for editing")
        return None
    
    try:
        client = Client("http://127.0.0.1:7860")
        
        # Load image to get dimensions
        current_image = Image.open(image_path)
        img_width, img_height = current_image.size
        print(f"Original image size: {img_width} x {img_height}")
        
        # Define bounding box (edit top-left 200x200 region)
        x_top = 0
        y_top = 0
        x_bottom = min(200, img_width)
        y_bottom = min(200, img_height)
        
        edit_request = "Change the color scheme to vibrant blues and purples with a modern aesthetic"
        
        print(f"\nEditing image region...")
        print(f"  Bounding box: ({x_top}, {y_top}) to ({x_bottom}, {y_bottom})")
        print(f"  Edit request: {edit_request}")
        print(f"  Using image: {image_path}")
        
        # Edit image - File component expects a file path string
        # Pass None for image_display, and the file path for image_path_file
        # Note: Edited image should replace the original file
        result = client.predict(
            None,  # image_display (not used when image_path_file is provided)
            image_path,  # image_path_file - pass the file path string
            int(x_top),
            int(y_top),
            int(x_bottom),
            int(y_bottom),
            edit_request,
            "gemini-3-pro-image-preview",
            "",  # edit_template (empty string = use default)
            api_name="/edit_image_region"
        )
        
        if not result:
            print("❌ No edited image result returned")
            return None
        
        # Extract path from result (could be object with path/url or direct path)
        if isinstance(result, dict):
            edited_image_path = result.get('path')
            edited_image_url = result.get('url')
            print(f"✅ Image edited")
            print(f"   Path: {edited_image_path}")
            print(f"   URL: {edited_image_url[:80] if edited_image_url else 'N/A'}...")
        elif isinstance(result, str):
            edited_image_path = result
            print(f"✅ Image edited: {edited_image_path}")
        else:
            print(f"❌ Unexpected result type: {type(result)}")
            return None
        
        # Check if edited image replaced the original (should be same path)
        if edited_image_path == image_path:
            print(f"✅ Edited image replaced original file: {image_path}")
        else:
            print(f"⚠️  Edited image saved to new file: {edited_image_path}")
            print(f"   Original file: {image_path}")
        
        # Verify the edited image exists
        if edited_image_path and os.path.exists(edited_image_path):
            edited_img = Image.open(edited_image_path)
            print(f"✅ Edited image saved to: {edited_image_path}")
            print(f"   Image size: {edited_img.size}")
            return edited_img
        else:
            print(f"❌ Edited image file not found or invalid: {edited_image_path}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


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


def main():
    """Run all tests"""
    print("=" * 60)
    print("API Testing with Output Files")
    print("=" * 60)
    print(f"Output directory: {OUTPUT_DIR}")
    print()
    
    # Wait for server
    if not wait_for_server():
        print("\n❌ Cannot proceed without server")
        return False
    
    # Test 1: Image generation
    image_path = test_image_generation()
    
    if image_path is None:
        print("\n❌ Image generation failed, skipping edit test")
        return False
    
    # Test 2: Image editing - use the file path returned from generation
    edited_image = test_image_editing(image_path)
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"✅ Image Generation: {'PASS' if image_path else 'FAIL'}")
    print(f"✅ Image Editing: {'PASS' if edited_image else 'FAIL'}")
    print(f"\nOutput files saved in: {OUTPUT_DIR}")
    
    all_passed = image_path is not None and edited_image is not None
    print("=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
    else:
        print("❌ Some tests failed")
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

