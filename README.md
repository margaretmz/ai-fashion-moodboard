# AI Fashion Moodboard

A tool that helps generate unique fashion moodboards to find your next design inspiration using Google Gemini AI.

## Prerequisites

- Python 3.11+ (with conda recommended)
- Node.js 18+ and npm
- Google Gemini API key (set as `GEMINI_API_KEY` or `GOOGLE_API_KEY` environment variable)

## Quick Start

### 1. Backend Setup (Gradio API)

```bash
# Create and activate conda environment (recommended)
conda create -n moodboard python=3.11
conda activate moodboard

# Install Python dependencies
pip install -r requirements.txt

# Set your API key
export GEMINI_API_KEY="your-api-key-here"
# OR
export GOOGLE_API_KEY="your-api-key-here"

# Run the Gradio backend
python mb_app.py
```

The backend will start at `http://127.0.0.1:7860`

### 2. Frontend Setup (React UI)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will start at `http://localhost:3000`

## Usage

1. Open `http://localhost:3000` in your browser
2. Select a Gemini model (3 Pro or 2.5 Flash)
3. Enter a subject description (e.g., "sustainable luxury dress collection")
4. Press `Cmd+Enter` (Mac) or `Ctrl+Enter` (Windows/Linux) to generate
5. After generation, you can edit the image by:
   - Optionally selecting a region by clicking and dragging on the image
   - Entering an edit request
   - Pressing `Cmd+Enter` or `Ctrl+Enter` to apply

## Example Prompts

- Create a textural, earthy fashion moodboard for a women's sustainable luxury dress collection, Lagos Spring/Summer 2026. The aesthetic is "Modern Heritage meets Zero-Waste".
- Create a layered fashion moodboard collage for a contemporary Indian bridal collection for the 2025-2026 season. The aesthetic theme is "The Modern Minimalist Bride: Ethereal Lightness".
- A moodboard for a Rococo era ballgown with accurate embroidery patterns.

## Project Structure

- `mb_app.py` - Main Gradio backend application
- `ref_app.py` - Reference implementation
- `frontend/` - React frontend application
- `prompt_templates/` - Prompt templates for generation and editing
- `outputs/` - Generated images are saved here
- `test/` - Test scripts

## API Usage

The Gradio backend exposes REST APIs at:
- `POST /api/generate_image` - Generate a new moodboard
- `POST /api/edit_image_region` - Edit an existing image

See `PRD.md` for detailed API documentation.

## Misc notes

### Search grounding

Gemini [can ground the results](https://ai.google.dev/gemini-api/docs/image-generation#use-with-grounding) in recency with Google Search. This is compelling, especially for prompts that contain date information, for example. We conditionally enable search grounding, depending on the input prompt. Below is an example of such a prompt:

> Create a layered fashion moodboard collage for a contemporary Indian bridal collection for the 2025-2026 season. The aesthetic theme is "The Modern Minimalist Bride: Ethereal Lightness".

### Reasoning traces

The outputs always contain the [reasoning](https://ai.google.dev/gemini-api/docs/thinking) Gemini used to arrive at the final output. This is particularly beneficial for this project, because the intricacies in fashion could be quite complex. Therefore, it helps the users to understand why and how Gemini reacted to input prompt.

### Gemini 3.0 Pro vs. 2.5 Flash

Even though we provide choosing between 3.0 Pro and 2.5 Flash, we haven't fully experimented with above-mentioned features along with 2.5 Flash. Users are welcome to run experiments and report issues should they find any.

## Acknowledgements

Thanks to the Google ML Developers Program for providing GCP credits that supported this project.