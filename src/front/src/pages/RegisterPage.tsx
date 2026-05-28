import { useNavigate } from 'react-router-dom'

export default function RegisterPage() {
  const navigate = useNavigate()

  return (
    <div className="max-w-sm mx-auto py-10 px-4">
      <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-8">
        <h1 className="text-2xl font-bold text-center mb-1 dark:text-gray-50">Регистрация</h1>
        <p className="text-center text-gray-500 dark:text-gray-400 text-sm mb-8">FoodScanner</p>

        {[
          { label: 'Имя',      type: 'text',     placeholder: 'Иван Иванов' },
          { label: 'Email',    type: 'email',    placeholder: 'ivan@example.com' },
          { label: 'Пароль',   type: 'password', placeholder: '••••••••' },
        ].map(({ label, type, placeholder }) => (
          <div className="mb-4" key={label}>
            <label className="block text-sm font-medium text-gray-600 dark:text-gray-400 mb-1.5">{label}</label>
            <input
              type={type}
              placeholder={placeholder}
              className="w-full px-3 py-2.5 border border-gray-300 dark:border-gray-700 rounded-lg text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-600 focus:outline-none focus:border-teal-600 dark:focus:border-teal-500 transition-colors"
            />
          </div>
        ))}

        <button className="w-full py-3 bg-teal-600 hover:bg-teal-700 text-white rounded-lg font-medium transition-colors mt-2 mb-4">
          Зарегистрироваться
        </button>

        <p className="text-center text-sm text-gray-500 dark:text-gray-400">
          Уже есть аккаунт?{' '}
          <button
            className="text-teal-600 dark:text-teal-400 font-medium hover:underline"
            onClick={() => navigate('/login')}
          >
            Войти
          </button>
        </p>
      </div>
    </div>
  )
}
