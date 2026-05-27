import { NavLink, useNavigate } from 'react-router-dom'

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

  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-5xl mx-auto px-4 h-14 flex items-center justify-between">
        <button
          onClick={() => navigate('/')}
          className="font-bold text-xl text-teal-600"
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
                    ? 'bg-teal-50 text-teal-600'
                    : 'text-gray-500 hover:text-teal-600 hover:bg-teal-50'
                }`
              }
            >
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="flex gap-2">
          <button
            onClick={() => navigate('/login')}
            className="px-3 py-1.5 text-sm border border-gray-300 rounded-lg hover:border-teal-600 transition-colors"
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
