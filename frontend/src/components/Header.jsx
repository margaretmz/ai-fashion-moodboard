function Header({
  selectedModel,
  onModelChange,
  apiKey,
  onApiKeyChange
}) {
  return (
    <header className="bg-white border-b border-gray-200 z-10">
      <div className="container mx-auto px-6 py-3">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold text-gray-800">
            Fashion Moodboard Generator
          </h1>
          
          <div className="flex flex-wrap items-center gap-4">
            <label className="flex items-center gap-2 text-sm text-gray-700">
              <span>API Key:</span>
              <input
                value={apiKey}
                onChange={(e) => onApiKeyChange(e.target.value)}
                placeholder="Optional (only if env not set)"
                type="password"
                className="w-56 px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
              />
            </label>
            <label className="flex items-center gap-2 text-sm text-gray-700">
              <span>Model:</span>
              <select
                value={selectedModel}
                onChange={(e) => onModelChange(e.target.value)}
                className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
              >
                <option value="gemini-3-pro-image-preview">Gemini 3 Pro</option>
                <option value="gemini-2.5-flash-image">Gemini 2.5 Flash</option>
              </select>
            </label>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header
