import type { ClassifyResponse } from '../types/api'
import { authFetch } from '../utils/authFetch'

export async function classifyImage(
  file: File,
  lat?: number,
  lng?: number,
): Promise<ClassifyResponse> {
  const formData = new FormData()
  formData.append('file', file)
  if (lat != null) formData.append('lat', String(lat))
  if (lng != null) formData.append('lng', String(lng))

  const res = await authFetch('/api/classify', { method: 'POST', body: formData })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || `Ошибка сервера: ${res.status}`)
  }
  return res.json()
}
