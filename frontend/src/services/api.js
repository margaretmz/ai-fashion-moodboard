import axios from 'axios'

// Prefer same-origin calls (works on Hugging Face Spaces + local dev via Vite proxy).
// Override with VITE_API_BASE_URL if you host the backend elsewhere.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

// Helper to wait for Gradio API to be ready
async function waitForAPI() {
  // Skip the check in browser - just proceed with API calls
  // The actual API calls will fail gracefully if server is not available
  return true
}

// Get API info to find correct endpoint indices
async function getAPIInfo() {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/info`, { timeout: 5000 })
    return response.data
  } catch (e) {
    // If /api/info doesn't work, we'll use default indices
    return null
  }
}

// Generate image
export async function generateImage(subject, modelId, apiKey = "") {
  await waitForAPI()
  
  try {
    // Gradio named endpoints use /gradio_api/api/{endpoint_name} format
    // The generate_image function needs 3 inputs: user_input, model_id, template
    // template can be null to use the default template
    // Use Vite proxy in dev mode (relative URL) or direct URL in production
    const apiUrl = API_BASE_URL ? `${API_BASE_URL}/gradio_api/api/generate_image` : '/gradio_api/api/generate_image'
    
    const response = await axios.post(
      apiUrl,
      {
        data: [
          subject, // user_input
          modelId, // model_id
          "", // template (empty string = use default)
          apiKey || "" // api_key (optional)
        ],
      },
      {
        headers: {
          'Content-Type': 'application/json'
        },
        timeout: 120000, // 2 minutes for image generation
        withCredentials: false
      }
    )

    if (response.data && response.data.data) {
      if (response.data.data.length > 1) {
        // Handle multiple outputs (image path and reasoning)
        // Backend now returns file path as string
        const imagePath = response.data.data[0]
        return {
          image: imagePath, // File path string
          reasoning: response.data.data[1]
        }
      } else if (response.data.data.length === 1) {
        // Handle single output (image path only)
        return { image: response.data.data[0], reasoning: '' }
      }
    }
    throw new Error('No data returned from API')
  } catch (error) {
    if (error.response) {
      const errorMsg = error.response.data?.error || error.response.data?.detail || error.response.statusText
      throw new Error(`API Error: ${error.response.status} - ${errorMsg}`)
    }
    throw new Error(error.message || 'Failed to generate image')
  }
}

// Edit image region
// bboxCoords can be null/undefined if no region is selected (edit entire image)
export async function editImageRegion(imagePath, bboxCoords, editRequest, modelId, apiKey = "") {
  await waitForAPI()
  
  try {
    // Gradio named endpoints use /gradio_api/api/{endpoint_name} format
    // Use Vite proxy in dev mode (relative URL) or direct URL in production
    const apiUrl = API_BASE_URL ? `${API_BASE_URL}/gradio_api/api/edit_image_region` : '/gradio_api/api/edit_image_region'
    
    // If bboxCoords is null/undefined, pass null for all coordinates (edit entire image)
    const xTop = bboxCoords ? bboxCoords.x1 : null
    const yTop = bboxCoords ? bboxCoords.y1 : null
    const xBottom = bboxCoords ? bboxCoords.x2 : null
    const yBottom = bboxCoords ? bboxCoords.y2 : null
    
    const response = await axios.post(
      apiUrl,
      {
        data: [
          null, // image_display (not used when image_path_input is provided)
          imagePath, // image_path_input - the file path
          xTop,
          yTop,
          xBottom,
          yBottom,
          editRequest,
          modelId,
          "", // edit_template (empty string = use default)
          apiKey || "" // api_key (optional)
        ],
      },
      {
        headers: {
          'Content-Type': 'application/json'
        },
        timeout: 120000 // 2 minutes for image editing
      }
    )

    if (response.data && response.data.data) {
      if (response.data.data.length > 1) {
        // Handle multiple outputs (image path and reasoning)
        // Backend now returns file path as string
        const imagePath = response.data.data[0]
        return {
          image: imagePath, // File path string
          reasoning: response.data.data[1]
        }
      } else if (response.data.data.length === 1) {
        // Handle single output (image path only)
        return { image: response.data.data[0], reasoning: '' }
      }
    }
    throw new Error('No data returned from API')
  } catch (error) {
    if (error.response) {
      const errorMsg = error.response.data?.error || error.response.data?.detail || error.response.statusText
      throw new Error(`API Error: ${error.response.status} - ${errorMsg}`)
    }
    throw new Error(error.message || 'Failed to edit image')
  }
}

// Helper to get image URL from file path, URL, or image data object
export function getImageUrl(filePathOrUrlOrObject) {
  if (!filePathOrUrlOrObject) return null
  
  // If it's an object with url or path property
  if (typeof filePathOrUrlOrObject === 'object') {
    // Prefer URL if available (full URL that can be accessed directly)
    if (filePathOrUrlOrObject.url) {
      return filePathOrUrlOrObject.url
    } else if (filePathOrUrlOrObject.path) {
      // Construct URL from path (filename)
      const filename = filePathOrUrlOrObject.path.split('/').pop().split('\\').pop()
      return API_BASE_URL ? `${API_BASE_URL}/gradio_api/file=${filename}` : `/gradio_api/file=${filename}`
    }
    return null
  }
  
  // If it's already a full URL, return it directly
  if (typeof filePathOrUrlOrObject === 'string' && filePathOrUrlOrObject.startsWith('http')) {
    return filePathOrUrlOrObject
  }
  
  // If it's a file path (string), extract filename and construct Gradio file URL
  // Backend now returns full file paths, but we only need the filename for Gradio
  // Extract just the filename from the path (handles both absolute and relative paths)
  const filename = filePathOrUrlOrObject.split('/').pop().split('\\').pop()
  return API_BASE_URL ? `${API_BASE_URL}/gradio_api/file=${filename}` : `/gradio_api/file=${filename}`
}
