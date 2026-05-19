export default function SearchPage() {
  return (
    <div className="max-w-2xl mx-auto py-10 px-4">
      <h1 className="text-2xl font-bold mb-2">Поиск продукта</h1>
      <p className="text-gray-500 mb-8">Введите название продукта для получения информации о составе.</p>

      <div className="relative mb-6">
        <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">🔍</span>
        <input
          type="text"
          placeholder="Например: яблоко, гречка, творог..."
          className="w-full pl-11 pr-4 py-3 border border-gray-300 rounded-lg bg-white text-base focus:outline-none focus:border-teal-600 transition-colors"
        />
      </div>

      <button className="w-full py-3 bg-teal-600 text-white rounded-lg font-medium cursor-default">
        Найти
      </button>

      <div className="mt-12 text-center text-gray-400">
        <div className="text-4xl mb-3">🥦</div>
        <p>Результаты поиска появятся здесь</p>
      </div>
    </div>
  )
}
