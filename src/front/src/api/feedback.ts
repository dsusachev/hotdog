import { authFetch } from '../utils/authFetch'

export async function submitFeedback(rating: number, message?: string): Promise<void> {
  const res = await authFetch('/api/feedback', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ rating, message }),
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
}
