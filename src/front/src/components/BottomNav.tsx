import { NavLink } from 'react-router-dom'

const LINKS = [
  { to: '/',        label: 'Главная', icon: '🏠' },
  { to: '/upload',  label: 'Фото',    icon: '📸' },
  { to: '/search',  label: 'Поиск',   icon: '🔍' },
  { to: '/history', label: 'История', icon: '📋' },
  { to: '/login',   label: 'Профиль', icon: '👤' },
]

export default function BottomNav() {
  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800 flex z-50 transition-colors duration-200">
      {LINKS.map(({ to, label, icon }) => (
        <NavLink
          key={to}
          to={to}
          end={to === '/'}
          className={({ isActive }) =>
            `flex-1 flex flex-col items-center justify-center py-2 text-xs font-medium transition-colors ${
              isActive
                ? 'text-teal-600 dark:text-teal-400'
                : 'text-gray-400 dark:text-gray-500'
            }`
          }
        >
          <span className="text-xl mb-0.5">{icon}</span>
          {label}
        </NavLink>
      ))}
    </nav>
  )
}
