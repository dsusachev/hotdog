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

export default function Navbar() {
  const navigate = useNavigate()
  const { theme, toggle } = useTheme()

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
          {/* dark mode toggle */}
          <button
            onClick={toggle}
            className="w-9 h-9 flex items-center justify-center rounded-lg border border-gray-200 dark:border-gray-700 text-gray-500 dark:text-gray-400 hover:border-teal-400 hover:text-teal-600 dark:hover:text-teal-400 transition-colors"
            title={theme === 'dark' ? 'Светлая тема' : 'Тёмная тема'}
          >
            {theme === 'dark' ? '☀️' : '🌙'}
          </button>

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
        </div>
      </div>
    </header>
  )
}
