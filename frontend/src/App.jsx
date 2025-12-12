import { useState } from 'react'
import UnifiedMoodboard from './components/UnifiedMoodboard'
import Header from './components/Header'

function App() {
  const [currentImage, setCurrentImage] = useState(null)
  const [selectedModel, setSelectedModel] = useState('gemini-3-pro-image-preview')
  const [apiKey, setApiKey] = useState('')

  return (
    <div className="h-screen flex flex-col overflow-hidden">
      <Header 
        selectedModel={selectedModel} 
        onModelChange={setSelectedModel}
        apiKey={apiKey}
        onApiKeyChange={setApiKey}
      />
      <UnifiedMoodboard 
        selectedModel={selectedModel}
        onImageChange={setCurrentImage}
        apiKey={apiKey}
      />
    </div>
  )
}

export default App
