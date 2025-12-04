import { useState } from 'react'
import UnifiedMoodboard from './components/UnifiedMoodboard'
import Header from './components/Header'

function App() {
  const [currentImage, setCurrentImage] = useState(null)
  const [selectedModel, setSelectedModel] = useState('gemini-3-pro-image-preview')
  const [includeReasoning, setIncludeReasoning] = useState(false)

  return (
    <div className="h-screen flex flex-col overflow-hidden">
      <Header 
        selectedModel={selectedModel} 
        onModelChange={setSelectedModel} 
        includeReasoning={includeReasoning}
        onIncludeReasoningChange={setIncludeReasoning}
      />
      <UnifiedMoodboard 
        selectedModel={selectedModel}
        onImageChange={setCurrentImage}
        includeReasoning={includeReasoning}
      />
    </div>
  )
}

export default App

