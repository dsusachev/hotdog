import { useNavigate } from 'react-router-dom'

export default function HomePage() {
  const navigate = useNavigate()

  return (
    <div className="flex flex-col items-center justify-center py-20 px-4 text-center">
      <h1 className="text-4xl font-bold mb-4 text-gray-900 dark:text-gray-50">FoodScanner</h1>
      <p className="text-gray-500 dark:text-gray-400 text-lg mb-10 max-w-md">
        Сервис для анализа продуктов питания. Загрузите фото или найдите продукт по названию.
      </p>
      <div className="flex gap-4 flex-wrap justify-center">
        <button
          onClick={() => navigate('/upload')}
          className="px-6 py-3 bg-teal-600 text-white rounded-lg font-medium hover:bg-teal-700 transition-colors"
        >
          Загрузить фото
        </button>
        <button
          onClick={() => navigate('/search')}
          className="px-6 py-3 border border-gray-300 dark:border-gray-600 dark:text-gray-300 rounded-lg font-medium hover:border-teal-600 dark:hover:border-teal-500 transition-colors"
        >
          Найти продукт
        </button>
      </div>
    </div>
  )
}
