import type { HistoryEntry } from '../types/api'
import { authFetch } from '../utils/authFetch'

export async function getHistory(): Promise<HistoryEntry[]> {
  const res = await authFetch('/api/history')
  if (!res.ok) throw new Error(`Ошибка сервера: ${res.status}`)
  return res.json()
}

export async function deleteHistoryEntry(id: string): Promise<void> {
  const res = await authFetch(`/api/history/${id}`, { method: 'DELETE' })
  if (!res.ok) throw new Error(`Ошибка сервера: ${res.status}`)
}
