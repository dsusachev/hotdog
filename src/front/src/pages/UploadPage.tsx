export default function UploadPage() {
  return (
    <div className="max-w-lg mx-auto py-10 px-4">
      <h1 className="text-2xl font-bold mb-2">Загрузка фото</h1>
      <p className="text-gray-500 mb-8">Загрузите фото блюда для анализа состава.</p>

      <div className="border-2 border-dashed border-teal-500 rounded-xl bg-teal-50 p-16 flex flex-col items-center gap-3 cursor-pointer">
        <span className="text-5xl">📷</span>
        <span className="font-medium text-gray-700">Зона загрузки фото</span>
        <span className="text-sm text-gray-400">PNG, JPG · до 10 МБ</span>
      </div>

      <div className="flex gap-3 mt-6">
        <button className="flex-1 py-3 border border-gray-300 rounded-lg font-medium text-gray-500 cursor-default">
          Выбрать файл
        </button>
        <button className="flex-1 py-3 bg-teal-600 text-white rounded-lg font-medium cursor-default">
          Анализировать
        </button>
      </div>
    </div>
  )
}
