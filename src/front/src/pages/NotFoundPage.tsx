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

  useEffect(() => {
    const id = setInterval(() => {
      setDots(d => d.length >= 3 ? '.' : d + '.')
    }, 450)
    return () => clearInterval(id)
  }, [])

  return (
    <div className="flex flex-col items-center justify-center py-24 px-4 text-center">
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
        <span
          className="absolute -top-3 -right-6 text-4xl"
          style={{ animation: 'float 3s ease-in-out infinite' }}
        >
          🥗
        </span>
      </div>

      <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-100 mb-2">
        Страница не найдена{dots}
      </h1>
      <p className="text-gray-500 dark:text-gray-400 text-sm max-w-xs mb-10">
        Похоже, этот продукт исчез с полки. Попробуй одну из страниц ниже.
      </p>

      <div className="flex flex-col gap-3 w-full max-w-xs mb-8">
        {SUGGESTIONS.map(({ to, label, icon }) => (
          <button
            key={to}
            onClick={() => navigate(to)}
            className="
              flex items-center gap-3 w-full px-4 py-3
              bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl
              text-sm font-medium text-gray-700 dark:text-gray-300
              hover:border-teal-400 hover:text-teal-700 dark:hover:text-teal-400 hover:bg-teal-50 dark:hover:bg-teal-900/30
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
        className="text-sm text-gray-400 dark:text-gray-500 hover:text-teal-600 dark:hover:text-teal-400 transition-colors"
      >
        ← Вернуться назад
      </button>

      <style>{`
        @keyframes float {
          0%, 100% { transform: translateY(0px) rotate(-5deg); }
          50%       { transform: translateY(-10px) rotate(5deg); }
        }
      `}</style>
    </div>
  )
}
