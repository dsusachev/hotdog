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
    <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 flex z-50">
      {LINKS.map(({ to, label, icon }) => (
        <NavLink
          key={to}
          to={to}
          end={to === '/'}
          className={({ isActive }) =>
            `flex-1 flex flex-col items-center justify-center py-2 text-xs font-medium ${
              isActive ? 'text-teal-600' : 'text-gray-400'
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
