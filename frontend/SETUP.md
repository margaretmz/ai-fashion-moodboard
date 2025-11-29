# Frontend Setup Guide

## Quick Start

1. **Install Dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start Gradio Backend** (in a separate terminal)
   ```bash
   cd ..
   conda activate moodboard
   python mb_app.py
   ```

3. **Start Frontend Development Server**
   ```bash
   npm run dev
   ```

4. **Open Browser**
   - Navigate to `http://localhost:3000`

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Header.jsx              # Header with model selector
│   │   ├── ImageGenerator.jsx     # Image generation component
│   │   ├── ImageEditor.jsx        # Image editing component
│   │   └── BoundingBoxSelector.jsx # Interactive bounding box selector
│   ├── services/
│   │   └── api.js                 # Gradio API integration
│   ├── App.jsx                    # Main application component
│   ├── main.jsx                   # React entry point
│   └── index.css                  # Global styles
├── public/                        # Static assets
├── package.json                   # Dependencies
├── vite.config.js                # Vite configuration
└── tailwind.config.js            # Tailwind CSS configuration
```

## Features

### Image Generation
- Enter subject description in the input field
- Click "Generate Image" or press Enter
- Generated images are displayed and saved with unique filenames

### Image Editing
- Generate an image first
- Click and drag on the image to select a bounding box region
- Or manually enter coordinates in the input fields
- Enter an edit request describing desired changes
- Click "Apply Edit" to update the selected region

### Interactive Bounding Box
- Visual bounding box selector with drag-to-select functionality
- Real-time coordinate updates
- Corner handles for visual feedback

## API Integration

The frontend connects to the Gradio backend API at `http://127.0.0.1:7860`:

- **Generate Image**: `POST /api/predict` with `api_name: '/generate_image'`
- **Edit Image**: `POST /api/predict` with `api_name: '/edit_image_region'`
- **File Serving**: Images served via `/file=` endpoint

## Configuration

- API URL can be configured via environment variable `VITE_API_BASE_URL`
- Default: `http://127.0.0.1:7860`
- CORS is handled via Vite proxy during development

## Build for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

