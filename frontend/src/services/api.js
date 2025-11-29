import axios from 'axios'

// Use Vite proxy in development, or direct URL in production
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || (import.meta.env.DEV ? '' : 'http://127.0.0.1:7860')

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
export async function generateImage(subject, modelId) {
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
        data: [subject, modelId, ""], // user_input, model_id, template (empty string = use default)
      },
      {
        headers: {
          'Content-Type': 'application/json'
        },
        timeout: 120000, // 2 minutes for image generation
        withCredentials: false
      }
    )

    if (response.data && response.data.data && response.data.data[0]) {
      const result = response.data.data[0]
      // Gradio returns image data as an object with 'url' and 'path' properties
      // Return the full result object so we can access both url (for display) and path (for API calls)
      if (typeof result === 'object') {
        return result
      } else if (typeof result === 'string') {
        // Direct path string - wrap it in an object for consistency
        return { path: result, url: result }
      }
      
      // Fallback: return the result as-is
      return result
    }
    throw new Error('No image path returned from API')
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
export async function editImageRegion(imagePath, bboxCoords, editRequest, modelId) {
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
          "" // edit_template (empty string = use default)
        ],
      },
      {
        headers: {
          'Content-Type': 'application/json'
        },
        timeout: 120000 // 2 minutes for image editing
      }
    )

    if (response.data && response.data.data && response.data.data[0]) {
      const result = response.data.data[0]
      // Gradio returns image data as an object with 'url' and 'path' properties
      // Return the full object so we can access both url (for display) and path (for API calls)
      if (typeof result === 'object') {
        return result
      } else if (typeof result === 'string') {
        // Direct path string - wrap it in an object for consistency
        return { path: result, url: result }
      }
      return result
    }
    throw new Error('No edited image path returned from API')
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
      // Construct URL from path
      const baseUrl = API_BASE_URL || 'http://127.0.0.1:7860'
      return `${baseUrl}/gradio_api/file=${filePathOrUrlOrObject.path}`
    }
    return null
  }
  
  // If it's already a full URL, return it directly
  if (filePathOrUrlOrObject.startsWith('http')) {
    return filePathOrUrlOrObject
  }
  
  // If it's a file path, construct the Gradio file URL
  // Gradio serves files via /gradio_api/file= endpoint
  const baseUrl = API_BASE_URL || 'http://127.0.0.1:7860'
  
  // If it's an absolute path, use it directly with /gradio_api/file=
  if (filePathOrUrlOrObject.startsWith('/')) {
    return `${baseUrl}/gradio_api/file=${filePathOrUrlOrObject}`
  }
  
  // Otherwise, extract filename and use it
  const filename = filePathOrUrlOrObject.split('/').pop()
  return `${baseUrl}/gradio_api/file=${filename}`
}

