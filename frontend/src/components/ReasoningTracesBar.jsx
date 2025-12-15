import { useState } from 'react'

// Helper function to extract sections with titles and content from markdown reasoning text
function extractReasoningSections(reasoningText) {
  if (!reasoningText || !reasoningText.trim()) {
    return []
  }
  
  const sections = []
  
  // Split by **Title** pattern and extract sections
  // Pattern: **Title**\n\ncontent (until next **Title** or end)
  const pattern = /\*\*(.+?)\*\*\s*\n\n(.+?)(?=\n\n\*\*|$)/gs
  let match
  
  while ((match = pattern.exec(reasoningText)) !== null) {
    const title = match[1].trim()
    const content = match[2].trim()
    if (title) {
      sections.push({ title, content: content || '' })
    }
  }
  
  // If no matches found with content, try simpler pattern: extract titles only
  if (sections.length === 0) {
    const titlePattern = /\*\*(.+?)\*\*/g
    while ((match = titlePattern.exec(reasoningText)) !== null) {
      const title = match[1].trim()
      if (title) {
        sections.push({ title, content: '' })
      }
    }
  }
  
  return sections
}

function ReasoningTracesBar({ reasoningTrace }) {
  const [hoveredIndex, setHoveredIndex] = useState(null)
  const sections = extractReasoningSections(reasoningTrace)

  if (sections.length === 0) {
    return null
  }
  
  return (
    <div className="bg-gradient-to-r from-blue-50 via-purple-50 to-blue-50 border-b border-gray-200 shadow-sm relative">
      <div className="w-full py-2.5">
        <div className="max-w-4xl mx-auto px-4">
            <div className="flex items-center justify-center gap-0 flex-wrap">
              {sections.map((section, index) => (
              <div 
                key={index} 
                className="flex items-center relative"
                onMouseEnter={() => setHoveredIndex(index)}
                onMouseLeave={() => setHoveredIndex(null)}
              >
                <div className="flex-shrink-0 relative">
                  <span className="text-sm font-bold text-gray-700 px-4 py-1.5 bg-white/90 rounded-full border border-gray-200/60 inline-block shadow-sm whitespace-nowrap backdrop-blur-sm cursor-pointer hover:bg-white hover:shadow-md transition-all">
                    {section.title}
                  </span>
                  
                  {/* Tooltip Popup */}
                  {hoveredIndex === index && section.content && (
                    <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-3 z-[100] w-80 max-w-md pointer-events-none">
                      <div className="bg-white rounded-lg shadow-2xl border border-gray-200 p-4 relative">
                        {/* Upside-down triangle pointer pointing down - seamlessly connected to box */}
                        <div className="absolute top-full left-1/2 transform -translate-x-1/2">
                          {/* Border triangle (outer) - positioned to overlap box border */}
                          <div className="w-0 h-0 border-l-[14px] border-r-[14px] border-t-[14px] border-l-transparent border-r-transparent border-t-gray-200 -mt-[1px]"></div>
                          {/* Fill triangle (inner) - covers top border edge for seamless connection */}
                          <div className="w-0 h-0 border-l-[12px] border-r-[12px] border-t-[12px] border-l-transparent border-r-transparent border-t-white absolute top-[1px] left-1/2 transform -translate-x-1/2"></div>
                        </div>
                        <h4 className="font-bold text-gray-800 mb-2 text-base">{section.title}</h4>
                        <p className="text-sm text-gray-600 whitespace-pre-wrap leading-relaxed max-h-64 overflow-y-auto">
                          {section.content}
                        </p>
                      </div>
                    </div>
                  )}
                </div>
                {index < sections.length - 1 && (
                  <div className="flex items-center">
                    <div className="w-1.5 h-1.5 rounded-full bg-gray-400/60"></div>
                    <div className="w-8 h-0.5 bg-gray-400/60 rounded-full"></div>
                    <div className="w-1.5 h-1.5 rounded-full bg-gray-400/60"></div>
                  </div>
                )}
              </div>
            ))}
            </div>
        </div>
      </div>
    </div>
  )
}

export default ReasoningTracesBar
