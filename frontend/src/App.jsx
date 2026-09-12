import { useState, useCallback, useEffect } from 'react'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api'

const SAMPLE_PROMPTS = [
  '"achha din hai"',
  '"yeh theek thak hai"',
  '"bhai yeh product bilkul bakwaas hai"',
]

const LABEL_COLORS = {
  positive: { bg: 'bg-primary-500/15', text: 'text-primary-500', bar: 'bg-primary-500', dot: 'bg-primary-500' },
  neutral: { bg: 'bg-amber-400/15', text: 'text-amber-500', bar: 'bg-amber-400', dot: 'bg-amber-400' },
  negative: { bg: 'bg-red-500/15', text: 'text-red-500', bar: 'bg-red-500', dot: 'bg-red-500' },
}

function useTheme() {
  const [dark, setDark] = useState(() => {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('theme')
      if (stored) return stored === 'dark'
      return window.matchMedia('(prefers-color-scheme: dark)').matches
    }
    return false
  })

  useEffect(() => {
    const root = document.documentElement
    if (dark) {
      root.classList.add('dark')
    } else {
      root.classList.remove('dark')
    }
    localStorage.setItem('theme', dark ? 'dark' : 'light')
  }, [dark])

  return [dark, setDark]
}

function LogoIcon() {
  return (
    <svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="14" cy="14" r="3" fill="var(--primary)" />
      <ellipse cx="14" cy="14" rx="12" ry="5" stroke="var(--primary)" strokeWidth="1.5" fill="none" />
      <ellipse cx="14" cy="14" rx="12" ry="5" stroke="var(--primary)" strokeWidth="1.5" fill="none" transform="rotate(60 14 14)" />
      <ellipse cx="14" cy="14" rx="12" ry="5" stroke="var(--primary)" strokeWidth="1.5" fill="none" transform="rotate(120 14 14)" />
    </svg>
  )
}

function Header({ dark, setDark }) {
  return (
    <header className="flex items-center justify-between px-6 py-4">
      <div className="flex items-center gap-2.5">
        <LogoIcon />
        <span className="font-display font-semibold text-lg tracking-tight">RomanUrdu.ai</span>
      </div>
      <button
        onClick={() => setDark(!dark)}
        className="p-2 rounded-lg transition-colors hover:bg-neutral-200/50 dark:hover:bg-neutral-800/50"
        aria-label="Toggle theme"
      >
        {dark ? (
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="5" />
            <line x1="12" y1="1" x2="12" y2="3" />
            <line x1="12" y1="21" x2="12" y2="23" />
            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
            <line x1="1" y1="12" x2="3" y2="12" />
            <line x1="21" y1="12" x2="23" y2="12" />
            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
            <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
          </svg>
        ) : (
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
          </svg>
        )}
      </button>
    </header>
  )
}

function Hero() {
  return (
    <div className="text-center py-10 px-4">
      <h1 className="font-display text-4xl md:text-5xl font-bold tracking-tight mb-3">
        Roman Urdu Text Classifier
      </h1>
      <p className="text-[var(--text-muted)] max-w-lg mx-auto">
        Classify Roman Urdu text sentiment in real-time.
      </p>
    </div>
  )
}

function InputSection({ inputText, setInputText, onSubmit, loading }) {
  const charCount = inputText.length

  const handleSampleClick = (prompt) => {
    const cleaned = prompt.replace(/^"|"$/g, '')
    setInputText(cleaned)
  }

  return (
    <div className="max-w-3xl mx-auto px-4 mb-10">
      <div className="flex items-center justify-between mb-2">
        <label className="font-display font-medium text-base">Classify Text</label>
        <span className="font-mono text-xs text-[var(--text-muted)]">{charCount} characters</span>
      </div>

      <div className="relative mb-4">
        <textarea
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          rows={5}
          className="w-full px-5 py-4 bg-[var(--bg-surface)] border border-[var(--border)] rounded-xl text-[var(--text)] placeholder-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-[var(--primary)]/50 focus:border-[var(--primary)] transition-all resize-none font-body text-sm leading-relaxed"
          placeholder="e.g., main khush hun, yeh bahut bura hai, theek thak hai"
        />
        {inputText.length > 0 && (
          <button
            onClick={() => setInputText('')}
            className="absolute bottom-3 right-3 flex items-center gap-1 px-3 py-1.5 text-xs font-mono text-[var(--text-muted)] hover:text-[var(--text)] bg-[var(--bg)] border border-[var(--border)] rounded-lg transition-colors"
          >
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
            Clear
          </button>
        )}
      </div>

      <div className="flex flex-wrap items-center gap-2 mb-5">
        <span className="font-mono text-xs text-[var(--text-muted)] uppercase tracking-wider">Sample Prompts:</span>
        {SAMPLE_PROMPTS.map((prompt) => (
          <button
            key={prompt}
            onClick={() => handleSampleClick(prompt)}
            className="px-3 py-1.5 text-xs font-mono text-[var(--text-muted)] bg-[var(--bg-surface)] border border-[var(--border)] rounded-lg hover:border-[var(--primary)] hover:text-[var(--primary)] transition-colors"
          >
            {prompt}
          </button>
        ))}
      </div>

      <button
        onClick={onSubmit}
        disabled={loading || !inputText.trim()}
        className="flex items-center gap-2 px-6 py-3 bg-[var(--primary)] text-white font-display font-medium text-sm rounded-xl hover:bg-[var(--primary-hover)] focus:outline-none focus:ring-2 focus:ring-[var(--primary)]/50 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all active:scale-[0.97]"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
        </svg>
        {loading ? 'Classifying...' : 'Classify Text'}
      </button>
    </div>
  )
}

function VerdictCard({ result }) {
  if (!result) return null

  const colors = LABEL_COLORS[result.label] || LABEL_COLORS.neutral
  const probs = result.probabilities
  const positivePct = (probs.positive * 100).toFixed(1)
  const neutralPct = (probs.neutral * 100).toFixed(1)
  const negativePct = (probs.negative * 100).toFixed(1)

  const sorted = [
    { label: 'positive', value: probs.positive, color: 'bg-primary-500', textColor: 'text-primary-500' },
    { label: 'neutral', value: probs.neutral, color: 'bg-amber-400', textColor: 'text-amber-500' },
    { label: 'negative', value: probs.negative, color: 'bg-red-500', textColor: 'text-red-500' },
  ].sort((a, b) => b.value - a.value)

  const dominant = sorted[0]

  return (
    <div className="max-w-3xl mx-auto px-4 mb-10 animate-fade-in-up">
      <div className="bg-[var(--bg-surface)] border border-[var(--border)] rounded-2xl p-6">
        <div className="flex items-center justify-between mb-4">
          <span className="font-mono text-xs text-[var(--text-muted)] uppercase tracking-wider">Verdict Assessment</span>
          <span className="font-mono text-xs text-[var(--text-muted)]">Model: gpt-oss-20b</span>
        </div>

        <div className="flex items-center gap-3 mb-5">
          <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-mono font-medium ${colors.bg} ${colors.text}`}>
            <span className={`w-1.5 h-1.5 rounded-full ${colors.dot}`} />
            {result.label.toUpperCase()}
          </span>
          <span className="font-display text-3xl font-bold tracking-tight">
            {(result.confidence * 100).toFixed(1)}%
          </span>
          <span className="text-[var(--text-muted)] text-sm">Confidence</span>
        </div>

        <div className="mb-3">
          <div className="flex items-center justify-between mb-1.5">
            <span className="font-mono text-xs text-[var(--text-muted)] uppercase tracking-wider">Sentiment Probability Distribution</span>
            <span className={`font-mono text-xs font-medium ${dominant.textColor}`}>{dominant.label.charAt(0).toUpperCase() + dominant.label.slice(1)}: {(dominant.value * 100).toFixed(1)}%</span>
          </div>
          <div className="w-full h-2.5 bg-neutral-200 dark:bg-neutral-800 rounded-full overflow-hidden flex">
            {sorted.map((item) => (
              item.value > 0 && (
                <div key={item.label} className={`h-full ${item.color} transition-all duration-500`} style={{ width: `${item.value * 100}%` }} />
              )
            ))}
          </div>
        </div>

        <div className="grid grid-cols-3 gap-3 mt-5">
          <div className="bg-[var(--bg)] border border-[var(--border)] rounded-xl p-3">
            <div className="text-xs text-[var(--text-muted)] mb-1">Positive</div>
            <div className="font-display text-lg font-bold text-primary-500">{positivePct}%</div>
          </div>
          <div className="bg-[var(--bg)] border border-[var(--border)] rounded-xl p-3">
            <div className="text-xs text-[var(--text-muted)] mb-1">Neutral</div>
            <div className="font-display text-lg font-bold text-amber-500">{neutralPct}%</div>
          </div>
          <div className="bg-[var(--bg)] border border-[var(--border)] rounded-xl p-3">
            <div className="text-xs text-[var(--text-muted)] mb-1">Negative</div>
            <div className="font-display text-lg font-bold text-red-500">{negativePct}%</div>
          </div>
        </div>
      </div>
    </div>
  )
}

function HistoryTable({ results, filterLabel, setFilterLabel, fetchResults }) {
  useEffect(() => {
    fetchResults()
  }, [fetchResults])

  const filteredResults = filterLabel
    ? results.filter((r) => r.label === filterLabel)
    : results

  return (
    <div className="max-w-3xl mx-auto px-4 mb-16">
      <div className="flex items-center justify-between mb-4">
        <h2 className="font-display text-xl font-semibold">Classification History</h2>
        <div className="flex items-center gap-2">
          <span className="font-mono text-xs text-[var(--text-muted)] uppercase tracking-wider">Filter By:</span>
          <select
            value={filterLabel}
            onChange={(e) => setFilterLabel(e.target.value)}
            className="px-3 py-1.5 text-xs font-mono bg-[var(--bg-surface)] border border-[var(--border)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--primary)]/50 text-[var(--text)] transition-colors cursor-pointer"
          >
            <option value="">All Labels</option>
            <option value="positive">Positive</option>
            <option value="neutral">Neutral</option>
            <option value="negative">Negative</option>
          </select>
        </div>
      </div>

      {filteredResults.length === 0 ? (
        <div className="py-16 text-center">
          <p className="text-[var(--text-muted)]">No classifications yet</p>
          <p className="text-[var(--text-muted)] text-sm mt-1">Classify some text above to see results here</p>
        </div>
      ) : (
        <div className="bg-[var(--bg-surface)] border border-[var(--border)] rounded-2xl overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b border-[var(--border)]">
                <th className="text-left px-5 py-3 font-mono text-xs text-[var(--text-muted)] uppercase tracking-wider">Text</th>
                <th className="text-left px-5 py-3 font-mono text-xs text-[var(--text-muted)] uppercase tracking-wider">Label</th>
                <th className="text-left px-5 py-3 font-mono text-xs text-[var(--text-muted)] uppercase tracking-wider">Confidence</th>
                <th className="text-left px-5 py-3 font-mono text-xs text-[var(--text-muted)] uppercase tracking-wider">Date</th>
              </tr>
            </thead>
            <tbody>
              {filteredResults.map((item) => {
                const lc = LABEL_COLORS[item.label] || LABEL_COLORS.neutral
                return (
                  <tr key={item.id} className="border-b border-[var(--border)] last:border-b-0 hover:bg-[var(--bg)]/50 transition-colors">
                    <td className="px-5 py-3.5 text-sm truncate max-w-[200px]" title={item.text}>{item.text}</td>
                    <td className="px-5 py-3.5">
                      <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-mono font-medium ${lc.bg} ${lc.text}`}>
                        <span className={`w-1.5 h-1.5 rounded-full ${lc.dot}`} />
                        {item.label.charAt(0).toUpperCase() + item.label.slice(1)}
                      </span>
                    </td>
                    <td className="px-5 py-3.5">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs text-[var(--text-muted)]">{(item.confidence * 100).toFixed(1)}%</span>
                        <div className="w-16 h-1.5 bg-neutral-200 dark:bg-neutral-800 rounded-full overflow-hidden">
                          <div className={`h-full rounded-full ${lc.bar}`} style={{ width: `${item.confidence * 100}%` }} />
                        </div>
                      </div>
                    </td>
                    <td className="px-5 py-3.5 font-mono text-xs text-[var(--text-muted)]">
                      {new Date(item.created_at).toLocaleString()}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

function Footer() {
  return (
    <footer className="max-w-3xl mx-auto px-4 py-6 border-t border-[var(--border)]">
      <p className="font-mono text-xs text-[var(--text-muted)]">
        Roman Urdu Text Classifier &copy; 2026
      </p>
    </footer>
  )
}

export default function App() {
  const [dark, setDark] = useTheme()
  const [inputText, setInputText] = useState('')
  const [result, setResult] = useState(null)
  const [results, setResults] = useState([])
  const [filterLabel, setFilterLabel] = useState('')
  const [loading, setLoading] = useState(false)

  const fetchResults = useCallback(async () => {
    try {
      const params = new URLSearchParams()
      if (filterLabel) params.append('label', filterLabel)
      params.append('limit', '50')

      const response = await fetch(`${API_BASE}/results?${params}`)
      if (!response.ok) throw new Error('Failed to fetch results')

      const data = await response.json()
      setResults(data.results)
    } catch (err) {
      console.error('Failed to fetch results:', err)
    }
  }, [filterLabel])

  const classifyText = async () => {
    if (!inputText.trim()) return

    setLoading(true)

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
      console.error('Classification error:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[var(--bg)] text-[var(--text)] transition-colors">
      <div className="max-w-5xl mx-auto">
        <Header dark={dark} setDark={setDark} />
        <Hero />
        <InputSection
          inputText={inputText}
          setInputText={setInputText}
          onSubmit={classifyText}
          loading={loading}
        />
        <VerdictCard result={result} />
        <HistoryTable
          results={results}
          filterLabel={filterLabel}
          setFilterLabel={setFilterLabel}
          fetchResults={fetchResults}
        />
        <Footer />
      </div>
    </div>
  )
}
