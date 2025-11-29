# Fashion Moodboard Frontend

Modern React-based frontend application for the Fashion Moodboard Generator.

## Features

- **Image Generation**: Generate fashion moodboards from text descriptions
- **Image Editing**: Edit specific regions of images using bounding box selection
- **Interactive Bounding Box**: Click and drag to select regions for editing
- **Model Selection**: Choose between Gemini 3 Pro and Gemini 2.5 Flash
- **Real-time Updates**: See generated and edited images instantly

## Prerequisites

- Node.js 18+ and npm
- Gradio backend running on `http://127.0.0.1:7860`

## Installation

```bash
npm install
```

## Development

```bash
npm run dev
```

The application will start on `http://localhost:3000`

## Build

```bash
npm run build
```

## Usage

1. Start the Gradio backend:
   ```bash
   cd ..
   conda activate moodboard
   python mb_app.py
   ```

2. Start the frontend:
   ```bash
   npm run dev
   ```

3. Open `http://localhost:3000` in your browser

## API Integration

The frontend connects to the Gradio API at `http://127.0.0.1:7860`:
- `/gradio_api/api/predict/` - For image generation and editing
- `/file=` - For serving generated image files

## Features

### Image Generation
- Enter a subject description (e.g., "sustainable luxury dress collection")
- Click "Generate Image" or press Enter
- Generated images are saved with unique filenames

### Image Editing
- Generate an image first
- Click and drag on the image to select a bounding box
- Or manually enter coordinates
- Enter an edit request describing the desired changes
- Click "Apply Edit" to update the selected region

## Technology Stack

- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **Axios** - HTTP client for API calls

