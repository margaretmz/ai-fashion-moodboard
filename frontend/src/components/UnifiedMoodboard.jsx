import { useState, useEffect, useRef } from 'react'
import { generateImage, editImageRegion, getImageUrl } from '../services/api'
import BoundingBoxSelector from './BoundingBoxSelector'
import ReasoningTracesBar from './ReasoningTracesBar'
import HistoryPanel from './HistoryPanel'

function UnifiedMoodboard({ selectedModel, onImageChange, includeReasoning, onReasoningChange }) {
  const [currentImage, setCurrentImage] = useState(null)
  const [inputText, setInputText] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [bbox, setBbox] = useState(null) // No default bbox - only set when user drags
  const [imageUrl, setImageUrl] = useState(null)
  const [isEditMode, setIsEditMode] = useState(false)
  const [reasoningTrace, setReasoningTrace] = useState('') // New state for reasoning trace
  const [history, setHistory] = useState([]) // History of all versions
  const [historyOpen, setHistoryOpen] = useState(false) // History panel visibility
  const [selectedVersionId, setSelectedVersionId] = useState(null) // ID of currently selected/active version
  const [isViewMode, setIsViewMode] = useState(false) // Track if we're viewing a non-active entry (read-only)
  const inputRef = useRef(null)
  
  // Detect if running on Mac
  const isMac = typeof navigator !== 'undefined' && navigator.platform.toUpperCase().indexOf('MAC') >= 0

  // Update image URL when currentImage changes
  useEffect(() => {
    if (currentImage) {
      const url = getImageUrl(currentImage)
      setImageUrl(url || (typeof currentImage === 'object' ? currentImage.url : currentImage))
      setIsEditMode(true) // Switch to edit mode once image is generated
    } else {
      setImageUrl(null)
      setIsEditMode(false)
      setReasoningTrace('') // Clear reasoning when image is cleared
    }
  }, [currentImage])

  // Notify parent of image changes
  useEffect(() => {
    if (onImageChange) {
      onImageChange(currentImage)
    }
  }, [currentImage, onImageChange])

  const handleSubmit = async () => {
    if (!inputText.trim()) {
      setError(isEditMode ? 'Please enter an edit request' : 'Please enter a subject description')
      return
    }

    if (isEditMode && !currentImage) {
      setError('Please generate an image first')
      return
    }

    // Exit view mode when submitting (user is creating new content)
    setIsViewMode(false)

    setLoading(true)
    setError(null)
    setReasoningTrace('') // Clear previous reasoning on new submission

    try {
      if (isEditMode && currentImage) {
        // Edit mode: edit the existing image
        const imagePath = typeof currentImage === 'object' && currentImage.path ? currentImage.path : currentImage
        
        // Pass bbox coordinates only if bbox is selected, otherwise pass null
        const bboxCoords = bbox ? {
          x1: bbox.x1,
          y1: bbox.y1,
          x2: bbox.x2,
          y2: bbox.y2
        } : null
        
        const response = await editImageRegion(
          imagePath,
          bboxCoords,
          inputText,
          selectedModel,
          includeReasoning
        )
        
        // Add to history (store snapshot of image, reasoning, and bbox)
        addToHistory(response.image, 'edit', inputText, response.reasoning, bbox)
        setReasoningTrace(response.reasoning)
        
        // Create an "active" duplicate entry for continued editing (without reasoning/bbox)
        // and automatically select it to clear reasoning/bbox
        const activeEntry = createActiveEntry(response.image, response.reasoning)
        handleSelectVersion(activeEntry) // Select active entry to clear reasoning/bbox and enable editing
        
        setInputText('') // Clear input after edit
        // Optionally clear bbox after edit
        // setBbox(null)
      } else {
        // Generate mode: create new image
        const response = await generateImage(inputText, selectedModel, includeReasoning)
        
        // Add to history (store snapshot of image, reasoning, and bbox)
        // For generation, bbox is null initially
        addToHistory(response.image, 'generate', inputText, response.reasoning, null)
        setReasoningTrace(response.reasoning)
        
        // Create an "active" duplicate entry for continued editing (without reasoning/bbox)
        // and automatically select it to clear reasoning/bbox
        const activeEntry = createActiveEntry(response.image, response.reasoning)
        handleSelectVersion(activeEntry) // Select active entry to clear reasoning/bbox and enable editing
        
        setInputText('') // Clear input after generation
      }
    } catch (err) {
      setError(err.message || (isEditMode ? 'Failed to edit image' : 'Failed to generate image'))
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    // Disable submission in view mode
    if (isViewMode) return
    
    // Submit on Cmd+Enter (Mac) or Ctrl+Enter (Windows/Linux)
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault()
      handleSubmit()
    }
    // Allow Enter key to create new lines normally (no preventDefault)
  }

  // Add item to history - create a snapshot to avoid reference issues
  const addToHistory = (image, type, prompt, reasoning, bbox) => {
    // Extract image data as primitives to avoid reference issues
    // Store the essential properties as separate values
    // The backend now returns file paths as strings, so extract the filename
    let imagePath = null
    let imageUrl = null
    
    if (typeof image === 'string') {
      // Backend returns file path as string - extract just the filename
      imagePath = image.split('/').pop().split('\\').pop() // Get filename from path
      imageUrl = getImageUrl(image) // Construct URL from full path
    } else if (typeof image === 'object' && image !== null) {
      // Handle Gradio response object (fallback for compatibility)
      imageUrl = getImageUrl(image)
      imagePath = image.path || (image.url ? image.url.split('/').pop().split('=').pop() : null)
    }
    
    // Create a snapshot object with primitive values
    const imageSnapshot = {
      url: imageUrl,
      path: imagePath // Store just the filename for reliable restoration
    }
    
    // Store bbox as a snapshot (copy, not reference)
    const bboxSnapshot = bbox ? {
      x1: bbox.x1,
      y1: bbox.y1,
      x2: bbox.x2,
      y2: bbox.y2
    } : null
    
    const historyItem = {
      id: Date.now() + Math.random(), // Unique ID
      image: imageSnapshot, // Store snapshot with primitive values, not references
      type: type, // 'generate' or 'edit'
      prompt: prompt,
      reasoning: reasoning || '', // Store reasoning trace
      bbox: bboxSnapshot, // Store bbox snapshot
      isActive: false, // Regular history entry
      timestamp: new Date().toISOString()
    }
    setHistory(prev => [historyItem, ...prev]) // Add to beginning (newest first)
    return historyItem // Return the item so we can track its ID
  }

  // Create an "active" entry - duplicate of latest for continued editing
  // Removes any existing active entries first to ensure only one active entry exists
  // Returns the active item so it can be selected
  const createActiveEntry = (image, reasoning = '') => {
    // Extract image data as primitives
    // The backend now returns file paths as strings, so extract the filename
    let imagePath = null
    let imageUrl = null
    
    if (typeof image === 'string') {
      // Backend returns file path as string - extract just the filename
      imagePath = image.split('/').pop().split('\\').pop() // Get filename from path
      imageUrl = getImageUrl(image) // Construct URL from full path
    } else if (typeof image === 'object' && image !== null) {
      // Handle Gradio response object (fallback for compatibility)
      imageUrl = getImageUrl(image)
      imagePath = image.path || (image.url ? image.url.split('/').pop().split('=').pop() : null)
    }
    
    const imageSnapshot = {
      url: imageUrl,
      path: imagePath // Store just the filename for reliable restoration
    }
    
    const activeItem = {
      id: Date.now() + Math.random() + 0.5, // Unique ID (slightly different to avoid conflicts)
      image: imageSnapshot,
      type: 'active', // Mark as active
      prompt: '', // No prompt for active entry
      reasoning: reasoning, // No reasoning for active entry (user will edit next)
      bbox: null, // No bbox for active entry (user will draw next)
      isActive: true, // Mark as active entry
      timestamp: new Date().toISOString()
    }
    
    // Remove any existing active entries first, then add new active entry
    setHistory(prev => {
      const withoutActive = prev.filter(item => !item.isActive)
      // Add new active entry at the beginning
      return [activeItem, ...withoutActive]
    })
    
    // Return the active item so it can be selected
    return activeItem
  }

  // Restore version from history
  const handleSelectVersion = (historyItem) => {
    // Reconstruct image object from stored snapshot
    // Use the stored filename to construct the full path
    const filename = historyItem.image.path
    if (!filename) {
      console.error('Cannot restore image: no filename in history item', historyItem)
      return
    }
    
    // Construct the full file path (assuming files are in outputs/ directory)
    // The backend serves files via /gradio_api/file= endpoint with just the filename
    const restoredImage = {
      url: historyItem.image.url || getImageUrl(filename), // Use stored URL or construct from filename
      path: filename // Store just the filename
    }
    
    setCurrentImage(restoredImage)
    
    // If this is an "active" entry, enable editing (not view mode)
    if (historyItem.isActive) {
      setIsViewMode(false) // Enable interactions
      setReasoningTrace(historyItem.reasoning || '') // Clear reasoning for active entry
      setBbox(null) // Clear bbox for active entry
    } else {
      // Regular history entry: view mode (read-only)
      setIsViewMode(true) // Disable interactions
      setReasoningTrace(historyItem.reasoning || '') // Restore reasoning trace for viewing
      
      // Restore bbox if it exists (for display only)
      if (historyItem.bbox) {
        setBbox({
          x1: historyItem.bbox.x1,
          y1: historyItem.bbox.y1,
          x2: historyItem.bbox.x2,
          y2: historyItem.bbox.y2
        })
      } else {
        setBbox(null) // Clear bbox if no bbox was stored
      }
    }
    
    setSelectedVersionId(historyItem.id) // Mark this version as selected
    // Don't move item to top - keep it in place so highlighting works correctly
  }

  return (
    <div className="flex flex-col flex-1 bg-gradient-to-br from-gray-50 to-gray-100 overflow-hidden relative">
      {/* History Panel */}
      <HistoryPanel
        history={history}
        onSelectVersion={handleSelectVersion}
        isOpen={historyOpen}
        onToggle={() => setHistoryOpen(!historyOpen)}
        selectedVersionId={selectedVersionId}
      />
      {/* Main Image Display Area */}
      <div className="flex-1 flex items-center justify-center p-4 overflow-hidden min-h-0 relative">
        {imageUrl ? (
          <div className="relative w-full h-full flex items-center justify-center">
            <div className="relative w-full h-full flex items-center justify-center border-2 border-gray-200 rounded-lg overflow-hidden shadow-2xl bg-gray-50" style={{ filter: 'blur(0.5px)' }}>
              <BoundingBoxSelector
                imageUrl={imageUrl}
                bbox={bbox}
                onBboxChange={setBbox}
                disabled={isViewMode}
              />
            </div>
            {isEditMode && !loading && !isViewMode && (
              <div className="absolute top-4 left-4 bg-blue-600 text-white text-sm px-4 py-2 rounded-lg shadow-lg z-10">
                Edit Mode: {bbox ? 'Region selected' : 'Click and drag to select region (optional)'}
              </div>
            )}
            {isViewMode && (
              <div className="absolute top-4 left-4 bg-gray-600 text-white text-sm px-4 py-2 rounded-lg shadow-lg z-10">
                View Mode: Select 'Active' entry to continue editing
              </div>
            )}
          </div>
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            {loading ? (
              <div className="flex flex-col items-center justify-center">
                <div className="relative">
                  {/* Outer glow ring */}
                  <div className="absolute inset-0 w-28 h-28 bg-blue-400/20 rounded-full blur-xl animate-pulse"></div>
                  {/* Outer rotating ring */}
                  <div className="w-28 h-28 border-4 border-blue-100 rounded-full"></div>
                  {/* Inner rotating ring - gradient */}
                  <div className="absolute top-0 left-0 w-28 h-28 border-4 border-transparent border-t-blue-600 border-r-blue-500 rounded-full animate-spin" style={{ animationDuration: '0.8s' }}></div>
                  {/* Secondary rotating ring - opposite direction */}
                  <div className="absolute top-0 left-0 w-24 h-24 border-[3px] border-transparent border-b-purple-500 border-l-purple-400 rounded-full animate-spin" style={{ animationDuration: '1.2s', animationDirection: 'reverse' }}></div>
                  {/* Center pulsing dot with gradient */}
                  <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-4 h-4 bg-gradient-to-br from-blue-600 to-purple-600 rounded-full animate-pulse shadow-lg"></div>
                </div>
                <p className="mt-8 text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent animate-pulse">
                  Generating your moodboard...
                </p>
                <p className="mt-3 text-base text-gray-600">
                  This may take a moment
                </p>
                {/* Animated Progress Dots */}
                <div className="flex justify-center gap-2 mt-4">
                  <div className="w-3 h-3 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full animate-bounce shadow-md" style={{ animationDelay: '0s' }}></div>
                  <div className="w-3 h-3 bg-gradient-to-br from-purple-500 to-purple-600 rounded-full animate-bounce shadow-md" style={{ animationDelay: '0.2s' }}></div>
                  <div className="w-3 h-3 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full animate-bounce shadow-md" style={{ animationDelay: '0.4s' }}></div>
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow-lg p-12 text-center max-w-md">
                <div className="text-6xl mb-4">🎨</div>
                <h2 className="text-2xl font-semibold text-gray-800 mb-2">Create Your Moodboard</h2>
                <p className="text-gray-600">
                  Enter a subject description below to generate a beautiful fashion moodboard
                </p>
              </div>
            )}
          </div>
        )}
        
        {/* Loading Overlay for Image Area */}
        {loading && imageUrl && (
          <div className="absolute inset-0 bg-gradient-to-br from-black/50 via-black/40 to-black/50 backdrop-blur-md flex items-center justify-center z-50 animate-fadeIn">
            <div className="bg-white/95 backdrop-blur-sm rounded-3xl shadow-2xl p-10 max-w-md mx-4 transform transition-all border border-white/20">
              {/* Animated Spinner */}
              <div className="flex justify-center mb-8">
                <div className="relative">
                  {/* Outer glow ring */}
                  <div className="absolute inset-0 w-24 h-24 bg-blue-400/20 rounded-full blur-xl animate-pulse"></div>
                  {/* Outer ring */}
                  <div className="w-24 h-24 border-4 border-blue-100 rounded-full"></div>
                  {/* Rotating ring - gradient effect */}
                  <div className="absolute top-0 left-0 w-24 h-24 border-4 border-transparent border-t-blue-600 border-r-blue-500 rounded-full animate-spin" style={{ animationDuration: '0.8s' }}></div>
                  {/* Secondary rotating ring - opposite direction */}
                  <div className="absolute top-0 left-0 w-20 h-20 border-[3px] border-transparent border-b-purple-500 border-l-purple-400 rounded-full animate-spin" style={{ animationDuration: '1.2s', animationDirection: 'reverse' }}></div>
                  {/* Inner pulsing circle with gradient */}
                  <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-10 h-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-full animate-pulse shadow-lg"></div>
                  {/* Center dot */}
                  <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-3 h-3 bg-white rounded-full shadow-md"></div>
                </div>
              </div>
              
              {/* Progress Text */}
              <div className="text-center">
                <h3 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-3">
                  {isEditMode ? 'Editing Image...' : 'Generating Moodboard...'}
                </h3>
                <p className="text-gray-600 mb-6 text-base">
                  {isEditMode 
                    ? 'Applying your changes to the selected region'
                    : 'Creating your fashion moodboard with AI'}
                </p>
                
                {/* Animated Progress Dots */}
                <div className="flex justify-center gap-2">
                  <div className="w-3 h-3 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full animate-bounce shadow-md" style={{ animationDelay: '0s' }}></div>
                  <div className="w-3 h-3 bg-gradient-to-br from-purple-500 to-purple-600 rounded-full animate-bounce shadow-md" style={{ animationDelay: '0.2s' }}></div>
                  <div className="w-3 h-3 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full animate-bounce shadow-md" style={{ animationDelay: '0.4s' }}></div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Bottom Input Area */}
      <div className="bg-white border-t border-gray-200 shadow-lg">
        <ReasoningTracesBar reasoningTrace={reasoningTrace} />
        <div className="p-4">
          <div className="max-w-4xl mx-auto">
            {error && (
              <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                {error}
              </div>
            )}
            
            <div className="flex gap-3 items-end">
            <div className="flex-1">
              <textarea
                ref={inputRef}
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={loading || isViewMode}
                placeholder={
                  isViewMode
                    ? "View mode: Select 'Active' entry to continue editing"
                    : isEditMode 
                      ? "Describe what you want to change (optional: click and drag on image to select a specific region)... Press Cmd+Enter or Ctrl+Enter to submit" 
                      : "e.g., sustainable luxury dress collection. Press Cmd+Enter or Ctrl+Enter to generate"
                }
                rows={3}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none text-base disabled:bg-gray-100 disabled:cursor-not-allowed"
              />
            </div>
          </div>
          
          {isEditMode && bbox && (
            <p className="text-xs text-gray-500 mt-2 text-center">
              Selected region: ({Math.round(bbox.x1)}, {Math.round(bbox.y1)}) to ({Math.round(bbox.x2)}, {Math.round(bbox.y2)}) • Click to clear
            </p>
          )}
          {isEditMode && !bbox && (
            <p className="text-xs text-gray-500 mt-2 text-center">
              Optional: Click and drag on the image to select a specific region, or leave empty to edit the entire image
            </p>
          )}
            <p className="text-xs text-gray-400 mt-1 text-center">
              {isMac ? '⌘' : 'Ctrl'}+Enter to submit • Enter for new line
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default UnifiedMoodboard

