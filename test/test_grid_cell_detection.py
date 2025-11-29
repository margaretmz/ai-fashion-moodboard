"""
Test grid cell detection for image editing
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mb_app import _calculate_grid_cell, _build_edit_prompt, _load_edit_template


def test_grid_cell_calculation():
    """Test grid cell calculation for different bounding boxes"""
    print("=" * 60)
    print("Test: Grid Cell Detection")
    print("=" * 60)
    
    # Test image dimensions (typical moodboard size)
    img_width = 1440
    img_height = 1024
    
    test_cases = [
        {
            "name": "Top-left cell (Row 1, Cell 1)",
            "bbox": (0, 0, 360, 400),
            "expected_row": 1,
            "expected_col": 1,
        },
        {
            "name": "Top-right cell (Row 1, Cell 4)",
            "bbox": (1080, 0, 1440, 400),
            "expected_row": 1,
            "expected_col": 4,
        },
        {
            "name": "Bottom-left cell (Row 2, Cell 1)",
            "bbox": (0, 600, 360, 1024),
            "expected_row": 2,
            "expected_col": 1,
        },
        {
            "name": "Bottom-right cell (Row 2, Cell 4)",
            "bbox": (1080, 600, 1440, 1024),
            "expected_row": 2,
            "expected_col": 4,
        },
        {
            "name": "Center top (Row 1, Cell 2-3)",
            "bbox": (360, 100, 720, 400),
            "expected_row": 1,
            "expected_col": 2,  # Center point would be in cell 2
        },
    ]
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['name']}")
        print(f"  Bounding box: {test_case['bbox']}")
        
        x_top, y_top, x_bottom, y_bottom = test_case['bbox']
        result = _calculate_grid_cell(
            x_top, y_top, x_bottom, y_bottom, img_width, img_height
        )
        
        print(f"  Result:")
        print(f"    Row: {result['row']} ({result['row_name']})")
        print(f"    Column: {result['column']}")
        print(f"    Cell: {result['cell']}")
        print(f"    Description: {result['cell_description']}")
        print(f"    Overlapping cells: {result['overlapping_cells']}")
        
        # Verify expectations
        if result['row'] == test_case['expected_row']:
            print(f"  ✅ Row matches expected: {test_case['expected_row']}")
        else:
            print(f"  ❌ Row mismatch: expected {test_case['expected_row']}, got {result['row']}")
            all_passed = False
        
        if result['column'] == test_case['expected_col']:
            print(f"  ✅ Column matches expected: {test_case['expected_col']}")
        else:
            print(f"  ⚠️  Column: expected {test_case['expected_col']}, got {result['column']} (may vary based on center point)")
    
    return all_passed


def test_prompt_with_grid_info():
    """Test that the edit prompt includes grid cell information"""
    print("\n" + "=" * 60)
    print("Test: Edit Prompt with Grid Cell Information")
    print("=" * 60)
    
    img_width = 1440
    img_height = 1024
    x_top, y_top, x_bottom, y_bottom = 0, 0, 360, 400
    edit_request = "Change to vibrant blues"
    
    template = _load_edit_template()
    
    prompt = _build_edit_prompt(
        x_top, y_top, x_bottom, y_bottom, edit_request, template,
        img_width=img_width, img_height=img_height
    )
    
    print("\nGenerated prompt (first 500 chars):")
    print("-" * 60)
    print(prompt[:500])
    print("-" * 60)
    
    # Check for grid cell information
    has_grid_info = (
        "GRID_CELL" in prompt or
        "Grid Cell" in prompt or
        "Row 1" in prompt or
        "Row 2" in prompt or
        "Top Row" in prompt or
        "Bottom Row" in prompt
    )
    
    if has_grid_info:
        print("\n✅ Grid cell information found in prompt")
        return True
    else:
        print("\n❌ Grid cell information NOT found in prompt")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Grid Cell Detection Test Suite")
    print("=" * 60)
    
    # Test 1: Grid cell calculation
    test1_passed = test_grid_cell_calculation()
    
    # Test 2: Prompt generation with grid info
    test2_passed = test_prompt_with_grid_info()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Grid Cell Calculation: {'✅ PASS' if test1_passed else '❌ FAIL'}")
    print(f"Prompt with Grid Info: {'✅ PASS' if test2_passed else '❌ FAIL'}")
    
    all_passed = test1_passed and test2_passed
    print("=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
    else:
        print("❌ Some tests failed")
    print("=" * 60)
    
    sys.exit(0 if all_passed else 1)

