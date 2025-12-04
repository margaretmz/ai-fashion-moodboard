import os
import re
import uuid
from datetime import datetime
from functools import lru_cache
from pathlib import Path

import gradio as gr
from google import genai
from google.genai import types

from real_time_patterns import (
    _REAL_TIME_DIRECT_PATTERNS,
    _REAL_TIME_TIME_PATTERN,
    _REAL_TIME_TOPIC_PATTERN,
)


GEMINI_3_MODEL_ID = "gemini-3-pro-image-preview"
GEMINI_25_MODEL_ID = "gemini-2.5-flash-image"
DEFAULT_MODEL_ID = GEMINI_3_MODEL_ID
MODEL_CHOICES = [GEMINI_3_MODEL_ID, GEMINI_25_MODEL_ID]
DEFAULT_ASPECT_RATIO = "16:9"
DEFAULT_IMAGE_SIZE = "1K"
PROMPT_TEMPLATE_FILE = Path(__file__).parent / "prompt_templates" / "prompt_template.txt"
EDIT_TEMPLATE_FILE = Path(__file__).parent / "prompt_templates" / "edit_template.txt"
OUTPUT_DIR = Path(__file__).parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)
SUBJECT_PLACEHOLDER = "{SUBJECT_PLACEHOLDER}"
EDIT_PLACEHOLDERS = {
    "X_TOP": "{X_TOP}",
    "Y_TOP": "{Y_TOP}",
    "X_BOTTOM": "{X_BOTTOM}",
    "Y_BOTTOM": "{Y_BOTTOM}",
    "WIDTH": "{WIDTH}",
    "HEIGHT": "{HEIGHT}",
    "EDIT_REQUEST": "{EDIT_REQUEST}",
}


@lru_cache(maxsize=1)
def _load_prompt_template() -> str:
    """Load the prompt template from external file"""
    if not PROMPT_TEMPLATE_FILE.exists():
        raise gr.Error(f"Prompt template file not found: {PROMPT_TEMPLATE_FILE}")
    
    with open(PROMPT_TEMPLATE_FILE, "r", encoding="utf-8") as f:
        return f.read()


@lru_cache(maxsize=1)
def _load_edit_template() -> str:
    """Load the edit template from external file"""
    if not EDIT_TEMPLATE_FILE.exists():
        raise gr.Error(f"Edit template file not found: {EDIT_TEMPLATE_FILE}")
    
    with open(EDIT_TEMPLATE_FILE, "r", encoding="utf-8") as f:
        return f.read()


_REAL_TIME_PROXIMITY_PATTERNS = [
    re.compile(
        rf"{_REAL_TIME_TIME_PATTERN}[\s\S]{{0,80}}{_REAL_TIME_TOPIC_PATTERN}",
        re.IGNORECASE | re.DOTALL,
    ),
    re.compile(
        rf"{_REAL_TIME_TOPIC_PATTERN}[\s\S]{{0,80}}{_REAL_TIME_TIME_PATTERN}",
        re.IGNORECASE | re.DOTALL,
    ),
]


def _contains_real_time_info(prompt: str) -> bool:
    """Return True if the prompt asks for real-time info (weather, stocks, runway coverage, etc.)."""
    if not prompt:
        return False
    
    normalized_prompt = prompt.lower()
    
    for pattern in _REAL_TIME_DIRECT_PATTERNS:
        if pattern.search(normalized_prompt):
            return True
    
    for pattern in _REAL_TIME_PROXIMITY_PATTERNS:
        if pattern.search(normalized_prompt):
            return True
    
    return False


def _build_prompt(user_input: str, template: str) -> str:
    """Build the final prompt by replacing placeholder with user input"""
    return template.replace(SUBJECT_PLACEHOLDER, user_input)


def _calculate_grid_cell(
    x_top: int,
    y_top: int,
    x_bottom: int,
    y_bottom: int,
    img_width: int,
    img_height: int,
) -> dict:
    """
    Calculate which grid cell(s) the bounding box overlaps with.
    The moodboard has a 2x4 grid:
    - Top row: 4 vertical portrait images (Row 1, Cells 1-4)
    - Bottom row: 4 square images (Row 2, Cells 1-4)
    """
    # Calculate the center point of the bounding box
    bbox_center_x = (x_top + x_bottom) / 2
    bbox_center_y = (y_top + y_bottom) / 2
    
    # Normalize center coordinates
    center_x_norm = bbox_center_x / img_width
    center_y_norm = bbox_center_y / img_height
    
    # Determine which row (top or bottom)
    # Assuming roughly equal height split between top and bottom rows
    # Top row typically takes more vertical space (taller images)
    # Based on the prompt: "Top Row appear significantly taller than the bottom row"
    # Let's estimate top row is ~60% of height, bottom row is ~40%
    row_split = 0.6  # Top row ends at 60% of image height
    
    if center_y_norm < row_split:
        row = 1  # Top row (The Look)
        row_name = "Top Row (The Look)"
        num_cells = 4
    else:
        row = 2  # Bottom row (The Details)
        row_name = "Bottom Row (The Details)"
        num_cells = 4
    
    # Determine which column (1-4)
    # Each row has 4 equal-width columns
    cell_width = 1.0 / num_cells
    column = min(int(center_x_norm / cell_width) + 1, num_cells)
    
    # Calculate cell boundaries for more precise description
    cell_left_norm = (column - 1) * cell_width
    cell_right_norm = column * cell_width
    
    # Determine if bbox overlaps multiple cells
    bbox_left_norm = x_top / img_width
    bbox_right_norm = x_bottom / img_width
    
    overlapping_cells = []
    for col in range(1, num_cells + 1):
        col_left = (col - 1) * cell_width
        col_right = col * cell_width
        # Check if bbox overlaps with this column
        if not (bbox_right_norm < col_left or bbox_left_norm > col_right):
            overlapping_cells.append(col)
    
    # Create description
    if len(overlapping_cells) == 1:
        cell_desc = f"Cell {overlapping_cells[0]}"
    elif len(overlapping_cells) == 2:
        cell_desc = f"Cells {overlapping_cells[0]} and {overlapping_cells[1]}"
    else:
        cell_desc = f"Cells {', '.join(map(str, overlapping_cells))}"
    
    return {
        "row": row,
        "row_name": row_name,
        "column": column,
        "cell": f"Row {row}, Cell {column}",
        "cell_description": f"{row_name}, {cell_desc}",
        "overlapping_cells": overlapping_cells,
        "cell_left_norm": cell_left_norm,
        "cell_right_norm": cell_right_norm,
    }


def _build_edit_prompt(
    x_top,
    y_top,
    x_bottom,
    y_bottom,
    edit_request: str,
    template: str,
    img_width: int = None,
    img_height: int = None,
    has_bbox: bool = True,
) -> str:
    """Build the edit prompt by replacing placeholders in template.
    If has_bbox is False, removes all bbox-related sections from the prompt."""
    
    prompt = template
    
    # Replace image dimensions (always available)
    if img_width and img_height:
        prompt = prompt.replace("{IMAGE_WIDTH}", str(img_width))
        prompt = prompt.replace("{IMAGE_HEIGHT}", str(img_height))
    else:
        prompt = prompt.replace("{IMAGE_WIDTH}", "N/A")
        prompt = prompt.replace("{IMAGE_HEIGHT}", "N/A")
    
    if has_bbox:
        # Bbox is provided - include all bbox-related information
        # Ensure coordinates are valid integers before doing arithmetic
        if x_top is None or y_top is None or x_bottom is None or y_bottom is None:
            # If any coordinate is None, treat as no bbox
            has_bbox = False
        else:
            try:
                x_top = int(x_top)
                y_top = int(y_top)
                x_bottom = int(x_bottom)
                y_bottom = int(y_bottom)
                width = x_bottom - x_top
                height = y_bottom - y_top
            except (ValueError, TypeError):
                # If conversion fails, treat as no bbox
                has_bbox = False
    
    if has_bbox:
        # Only proceed with bbox-related processing if has_bbox is still True
        
        # Calculate normalized coordinates (0.0 to 1.0) if image dimensions are provided
        x_top_norm = None
        y_top_norm = None
        x_bottom_norm = None
        y_bottom_norm = None
        width_norm = None
        height_norm = None
        
        if img_width and img_height and img_width > 0 and img_height > 0:
            x_top_norm = round(x_top / img_width, 4)
            y_top_norm = round(y_top / img_height, 4)
            x_bottom_norm = round(x_bottom / img_width, 4)
            y_bottom_norm = round(y_bottom / img_height, 4)
            width_norm = round(width / img_width, 4)
            height_norm = round(height / img_height, 4)
            
            # Calculate grid cell information
            grid_info = _calculate_grid_cell(
                x_top, y_top, x_bottom, y_bottom, img_width, img_height
            )
        else:
            grid_info = None
        
        # Replace absolute coordinates (bbox dimensions)
        prompt = prompt.replace(EDIT_PLACEHOLDERS["X_TOP"], str(x_top))
        prompt = prompt.replace(EDIT_PLACEHOLDERS["Y_TOP"], str(y_top))
        prompt = prompt.replace(EDIT_PLACEHOLDERS["X_BOTTOM"], str(x_bottom))
        prompt = prompt.replace(EDIT_PLACEHOLDERS["Y_BOTTOM"], str(y_bottom))
        prompt = prompt.replace(EDIT_PLACEHOLDERS["WIDTH"], str(width))
        prompt = prompt.replace(EDIT_PLACEHOLDERS["HEIGHT"], str(height))
        
        # Replace normalized coordinates if available
        if x_top_norm is not None:
            prompt = prompt.replace("{X_TOP_NORM}", str(x_top_norm))
            prompt = prompt.replace("{Y_TOP_NORM}", str(y_top_norm))
            prompt = prompt.replace("{X_BOTTOM_NORM}", str(x_bottom_norm))
            prompt = prompt.replace("{Y_BOTTOM_NORM}", str(y_bottom_norm))
            prompt = prompt.replace("{WIDTH_NORM}", str(width_norm))
            prompt = prompt.replace("{HEIGHT_NORM}", str(height_norm))
        else:
            # Remove normalized coordinate placeholders if not available
            prompt = prompt.replace("{X_TOP_NORM}", "N/A")
            prompt = prompt.replace("{Y_TOP_NORM}", "N/A")
            prompt = prompt.replace("{X_BOTTOM_NORM}", "N/A")
            prompt = prompt.replace("{Y_BOTTOM_NORM}", "N/A")
            prompt = prompt.replace("{WIDTH_NORM}", "N/A")
            prompt = prompt.replace("{HEIGHT_NORM}", "N/A")
        
        # Replace grid cell information if available
        if grid_info:
            prompt = prompt.replace("{GRID_ROW}", str(grid_info["row"]))
            prompt = prompt.replace("{GRID_ROW_NAME}", grid_info["row_name"])
            prompt = prompt.replace("{GRID_COLUMN}", str(grid_info["column"]))
            prompt = prompt.replace("{GRID_CELL}", grid_info["cell"])
            prompt = prompt.replace("{GRID_CELL_DESCRIPTION}", grid_info["cell_description"])
            prompt = prompt.replace("{GRID_OVERLAPPING_CELLS}", ", ".join(map(str, grid_info["overlapping_cells"])))
        else:
            prompt = prompt.replace("{GRID_ROW}", "N/A")
            prompt = prompt.replace("{GRID_ROW_NAME}", "N/A")
            prompt = prompt.replace("{GRID_COLUMN}", "N/A")
            prompt = prompt.replace("{GRID_CELL}", "N/A")
            prompt = prompt.replace("{GRID_CELL_DESCRIPTION}", "N/A")
            prompt = prompt.replace("{GRID_OVERLAPPING_CELLS}", "N/A")
    else:
        # No bbox - remove all bbox-related sections from prompt
        # Remove the entire "Grid Cell Location" section (from header to end of overlapping cells)
        prompt = re.sub(r'\*\*Grid Cell Location.*?Overlapping Cells:.*?\n', '', prompt, flags=re.DOTALL)
        # Remove "Technical Reference" section (contains coordinates)
        prompt = re.sub(r'\*\*Technical Reference.*?Full image size:.*?pixels\n', '', prompt, flags=re.DOTALL)
        
        # Replace all bbox placeholders with empty strings
        prompt = prompt.replace(EDIT_PLACEHOLDERS["X_TOP"], "")
        prompt = prompt.replace(EDIT_PLACEHOLDERS["Y_TOP"], "")
        prompt = prompt.replace(EDIT_PLACEHOLDERS["X_BOTTOM"], "")
        prompt = prompt.replace(EDIT_PLACEHOLDERS["Y_BOTTOM"], "")
        prompt = prompt.replace(EDIT_PLACEHOLDERS["WIDTH"], "")
        prompt = prompt.replace(EDIT_PLACEHOLDERS["HEIGHT"], "")
        prompt = prompt.replace("{X_TOP_NORM}", "")
        prompt = prompt.replace("{Y_TOP_NORM}", "")
        prompt = prompt.replace("{X_BOTTOM_NORM}", "")
        prompt = prompt.replace("{Y_BOTTOM_NORM}", "")
        prompt = prompt.replace("{WIDTH_NORM}", "")
        prompt = prompt.replace("{HEIGHT_NORM}", "")
        prompt = prompt.replace("{GRID_ROW}", "")
        prompt = prompt.replace("{GRID_ROW_NAME}", "")
        prompt = prompt.replace("{GRID_COLUMN}", "")
        prompt = prompt.replace("{GRID_CELL}", "")
        prompt = prompt.replace("{GRID_CELL_DESCRIPTION}", "")
        prompt = prompt.replace("{GRID_OVERLAPPING_CELLS}", "")
    
    prompt = prompt.replace(EDIT_PLACEHOLDERS["EDIT_REQUEST"], edit_request)
    
    # Clean up any double newlines or empty sections
    prompt = re.sub(r'\n\n+', '\n\n', prompt)
    
    return prompt


def _extract_image_from_parts(parts):
    """Replicate the original logic: return the first inline image part, else None."""
    for part in parts:
        if getattr(part, "inline_data", None):
            return part.as_image()
    return None


def _collect_reasoning_text(parts):
    """Collect intermediate thoughts emitted by the model."""
    reasoning_segments = []
    
    for part in parts:
        if part.thought:
            text_content = getattr(part, "text", None)
            if text_content:
                reasoning_segments.append(text_content.strip())
    
    if reasoning_segments:
        return "\n\n".join(segment for segment in reasoning_segments if segment).strip()
    else:
        return "No reasoning traces recovered."


@lru_cache(maxsize=1)
def _get_client() -> genai.Client:
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise gr.Error("Set the GEMINI_API_KEY or GOOGLE_API_KEY environment variable with your Gemini API key.")
    return genai.Client(api_key=api_key)


def _generate_single_image(prompt: str, model_id: str, include_reasoning: bool = False):
    tools = None
    if _contains_real_time_info(prompt):
        print(f"{prompt} likely contains some info that could benefit from search-grounding.")
        tools = [{"google_search": {}}]
    
    client = _get_client()
    image_config = {"aspect_ratio": DEFAULT_ASPECT_RATIO}
    config_kwargs = {}

    if model_id == GEMINI_3_MODEL_ID:
        image_config["image_size"] = DEFAULT_IMAGE_SIZE

    image_config = types.ImageConfig(**image_config)
    config_kwargs["image_config"] = image_config
    
    if include_reasoning:
        config_kwargs["response_modalities"] = ["TEXT", "IMAGE"]
    if tools:
        config_kwargs["tools"] = tools

    response = client.models.generate_content(
        model=model_id,
        contents=prompt,
        config=types.GenerateContentConfig(**config_kwargs),
    )
    
    image = _extract_image_from_parts(response.parts)
    reasoning_text = _collect_reasoning_text(response.parts) if include_reasoning else ""
    return image, reasoning_text


def generate_image(user_input: str, model_id: str, template: str, include_reasoning: bool):
    """Generate image using the prompt template with user input"""
    user_input = user_input.strip()
    if not user_input:
        raise gr.Error("Input cannot be empty. Please describe the fashion moodboard subject.")
    
    # If template is empty or None, use the default template
    if not template or not template.strip():
        template = _load_prompt_template()

    # Build the full prompt from template
    full_prompt = _build_prompt(user_input, template)
    
    image, reasoning_text = _generate_single_image(
        full_prompt,
        model_id=model_id,
        include_reasoning=include_reasoning,
    )
    
    if not image:
        raise gr.Error("The model did not return any image data. Please try again.")

    pil_image = image._pil_image
    
    # Save image with unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    filename = f"generated_{timestamp}_{unique_id}.png"
    output_path = OUTPUT_DIR / filename
    pil_image.save(output_path)
    
    # Return the PIL Image object directly - Gradio can display it and serve it via /file= endpoint
    # The image is also saved to outputs/ for persistence
    reasoning_output = reasoning_text if include_reasoning else ""
    return pil_image, reasoning_output


def edit_image_region(
    current_image,
    image_path_file,
    x_top,
    y_top,
    x_bottom,
    y_bottom,
    edit_request: str,
    model_id: str,
    edit_template: str,
    include_reasoning: bool,
):
    """Edit a specific region of the image defined by bounding box, or entire image if bbox is None"""
    from PIL import Image
    
    # Priority: use image_path_file if provided (for API), otherwise use current_image (for UI)
    image_to_edit = None
    original_file_path = None  # Track original file path to replace it with edited version
    
    if image_path_file and image_path_file.strip():
        # Textbox returns a string path
        file_path = image_path_file.strip()
        
        # Handle case where path might be a URL or temp file path
        # If it's a URL, extract the filename and look for it in outputs/
        if file_path.startswith('http'):
            # Extract filename from URL (e.g., "generated_20251129_102303_74a7602b.png")
            filename = file_path.split('/')[-1].split('=')[-1] if '=' in file_path else file_path.split('/')[-1]
            # Try to find the file in outputs directory
            potential_path = OUTPUT_DIR / filename
            if potential_path.exists():
                file_path = str(potential_path)
            else:
                raise gr.Error(f"Image file not found. Tried to locate: {potential_path}")
        # If it's a temp file path (Gradio's temp directory), try to find the original in outputs/
        elif '/tmp/' in file_path or '/private/var/folders' in file_path or 'gradio' in file_path.lower():
            # Extract filename from temp path
            filename = os.path.basename(file_path)
            # Try to find the file in outputs directory
            potential_path = OUTPUT_DIR / filename
            if potential_path.exists():
                file_path = str(potential_path)
            elif os.path.exists(file_path):
                # Use the temp file if it exists
                pass
            else:
                raise gr.Error(f"Image file not found. Tried to locate: {potential_path}")
        
        if os.path.exists(file_path):
            image_to_edit = Image.open(file_path)
            # Store the original file path for later (to replace the file)
            original_file_path = file_path
        else:
            raise gr.Error(f"Image file not found: {file_path}")
    elif current_image is not None:
        # Handle both file path (str) and PIL Image from image_display
        if isinstance(current_image, str):
            # It's a file path, load it
            file_path = current_image
            # Handle URL or temp file path similar to above
            if file_path.startswith('http'):
                filename = file_path.split('/')[-1].split('=')[-1] if '=' in file_path else file_path.split('/')[-1]
                potential_path = OUTPUT_DIR / filename
                if potential_path.exists():
                    file_path = str(potential_path)
            elif '/tmp/' in file_path or '/private/var/folders' in file_path or 'gradio' in file_path.lower():
                filename = os.path.basename(file_path)
                potential_path = OUTPUT_DIR / filename
                if potential_path.exists():
                    file_path = str(potential_path)
            
            if not os.path.exists(file_path):
                raise gr.Error(f"Image file not found: {file_path}")
            image_to_edit = Image.open(file_path)
            original_file_path = file_path
        elif hasattr(current_image, 'size'):
            # It's a PIL Image - we can't track the original path, so we'll create a new file
            image_to_edit = current_image
        else:
            raise gr.Error("Invalid image format. Expected PIL Image or file path.")
    else:
        raise gr.Error("No image available. Please generate an image first or provide an image file.")
    
    current_image = image_to_edit
    
    edit_request = edit_request.strip()
    if not edit_request:
        raise gr.Error("Edit request cannot be empty.")
    
    # Get image dimensions
    img_width, img_height = current_image.size
    
    # Check if bbox is provided (all coordinates must be non-None and non-empty)
    # Handle both None and empty string cases from API
    # Also handle the case where Gradio might pass None as a string "None" or "null"
    def is_valid_coord(coord):
        # Check for None first
        if coord is None:
            return False
        # Check for empty string
        if coord == "":
            return False
        # Check for string representations of None/null
        if isinstance(coord, str):
            coord_lower = coord.strip().lower()
            if coord_lower in ("", "none", "null", "undefined"):
                return False
            # Try to parse as int - if it fails, it's not a valid coordinate
            try:
                int(coord)
                return True
            except (ValueError, TypeError):
                return False
        # For numeric types, consider them valid
        try:
            int(coord)
            return True
        except (ValueError, TypeError):
            return False
    
    has_bbox = (
        is_valid_coord(x_top) and
        is_valid_coord(y_top) and
        is_valid_coord(x_bottom) and
        is_valid_coord(y_bottom)
    )
    
    if has_bbox:
        # Validate bounding box coordinates - convert to int only if they're valid
        # Double-check that coordinates are not None before conversion
        if x_top is None or y_top is None or x_bottom is None or y_bottom is None:
            has_bbox = False
        else:
            try:
                x_top = int(x_top)
                y_top = int(y_top)
                x_bottom = int(x_bottom)
                y_bottom = int(y_bottom)
            except (ValueError, TypeError) as e:
                # If conversion fails, treat as no bbox instead of raising error
                has_bbox = False
        
        # Validate bounding box (top < bottom, left < right)
        if x_top >= x_bottom or y_top >= y_bottom:
            raise gr.Error("Invalid bounding box: top coordinates must be less than bottom coordinates.")
        
        # Validate coordinates are within image bounds
        if x_top < 0 or y_top < 0 or x_bottom > img_width or y_bottom > img_height:
            raise gr.Error(f"Bounding box coordinates must be within image bounds (0-{img_width} for x, 0-{img_height} for y).")
    
    # Validate edit template
    # If edit_template is empty or None, use the default template
    if not edit_template or not edit_template.strip():
        edit_template = _load_edit_template()
    
    # Build the edit prompt from template (with or without bbox)
    # When has_bbox is False, pass None for coordinates to avoid any arithmetic issues
    edit_prompt = _build_edit_prompt(
        x_top if has_bbox else None,
        y_top if has_bbox else None,
        x_bottom if has_bbox else None,
        y_bottom if has_bbox else None,
        edit_request, edit_template,
        img_width=img_width, img_height=img_height, has_bbox=has_bbox
    )
    
    client = _get_client()
    
    # Prepare image for API - convert PIL Image to format expected by Gemini
    import io
    
    # Convert PIL image to bytes
    img_bytes = io.BytesIO()
    current_image.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    image_data = img_bytes.read()
    
    # Create content with image and text prompt
    # Gemini API expects a list of parts (image + text)
    contents = [
        types.Part.from_bytes(
            data=image_data,
            mime_type="image/png"
        ),
        edit_prompt
    ]
    
    # Configure image generation
    image_config = {"aspect_ratio": DEFAULT_ASPECT_RATIO}
    config_kwargs = {}
    
    if model_id == GEMINI_3_MODEL_ID:
        image_config["image_size"] = DEFAULT_IMAGE_SIZE
    
    image_config = types.ImageConfig(**image_config)
    config_kwargs["image_config"] = image_config
    
    if include_reasoning:
        config_kwargs["response_modalities"] = ["TEXT", "IMAGE"]
    
    # Generate edited image
    response = client.models.generate_content(
        model=model_id,
        contents=contents,
        config=types.GenerateContentConfig(**config_kwargs),
    )
    
    edited_image = _extract_image_from_parts(response.parts)
    if not edited_image:
        raise gr.Error("The model did not return any image data. Please try again.")
    
    pil_image = edited_image._pil_image
    
    # Save edited image - replace original if we have the original path, otherwise create new file
    if original_file_path and os.path.exists(original_file_path):
        output_path = Path(original_file_path)
        pil_image.save(output_path)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"edited_{timestamp}_{unique_id}.png"
        output_path = OUTPUT_DIR / filename
        pil_image.save(output_path)
    
    reasoning_output = _collect_reasoning_text(response.parts) if include_reasoning else ""
    
    # Return the PIL Image object directly - Gradio can display it and serve it via /file= endpoint
    # The image is also saved to outputs/ for persistence (replacing original if applicable)
    return pil_image, reasoning_output


with gr.Blocks(title="Fashion Moodboard", css="""
    .main-container {
        display: flex;
        flex-direction: column;
        height: 100vh;
    }
    .image-section {
        flex: 5;
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 0;
    }
    .input-section {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 20px;
    }
    .input-wrapper {
        width: 100%;
        max-width: 900px;
        display: flex;
        gap: 10px;
    }
""") as demo:
    # Load default template content
    try:
        default_template = _load_prompt_template()
    except Exception as e:
        default_template = f"Error loading template: {str(e)}"
    
    try:
        default_edit_template = _load_edit_template()
    except Exception as e:
        default_edit_template = f"Error loading edit template: {str(e)}"
    
    # Model selector and prompt templates at the top
    with gr.Row():
        with gr.Column(scale=0):
            model_selector = gr.Radio(
                choices=MODEL_CHOICES,
                value=DEFAULT_MODEL_ID,
                label="Model",
            )
            reasoning_checkbox = gr.Checkbox(
                label="Show reasoning trace",
                value=False,
            )
        with gr.Tabs():
            with gr.Tab("Generation Template"):
                prompt_template_component = gr.Textbox(
                    label="Prompt Template",
                    value=default_template,
                    lines=10,
                    placeholder="Enter or modify the prompt template. Use {SUBJECT_PLACEHOLDER} for user input.",
                )
            with gr.Tab("Edit Template"):
                with gr.Column():
                    edit_template_component = gr.Textbox(
                        label="Edit Template",
                        value=default_edit_template,
                        lines=10,
                        placeholder="Enter or modify the edit template. Use {X_TOP}, {Y_TOP}, {X_BOTTOM}, {Y_BOTTOM}, {WIDTH}, {HEIGHT}, {EDIT_REQUEST} as placeholders.",
                    )
                    gr.Markdown("### Edit Image Region")
                    image_path_input = gr.Textbox(
                        label="Image File Path (for API usage - use the path returned from generation)",
                        placeholder="Leave empty to use the displayed image, or enter a file path",
                        visible=False,  # Hidden in UI, but available for API
                    )
                    with gr.Row():
                        bbox_x_top = gr.Number(
                            label="X Top",
                            value=0,
                            precision=0,
                            minimum=0,
                        )
                        bbox_y_top = gr.Number(
                            label="Y Top",
                            value=0,
                            precision=0,
                            minimum=0,
                        )
                    with gr.Row():
                        bbox_x_bottom = gr.Number(
                            label="X Bottom",
                            value=100,
                            precision=0,
                            minimum=0,
                        )
                        bbox_y_bottom = gr.Number(
                            label="Y Bottom",
                            value=100,
                            precision=0,
                            minimum=0,
                        )
                    edit_request_input = gr.Textbox(
                        label="Edit Request",
                        placeholder="Describe what you want to change in this region...",
                        lines=3,
                    )
                    edit_button = gr.Button(
                        "Apply Edit",
                        variant="secondary",
                        size="lg",
                    )
    
    # Image display area (5 parts of height ratio)
    with gr.Row(elem_classes=["image-section"]):
        with gr.Column():
            image_display = gr.Image(
                label="",
                type="filepath",  # Changed to filepath to work with saved file paths
                show_label=False,
                container=True,
            )
            reasoning_display = gr.Textbox(
                label="Reasoning Trace",
                value="",
                lines=6,
                interactive=False,
            )
    
    # Input area at bottom center (1 part of height ratio)
    with gr.Row(elem_classes=["input-section"]):
        with gr.Row(elem_classes=["input-wrapper"]):
            prompt_input = gr.Textbox(
                label="",
                placeholder="Enter the fashion moodboard subject (e.g., 'sustainable luxury dress collection')...",
                lines=1,
                show_label=False,
                scale=10,
            )
            send_button = gr.Button(
                "Send",
                variant="primary",
                size="lg",
                scale=1,
            )
    
    # Set up the click handler
    send_button.click(
        fn=generate_image,
        inputs=[prompt_input, model_selector, prompt_template_component, reasoning_checkbox],
        outputs=[image_display, reasoning_display],
        api_name="generate_image",
    )
    
    # Also allow Enter key to submit
    prompt_input.submit(
        fn=generate_image,
        inputs=[prompt_input, model_selector, prompt_template_component, reasoning_checkbox],
        outputs=[image_display, reasoning_display],
        api_name="generate_image_1",
    )
    
    # Image editing handler
    edit_button.click(
        fn=edit_image_region,
        inputs=[
            image_display,
            image_path_input,
            bbox_x_top,
            bbox_y_top,
            bbox_x_bottom,
            bbox_y_bottom,
            edit_request_input,
            model_selector,
            edit_template_component,
            reasoning_checkbox,
        ],
        outputs=[image_display, reasoning_display],
        api_name="edit_image_region",
    )


if __name__ == "__main__":
    demo.launch(show_error=True, server_name="0.0.0.0", server_port=7860, share=False)
