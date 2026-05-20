import hotdogImg from '../assets/hotdog.jpeg'

export default function Footer() {
  return (
    <footer className="bg-white border-t border-gray-200 mt-auto">
      <div className="max-w-5xl mx-auto px-4 py-6 flex items-end gap-6">
        <div className="space-y-3 flex-1">
          <p className="text-sm text-gray-500">
            Если вы нашли ошибку, сообщите нам об этом:{' '}
            <a
              href="mailto:support@hotdog.ru"
              className="text-teal-600 hover:underline"
            >
              support@hotdog.ru
            </a>
          </p>

          <p className="text-xs text-gray-400 leading-relaxed">
            В нашем сервисе применяются рекомендательные технологии (информационные технологии
            предоставления информации на основе сбора, систематизации и анализа сведений,
            относящихся к предпочтениям пользователей сети «Интернет», находящихся на территории
            Российской Федерации).
          </p>

          <p className="text-sm text-gray-400">2026 © Hotdog team</p>
        </div>

        <img
          src={hotdogImg}
          alt="Hotdog mascot"
          className="w-24 h-24 object-contain flex-shrink-0 ml-auto"
        />
      </div>
    </footer>
  )
}
