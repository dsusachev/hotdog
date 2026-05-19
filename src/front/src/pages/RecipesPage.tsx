export default function RecipesPage() {
  return (
    <div className="max-w-2xl mx-auto py-10 px-4">
      <h1 className="text-2xl font-bold mb-2">Рецепты</h1>
      <p className="text-gray-500 mb-8">Здоровые рецепты с учётом состава продуктов.</p>

      <div className="flex gap-2 flex-wrap mb-8">
        {['Все', 'Завтрак', 'Обед', 'Ужин', 'Перекус'].map((f) => (
          <button
            key={f}
            className="px-4 py-1.5 rounded-full text-sm border border-gray-300 bg-white cursor-default"
          >
            {f}
          </button>
        ))}
      </div>

      <div className="text-center text-gray-400 py-16">
        <div className="text-4xl mb-3">🍽️</div>
        <p>Рецепты появятся здесь</p>
      </div>
    </div>
  )
}
