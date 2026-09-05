import { useState, useCallback } from 'react'
import './App.css'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api'

function App() {
  const [inputText, setInputText] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [results, setResults] = useState([])
  const [filterLabel, setFilterLabel] = useState('')
  const [loadingResults, setLoadingResults] = useState(false)
  const [totalResults, setTotalResults] = useState(0)

  const labels = ['positive', 'negative', 'neutral', 'unclassifiable']

  const fetchResults = useCallback(async () => {
    setLoadingResults(true)
    try {
      const params = new URLSearchParams()
      if (filterLabel) params.append('label', filterLabel)
      params.append('limit', '50')

      const response = await fetch(`${API_BASE}/results?${params}`)
      if (!response.ok) throw new Error('Failed to fetch results')

      const data = await response.json()
      setResults(data.results)
      setTotalResults(data.total)
    } catch (err) {
      console.error('Failed to fetch results:', err)
    } finally {
      setLoadingResults(false)
    }
  }, [filterLabel])

  const classifyText = async () => {
    if (!inputText.trim()) {
      setError('Please enter some text')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await fetch(`${API_BASE}/classify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: inputText })
      })

      if (!response.ok) {
        const err = await response.json()
        throw new Error(err.detail || 'Classification failed')
      }

      const data = await response.json()
      setResult(data)
      fetchResults()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const getLabelColor = (label) => {
    switch (label) {
      case 'positive': return 'bg-green-100 text-green-800'
      case 'negative': return 'bg-red-100 text-red-800'
      case 'neutral': return 'bg-yellow-100 text-yellow-800'
      case 'unclassifiable': return 'bg-gray-100 text-gray-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleString()
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Roman Urdu Text Classifier</h1>
          <p className="text-gray-600">Classify Roman Urdu text sentiment (positive / negative / neutral)</p>
        </div>

        {/* Input Section */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Classify Text</h2>
          
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Enter Roman Urdu Text
            </label>
            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              rows={4}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              placeholder="e.g., main khush hun, yeh bahut bura hai, theek thak hai"
              disabled={loading}
            />
          </div>

          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
              {error}
            </div>
          )}

          <button
            onClick={classifyText}
            disabled={loading || !inputText.trim()}
            className="w-full md:w-auto px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? 'Classifying...' : 'Classify'}
          </button>

          {/* Result Display */}
          {result && (
            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium text-gray-900">Result:</span>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${getLabelColor(result.label)}`}>
                  {result.label}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Confidence: {Math.round(result.confidence * 100)}%</span>
                <div className="w-32 bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full transition-all"
                    style={{ width: `${result.confidence * 100}%` }}
                  ></div>
                </div>
              </div>
              {result.raw_output && (
                <details className="mt-3">
                  <summary className="text-sm text-gray-500 cursor-pointer">Raw Model Output</summary>
                  <pre className="mt-2 p-2 bg-gray-100 rounded text-xs overflow-auto">{result.raw_output}</pre>
                </details>
              )}
            </div>
          )}
        </div>

        {/* Results Table Section */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6 gap-4">
            <h2 className="text-xl font-semibold text-gray-900">Classification History</h2>
            <div className="flex items-center gap-2">
              <label className="text-sm text-gray-700">Filter by:</label>
              <select
                value={filterLabel}
                onChange={(e) => {
                  setFilterLabel(e.target.value)
                  fetchResults()
                }}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">All Labels</option>
                {labels.map(label => (
                  <option key={label} value={label}>{label.charAt(0).toUpperCase() + label.slice(1)}</option>
                ))}
              </select>
            </div>
          </div>

          {loadingResults ? (
            <div className="text-center py-8 text-gray-500">Loading results...</div>
          ) : results.length === 0 ? (
            <div className="text-center py-8 text-gray-500">No classifications yet. Classify some text above!</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4 font-medium text-gray-500 uppercase text-sm">Text</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500 uppercase text-sm">Label</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500 uppercase text-sm">Confidence</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-500 uppercase text-sm">Date</th>
                  </tr>
                </thead>
                <tbody>
                  {results.map((item) => (
                    <tr key={item.id} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-3 px-4 text-gray-900 max-w-xs truncate" title={item.text}>
                        {item.text}
                      </td>
                      <td className="py-3 px-4">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getLabelColor(item.label)}`}>
                          {item.label}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-gray-600">
                        {Math.round(item.confidence * 100)}%
                      </td>
                      <td className="py-3 px-4 text-gray-500 text-sm">
                        {formatDate(item.created_at)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          <div className="mt-4 text-sm text-gray-500 text-center">
            Showing {results.length} of {totalResults} results
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
