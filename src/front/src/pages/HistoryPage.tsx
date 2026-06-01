import { useState, useEffect } from 'react'
import { SkeletonHistoryItem } from '../components/Skeleton'
import { authFetch } from '../utils/authFetch'

type HistoryEntry = {
  id: string
  label: string
  query: string
  entry_type: string
  confidence?: number
  created_at: string
}

export default function HistoryPage() {
  const [isLoading, setIsLoading] = useState(true)
  const [history, setHistory]     = useState<HistoryEntry[]>([])
  const [deleting, setDeleting]   = useState<string | null>(null)

  useEffect(() => {
    authFetch('/api/history')
      .then(r => r.json())
      .then(data => { setHistory(data); setIsLoading(false) })
      .catch(() => setIsLoading(false))
  }, [])

  const handleDelete = async (id: string) => {
    setDeleting(id)
    try {
      await authFetch(`/api/history/${id}`, { method: 'DELETE' })
      setHistory(prev => prev.filter(e => e.id !== id))
    } finally {
      setDeleting(null)
    }
  }

  const entryIcon = (type: string) => type === 'search' ? '🔍' : '🍽️'

  return (
    <div className="max-w-2xl mx-auto py-10 px-4">
      <h1 className="text-2xl font-bold mb-8 dark:text-gray-50">История запросов</h1>

      {isLoading ? (
        <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl px-4 py-2">
          {Array.from({ length: 6 }).map((_, i) => (
            <SkeletonHistoryItem key={i} />
          ))}
        </div>
      ) : history.length === 0 ? (
        <div className="text-center text-gray-400 dark:text-gray-500 py-16">
          <div className="text-4xl mb-3">📋</div>
          <p>История запросов пуста</p>
        </div>
      ) : (
        <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl px-4 py-2">
          {history.map(entry => (
            <div key={entry.id} className="flex items-center gap-3 py-3 border-b border-gray-100 dark:border-gray-800 last:border-0">
              <div className="w-12 h-12 rounded-lg bg-teal-50 dark:bg-teal-900/40 flex items-center justify-center text-xl flex-shrink-0">
                {entryIcon(entry.entry_type)}
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-gray-800 dark:text-gray-100 text-sm truncate">{entry.label}</p>
                <p className="text-xs text-gray-400 dark:text-gray-500 truncate">{entry.query}</p>
                {entry.confidence != null && (
                  <p className="text-xs text-teal-500 dark:text-teal-400">{Math.round(entry.confidence * 100)}% уверенность</p>
                )}
              </div>
              <span className="text-xs text-gray-400 dark:text-gray-500 whitespace-nowrap mr-2">
                {new Date(entry.created_at).toLocaleDateString('ru-RU')}
              </span>
              <button
                onClick={() => handleDelete(entry.id)}
                disabled={deleting === entry.id}
                className="w-7 h-7 flex items-center justify-center rounded-full text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors flex-shrink-0 disabled:opacity-40"
                title="Удалить"
              >
                {deleting === entry.id ? (
                  <span className="inline-block w-3 h-3 border border-gray-400 border-t-transparent rounded-full animate-spin" />
                ) : '✕'}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
