function Header({ selectedModel, onModelChange }) {
  return (
    <header className="bg-white border-b border-gray-200 z-10">
      <div className="container mx-auto px-6 py-3">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold text-gray-800">
            Fashion Moodboard Generator
          </h1>
          
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-3">
              <label className="text-sm font-medium text-gray-700">
                Model:
              </label>
              <select
                value={selectedModel}
                onChange={(e) => onModelChange(e.target.value)}
                className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
              >
                <option value="gemini-3-pro-image-preview">Gemini 3 Pro</option>
                <option value="gemini-2.5-flash-image">Gemini 2.5 Flash</option>
              </select>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header

