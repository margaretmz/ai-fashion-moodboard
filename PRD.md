# Product Requirements Document (PRD)
## AI Fashion Moodboard Generator

### 1. Product Overview

**Product Name:** AI Fashion Moodboard Generator

**Product Description:**
An AI-powered web application that generates unique fashion moodboards using Google's Gemini AI models. The tool enables fashion designers, stylists, and creative professionals to quickly visualize design concepts, color palettes, and aesthetic themes through AI-generated moodboard images.

**Target Audience:**
- Fashion designers seeking design inspiration
- Stylists creating visual references for clients
- Fashion students and educators
- Creative professionals in the fashion industry
- Fashion brands developing seasonal collections

**Problem Statement:**
Creating fashion moodboards traditionally requires extensive time gathering reference images, arranging layouts, and curating visual elements. This tool automates the moodboard creation process, allowing users to generate multiple variations instantly from text descriptions.

---

### 2. Goals and Objectives

**Primary Goals:**
1. Enable rapid generation of fashion moodboards from text prompts
2. Provide multiple image variations to explore different design directions
3. Support various fashion aesthetics and themes (sustainable luxury, bridal, historical, etc.)
4. Offer an intuitive, accessible interface for non-technical users

**Success Metrics:**
- User satisfaction with generated moodboard quality
- Number of images generated per session
- Time saved compared to manual moodboard creation
- User retention and repeat usage

---

### 3. User Stories

**As a fashion designer, I want to:**
- Generate moodboards for seasonal collections quickly
- Explore multiple visual variations of a design concept
- Specify detailed aesthetic requirements (e.g., "Modern Heritage meets Zero-Waste")
- Generate moodboards for specific regions and seasons

**As a stylist, I want to:**
- Create visual references for client presentations
- Generate moodboards that capture specific themes or eras
- Export generated images for use in presentations

**As a fashion student, I want to:**
- Experiment with different design aesthetics
- Learn about historical fashion periods through visual generation
- Create moodboards for academic projects

---

### 4. Current Features

#### 4.1 Implementation Variants

The project includes two implementation variants:

**A. Reference Implementation (`app.py`)**
- Full-featured interface with multiple image generation
- Example prompts and advanced controls
- Gallery view for multiple images

**B. Streamlined Implementation (`mb_app.py`)**
- Minimalist, focused interface optimized for single image generation
- Large image display area with 5:1 height ratio (image:input)
- Bottom-centered input with send button
- Clean, distraction-free design
- **Prompt Template System**: Uses external template file (`prompt_templates/prompt_template.txt`) for structured moodboard generation
- **Structured Output**: Generates 2x4 grid moodboards with specific layout requirements
- **Image Region Editing**: Edit specific regions of generated images using bounding box coordinates
  - Bounding box input controls (x_top, y_top, x_bottom, y_bottom)
  - Text-based edit requests for targeted modifications
  - API support for programmatic image editing

#### 4.2 Core Functionality
- **Text-to-Image Generation**: Convert text prompts into fashion moodboard images
- **Prompt Template System** (`mb_app.py`):
  - External template file (`prompt_templates/prompt_template.txt`) for flexible prompt management
  - User input replaces `{SUBJECT_PLACEHOLDER}` in template
  - Structured output format: 2x4 grid layout (4 vertical portraits + 4 square detail images)
  - Canvas size: 1440x1024 with specific layout constraints
- **Single/Multiple Image Generation**: 
  - `mb_app.py`: Single image per request with structured template
  - `app.py`: Generate 1-4 images per request (parallel processing)
- **Model Selection**: Choose between two Gemini models:
  - Gemini 3 Pro Image Preview (default)
  - Gemini 2.5 Flash Image
- **Image Region Editing** (`mb_app.py`):
  - Edit specific regions of generated images using bounding box coordinates
  - Bounding box defined by (x_top, y_top, x_bottom, y_bottom) coordinates
  - Text-based edit requests for targeted modifications
  - Only the specified region is modified, rest of image remains unchanged
  - Supports iterative editing of the same image
- **Example Prompts**: Pre-configured example prompts for quick testing (`app.py` only)
- **Web Interface**: Gradio-based user interface accessible via web browser

#### 4.3 Technical Specifications
- **Image Configuration**:
  - Default aspect ratio: 16:9
  - Default image size: 1K (for Gemini 3 Pro)
  - Maximum images per request: 4 (`app.py`), 1 (`mb_app.py`)
- **Performance**:
  - Parallel image generation using ThreadPoolExecutor (`app.py`)
  - Sequential single image generation (`mb_app.py`)
  - Client caching for optimized API calls
- **API Integration**:
  - Google Gemini API integration
  - Environment variable-based API key management

#### 4.4 User Interface Components

**Reference Implementation (`app.py`):**
- Model selector (radio buttons)
- Text prompt input (multi-line textbox)
- Example prompt selector (radio buttons)
- Number of images slider (1-4)
- Generate button
- Image gallery (2-column layout)

**Streamlined Implementation (`mb_app.py`):**
- Model selector (radio buttons, top)
- **Template Editors** (Tab UI, top, next to model selector)
  - **Generation Template Tab**: Displays and edits generation template (from `prompt_templates/prompt_template.txt`)
    - Uses `{SUBJECT_PLACEHOLDER}` for user input replacement
  - **Edit Template Tab**: Displays and edits edit template (from `prompt_templates/edit_template.txt`)
    - Uses `{X_TOP}`, `{Y_TOP}`, `{X_BOTTOM}`, `{Y_BOTTOM}`, `{WIDTH}`, `{HEIGHT}`, `{EDIT_REQUEST}` placeholders
    - **Image Editing Controls** (visible only when Edit Template tab is selected):
      - Bounding box coordinate inputs (x_top, y_top, x_bottom, y_bottom)
      - Edit request textbox for describing desired changes
      - Apply Edit button to trigger region-specific edits
  - Both templates are editable and customizable per request
- Large image display area (5 parts of screen height)
- Text prompt input (single-line textbox, bottom center)
- Send button (next to textbox)
- Keyboard support (Enter key to submit)

---

### 5. Technical Requirements

#### 5.1 Dependencies
- `gradio`: Web interface framework
- `google-genai>=1.51.0`: Google Gemini API client

#### 5.2 Environment Requirements
- `GEMINI_API_KEY` or `GOOGLE_API_KEY`: Required environment variable for Gemini API access (either variable can be used)

#### 5.3 System Requirements
- Python 3.x
- Internet connection for API calls
- Web browser for accessing the Gradio interface

#### 5.4 API Configuration
- Supported models:
  - `gemini-3-pro-image-preview` (default)
  - `gemini-2.5-flash-image`
- Image generation parameters:
  - Aspect ratio: 16:9 (configurable)
  - Image size: 1K (for Gemini 3 Pro)

#### 5.5 Prompt Template System (`mb_app.py`)
- **Template Files** (located in `prompt_templates/` directory): 
  - `prompt_templates/prompt_template.txt`: External file for image generation template
  - `prompt_templates/edit_template.txt`: External file for image editing template
- **Template UI**: Tab-based interface showing both templates
  - **Generation Template Tab**: Displays and allows editing of generation template
  - **Edit Template Tab**: Displays and allows editing of edit template
  - Both templates are editable in the UI
  - Default values loaded from respective template files
  - Changes apply immediately to next operation
- **Generation Template**:
  - **Placeholder**: `{SUBJECT_PLACEHOLDER}` - replaced with user input
  - **Template Structure**:
    - Subject line with user input
    - Critical constraints (no text in output)
    - Layout configuration (2x4 grid, 1440x1024 canvas)
    - Row 1 specifications (4 vertical portrait images)
    - Row 2 specifications (4 square detail images)
    - Quality and layout notes
  - **Usage**: 
    - User enters subject description in bottom textbox
    - Template from `prompt_template_component` is used (defaults to file content)
    - Subject is inserted into template via `{SUBJECT_PLACEHOLDER}` replacement
- **Edit Template**:
  - **Placeholders**: 
    - `{X_TOP}`, `{Y_TOP}`: Top-left corner coordinates
    - `{X_BOTTOM}`, `{Y_BOTTOM}`: Bottom-right corner coordinates
    - `{WIDTH}`, `{HEIGHT}`: Calculated region dimensions
    - `{EDIT_REQUEST}`: User's edit request text
  - **Usage**:
    - Template from `edit_template_component` is used (defaults to file content)
    - Placeholders are replaced with actual values during edit operation
- **API Usage**: Both templates can be provided via API call (see API Usage Guide)
- **Benefits**: 
  - Easy to modify prompt structure without code changes
  - Can customize templates per request via UI or API
  - Consistent output format across generations
  - Structured moodboard layout with specific requirements
  - Flexible editing instructions for region-specific modifications

---

### 6. User Interface Requirements

#### 6.1 Layout

**Reference Implementation (`app.py`):**
- Clean, minimalist design
- Clear section headers and labels
- Responsive gallery display (2 columns)
- Auto-height gallery for varying image counts

**Streamlined Implementation (`mb_app.py`):**
- Full-screen optimized layout
- Image display area: 83.33% of viewport height (5 parts)
- Input area: 16.67% of viewport height (1 part)
- Bottom-centered input controls
- Wide landscape image display area
- Minimal UI chrome for distraction-free experience

#### 6.2 User Flow

**Reference Implementation (`app.py`):**
1. User selects a model (optional, defaults to Gemini 3 Pro)
2. User enters a text prompt OR selects an example prompt
3. User selects number of images to generate (1-4)
4. User clicks "Generate" button
5. Images appear in gallery below

**Streamlined Implementation (`mb_app.py`):**
1. User selects a model (optional, defaults to Gemini 3 Pro)
2. User can optionally modify the prompt template in the template textbox (defaults to `prompt_templates/prompt_template.txt` content)
3. User enters a subject description in the bottom textbox (e.g., "sustainable luxury dress collection")
4. User clicks "Send" button or presses Enter
5. System builds full prompt by replacing `{SUBJECT_PLACEHOLDER}` in the template (from template component) with user input
6. Generated structured moodboard (2x4 grid) appears in the large display area above
7. **Optional - Image Editing**:
   - User enters bounding box coordinates (x_top, y_top, x_bottom, y_bottom) for the region to edit
   - User enters edit request describing desired changes
   - User clicks "Apply Edit" button
   - System edits only the specified region while keeping the rest of the image unchanged
   - Updated image replaces the current image in the display

#### 6.3 Error Handling
- Validation for empty prompts
- API key validation on startup
- Error messages for failed image generation
- Graceful handling of API failures

---

### 7. Future Enhancements

#### 7.1 Planned Features (from codebase TODO)
- **Search Grounding**: Automatically detect date/place information in prompts and include search grounding in the generation process
  - Implementation: Use `nltk` for natural language processing to detect temporal and geographical references

#### 7.2 Potential Enhancements
- **Image Export**: Download individual or all generated images
- **Prompt Templates**: Library of pre-built prompt templates for common fashion categories
- **Aspect Ratio Selection**: Allow users to choose different aspect ratios (1:1, 4:3, 9:16, etc.)
- **Image Size Options**: Provide multiple image size options
- **Prompt History**: Save and reuse previous prompts
- **Image Editing**: Basic editing capabilities (crop, adjust colors, etc.)
- **Batch Processing**: Process multiple prompts in sequence
- **Style Presets**: Pre-defined style options (minimalist, maximalist, vintage, etc.)
- **Color Palette Extraction**: Extract and display color palettes from generated moodboards
- **Collaboration Features**: Share moodboards with team members
- **Integration**: Export to design tools (Figma, Adobe Creative Suite)

---

### 8. Constraints and Limitations

#### 8.1 Current Limitations
- **Image generation limits:**
  - `app.py`: Maximum 4 images per generation request
  - `mb_app.py`: Single image per generation request
- Fixed aspect ratio (16:9)
- No image persistence (images lost on page refresh)
- Requires active internet connection
- API rate limits dependent on Google Gemini API

#### 8.2 Technical Constraints
- Dependent on Google Gemini API availability and pricing
- Image quality and style dependent on model capabilities
- No offline functionality

---

### 9. Security and Privacy

#### 9.1 Data Handling
- API keys stored as environment variables (not in code)
- No user data storage currently implemented
- Generated images processed through Google's API

#### 9.2 Recommendations
- Implement user session management if adding authentication
- Add data retention policies for generated images
- Consider GDPR compliance for international users

---

### 10. Testing Requirements

#### 10.1 Functional Testing
- Prompt validation
- Image generation with different models
- Single image generation (`mb_app.py`)
- Multiple image generation (1-4 images) (`app.py`)
- Example prompt selection (`app.py`)
- Error handling for invalid inputs
- API key validation (supports both `GEMINI_API_KEY` and `GOOGLE_API_KEY`)

#### 10.2 API Testing
- **Direct Function Testing**: Test `generate_image()` function directly
- **Gradio Client API Testing**: Test via Gradio's client API
- **Endpoint Testing**: Verify both endpoints work:
  - `/generate_image` (button click handler)
  - `/generate_image_1` (Enter key submission handler)
- **Model Testing**: Verify both Gemini models work correctly
- **Test Scripts Available** (located in `test/` directory):
  - `test/test_mb_app.py`: Basic functionality tests
  - `test/test_gradio_api.py`: HTTP API endpoint tests
  - `test/test_gradio_client.py`: Gradio client API tests
  - `test/test_summary.py`: Comprehensive test suite
  - `test/test_api_with_outputs.py`: API tests with file output verification

#### 10.3 Performance Testing
- Parallel image generation performance (`app.py`)
- Sequential image generation performance (`mb_app.py`)
- API response time
- UI responsiveness during generation

#### 10.4 User Acceptance Testing
- Test with fashion designers and stylists
- Gather feedback on image quality
- Validate prompt effectiveness

---

### 11. Deployment

#### 11.1 Current Deployment
- Local development: 
  - Reference implementation: `python app.py`
  - Streamlined implementation: `python mb_app.py`
- Gradio default server (localhost:7860)

#### 11.2 Recommended Deployment Options
- Cloud platforms (AWS, GCP, Azure)
- Containerization (Docker)
- Serverless functions for API calls
- CDN for static assets

---

### 12. API Usage Guide

#### 12.1 Starting the API Server

To use `mb_app.py` as an API, start the Gradio server:

```bash
# Activate conda environment
conda activate moodboard

# Set API key (if not already set)
export GEMINI_API_KEY="your-api-key-here"
# OR
export GOOGLE_API_KEY="your-api-key-here"

# Start the server
python mb_app.py
```

The server will start on `http://127.0.0.1:7860` by default. You can access:
- **Web UI**: `http://127.0.0.1:7860`
- **API Endpoint**: `http://127.0.0.1:7860/gradio_api/api/predict/`

#### 12.2 Using Gradio Client API (Python)

The recommended way to interact with the API programmatically is using Gradio's client library:

```python
from gradio_client import Client

# Connect to the running server
client = Client("http://127.0.0.1:7860")

# Generate an image
result = client.predict(
    "A minimalist fashion moodboard with neutral colors",
    "gemini-3-pro-image-preview",  # or "gemini-2.5-flash-image"
    api_name="/generate_image"
)

# Result contains image information
print(f"Image path: {result}")
```

**Available Endpoints:**
- `/generate_image`: Button click handler
- `/generate_image_1`: Enter key submission handler

Both endpoints accept the same parameters:
- `prompt` (str, required): Subject description for the fashion moodboard (e.g., "sustainable luxury dress collection")
  - This input replaces `{SUBJECT_PLACEHOLDER}` in the prompt template
- `model_id` (str, optional): Model to use. Options:
  - `"gemini-3-pro-image-preview"` (default)
  - `"gemini-2.5-flash-image"`
- `template` (str, optional): Prompt template to use. If not provided, defaults to content from `prompt_templates/prompt_template.txt`
  - Must contain `{SUBJECT_PLACEHOLDER}` for subject replacement
  - Allows custom templates per API call

**Return Value:**
The API returns a PIL Image object. Gradio automatically serves this via its `/file=` endpoint and provides both a `url` (for display) and `path` (for API calls) in the response. The image is also saved to the `outputs/` directory with a unique filename for persistence.

**Note**: The generated moodboard follows a structured 2x4 grid layout (4 vertical portraits + 4 square detail images) as defined in the prompt template. The template can be customized per request.

#### 12.3 Image Editing API

The image editing endpoint allows you to edit specific regions of an image using bounding box coordinates:

**Endpoint**: `/edit_image_region`

**Parameters**:
- `current_image` (PIL Image or file path, optional): The image to edit (for UI usage)
- `image_path_file` (str, optional): File path to the image to edit (for API usage). If provided, takes priority over `current_image`
  - Can be a file path in `outputs/` directory or a Gradio temp file path
  - System automatically resolves temp file paths to original files in `outputs/` directory
- `x_top` (int, required): Top-left X coordinate of bounding box
- `y_top` (int, required): Top-left Y coordinate of bounding box
- `x_bottom` (int, required): Bottom-right X coordinate of bounding box
- `y_bottom` (int, required): Bottom-right Y coordinate of bounding box
- `edit_request` (str, required): Text description of desired changes
- `model_id` (str, optional): Model to use (defaults to `gemini-3-pro-image-preview`)
- `edit_template` (str, optional): Edit template to use. If not provided, defaults to content from `prompt_templates/edit_template.txt`
  - Must contain placeholders: `{X_TOP}`, `{Y_TOP}`, `{X_BOTTOM}`, `{Y_BOTTOM}`, `{WIDTH}`, `{HEIGHT}`, `{EDIT_REQUEST}`
  - **Grid cell placeholders (PRIMARY REFERENCE)**: `{GRID_ROW}`, `{GRID_ROW_NAME}`, `{GRID_COLUMN}`, `{GRID_CELL}`, `{GRID_CELL_DESCRIPTION}`, `{GRID_OVERLAPPING_CELLS}`
    - Automatically calculated based on bbox position in the 2x4 moodboard grid
    - More intuitive for AI models than raw coordinates (e.g., "Top Row (The Look), Cell 1")
  - **Normalized coordinate placeholders (SECONDARY REFERENCE)**: `{X_TOP_NORM}`, `{Y_TOP_NORM}`, `{X_BOTTOM_NORM}`, `{Y_BOTTOM_NORM}`, `{WIDTH_NORM}`, `{HEIGHT_NORM}` (values 0.0-1.0)
    - Resolution-independent coordinates for precise region boundaries
  - **Image dimension placeholders**: `{IMAGE_WIDTH}`, `{IMAGE_HEIGHT}` (full image dimensions)
  - Allows custom edit instructions per API call

**Return Value:**
The API returns a PIL Image object. Gradio automatically serves this via its `/file=` endpoint and provides both a `url` (for display) and `path` (for API calls) in the response. **Important:** If the original image file path is provided and exists in the `outputs/` directory, the edited image replaces the original file. Otherwise, a new file is created with a unique filename.

**Example Usage**:

```python
from gradio_client import Client
from PIL import Image

client = Client("http://127.0.0.1:7860")

# First, generate an image
image_path = client.predict(
    "sustainable luxury dress collection",
    "gemini-3-pro-image-preview",
    api_name="/generate_image"
)

# Load the image
current_image = Image.open(image_path)

# Edit a specific region (e.g., top-left 200x200 area)
# edit_template is optional - if not provided, uses default from prompt_templates/edit_template.txt
edited_image_path = client.predict(
    current_image,  # Current image
    0,              # x_top
    0,              # y_top
    200,            # x_bottom
    200,            # y_bottom
    "Change the color scheme to vibrant blues and purples",  # edit_request
    "gemini-3-pro-image-preview",  # model_id
    # edit_template,  # Optional: custom edit template
    api_name="/edit_image_region"
)
```

**Bounding Box Validation**:
- Coordinates must be integers
- `x_top < x_bottom` and `y_top < y_bottom`
- All coordinates must be within image bounds
- The region defined by the bounding box will be edited according to the edit request

#### 12.3 Using HTTP API Directly

You can also make direct HTTP requests to the API:

```python
import requests

# Prepare the request
url = "http://127.0.0.1:7860/gradio_api/api/predict/"
payload = {
    "data": [
        "A modern fashion moodboard with vibrant colors",
        "gemini-3-pro-image-preview"
    ],
    "event_data": None,
    "fn_index": 0,
    "trigger_id": 0,
    "session_hash": None
}

# Make the request
response = requests.post(url, json=payload, timeout=120)
result = response.json()

# Extract image path
image_path = result.get("data", [None])[0]
```

#### 12.4 Example: Complete Python Script

```python
from gradio_client import Client
from PIL import Image
import os

# Connect to server
client = Client("http://127.0.0.1:7860")

# Generate moodboard
# Note: The input is the subject description, which will be inserted into the prompt template
subject = "sustainable luxury dress collection"
model = "gemini-3-pro-image-preview"
# Template is optional - if not provided, uses default from prompt_templates/prompt_template.txt
# template = "Custom template with {SUBJECT_PLACEHOLDER}..."

image_path = client.predict(
    subject,
    model,
    # template,  # Uncomment to use custom template
    api_name="/generate_image"
)

# Load and display the image
if image_path and os.path.exists(image_path):
    image = Image.open(image_path)
    image.show()
    print(f"Generated image: {image_path}")
else:
    print("Failed to generate image")
```

#### 12.5 API Response Format

**Success Response:**
```json
{
  "data": ["/path/to/generated/image.png"],
  "is_generating": false,
  "duration": 5.23,
  "average_duration": 4.87
}
```

**Error Response:**
```json
{
  "error": "Error message here",
  "is_generating": false
}
```

#### 12.6 Integration Examples

**Flask/FastAPI Integration:**
```python
from fastapi import FastAPI
from gradio_client import Client

app = FastAPI()
gradio_client = Client("http://127.0.0.1:7860")

@app.post("/generate-moodboard")
async def generate_moodboard(prompt: str, model: str = "gemini-3-pro-image-preview"):
    image_path = gradio_client.predict(
        prompt,
        model,
        api_name="/generate_image"
    )
    return {"image_path": image_path, "prompt": prompt}
```

**Batch Processing:**
```python
from gradio_client import Client
from concurrent.futures import ThreadPoolExecutor

client = Client("http://127.0.0.1:7860")
prompts = [
    "Minimalist fashion moodboard",
    "Vintage fashion moodboard",
    "Modern luxury fashion moodboard"
]

def generate(prompt):
    return client.predict(prompt, "gemini-3-pro-image-preview", api_name="/generate_image")

# Process in parallel
with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(generate, prompts))
```

#### 12.7 Testing the API

Test scripts are available in the `test/` directory:

```bash
# Run comprehensive tests
python test/test_summary.py

# Test direct function calls
python test/test_mb_app.py

# Test Gradio client API
python test/test_gradio_client.py

# Test HTTP API endpoints
python test/test_gradio_api.py
```

#### 12.8 API Configuration

**Server Options:**
- Default port: `7860`
- Default host: `127.0.0.1` (localhost)
- To change: Modify `demo.launch(server_name="0.0.0.0", server_port=8080)` in `mb_app.py`

**Environment Variables:**
- `GEMINI_API_KEY` or `GOOGLE_API_KEY`: Required for Gemini API access

**Rate Limiting:**
- Rate limits are determined by Google Gemini API quotas
- No built-in rate limiting in the application
- Consider implementing rate limiting for production use

---

### 13. Maintenance and Support

#### 12.1 Monitoring
- API usage tracking
- Error rate monitoring
- User session analytics

#### 12.2 Updates
- Regular dependency updates
- Model version updates as new Gemini models are released
- Feature additions based on user feedback

---

### 14. Appendix

#### 14.1 Example Subject Inputs (for `mb_app.py`)
1. "sustainable luxury dress collection"
2. "contemporary Indian bridal collection"
3. "Rococo era ballgown with accurate embroidery patterns"
4. "minimalist streetwear for urban professionals"
5. "vintage-inspired evening wear collection"

#### 14.2 Example Prompts (for `app.py`)
1. "Create a textural, earthy fashion moodboard for a women's sustainable luxury dress collection, Lagos Spring/Summer 2026. The aesthetic is 'Modern Heritage meets Zero-Waste'."
2. "Create a layered fashion moodboard collage for a contemporary Indian bridal collection for the 2025-2026 season. The aesthetic theme is 'The Modern Minimalist Bride: Ethereal Lightness'."
3. "A moodboard for a Rococo era ballgown with accurate embroidery patterns."

#### 14.3 Glossary
- **Moodboard**: A visual collection of images, colors, textures, and materials that represent a design concept or aesthetic
- **Gemini**: Google's family of AI models for content generation
- **Search Grounding**: Using web search results to ground AI responses in factual, up-to-date information
- **Prompt Template**: External file (`prompt_templates/prompt_template.txt`) containing the structured prompt with placeholders for user input

### 15. Changelog

#### Version 1.11 (Current)
- **Grid Cell Detection for Image Editing:**
  - Added automatic grid cell detection based on bounding box coordinates
  - System calculates which grid cell(s) the bbox overlaps with in the 2x4 moodboard layout
  - Edit prompts now include grid cell location as PRIMARY REFERENCE (e.g., "Top Row (The Look), Cell 1")
  - Grid cell information is more intuitive for AI models than raw coordinates
  - Template includes placeholders: `{GRID_ROW}`, `{GRID_ROW_NAME}`, `{GRID_COLUMN}`, `{GRID_CELL}`, `{GRID_CELL_DESCRIPTION}`, `{GRID_OVERLAPPING_CELLS}`
  - Detects overlapping cells when bbox spans multiple grid cells
  - Updated edit template to prioritize grid cell location over coordinates
- **Normalized Coordinates for Image Editing:**
  - Added normalized coordinate support (0.0-1.0) to edit template
  - Edit prompts now include both absolute (pixel) and normalized coordinates
  - Normalized coordinates are resolution-independent and more reliable for AI models
  - Template includes placeholders: `{X_TOP_NORM}`, `{Y_TOP_NORM}`, `{X_BOTTOM_NORM}`, `{Y_BOTTOM_NORM}`, `{WIDTH_NORM}`, `{HEIGHT_NORM}`
  - Normalized coordinates serve as secondary reference after grid cell location
- **Image Editing Improvements:**
  - Fixed file path handling for image editing API calls
  - Edited images now replace the original file instead of creating new files
  - Improved path resolution for Gradio temp files and URLs
  - System now correctly locates original image files in `outputs/` directory when editing
  - Frontend now properly extracts and uses file paths from Gradio response objects
- **Frontend Integration:**
  - Updated image data handling to use full Gradio response objects (with `url` and `path` properties)
  - Fixed image URL generation to handle both objects and strings
  - Improved error handling for file path resolution

#### Version 1.9

#### Version 1.8
- Reorganized project structure:
  - Moved test files to `test/` directory (including `test_api_with_outputs.py`)
  - Moved template files to `prompt_templates/` directory
  - Template files: `prompt_templates/prompt_template.txt` and `prompt_templates/edit_template.txt`
- Updated file paths in code to reflect new directory structure
- All tests and templates now properly organized

#### Version 1.7
- Moved image editing prompt to external file (`prompt_templates/edit_template.txt`)
- Added Tab UI to organize multiple templates (Generation Template and Edit Template)
- Edit template uses placeholders: `{X_TOP}`, `{Y_TOP}`, `{X_BOTTOM}`, `{Y_BOTTOM}`, `{WIDTH}`, `{HEIGHT}`, `{EDIT_REQUEST}`
- Both templates are editable in UI and customizable via API
- Template system now supports both generation and editing workflows
- Image editing controls are now inside Edit Template tab (only visible when tab is selected)

#### Version 1.6
- Added image region editing feature with bounding box support
- UI controls for bounding box coordinates (x_top, y_top, x_bottom, y_bottom)
- Text-based edit requests for targeted image modifications
- API endpoint `/edit_image_region` for programmatic image editing
- Edit function validates bounding box coordinates and image bounds
- Only specified region is modified, rest of image remains unchanged
- **Note:** Version 1.10 added normalized coordinates (0.0-1.0) for improved AI model region understanding

#### Version 1.5
- Added editable prompt template component in UI (textbox next to model selector)
- Template component displays default content from `prompt_templates/prompt_template.txt`
- Users can customize template per request via UI or API
- API now accepts template as a parameter for flexible prompt customization
- Template is loaded from component instead of always reading from file

#### Version 1.4
- Implemented prompt template system for `mb_app.py`
- Added external `prompt_templates/prompt_template.txt` file for flexible prompt management
- User input now replaces `{SUBJECT_PLACEHOLDER}` in template
- Structured 2x4 grid moodboard output format (1440x1024 canvas)
- Fixed CSS deprecation warning (moved CSS to `launch()` method)
- Updated UI placeholder text to reflect subject input usage

#### Version 1.3
- Reorganized test files into `test/` directory
- Added comprehensive API usage guide to PRD
- Documented Gradio Client API integration examples
- Added HTTP API usage examples
- Added integration examples (Flask/FastAPI, batch processing)

#### Version 1.2
- Updated API key environment variable support: `mb_app.py` now accepts both `GEMINI_API_KEY` and `GOOGLE_API_KEY` environment variables
- Added comprehensive test suite for validating functionality
- Verified Gradio API endpoints work correctly
- Tested both input methods (button click and Enter key submission)

#### Version 1.1
- Added streamlined implementation (`mb_app.py`) with optimized UI layout
- Implemented 5:1 height ratio layout (image:input areas)
- Added bottom-centered input with send button
- Single image generation variant for focused workflow
- Keyboard support (Enter key submission)

#### Version 1.0 (Initial)
- Initial reference implementation (`app.py`)
- Multiple image generation (1-4 images)
- Example prompts feature
- Gallery view interface

---

**Document Version:** 1.11  
**Last Updated:** Added grid cell detection for image editing - automatically identifies which grid cell (2x4 layout) the bounding box overlaps with  
**Status:** Active Development

