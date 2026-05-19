import { useState } from 'react'

export default function FeedbackPage() {
  const [rating, setRating] = useState(0)
  const [hover, setHover]   = useState(0)

  return (
    <div className="max-w-md mx-auto py-10 px-4">
      <div className="bg-white border border-gray-200 rounded-2xl p-8">
        <h1 className="text-2xl font-bold mb-1">Обратная связь</h1>
        <p className="text-gray-500 text-sm mb-8">Оцените наш сервис</p>

        {/* Stars */}
        <div className="flex gap-2 mb-6">
          {[1,2,3,4,5].map((i) => (
            <span
              key={i}
              className="text-3xl cursor-pointer select-none transition-transform hover:scale-110"
              style={{ color: (hover || rating) >= i ? '#D97706' : '#D1D5DB' }}
              onMouseEnter={() => setHover(i)}
              onMouseLeave={() => setHover(0)}
              onClick={() => setRating(i)}
            >
              ★
            </span>
          ))}
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-600 mb-1.5">Сообщение</label>
          <textarea
            placeholder="Ваш отзыв..."
            rows={4}
            className="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm resize-none focus:outline-none focus:border-teal-600 transition-colors"
          />
        </div>

        <div className="flex justify-end">
          <button className="px-6 py-2.5 bg-teal-600 text-white rounded-lg font-medium cursor-default">
            Отправить
          </button>
        </div>
      </div>
    </div>
  )
}
