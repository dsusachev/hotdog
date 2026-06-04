import type { PricesResponse } from '../types/api'

export async function getPrices(
  product: string,
  lat: number,
  lng: number,
): Promise<PricesResponse> {
  const url = new URL('/api/prices', window.location.origin)
  url.searchParams.set('product', product)
  url.searchParams.set('lat', String(lat))
  url.searchParams.set('lng', String(lng))

  const res = await fetch(url.toString())
  if (!res.ok) throw new Error(`Ошибка сервера: ${res.status}`)
  return res.json()
}
