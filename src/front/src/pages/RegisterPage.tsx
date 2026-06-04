import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { register } from '../api/auth'

type Status = 'idle' | 'loading' | 'error'

export default function RegisterPage() {
  const navigate = useNavigate()
  const [name, setName]         = useState('')
  const [email, setEmail]       = useState('')
  const [password, setPassword] = useState('')
  const [status, setStatus]     = useState<Status>('idle')
  const [error, setError]       = useState('')

  const handleSubmit = async () => {
    if (!name || !email || !password) return
    setStatus('loading')
    setError('')

    try {
      await register(email, password, name)
      navigate('/login')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка соединения с сервером')
      setStatus('error')
    }
  }

  const isLoading = status === 'loading'

  const fields = [
    { label: 'Имя',    type: 'text',     placeholder: 'Иван Иванов',     value: name,     onChange: setName },
    { label: 'Email',  type: 'email',    placeholder: 'ivan@example.com', value: email,    onChange: setEmail },
    { label: 'Пароль', type: 'password', placeholder: '••••••••',         value: password, onChange: setPassword },
  ]

  return (
    <div className="max-w-sm mx-auto py-10 px-4">
      <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-8">
        <h1 className="text-2xl font-bold text-center mb-1 dark:text-gray-50">Регистрация</h1>
        <p className="text-center text-gray-500 dark:text-gray-400 text-sm mb-8">FoodScanner</p>

        {fields.map(({ label, type, placeholder, value, onChange }) => (
          <div className="mb-4" key={label}>
            <label className="block text-sm font-medium text-gray-600 dark:text-gray-400 mb-1.5">{label}</label>
            <input
              type={type}
              placeholder={placeholder}
              value={value}
              onChange={(e) => onChange(e.target.value)}
              disabled={isLoading}
              className="w-full px-3 py-2.5 border border-gray-300 dark:border-gray-700 rounded-lg text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-600 focus:outline-none focus:border-teal-600 dark:focus:border-teal-500 transition-colors disabled:opacity-50"
            />
          </div>
        ))}

        {status === 'error' && (
          <p className="text-sm text-red-500 mb-4">{error}</p>
        )}

        <button
          onClick={handleSubmit}
          disabled={isLoading || !name || !email || !password}
          className={`w-full py-3 rounded-lg font-medium mt-2 mb-4 transition-colors flex items-center justify-center gap-2
            ${isLoading || !name || !email || !password
              ? 'bg-teal-300 text-white cursor-not-allowed'
              : 'bg-teal-600 text-white hover:bg-teal-700 cursor-pointer'
            }`}
        >
          {isLoading ? (
            <>
              <span className="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Регистрируем…
            </>
          ) : (
            'Зарегистрироваться'
          )}
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
