import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

type Status = 'idle' | 'loading' | 'error'

export default function LoginPage() {
  const navigate = useNavigate()
  const [email, setEmail]       = useState('')
  const [password, setPassword] = useState('')
  const [status, setStatus]     = useState<Status>('idle')
  const [error, setError]       = useState('')

  const handleSubmit = async () => {
    if (!email || !password) return
    setStatus('loading')
    setError('')

    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      })

      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        setError(data.detail ?? 'Неверный email или пароль')
        setStatus('error')
        return
      }

      const data = await res.json()
      localStorage.setItem('token', data.access_token)
      navigate('/')
    } catch {
      setError('Ошибка соединения с сервером')
      setStatus('error')
    }
  }

  const isLoading = status === 'loading'

  return (
    <div className="max-w-sm mx-auto py-10 px-4">
      <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-8">
        <h1 className="text-2xl font-bold text-center mb-1 dark:text-gray-50">Вход</h1>
        <p className="text-center text-gray-500 dark:text-gray-400 text-sm mb-8">FoodScanner</p>

        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-600 dark:text-gray-400 mb-1.5">Email</label>
          <input
            type="email"
            placeholder="ivan@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            disabled={isLoading}
            className="w-full px-3 py-2.5 border border-gray-300 dark:border-gray-700 rounded-lg text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-600 focus:outline-none focus:border-teal-600 dark:focus:border-teal-500 transition-colors disabled:opacity-50"
          />
        </div>

        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-600 dark:text-gray-400 mb-1.5">Пароль</label>
          <input
            type="password"
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={isLoading}
            onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
            className="w-full px-3 py-2.5 border border-gray-300 dark:border-gray-700 rounded-lg text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-600 focus:outline-none focus:border-teal-600 dark:focus:border-teal-500 transition-colors disabled:opacity-50"
          />
        </div>

        {status === 'error' && (
          <p className="text-sm text-red-500 mb-4">{error}</p>
        )}

        <button
          onClick={handleSubmit}
          disabled={isLoading || !email || !password}
          className={`w-full py-3 rounded-lg font-medium mb-4 transition-colors flex items-center justify-center gap-2
            ${isLoading || !email || !password
              ? 'bg-teal-300 text-white cursor-not-allowed'
              : 'bg-teal-600 text-white hover:bg-teal-700 cursor-pointer'
            }`}
        >
          {isLoading ? (
            <>
              <span className="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Входим…
            </>
          ) : (
            'Войти'
          )}
        </button>

        <p className="text-center text-sm text-gray-500 dark:text-gray-400">
          Нет аккаунта?{' '}
          <button
            className="text-teal-600 dark:text-teal-400 font-medium hover:underline"
            onClick={() => navigate('/register')}
          >
            Зарегистрироваться
          </button>
        </p>
      </div>
    </div>
  )
}
