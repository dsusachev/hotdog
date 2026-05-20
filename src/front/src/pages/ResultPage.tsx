import { useNavigate } from 'react-router-dom'

export default function ResultPage() {
  const navigate = useNavigate()

  return (
    <div className="max-w-md mx-auto py-10 px-4">
      <button
        onClick={() => navigate(-1)}
        className="text-sm text-gray-500 hover:text-teal-600 mb-6 block"
      >
        ← Назад
      </button>

      <div className="bg-white border border-gray-200 rounded-2xl p-8 text-center text-gray-400">
        <div className="text-5xl mb-4">📊</div>
        <p>Результат анализа появится здесь</p>
      </div>
    </div>
  )
}
