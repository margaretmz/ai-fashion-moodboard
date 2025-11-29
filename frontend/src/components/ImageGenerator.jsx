import { useState } from 'react'
import { generateImage, getImageUrl } from '../services/api'

function ImageGenerator({ onImageGenerated, selectedModel, currentImage }) {
  const [subject, setSubject] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [generatedImage, setGeneratedImage] = useState(null)
  
  // Use currentImage if available (includes edited images), otherwise use local generatedImage
  const displayImage = currentImage || generatedImage

  const handleGenerate = async () => {
    if (!subject.trim()) {
      setError('Please enter a subject description')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const imageData = await generateImage(subject, selectedModel)
      setGeneratedImage(imageData)
      onImageGenerated(imageData)
    } catch (err) {
      setError(err.message || 'Failed to generate image')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold text-gray-800">Generate Moodboard</h2>
      
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700">
          Subject Description
        </label>
        <input
          type="text"
          value={subject}
          onChange={(e) => setSubject(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleGenerate()}
          placeholder="e.g., sustainable luxury dress collection"
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      <button
        onClick={handleGenerate}
        disabled={loading}
        className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
      >
        {loading ? 'Generating...' : 'Generate Image'}
      </button>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {displayImage && (
        <div className="mt-4">
          <img
            src={getImageUrl(displayImage)}
            alt={currentImage ? "Edited moodboard" : "Generated moodboard"}
            className="w-full rounded-lg shadow-md"
            onError={(e) => {
              // Fallback: try using the URL directly if it's an object
              if (typeof displayImage === 'object' && displayImage.url) {
                e.target.src = displayImage.url
              }
            }}
          />
          <p className="text-xs text-gray-500 mt-2 break-all">
            {currentImage ? "Edited" : "Generated"} Image: {typeof displayImage === 'object' ? displayImage.path || displayImage.url : displayImage}
          </p>
        </div>
      )}
    </div>
  )
}

export default ImageGenerator

