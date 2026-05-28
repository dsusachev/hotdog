import { useNavigate } from 'react-router-dom'
import { useEffect, useRef } from 'react'

const STEPS = [
  {
    num: '01',
    title: 'Сфотографируй или введи',
    desc: 'Загрузи фото блюда или найди продукт по названию в поиске.',
  },
  {
    num: '02',
    title: 'ИИ анализирует',
    desc: 'Модель определяет продукт и рассчитывает питательный состав.',
  },
  {
    num: '03',
    title: 'Получи результат',
    desc: 'БЖУ, калории, история запросов и места рядом, где купить.',
  },
]

const FACTS = [
  { num: '1 000+', desc: 'продуктов в базе' },
  { num: '94%',    desc: 'точность распознавания' },
  { num: '< 2 с',  desc: 'время анализа фото' },
]

const BARS = [
  { label: 'Белки',    val: '4.1 г', pct: 28,  color: '#1A6B6B' },
  { label: 'Жиры',     val: '8.2 г', pct: 55,  color: '#D97706' },
  { label: 'Углеводы', val: '5.7 г', pct: 38,  color: '#145858' },
]

export default function HomePage() {
  const navigate = useNavigate()
  const barsRef = useRef<HTMLDivElement>(null)

  // animate bars on mount
  useEffect(() => {
    const fills = barsRef.current?.querySelectorAll<HTMLDivElement>('.bar-fill')
    if (!fills) return
    fills.forEach((el, i) => {
      const target = el.dataset.pct ?? '0'
      el.style.width = '0%'
      setTimeout(() => {
        el.style.transition = 'width 1s cubic-bezier(0.22,1,0.36,1)'
        el.style.width = `${target}%`
      }, 80 + i * 100)
    })
  }, [])

  return (
    <div className="flex flex-col gap-0">

      {/* ── Hero ── */}
      <section className="grid md:grid-cols-2 gap-8 items-center py-12">
        <div>
          <div className="inline-flex items-center gap-2 bg-teal-50 dark:bg-teal-900/30 text-teal-700 dark:text-teal-400 text-xs font-medium rounded-full px-3 py-1.5 mb-5">
            <span className="w-2 h-2 rounded-full bg-teal-600 dark:bg-teal-400 inline-block" />
            Зарегистрируйся — это бесплатно
          </div>

          <h1 className="font-serif text-5xl md:text-6xl leading-[1.07] mb-5 text-gray-900 dark:text-gray-50">
            Узнай, что<br />
            <em className="not-italic text-teal-600 dark:text-teal-400">в твоей</em><br />
            тарелке
          </h1>

          <p className="text-gray-500 dark:text-gray-400 text-base leading-relaxed mb-8 max-w-md">
            Сфотографируй блюдо или введи название — FoodScanner мгновенно
            определит состав, калории и питательную ценность.
          </p>

          <div className="flex gap-3 flex-wrap">
            <button
              onClick={() => navigate('/upload')}
              className="flex items-center gap-2 px-6 py-3 bg-teal-600 hover:bg-teal-700 text-white rounded-xl font-medium transition-colors"
            >
              📸 Загрузить фото
            </button>
            <button
              onClick={() => navigate('/search')}
              className="flex items-center gap-2 px-6 py-3 border border-gray-300 dark:border-gray-700 dark:text-gray-300 rounded-xl font-medium hover:border-teal-500 hover:text-teal-600 dark:hover:border-teal-500 dark:hover:text-teal-400 transition-colors"
            >
              🔍 Найти продукт
            </button>
          </div>
        </div>

        {/* Demo card */}
        <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-5 shadow-sm">
          <div className="w-full h-40 rounded-xl bg-teal-50 dark:bg-teal-900/30 flex items-center justify-center text-6xl mb-4 select-none">
            🥗
          </div>
          <p className="font-semibold text-gray-800 dark:text-gray-100 mb-0.5">Греческий салат</p>
          <p className="text-xs text-gray-400 dark:text-gray-500 mb-4">Уверенность: 94% · 100 г</p>

          <div ref={barsRef} className="flex flex-col gap-2">
            {BARS.map(({ label, val, pct, color }) => (
              <div key={label} className="flex items-center gap-2">
                <span className="text-xs text-gray-500 dark:text-gray-400 w-16 flex-shrink-0">{label}</span>
                <div className="flex-1 h-1.5 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
                  <div
                    className="bar-fill h-full rounded-full"
                    data-pct={pct}
                    style={{ backgroundColor: color, width: 0 }}
                  />
                </div>
                <span className="text-xs font-medium text-gray-700 dark:text-gray-300 w-9 text-right">{val}</span>
              </div>
            ))}
          </div>

          <div className="flex items-baseline gap-1.5 mt-4 pt-4 border-t border-gray-100 dark:border-gray-800">
            <span className="font-serif text-3xl text-teal-600 dark:text-teal-400">112</span>
            <span className="text-sm text-gray-400 dark:text-gray-500">ккал на 100 г</span>
          </div>
        </div>
      </section>

      <hr className="border-gray-200 dark:border-gray-800" />

      {/* ── How it works ── */}
      <section className="py-10">
        <p className="text-xs font-medium tracking-widest uppercase text-gray-400 dark:text-gray-500 mb-6">
          Как это работает
        </p>
        <div className="grid md:grid-cols-3 gap-4">
          {STEPS.map(({ num, title, desc }) => (
            <div
              key={num}
              className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-5 flex flex-col gap-3"
            >
              <span className="font-serif text-3xl text-teal-600 dark:text-teal-400 leading-none">{num}</span>
              <p className="font-medium text-gray-800 dark:text-gray-100 text-sm">{title}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400 leading-relaxed">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      <hr className="border-gray-200 dark:border-gray-800" />

      {/* ── Facts ── */}
      <section className="py-10">
        <p className="text-xs font-medium tracking-widest uppercase text-gray-400 dark:text-gray-500 mb-6">
          Цифры
        </p>
        <div className="grid grid-cols-3 gap-3">
          {FACTS.map(({ num, desc }) => (
            <div key={num} className="bg-gray-50 dark:bg-gray-900/60 rounded-xl p-4">
              <p className="font-serif text-3xl text-teal-600 dark:text-teal-400 leading-none mb-1">{num}</p>
              <p className="text-xs text-gray-500 dark:text-gray-400">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      <hr className="border-gray-200 dark:border-gray-800" />

      {/* ── CTA ── */}
      <section className="py-10">
        <div className="bg-teal-600 dark:bg-teal-700 rounded-2xl p-10 text-center">
          <h2 className="font-serif text-3xl text-white mb-2 font-normal">
            Попробуй прямо сейчас
          </h2>
          <p className="text-teal-100 text-sm mb-6">
            Загрузи первое фото — это займёт меньше минуты
          </p>
          <div className="flex gap-3 justify-center flex-wrap">
            <button
              onClick={() => navigate('/upload')}
              className="px-6 py-3 bg-white text-teal-700 rounded-xl font-medium hover:bg-teal-50 transition-colors"
            >
              Загрузить фото
            </button>
            <button
              onClick={() => navigate('/register')}
              className="px-6 py-3 border border-teal-400 text-white rounded-xl font-medium hover:bg-teal-500 transition-colors"
            >
              Зарегистрироваться
            </button>
          </div>
        </div>
      </section>

    </div>
  )
}
