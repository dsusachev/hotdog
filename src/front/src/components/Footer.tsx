import hotdogImg from '../assets/hotdog.jpeg'

export default function Footer() {
  return (
    <footer className="bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800 mt-auto transition-colors duration-200">
      <div className="max-w-5xl mx-auto px-4 py-6 flex items-end gap-6">
        <div className="space-y-3 flex-1">
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Если вы нашли ошибку, сообщите нам об этом:{' '}
            <a
              href="mailto:support@hotdog.ru"
              className="text-teal-600 dark:text-teal-400 hover:underline"
            >
              support@hotdog.ru
            </a>
          </p>

          <p className="text-xs text-gray-400 dark:text-gray-500 leading-relaxed">
            В нашем сервисе применяются рекомендательные технологии (информационные технологии
            предоставления информации на основе сбора, систематизации и анализа сведений,
            относящихся к предпочтениям пользователей сети «Интернет», находящихся на территории
            Российской Федерации).
          </p>

          <p className="text-sm text-gray-400 dark:text-gray-500">2026 © Hotdog team</p>
        </div>

        <img
          src={hotdogImg}
          alt="Hotdog mascot"
          className="w-24 h-24 object-contain flex-shrink-0 ml-auto opacity-90 dark:opacity-70"
        />
      </div>
    </footer>
  )
}
