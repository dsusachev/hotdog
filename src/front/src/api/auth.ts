import type { TokenResponse } from '../types/api'

export function getToken(): string | null {
  return localStorage.getItem('token')
}

export function saveToken(token: string): void {
  localStorage.setItem('token', token)
}

export function removeToken(): void {
  localStorage.removeItem('token')
}

export function getEmailFromToken(): string | null {
  try {
    const token = getToken()
    if (!token) return null
    const payload = JSON.parse(atob(token.split('.')[1]))
    return payload.sub ?? payload.email ?? null
  } catch {
    return null
  }
}

export async function login(email: string, password: string): Promise<TokenResponse> {
  const res = await fetch('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    throw new Error(data.detail ?? 'Неверный email или пароль')
  }
  return res.json()
}

export async function register(
  email: string,
  password: string,
  display_name?: string,
): Promise<void> {
  const res = await fetch('/api/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, display_name }),
  })
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    throw new Error(data.detail ?? 'Ошибка регистрации')
  }
}
