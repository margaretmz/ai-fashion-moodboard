import { useState, useRef, useEffect } from 'react'
import { editImageRegion, getImageUrl } from '../services/api'
import BoundingBoxSelector from './BoundingBoxSelector'

function ImageEditor({ image, selectedModel, onImageEdited, apiKey }) {
  const [editRequest, setEditRequest] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [bbox, setBbox] = useState({ x1: 0, y1: 0, x2: 100, y2: 100 })
  const [imageUrl, setImageUrl] = useState(null)

  useEffect(() => {
    if (image) {
      // Convert file path or image object to URL for display
      const url = getImageUrl(image)
      setImageUrl(url || (typeof image === 'object' ? image.url : image))
    } else {
      setImageUrl(null)
    }
  }, [image])

  const handleEdit = async () => {
    if (!image) {
      setError('Please generate an image first')
      return
    }

    if (!editRequest.trim()) {
      setError('Please enter an edit request')
      return
    }

    setLoading(true)
    setError(null)

    try {
      // Extract the file path from the image object (for API call)
      // If image is an object with 'path', use that; otherwise use the image directly
      const imagePath = typeof image === 'object' && image.path ? image.path : image
      
      const { x1, y1, x2, y2 } = bbox
      const bboxCoords = { x1, y1, x2, y2 }
      const editedImageData = await editImageRegion(
        imagePath,
        bboxCoords,
        editRequest,
        selectedModel,
        apiKey
      )
      // Update the parent component with the edited image
      onImageEdited(editedImageData)
      // Also update local imageUrl immediately for display
      const newUrl = getImageUrl(editedImageData)
      setImageUrl(newUrl)
      // Force a re-render by updating the image state
      // The useEffect will also handle this when the image prop updates
    } catch (err) {
      setError(err.message || 'Failed to edit image')
    } finally {
      setLoading(false)
    }
  }

  if (!image) {
    return (
      <div className="space-y-4">
        <h2 className="text-xl font-semibold text-gray-800">Edit Image Region</h2>
        <div className="bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg p-12 text-center">
          <p className="text-gray-500">
            Generate an image first to enable editing
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold text-gray-800">Edit Image Region</h2>
      
      {imageUrl ? (
        <div className="relative border-2 border-gray-200 rounded-lg overflow-hidden">
          <BoundingBoxSelector
            imageUrl={imageUrl}
            bbox={bbox}
            onBboxChange={setBbox}
          />
          <p className="text-xs text-gray-500 mt-2 text-center">
            Current Image: {typeof image === 'object' ? (image.path || image.url || 'N/A') : image || 'N/A'}
          </p>
        </div>
      ) : (
        <div className="bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
          <p className="text-gray-500">No image to display</p>
        </div>
      )}

      <div className="grid grid-cols-2 gap-2">
        <div>
          <label className="block text-xs font-medium text-gray-700 mb-1">
            X Top
          </label>
          <input
            type="number"
            value={bbox.x1}
            onChange={(e) => setBbox({ ...bbox, x1: parseInt(e.target.value) || 0 })}
            className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-700 mb-1">
            Y Top
          </label>
          <input
            type="number"
            value={bbox.y1}
            onChange={(e) => setBbox({ ...bbox, y1: parseInt(e.target.value) || 0 })}
            className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-700 mb-1">
            X Bottom
          </label>
          <input
            type="number"
            value={bbox.x2}
            onChange={(e) => setBbox({ ...bbox, x2: parseInt(e.target.value) || 0 })}
            className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-700 mb-1">
            Y Bottom
          </label>
          <input
            type="number"
            value={bbox.y2}
            onChange={(e) => setBbox({ ...bbox, y2: parseInt(e.target.value) || 0 })}
            className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Edit Request
        </label>
        <textarea
          value={editRequest}
          onChange={(e) => setEditRequest(e.target.value)}
          placeholder="Describe what you want to change in this region..."
          rows={3}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      <button
        onClick={handleEdit}
        disabled={loading}
        className="w-full bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
      >
        {loading ? 'Editing...' : 'Apply Edit'}
      </button>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}
    </div>
  )
}

export default ImageEditor
