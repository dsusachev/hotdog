// NotFoundPage.tsx
// Страница 404 — добавь маршрут в App.tsx:
//   import NotFoundPage from './pages/NotFoundPage'
//   <Route path="*" element={<NotFoundPage />} />

import { useNavigate } from 'react-router-dom'
import { useEffect, useState } from 'react'

const SUGGESTIONS = [
  { to: '/',        label: 'Главная',  icon: '🏠' },
  { to: '/upload',  label: 'Загрузить фото', icon: '📸' },
  { to: '/search',  label: 'Поиск продукта', icon: '🔍' },
]

export default function NotFoundPage() {
  const navigate = useNavigate()
  const [dots, setDots] = useState('.')

  // анимация троеточия — маленький живой штрих
  useEffect(() => {
    const id = setInterval(() => {
      setDots(d => d.length >= 3 ? '.' : d + '.')
    }, 450)
    return () => clearInterval(id)
  }, [])

  return (
    <div className="flex flex-col items-center justify-center py-24 px-4 text-center">

      {/* big number */}
      <div className="relative mb-6 select-none">
        <span
          className="text-[9rem] font-bold leading-none"
          style={{
            fontFamily: '"DM Serif Display", serif',
            background: 'linear-gradient(135deg, #1A6B6B 0%, #a3d4d4 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}
        >
          404
        </span>
        {/* floating emoji */}
        <span
          className="absolute -top-3 -right-6 text-4xl"
          style={{ animation: 'float 3s ease-in-out infinite' }}
        >
          🥗
        </span>
      </div>

      <h1 className="text-2xl font-bold text-gray-800 mb-2">
        Страница не найдена{dots}
      </h1>
      <p className="text-gray-500 text-sm max-w-xs mb-10">
        Похоже, этот продукт исчез с полки. Попробуй одну из страниц ниже.
      </p>

      {/* suggestions */}
      <div className="flex flex-col gap-3 w-full max-w-xs mb-8">
        {SUGGESTIONS.map(({ to, label, icon }) => (
          <button
            key={to}
            onClick={() => navigate(to)}
            className="
              flex items-center gap-3 w-full px-4 py-3
              bg-white border border-gray-200 rounded-xl
              text-sm font-medium text-gray-700
              hover:border-teal-400 hover:text-teal-700 hover:bg-teal-50
              transition-colors text-left
            "
          >
            <span className="text-xl">{icon}</span>
            {label}
          </button>
        ))}
      </div>

      <button
        onClick={() => navigate(-1)}
        className="text-sm text-gray-400 hover:text-teal-600 transition-colors"
      >
        ← Вернуться назад
      </button>

      {/* float keyframes injected inline so no extra CSS file needed */}
      <style>{`
        @keyframes float {
          0%, 100% { transform: translateY(0px) rotate(-5deg); }
          50%       { transform: translateY(-10px) rotate(5deg); }
        }
      `}</style>
    </div>
  )
}
