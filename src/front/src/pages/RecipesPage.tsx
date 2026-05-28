import { useState, useEffect } from 'react'

type Category = 'all' | 'breakfast' | 'lunch' | 'dinner' | 'snack'

const CATEGORIES: { key: Category; label: string }[] = [
  { key: 'all',       label: 'Все' },
  { key: 'breakfast', label: 'Завтрак' },
  { key: 'lunch',     label: 'Обед' },
  { key: 'dinner',    label: 'Ужин' },
  { key: 'snack',     label: 'Перекус' },
]

type RecipeCard = {
  id: string
  name: string
  category: string
  image_url: string
}

type Ingredient = {
  name: string
  measure: string
}

type RecipeDetail = {
  id: string
  name: string
  category: string
  area: string | null
  image_url: string
  instructions: string
  ingredients: Ingredient[]
  youtube: string | null
}

export default function RecipesPage() {
  const [category, setCategory]   = useState<Category>('all')
  const [recipes, setRecipes]     = useState<RecipeCard[]>([])
  const [loading, setLoading]     = useState(true)
  const [selected, setSelected]   = useState<RecipeDetail | null>(null)
  const [detailLoading, setDetailLoading] = useState(false)

  useEffect(() => {
    setLoading(true)
    setRecipes([])
    fetch(`/api/recipes?category=${category}`)
      .then(r => r.json())
      .then(data => { setRecipes(data); setLoading(false) })
      .catch(() => setLoading(false))
  }, [category])

  const openRecipe = async (id: string) => {
    setDetailLoading(true)
    setSelected(null)
    try {
      const r = await fetch(`/api/recipes/${id}`)
      const data = await r.json()
      setSelected(data)
    } finally {
      setDetailLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto py-10 px-4">
      <h1 className="text-2xl font-bold mb-2 dark:text-gray-50">Рецепты</h1>
      <p className="text-gray-500 dark:text-gray-400 mb-6">Здоровые рецепты с учётом состава продуктов.</p>

      {/* Фильтры */}
      <div className="flex gap-2 flex-wrap mb-8">
        {CATEGORIES.map(({ key, label }) => (
          <button
            key={key}
            onClick={() => { setCategory(key); setSelected(null) }}
            className={`px-4 py-1.5 rounded-full text-sm border transition-colors
              ${category === key
                ? 'bg-teal-600 text-white border-teal-600'
                : 'border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 dark:text-gray-300 hover:border-teal-400'
              }`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Детальная карточка */}
      {(selected || detailLoading) && (
        <div className="mb-8 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl overflow-hidden">
          {detailLoading ? (
            <div className="flex items-center justify-center py-16">
              <span className="inline-block w-6 h-6 border-2 border-teal-500 border-t-transparent rounded-full animate-spin" />
            </div>
          ) : selected && (
            <>
              <div className="relative">
                <img src={selected.image_url} alt={selected.name} className="w-full h-56 object-cover" />
                <button
                  onClick={() => setSelected(null)}
                  className="absolute top-3 right-3 w-8 h-8 bg-black/50 text-white rounded-full flex items-center justify-center hover:bg-black/70 transition-colors text-sm"
                >
                  ✕
                </button>
              </div>
              <div className="p-6">
                <div className="flex items-start justify-between gap-4 mb-4">
                  <h2 className="text-xl font-bold dark:text-gray-50">{selected.name}</h2>
                  <div className="flex flex-col gap-1 items-end flex-shrink-0">
                    {selected.area && (
                      <span className="text-xs bg-teal-50 dark:bg-teal-900/40 text-teal-700 dark:text-teal-400 px-2 py-0.5 rounded-full">
                        {selected.area}
                      </span>
                    )}
                    {selected.youtube && (
                      <a
                        href={selected.youtube}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-red-500 hover:underline"
                      >
                        ▶ YouTube
                      </a>
                    )}
                  </div>
                </div>

                {/* Ингредиенты */}
                <h3 className="font-semibold text-gray-700 dark:text-gray-300 mb-3">Ингредиенты</h3>
                <div className="grid grid-cols-2 gap-1.5 mb-6">
                  {selected.ingredients.map((ing, i) => (
                    <div key={i} className="flex justify-between text-sm bg-gray-50 dark:bg-gray-800 rounded-lg px-3 py-1.5">
                      <span className="text-gray-700 dark:text-gray-300 truncate">{ing.name}</span>
                      <span className="text-gray-400 dark:text-gray-500 ml-2 flex-shrink-0">{ing.measure}</span>
                    </div>
                  ))}
                </div>

                {/* Инструкция */}
                <h3 className="font-semibold text-gray-700 dark:text-gray-300 mb-3">Приготовление</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed whitespace-pre-line">
                  {selected.instructions}
                </p>
              </div>
            </>
          )}
        </div>
      )}

      {/* Список карточек */}
      {loading ? (
        <div className="grid grid-cols-2 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="rounded-2xl overflow-hidden border border-gray-200 dark:border-gray-800 animate-pulse">
              <div className="w-full h-36 bg-gray-200 dark:bg-gray-800" />
              <div className="p-3">
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded mb-2 w-3/4" />
                <div className="h-3 bg-gray-100 dark:bg-gray-800 rounded w-1/2" />
              </div>
            </div>
          ))}
        </div>
      ) : recipes.length === 0 ? (
        <div className="text-center text-gray-400 dark:text-gray-500 py-16">
          <div className="text-4xl mb-3">🍽️</div>
          <p>Рецепты не найдены</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-4">
          {recipes.map(recipe => (
            <button
              key={recipe.id}
              onClick={() => openRecipe(recipe.id)}
              className="text-left rounded-2xl overflow-hidden border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 hover:border-teal-400 dark:hover:border-teal-600 transition-colors group"
            >
              <img
                src={recipe.image_url}
                alt={recipe.name}
                className="w-full h-36 object-cover group-hover:opacity-90 transition-opacity"
              />
              <div className="p-3">
                <p className="font-medium text-sm text-gray-800 dark:text-gray-100 line-clamp-2">{recipe.name}</p>
                <p className="text-xs text-teal-600 dark:text-teal-400 mt-1">Подробнее →</p>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
