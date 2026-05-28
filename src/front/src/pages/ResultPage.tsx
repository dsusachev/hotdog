import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'

const YANDEX_API_KEY = 'ВАШ_КЛЮЧ_ЗДЕСЬ'

type Place = {
  name: string
  address: string
  distance: string
  category: string
}

type GeoStatus = 'idle' | 'loading' | 'success' | 'error'
type PlacesStatus = 'idle' | 'loading' | 'success' | 'error'

type Props = {
  mockResult?: { label: string; confidence: number; calories: number } | null
}

export default function ResultPage({ mockResult }: Props) {
  const navigate = useNavigate()
  const { state } = useLocation()
  const result = state?.result ?? mockResult ?? null

  const [geoStatus, setGeoStatus]       = useState<GeoStatus>('idle')
  const [placesStatus, setPlacesStatus] = useState<PlacesStatus>('idle')
  const [places, setPlaces]             = useState<Place[]>([])
  const [geoError, setGeoError]         = useState('')
  const [placesError, setPlacesError]   = useState('')

  const fetchNearby = () => {
    if (!navigator.geolocation) {
      setGeoError('Геолокация не поддерживается вашим браузером')
      setGeoStatus('error')
      return
    }
    setGeoStatus('loading')
    setPlaces([])
    setGeoError('')
    setPlacesError('')

    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        setGeoStatus('success')
        const { latitude, longitude } = pos.coords
        await loadPlaces(latitude, longitude)
      },
      (err) => {
        setGeoStatus('error')
        if (err.code === err.PERMISSION_DENIED) {
          setGeoError('Вы запретили доступ к геолокации')
        } else {
          setGeoError('Не удалось определить местоположение')
        }
      },
      { timeout: 8000 }
    )
  }

  const loadPlaces = async (lat: number, lon: number) => {
    setPlacesStatus('loading')
    try {
      const url = new URL('https://search-maps.yandex.ru/v1/')
      url.searchParams.set('apikey', YANDEX_API_KEY)
      url.searchParams.set('text', 'магазины продукты кафе рестораны')
      url.searchParams.set('ll', `${lon},${lat}`)
      url.searchParams.set('spn', '0.05,0.05')
      url.searchParams.set('lang', 'ru_RU')
      url.searchParams.set('results', '8')
      url.searchParams.set('type', 'biz')

      const res = await fetch(url.toString())
      if (!res.ok) throw new Error(`Ошибка Яндекс API: ${res.status}`)

      const data = await res.json()
      const features = data.features ?? []

      const rawDistances: number[] = features.map((f: any) => {
        const coords: [number, number] = f.geometry.coordinates
        return haversine(lat, lon, coords[1], coords[0])
      })

      const parsed: Place[] = features.map((f: any, i: number) => {
        const props = f.properties
        const dist = rawDistances[i]
        return {
          name:     props.name ?? 'Без названия',
          address:  props.description ?? '',
          category: props.CompanyMetaData?.Categories?.[0]?.name ?? '',
          distance: dist < 1000
            ? `${Math.round(dist)} м`
            : `${(dist / 1000).toFixed(1)} км`,
        }
      })

      parsed.sort((a, b) => rawDistances[features.indexOf(a)] - rawDistances[features.indexOf(b)])

      setPlaces(parsed)
      setPlacesStatus('success')
    } catch (err) {
      setPlacesStatus('error')
      setPlacesError(err instanceof Error ? err.message : 'Не удалось загрузить места')
    }
  }

  const isMock = !state?.result && !!mockResult

  return (
    <div className="max-w-md mx-auto py-10 px-4">
      <button
        onClick={() => navigate(-1)}
        className="text-sm text-gray-500 dark:text-gray-400 hover:text-teal-600 dark:hover:text-teal-400 mb-6 block transition-colors"
      >
        ← Назад
      </button>

      {isMock && (
        <div className="mb-4 px-4 py-2.5 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-700 rounded-lg text-amber-700 dark:text-amber-400 text-sm">
          🧪 Демо-режим — данные ненастоящие, геолокация работает
        </div>
      )}

      {/* Classification result */}
      <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6 mb-6">
        {result ? (
          <>
            <div className="text-4xl mb-3 text-center">🍽️</div>
            <h2 className="text-xl font-bold text-center mb-4 dark:text-gray-50">
              {result.is_unknown
                ? 'Не удалось распознать 🤔'
                : (result.category ?? result.label ?? 'Результат анализа')}
            </h2>
            {result.confidence !== undefined && (
              <div className="flex justify-between text-sm text-gray-500 dark:text-gray-400 mb-2">
                <span>Уверенность</span>
                <span className="font-medium text-teal-600 dark:text-teal-400">
                  {Math.round(result.confidence * 100)}%
                </span>
              </div>
            )}
            {result.calories !== undefined && (
              <div className="flex justify-between text-sm text-gray-500 dark:text-gray-400">
                <span>Калории (на 100г)</span>
                <span className="font-medium dark:text-gray-200">{result.calories} ккал</span>
              </div>
            )}
          </>
        ) : (
          <div className="text-center text-gray-400 dark:text-gray-500">
            <div className="text-5xl mb-4">📊</div>
            <p>Результат анализа появится здесь</p>
          </div>
        )}
      </div>

      {/* Nearby places */}
      <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-gray-800 dark:text-gray-100">Поблизости</h3>
          <button
            onClick={fetchNearby}
            disabled={geoStatus === 'loading' || placesStatus === 'loading'}
            className="text-sm text-teal-600 dark:text-teal-400 font-medium hover:underline disabled:opacity-50 disabled:no-underline"
          >
            {geoStatus === 'idle' ? 'Найти рядом' : 'Обновить'}
          </button>
        </div>

        {geoStatus === 'idle' && (
          <div className="text-center text-gray-400 dark:text-gray-500 py-8">
            <div className="text-3xl mb-2">📍</div>
            <p className="text-sm">Нажмите «Найти рядом» чтобы увидеть магазины и кафе поблизости</p>
          </div>
        )}

        {(geoStatus === 'loading' || placesStatus === 'loading') && (
          <div className="text-center text-gray-400 dark:text-gray-500 py-8">
            <div className="inline-block w-6 h-6 border-2 border-teal-500 border-t-transparent rounded-full animate-spin mb-3" />
            <p className="text-sm">
              {geoStatus === 'loading' ? 'Определяем местоположение…' : 'Ищем места рядом…'}
            </p>
          </div>
        )}

        {geoStatus === 'error' && (
          <div className="text-center py-6">
            <p className="text-red-500 dark:text-red-400 text-sm mb-3">{geoError}</p>
            <button onClick={fetchNearby} className="text-sm text-teal-600 dark:text-teal-400 hover:underline">
              Попробовать снова
            </button>
          </div>
        )}

        {placesStatus === 'error' && (
          <div className="text-center py-6">
            <p className="text-red-500 dark:text-red-400 text-sm mb-3">{placesError}</p>
            <button onClick={fetchNearby} className="text-sm text-teal-600 dark:text-teal-400 hover:underline">
              Попробовать снова
            </button>
          </div>
        )}

        {placesStatus === 'success' && places.length === 0 && (
          <div className="text-center text-gray-400 dark:text-gray-500 py-8">
            <p className="text-sm">Рядом ничего не найдено</p>
          </div>
        )}

        {placesStatus === 'success' && places.length > 0 && (
          <ul className="divide-y divide-gray-100 dark:divide-gray-800">
            {places.map((place, i) => (
              <li key={i} className="py-3 flex items-start gap-3">
                <span className="text-xl mt-0.5">
                  {place.category.includes('кафе') || place.category.includes('ресторан')
                    ? '☕'
                    : '🛒'}
                </span>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-gray-800 dark:text-gray-100 text-sm truncate">{place.name}</p>
                  {place.category && (
                    <p className="text-xs text-teal-600 dark:text-teal-400 mb-0.5">{place.category}</p>
                  )}
                  {place.address && (
                    <p className="text-xs text-gray-400 dark:text-gray-500 truncate">{place.address}</p>
                  )}
                </div>
                <span className="text-xs text-gray-400 dark:text-gray-500 whitespace-nowrap mt-1">
                  {place.distance}
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}

function haversine(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const R = 6371000
  const toRad = (x: number) => (x * Math.PI) / 180
  const dLat = toRad(lat2 - lat1)
  const dLon = toRad(lon2 - lon1)
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) ** 2
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
}
