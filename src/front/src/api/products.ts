import type { Product } from '../types/api'

export async function searchProducts(query: string): Promise<Product[]> {
  const res = await fetch(`/api/products/search?query=${encodeURIComponent(query.trim())}`)
  if (!res.ok) throw new Error(`Ошибка сервера: ${res.status}`)
  const data = await res.json()
  return data.products ?? []
}
