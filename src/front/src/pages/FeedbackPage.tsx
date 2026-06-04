import { useState } from 'react'
import { useToast } from '../components/Toast'
import { submitFeedback } from '../api/feedback'

type Status = 'idle' | 'loading' | 'success' | 'error'

export default function FeedbackPage() {
  const [rating, setRating]   = useState(0)
  const [hover, setHover]     = useState(0)
  const [message, setMessage] = useState('')
  const [status, setStatus]   = useState<Status>('idle')
  const { toast } = useToast()

  const handleSubmit = async () => {
    if (!rating) return
    setStatus('loading')
    try {
      await submitFeedback(rating, message || undefined)
      setStatus('success')
      toast.success('Спасибо! Ваш отзыв отправлен.')
    } catch {
      setStatus('error')
      toast.error('Что-то пошло не так. Попробуйте ещё раз.')
    }
  }

  const reset = () => {
    setRating(0)
    setMessage('')
    setStatus('idle')
  }

  if (status === 'success') {
    return (
      <div className="max-w-md mx-auto py-10 px-4">
        <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-8 text-center">
          <div className="text-5xl mb-4">✅</div>
          <h2 className="text-xl font-bold mb-2 dark:text-gray-50">Спасибо за отзыв!</h2>
          <p className="text-gray-500 dark:text-gray-400 text-sm mb-6">Ваше мнение помогает нам становиться лучше.</p>
          <button
            onClick={reset}
            className="px-6 py-2.5 border border-gray-300 dark:border-gray-700 dark:text-gray-300 rounded-lg font-medium text-gray-600 hover:border-teal-500 hover:text-teal-600 dark:hover:border-teal-500 dark:hover:text-teal-400 transition-colors"
          >
            Отправить ещё
          </button>
        </div>
      </div>
    )
  }

  const isLoading = status === 'loading'

  return (
    <div className="max-w-md mx-auto py-10 px-4">
      <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-8">
        <h1 className="text-2xl font-bold mb-1 dark:text-gray-50">Обратная связь</h1>
        <p className="text-gray-500 dark:text-gray-400 text-sm mb-8">Оцените наш сервис</p>

        <div className="flex gap-2 mb-6">
          {[1,2,3,4,5].map((i) => (
            <span
              key={i}
              className="text-3xl cursor-pointer select-none transition-transform hover:scale-110"
              style={{ color: (hover || rating) >= i ? '#D97706' : '#6B7280' }}
              onMouseEnter={() => setHover(i)}
              onMouseLeave={() => setHover(0)}
              onClick={() => !isLoading && setRating(i)}
            >
              ★
            </span>
          ))}
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-600 dark:text-gray-400 mb-1.5">Сообщение</label>
          <textarea
            placeholder="Ваш отзыв..."
            rows={4}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            disabled={isLoading}
            className="w-full px-3 py-2.5 border border-gray-300 dark:border-gray-700 rounded-lg text-sm resize-none bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-600 focus:outline-none focus:border-teal-600 dark:focus:border-teal-500 transition-colors disabled:opacity-50"
          />
        </div>

        {status === 'error' && (
          <p className="text-sm text-red-500 mb-4">Что-то пошло не так. Попробуйте ещё раз.</p>
        )}

        {!rating && (
          <p className="text-xs text-gray-400 dark:text-gray-500 mb-3">Поставьте оценку чтобы отправить отзыв</p>
        )}

        <div className="flex justify-end">
          <button
            onClick={handleSubmit}
            disabled={!rating || isLoading}
            className={`px-6 py-2.5 rounded-lg font-medium transition-colors flex items-center gap-2
              ${!rating || isLoading
                ? 'bg-teal-300 dark:bg-teal-800 text-white cursor-not-allowed'
                : 'bg-teal-600 text-white hover:bg-teal-700 cursor-pointer'
              }`}
          >
            {isLoading ? (
              <>
                <span className="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Отправляем…
              </>
            ) : (
              'Отправить'
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
