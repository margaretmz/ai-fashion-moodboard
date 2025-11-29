import { useState, useRef, useEffect } from 'react'

function BoundingBoxSelector({ imageUrl, bbox, onBboxChange }) {
  const [isDrawing, setIsDrawing] = useState(false)
  const [startPos, setStartPos] = useState(null)
  const [hasMoved, setHasMoved] = useState(false) // Track if mouse moved during drag
  const canvasRef = useRef(null)
  const imageRef = useRef(null)
  const containerRef = useRef(null)

  useEffect(() => {
    const img = new Image()
    img.crossOrigin = 'anonymous'
    img.onload = () => {
      const canvas = canvasRef.current
      const container = containerRef.current
      if (canvas && container) {
        // Set canvas size to fit container while maintaining aspect ratio
        const containerWidth = container.clientWidth
        const containerHeight = container.clientHeight
        const imgAspectRatio = img.height / img.width
        const containerAspectRatio = containerHeight / containerWidth
        
        let canvasWidth, canvasHeight
        if (imgAspectRatio > containerAspectRatio) {
          // Image is taller - fit to height
          canvasHeight = containerHeight
          canvasWidth = canvasHeight / imgAspectRatio
        } else {
          // Image is wider - fit to width
          canvasWidth = containerWidth
          canvasHeight = canvasWidth * imgAspectRatio
        }
        
        canvas.width = canvasWidth
        canvas.height = canvasHeight
        
        const ctx = canvas.getContext('2d')
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height)
        drawBbox(ctx, canvas.width, canvas.height)
      }
    }
    img.onerror = () => {
      console.error('Failed to load image:', imageUrl)
    }
    img.src = imageUrl
    imageRef.current = img
  }, [imageUrl])

  useEffect(() => {
    const canvas = canvasRef.current
    if (canvas && imageRef.current) {
      const ctx = canvas.getContext('2d')
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      ctx.drawImage(imageRef.current, 0, 0, canvas.width, canvas.height)
      drawBbox(ctx, canvas.width, canvas.height)
    }
  }, [bbox])

  const drawBbox = (ctx, canvasWidth, canvasHeight) => {
    if (!ctx) return
    
    // Only draw bbox if it exists (user has selected a region)
    if (!bbox) return
    
    // Scale bbox coordinates to canvas size
    // Assuming original image dimensions are stored or we use relative coordinates
    const scaleX = canvasWidth / (imageRef.current?.naturalWidth || 1)
    const scaleY = canvasHeight / (imageRef.current?.naturalHeight || 1)
    
    const { x1, y1, x2, y2 } = bbox
    const scaledX1 = x1 * scaleX
    const scaledY1 = y1 * scaleY
    const scaledX2 = x2 * scaleX
    const scaledY2 = y2 * scaleY
    
    // Draw bounding box
    ctx.strokeStyle = '#3b82f6'
    ctx.lineWidth = 3
    ctx.setLineDash([5, 5])
    ctx.strokeRect(scaledX1, scaledY1, scaledX2 - scaledX1, scaledY2 - scaledY1)
    
    // Draw corner handles
    ctx.fillStyle = '#3b82f6'
    ctx.setLineDash([])
    const handleSize = 8
    ctx.fillRect(scaledX1 - handleSize/2, scaledY1 - handleSize/2, handleSize, handleSize)
    ctx.fillRect(scaledX2 - handleSize/2, scaledY2 - handleSize/2, handleSize, handleSize)
    ctx.fillRect(scaledX1 - handleSize/2, scaledY2 - handleSize/2, handleSize, handleSize)
    ctx.fillRect(scaledX2 - handleSize/2, scaledY1 - handleSize/2, handleSize, handleSize)
  }

  const getMousePos = (e) => {
    const canvas = canvasRef.current
    if (!canvas) return { x: 0, y: 0 }
    
    const rect = canvas.getBoundingClientRect()
    const scaleX = (imageRef.current?.naturalWidth || canvas.width) / canvas.width
    const scaleY = (imageRef.current?.naturalHeight || canvas.height) / canvas.height
    
    return {
      x: (e.clientX - rect.left) * scaleX,
      y: (e.clientY - rect.top) * scaleY
    }
  }

  const handleMouseDown = (e) => {
    const pos = getMousePos(e)
    setStartPos(pos)
    setIsDrawing(true)
    setHasMoved(false) // Reset movement tracking
  }

  const handleMouseMove = (e) => {
    if (!isDrawing || !startPos) return
    
    const pos = getMousePos(e)
    // Check if mouse has moved a meaningful distance (at least 5 pixels)
    const distance = Math.sqrt(
      Math.pow(pos.x - startPos.x, 2) + Math.pow(pos.y - startPos.y, 2)
    )
    
    if (distance > 5) {
      setHasMoved(true)
      onBboxChange({
        x1: Math.min(startPos.x, pos.x),
        y1: Math.min(startPos.y, pos.y),
        x2: Math.max(startPos.x, pos.x),
        y2: Math.max(startPos.y, pos.y)
      })
    }
  }

  const handleMouseUp = () => {
    // If user just clicked (didn't drag), clear the bbox
    if (isDrawing && startPos && !hasMoved) {
      onBboxChange(null)
    }
    
    setIsDrawing(false)
    setStartPos(null)
    setHasMoved(false)
  }

  return (
    <div ref={containerRef} className="relative w-full h-full flex items-center justify-center">
      <canvas
        ref={canvasRef}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        className="max-w-full max-h-full cursor-crosshair"
        style={{ objectFit: 'contain' }}
      />
    </div>
  )
}

export default BoundingBoxSelector
