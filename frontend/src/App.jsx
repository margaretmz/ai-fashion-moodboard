import { useState } from 'react'
import UnifiedMoodboard from './components/UnifiedMoodboard'
import Header from './components/Header'

function App() {
  const [currentImage, setCurrentImage] = useState(null)
  const [selectedModel, setSelectedModel] = useState('gemini-3-pro-image-preview')

  return (
    <div className="h-screen flex flex-col overflow-hidden">
      <Header 
        selectedModel={selectedModel} 
        onModelChange={setSelectedModel}
      />
      <UnifiedMoodboard 
        selectedModel={selectedModel}
        onImageChange={setCurrentImage}
        includeReasoning={true}
      />
    </div>
  )
}

export default App

