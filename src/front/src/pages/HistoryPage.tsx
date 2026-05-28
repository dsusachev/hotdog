import { useState, useEffect } from 'react'
import { SkeletonHistoryItem } from '../components/Skeleton'

type HistoryEntry = {
  id: string
  label: string
  query: string
  confidence?: number
  created_at: string
}

export default function HistoryPage() {
  const [isLoading, setIsLoading] = useState(true)
  const [history, setHistory]     = useState<HistoryEntry[]>([])

  useEffect(() => {
    // TODO: заменить на реальный GET /history когда будет готов бэкенд
    const timer = setTimeout(() => {
      setHistory([])   // пока пусто — сервер ещё не подключён
      setIsLoading(false)
    }, 900)
    return () => clearTimeout(timer)
  }, [])

  return (
    <div className="max-w-2xl mx-auto py-10 px-4">
      <h1 className="text-2xl font-bold mb-8">История запросов</h1>

      {isLoading ? (
        <div className="bg-white border border-gray-200 rounded-2xl px-4 py-2">
          {Array.from({ length: 6 }).map((_, i) => (
            <SkeletonHistoryItem key={i} />
          ))}
        </div>
      ) : history.length === 0 ? (
        <div className="text-center text-gray-400 py-16">
          <div className="text-4xl mb-3">📋</div>
          <p>История запросов пуста</p>
        </div>
      ) : (
        <div className="bg-white border border-gray-200 rounded-2xl px-4 py-2">
          {history.map(entry => (
            <div key={entry.id} className="flex items-center gap-3 py-3 border-b border-gray-100 last:border-0">
              <div className="w-12 h-12 rounded-lg bg-teal-50 flex items-center justify-center text-xl flex-shrink-0">
                🍽️
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-gray-800 text-sm truncate">{entry.label}</p>
                <p className="text-xs text-gray-400 truncate">{entry.query}</p>
              </div>
              <span className="text-xs text-gray-400 whitespace-nowrap">
                {new Date(entry.created_at).toLocaleDateString('ru-RU')}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
