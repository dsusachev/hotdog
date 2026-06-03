import { NavLink, useNavigate } from 'react-router-dom'
import { useTheme } from './ThemeContext'

const LINKS = [
  { to: '/',         label: 'Главная' },
  { to: '/upload',   label: 'Загрузка' },
  { to: '/search',   label: 'Поиск' },
  { to: '/recipes',  label: 'Рецепты' },
  { to: '/history',  label: 'История' },
  { to: '/feedback', label: 'Отзывы' },
]

const THEME_OPTIONS: { value: 'light' | 'dark' | 'system'; icon: string; label: string }[] = [
  { value: 'light',  icon: '☀️', label: 'Светлая' },
  { value: 'system', icon: '💻', label: 'Авто'    },
  { value: 'dark',   icon: '🌙', label: 'Тёмная'  },
]

function getEmailFromToken(): string | null {
  try {
    const token = localStorage.getItem('token')
    if (!token) return null
    const payload = JSON.parse(atob(token.split('.')[1]))
    return payload.sub ?? payload.email ?? null
  } catch {
    return null
  }
}

export default function Navbar() {
  const navigate = useNavigate()
  const { theme, setTheme } = useTheme()
  const email = getEmailFromToken()

  return (
    <header className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 sticky top-0 z-50 transition-colors duration-200">
      <div className="max-w-5xl mx-auto px-4 h-14 flex items-center justify-between">
        <button
          onClick={() => navigate('/')}
          className="font-bold text-xl text-teal-600 dark:text-teal-400"
        >
          FoodScanner
        </button>

        <nav className="hidden md:flex gap-1">
          {LINKS.map(({ to, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-teal-50 dark:bg-teal-900/40 text-teal-600 dark:text-teal-400'
                    : 'text-gray-500 dark:text-gray-400 hover:text-teal-600 dark:hover:text-teal-400 hover:bg-teal-50 dark:hover:bg-teal-900/40'
                }`
              }
            >
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="flex gap-2 items-center">
          <div className="flex items-center gap-0.5 bg-gray-100 dark:bg-gray-800 rounded-lg p-0.5">
            {THEME_OPTIONS.map(({ value, icon, label }) => (
              <button
                key={value}
                onClick={() => setTheme(value)}
                title={label}
                className={`w-8 h-8 flex items-center justify-center rounded-md text-base transition-all ${
                  theme === value
                    ? 'bg-white dark:bg-gray-700 shadow-sm text-gray-800 dark:text-gray-100'
                    : 'text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300'
                }`}
              >
                {icon}
              </button>
            ))}
          </div>

          {email ? (
            <>
              <span className="text-sm text-gray-600 dark:text-gray-300">{email}</span>
              <button
                onClick={() => { localStorage.removeItem('token'); navigate('/login') }}
                className="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-700 dark:text-gray-300 rounded-lg hover:border-red-400 hover:text-red-400 transition-colors"
              >
                Выйти
              </button>
            </>
          ) : (
            <>
              <button
                onClick={() => navigate('/login')}
                className="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-700 dark:text-gray-300 rounded-lg hover:border-teal-600 transition-colors"
              >
                Войти
              </button>
              <button
                onClick={() => navigate('/register')}
                className="px-3 py-1.5 text-sm bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors"
              >
                Регистрация
              </button>
            </>
          )}
        </div>
      </div>
    </header>
  )
}
