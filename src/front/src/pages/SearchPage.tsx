import { useState } from 'react'
import { SkeletonSearchResult } from '../components/Skeleton'
import { useToast } from '../components/Toast'

type SearchResult = {
  id: string
  name: string
  description: string
  calories: number
}

type Status = 'idle' | 'loading' | 'done' | 'error'

export default function SearchPage() {
  const [query, setQuery]       = useState('')
  const [status, setStatus]     = useState<Status>('idle')
  const [results, setResults]   = useState<SearchResult[]>([])
  const { toast } = useToast()

  const handleSearch = async () => {
    if (!query.trim()) return
    setStatus('loading')
    setResults([])

    try {
      const res = await fetch(`/api/products/search?query=${encodeURIComponent(query.trim())}`)
      if (!res.ok) throw new Error(`Ошибка сервера: ${res.status}`)
      const data = await res.json()
      setResults(data)
      setStatus('done')
      if (data.length === 0) toast.info('Ничего не найдено — попробуйте другой запрос')
    } catch {
      setStatus('error')
      toast.error('Не удалось выполнить поиск. Попробуйте ещё раз.')
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') handleSearch()
  }

  return (
    <div className="max-w-2xl mx-auto py-10 px-4">
      <h1 className="text-2xl font-bold mb-2 dark:text-gray-50">Поиск продукта</h1>
      <p className="text-gray-500 dark:text-gray-400 mb-8">Введите название продукта для получения информации о составе.</p>

      <div className="relative mb-4">
        <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">🔍</span>
        <input
          type="text"
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Например: яблоко, гречка, творог..."
          className="w-full pl-11 pr-4 py-3 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-base text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-600 focus:outline-none focus:border-teal-600 dark:focus:border-teal-500 transition-colors"
        />
      </div>

      <button
        onClick={handleSearch}
        disabled={!query.trim() || status === 'loading'}
        className={`w-full py-3 rounded-lg font-medium transition-colors mb-8
          ${!query.trim() || status === 'loading'
            ? 'bg-teal-300 dark:bg-teal-800 text-white cursor-not-allowed'
            : 'bg-teal-600 text-white hover:bg-teal-700 cursor-pointer'
          }`}
      >
        {status === 'loading' ? (
          <span className="flex items-center justify-center gap-2">
            <span className="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
            Ищем…
          </span>
        ) : 'Найти'}
      </button>

      {status === 'loading' && (
        <div className="space-y-3">
          {Array.from({ length: 4 }).map((_, i) => <SkeletonSearchResult key={i} />)}
        </div>
      )}

      {status === 'done' && results.length > 0 && (
        <div className="space-y-3">
          {results.map(r => (
            <div key={r.id} className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-4 flex items-center gap-4">
              <div className="w-10 h-10 rounded-lg bg-teal-50 dark:bg-teal-900/40 flex items-center justify-center text-xl flex-shrink-0">
                🥦
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-gray-800 dark:text-gray-100 text-sm truncate">{r.name}</p>
                <p className="text-xs text-gray-400 dark:text-gray-500 truncate">{r.description}</p>
              </div>
              <span className="text-xs font-medium text-teal-600 dark:text-teal-400 whitespace-nowrap bg-teal-50 dark:bg-teal-900/40 px-2 py-1 rounded-full flex-shrink-0">
                {r.calories} ккал
              </span>
            </div>
          ))}
        </div>
      )}

      {status === 'idle' && (
        <div className="text-center text-gray-400 dark:text-gray-500">
          <div className="text-4xl mb-3">🥦</div>
          <p>Результаты поиска появятся здесь</p>
        </div>
      )}

      {status === 'done' && results.length === 0 && (
        <div className="text-center text-gray-400 dark:text-gray-500">
          <div className="text-4xl mb-3">🔍</div>
          <p>По запросу «{query}» ничего не найдено</p>
        </div>
      )}
    </div>
  )
}
