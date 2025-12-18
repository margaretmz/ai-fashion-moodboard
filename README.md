---
title: NB Fashion Moodboard
emoji: 👗
colorFrom: pink
sdk: docker
pinned: false
short_description: Nano Banana powered fashion moodboard
---

# AI Fashion Moodboard

A tool that helps generate unique fashion moodboards to find your next design inspiration using Google Gemini AI.

> [!TIP]
> Check out the accompanying blog post on [Medium](https://margaretmz.medium.com/0d5bfd54a557) and Hugging Face [blog](https://huggingface.co/blog/margaretmz/ai-fashion-moodboard). Quickly try out the demo on Hugging Face Spaces [here](https://huggingface.co/spaces/sayakpaul/nb-fashion-moodboard) 🤗

## Prerequisites

- Python 3.11+ (with conda recommended)
- Node.js 18+ and npm
- Google Gemini API key (set as `GEMINI_API_KEY` or `GOOGLE_API_KEY` environment variable, or paste it into the UI if running without env vars)

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

## Deploy on Hugging Face Spaces (Docker)

This repo includes a `Dockerfile` that runs:
- the Gradio backend internally on port `7861`
- the React UI + reverse-proxy on port `7860` (the port Spaces expects)

### Steps

1. Create a new Hugging Face Space:
   - **SDK**: `Docker`
   - **Space name**: anything you like

2. Push this repository to the Space (either via git or “Files” upload).

3. Add your API key as a Space secret:
   - `GEMINI_API_KEY` (recommended)
   - or `GOOGLE_API_KEY`

4. Wait for the Space image to build, then open the Space URL.

### Local Docker run (optional)

```bash
docker build -t ai-fashion-moodboard .
docker run --rm -p 7860:7860 -e GEMINI_API_KEY="your-api-key-here" ai-fashion-moodboard
```

Open `http://127.0.0.1:7860`.

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

## Acknowledgements

Thanks to the Google ML Developers Program for providing GCP credits that supported this project.
