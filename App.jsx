import { useState } from 'react'

const API_URL = import.meta.env.VITE_API_URL || ''

function App() {
  const [youtubeUrl, setYoutubeUrl] = useState('')
  const [query, setQuery] = useState('')
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSearch = async (e) => {
    e.preventDefault()
    
    if (!youtubeUrl || !query) {
      setError('Please enter both a YouTube URL and a search query')
      return
    }

    setLoading(true)
    setError(null)
    setResults(null)

    try {
      const response = await fetch(`${API_URL}/api/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          youtube_url: youtubeUrl,
          query: query,
          max_results: 5,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail?.error || 'Search failed')
      }

      setResults(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const extractVideoId = (url) => {
    const match = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})/)
    return match ? match[1] : null
  }

  const videoId = extractVideoId(youtubeUrl)

  return (
    <div className="min-h-screen bg-[#0f0f1a] text-white">
      {/* Header */}
      <header className="border-b border-gray-800">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <h1 className="text-2xl font-bold">
            <span className="text-red-500">Clip</span>Context
          </h1>
          <p className="text-gray-400 mt-1">Find any moment in any YouTube video</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 py-8">
        {/* Search Form */}
        <form onSubmit={handleSearch} className="space-y-4">
          <div>
            <label htmlFor="youtube-url" className="block text-sm font-medium text-gray-300 mb-2">
              YouTube URL
            </label>
            <input
              id="youtube-url"
              type="text"
              placeholder="https://www.youtube.com/watch?v=..."
              value={youtubeUrl}
              onChange={(e) => setYoutubeUrl(e.target.value)}
              className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-red-500 transition-colors"
            />
          </div>

          <div>
            <label htmlFor="query" className="block text-sm font-medium text-gray-300 mb-2">
              What are you looking for?
            </label>
            <input
              id="query"
              type="text"
              placeholder="e.g., stay hungry stay foolish"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:border-red-500 transition-colors"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-red-600 hover:bg-red-700 disabled:bg-gray-700 disabled:cursor-not-allowed rounded-lg font-medium transition-colors"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Searching... (first search takes ~15s)
              </span>
            ) : (
              'Search'
            )}
          </button>
        </form>

        {/* Error Message */}
        {error && (
          <div className="mt-6 p-4 bg-red-900/30 border border-red-800 rounded-lg text-red-300">
            {error}
          </div>
        )}

        {/* Results */}
        {results && (
          <div className="mt-8">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-medium">
                Results for "{results.query}"
              </h2>
              <span className="text-sm text-gray-500">
                {results.search_time_ms.toFixed(0)}ms {results.cached && '(cached)'}
              </span>
            </div>

            {/* Video Preview */}
            {videoId && (
              <div className="mb-6 aspect-video rounded-lg overflow-hidden bg-gray-900">
                <iframe
                  width="100%"
                  height="100%"
                  src={`https://www.youtube.com/embed/${videoId}`}
                  title="YouTube video player"
                  frameBorder="0"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                />
              </div>
            )}

            {/* Results List */}
            {results.results.length === 0 ? (
              <p className="text-gray-400">No results found. Try a different search term.</p>
            ) : (
              <div className="space-y-3">
                {results.results.map((result, index) => (
                  <a
                    key={index}
                    href={result.youtube_link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block p-4 bg-gray-900 border border-gray-800 rounded-lg hover:border-gray-700 hover:bg-gray-800/50 transition-colors group"
                  >
                    <div className="flex items-start gap-4">
                      <div className="flex-shrink-0 px-3 py-1 bg-red-600 rounded text-sm font-mono">
                        {result.timestamp_formatted}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-gray-300 line-clamp-2">
                          {result.text}
                        </p>
                        <div className="mt-2 flex items-center gap-4 text-sm text-gray-500">
                          <span>Score: {(result.score * 100).toFixed(0)}%</span>
                          <span className="group-hover:text-red-400 transition-colors">
                            Click to watch →
                          </span>
                        </div>
                      </div>
                    </div>
                  </a>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Example */}
        {!results && !loading && (
          <div className="mt-12 p-6 bg-gray-900/50 border border-gray-800 rounded-lg">
            <h3 className="text-sm font-medium text-gray-400 mb-3">Try an example</h3>
            <button
              onClick={() => {
                setYoutubeUrl('https://www.youtube.com/watch?v=UF8uR6Z6KLc')
                setQuery('stay hungry stay foolish')
              }}
              className="text-left hover:bg-gray-800 p-3 rounded-lg transition-colors w-full"
            >
              <p className="text-white font-medium">Steve Jobs Stanford Speech</p>
              <p className="text-gray-400 text-sm mt-1">Search: "stay hungry stay foolish"</p>
            </button>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-800 mt-12">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <p className="text-gray-500 text-sm text-center">
            Built in public by{' '}
            <a href="https://x.com/ermiaboruoffcl" className="text-red-400 hover:underline">
              @ermiaboruoffcl
            </a>
            {' '}•{' '}
            <a href="https://github.com/ermiaswalelgne/clipcontext" className="text-red-400 hover:underline">
              GitHub
            </a>
            {' '}• #buildinpublic
          </p>
        </div>
      </footer>
    </div>
  )
}

export default App
