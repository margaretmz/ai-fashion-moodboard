import { useState, useEffect, useRef } from 'react'
import { getImageUrl } from '../services/api'

function HistoryPanel({ history, onSelectVersion, isOpen, onToggle, selectedVersionId }) {
  const [isAutoPlaying, setIsAutoPlaying] = useState(false)
  const [currentAutoPlayIndex, setCurrentAutoPlayIndex] = useState(0)
  const intervalRef = useRef(null)
  const onSelectVersionRef = useRef(onSelectVersion)

  // Update ref when callback changes
  useEffect(() => {
    onSelectVersionRef.current = onSelectVersion
  }, [onSelectVersion])

  // Filter out active entries for auto-play (only show actual versions)
  const versionsForAutoPlay = history.filter(item => !item.isActive).reverse() // Reverse to go from oldest to newest

  // Auto-play logic
  useEffect(() => {
    if (isAutoPlaying && versionsForAutoPlay.length > 0 && isOpen) {
      // Start from the beginning (oldest)
      setCurrentAutoPlayIndex(0)
      
      intervalRef.current = setInterval(() => {
        setCurrentAutoPlayIndex(prevIndex => {
          const nextIndex = prevIndex + 1
          
          // If we've reached the end, stop auto-play
          if (nextIndex >= versionsForAutoPlay.length) {
            setIsAutoPlaying(false)
            return prevIndex
          }
          
          // Select the next version using ref to avoid dependency issues
          onSelectVersionRef.current(versionsForAutoPlay[nextIndex])
          return nextIndex
        })
      }, 2000) // 2 seconds interval
    } else {
      // Clear interval when auto-play stops or panel closes
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }
    }

    // Cleanup on unmount
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [isAutoPlaying, versionsForAutoPlay.length, isOpen])

  // Stop auto-play when panel closes
  useEffect(() => {
    if (!isOpen && isAutoPlaying) {
      setIsAutoPlaying(false)
    }
  }, [isOpen, isAutoPlaying])

  // Stop auto-play when user manually selects a version
  const handleManualSelect = (item) => {
    if (isAutoPlaying) {
      setIsAutoPlaying(false)
    }
    onSelectVersion(item)
  }

  // Handle auto-play toggle
  const handleAutoPlayToggle = () => {
    if (isAutoPlaying) {
      // Stop auto-play
      setIsAutoPlaying(false)
      setCurrentAutoPlayIndex(0)
    } else {
      // Start auto-play from the oldest version
      if (versionsForAutoPlay.length > 0) {
        setIsAutoPlaying(true)
        setCurrentAutoPlayIndex(0)
        // Immediately select the first (oldest) version
        onSelectVersion(versionsForAutoPlay[0])
      }
    }
  }

  // Always render both the indicator and panel, control visibility with classes
  return (
    <>
      {/* Elegant History Indicator - Always visible when panel is closed */}
      {!isOpen && (
        <button
          onClick={onToggle}
          className="fixed right-0 top-1/2 transform -translate-y-1/2 z-40 group transition-all duration-300 hover:right-2"
          title="View Version History"
        >
          <div className="relative">
            {/* Subtle glow effect */}
            <div className="absolute inset-0 bg-gradient-to-r from-blue-500/20 to-purple-500/20 rounded-l-2xl blur-md opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            
            {/* Main indicator card */}
            <div className="relative bg-white/95 backdrop-blur-sm shadow-xl rounded-l-2xl px-4 py-6 border-l-2 border-t border-b border-gray-200 group-hover:border-blue-300 transition-all duration-300">
              {/* Icon */}
              <div className="flex flex-col items-center gap-2">
                <svg className="w-6 h-6 text-gray-600 group-hover:text-blue-600 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
                
                {/* History count badge */}
                {history.length > 0 && (
                  <div className="relative">
                    <span className="inline-flex items-center justify-center min-w-[24px] h-6 px-2 bg-gradient-to-br from-blue-500 to-purple-500 text-white text-xs font-bold rounded-full shadow-lg animate-pulse">
                      {history.length}
                    </span>
                    {/* Pulse ring animation */}
                    <span className="absolute inset-0 inline-flex items-center justify-center">
                      <span className="absolute w-6 h-6 bg-blue-500 rounded-full animate-ping opacity-75"></span>
                    </span>
                  </div>
                )}
              </div>
              
              {/* Subtle arrow hint */}
              <div className="absolute left-0 top-1/2 transform -translate-y-1/2 -translate-x-1 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <svg className="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </div>
          </div>
        </button>
      )}

      {/* History Panel with slide-in animation */}
      <div className={`fixed right-0 top-0 h-full w-80 bg-white shadow-2xl z-40 flex flex-col border-l border-gray-200 transform transition-transform duration-500 ease-out ${
        isOpen ? 'translate-x-0' : 'translate-x-full'
      }`}>
      {/* Auto-play Progress Indicator */}
      {isAutoPlaying && versionsForAutoPlay.length > 0 && (
        <div className="h-1 bg-gray-100 relative overflow-hidden">
          <div 
            className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-300 ease-linear"
            style={{ 
              width: `${((currentAutoPlayIndex + 1) / versionsForAutoPlay.length) * 100}%` 
            }}
          />
        </div>
      )}
      
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-gradient-to-r from-gray-50 to-white">
        <h2 className="text-lg font-bold text-gray-800">Version History</h2>
        <button
          onClick={onToggle}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          title="Hide History"
        >
          <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      {/* History List */}
      <div className="flex-1 overflow-y-auto p-4">
        {history.length === 0 ? (
          <div className="text-center py-12 text-gray-400">
            <svg className="w-16 h-16 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            <p className="text-sm">No history yet</p>
            <p className="text-xs mt-1">Generated and edited images will appear here</p>
          </div>
        ) : (
          <div className="space-y-3">
            {history.map((item, index) => {
              const imageUrl = getImageUrl(item.image)
              const isActive = item.isActive === true
              // Find the first non-active entry to mark as "Latest"
              const firstNonActiveIndex = history.findIndex(h => !h.isActive)
              const isLatest = !isActive && index === firstNonActiveIndex
              const isSelected = selectedVersionId !== null && selectedVersionId !== undefined && selectedVersionId === item.id
              
              return (
                <div
                  key={item.id}
                  onClick={() => handleManualSelect(item)}
                  className={`relative group cursor-pointer rounded-lg overflow-hidden border-2 transition-all ${
                    isSelected
                      ? 'border-green-500 shadow-xl ring-2 ring-green-300 ring-opacity-50'
                      : isActive
                        ? 'border-purple-500 shadow-lg'
                        : isLatest 
                          ? 'border-blue-500 shadow-lg' 
                          : 'border-gray-200 hover:border-blue-300 hover:shadow-md'
                  }`}
                >
                  {/* Thumbnail */}
                  <div className="aspect-video bg-gray-100 relative overflow-hidden">
                    <img
                      src={imageUrl}
                      alt={`Version ${history.length - index}`}
                      className="w-full h-full object-cover"
                      loading="lazy"
                    />
                    {/* Overlay on hover */}
                    <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-all flex items-center justify-center">
                      <div className="opacity-0 group-hover:opacity-100 transition-opacity bg-white/90 px-4 py-2 rounded-lg shadow-lg">
                        <span className="text-sm font-semibold text-gray-800">
                          {isActive ? 'Continue' : 'View'}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  {/* Info */}
                  <div className="p-3 bg-white">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs font-semibold text-gray-600">
                        {isActive ? 'Active' : (item.type === 'generate' ? 'Generated' : 'Edited')}
                      </span>
                      {isActive ? (
                        <span className="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded-full font-medium">
                          Active
                        </span>
                      ) : isLatest ? (
                        <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full font-medium">
                          Latest
                        </span>
                      ) : (
                        <span className="text-xs bg-gray-100 text-gray-700 px-2 py-0.5 rounded-full font-medium">
                          v{history.slice(0, index).filter(h => !h.isActive).length}
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-gray-500 truncate" title={item.prompt}>
                      {item.prompt || 'No description'}
                    </p>
                    <p className="text-xs text-gray-400 mt-1">
                      {new Date(item.timestamp).toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* Footer */}
      {history.length > 0 && (
        <div className="p-4 border-t border-gray-200 bg-gray-50 space-y-3">
          <p className="text-xs text-gray-500 text-center">
            {history.length} version{history.length !== 1 ? 's' : ''} in history
          </p>
          {versionsForAutoPlay.length > 0 && (
            <button
              onClick={handleAutoPlayToggle}
              className={`w-full px-4 py-2 rounded-lg font-semibold text-sm transition-all duration-200 ${
                isAutoPlaying
                  ? 'bg-red-500 hover:bg-red-600 text-white shadow-lg'
                  : 'bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white shadow-md hover:shadow-lg'
              }`}
            >
              {isAutoPlaying ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 00-1 1v4a1 1 0 001 1h4a1 1 0 001-1V8a1 1 0 00-1-1H8z" clipRule="evenodd" />
                  </svg>
                  Stop Auto Play
                </span>
              ) : (
                <span className="flex items-center justify-center gap-2">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
                  </svg>
                  Auto Play ({versionsForAutoPlay.length} versions)
                </span>
              )}
            </button>
          )}
        </div>
      )}
      </div>
    </>
  )
}

export default HistoryPanel

