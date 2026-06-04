export type TokenResponse = {
  access_token: string
  token_type: string
}

export type TopPrediction = {
  category: string
  confidence: number
}

export type ClassifyResponse = {
  status: 'ok' | 'unknown'
  is_unknown: boolean
  category: string | null
  confidence: number | null
  top_k: TopPrediction[]
  mock: boolean
}

export type HistoryEntry = {
  id: string
  label: string
  query: string
  entry_type: 'classify' | 'search'
  confidence?: number
  created_at: string
}

export type NutritionFacts = {
  calories_per_100g: number | null
  proteins_per_100g: number | null
  fats_per_100g: number | null
  carbs_per_100g: number | null
}

export type Product = {
  id: string
  name: string
  brand: string | null
  categories: string | null
  image_url: string | null
  nutrition: NutritionFacts
}

export type ApiPlace = {
  name: string
  address?: string
  latitude?: number
  longitude?: number
  category?: string
}

export type PricesResponse = {
  places: ApiPlace[]
}
