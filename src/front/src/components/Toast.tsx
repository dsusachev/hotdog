// Toast.tsx
// Использование:
//   1. Оберни приложение в <ToastProvider> (в App.tsx)
//   2. В любом компоненте: const { toast } = useToast()
//      toast.success('Готово!') / toast.error('Ошибка') / toast.info('Инфо')

import { createContext, useContext, useState, useCallback, useEffect, useRef } from 'react'

// ─── Types ───────────────────────────────────────────────────────────────────

type ToastType = 'success' | 'error' | 'info'

interface Toast {
  id: string
  message: string
  type: ToastType
  duration?: number
}

interface ToastContextValue {
  toast: {
    success: (msg: string, duration?: number) => void
    error:   (msg: string, duration?: number) => void
    info:    (msg: string, duration?: number) => void
  }
}

// ─── Context ─────────────────────────────────────────────────────────────────

const ToastContext = createContext<ToastContextValue | null>(null)

export function useToast(): ToastContextValue {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error('useToast must be used inside <ToastProvider>')
  return ctx
}

// ─── Single Toast Item ────────────────────────────────────────────────────────

function ToastItem({
  toast,
  onRemove,
}: {
  toast: Toast
  onRemove: (id: string) => void
}) {
  const [visible, setVisible] = useState(false)
  const [leaving, setLeaving] = useState(false)
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  // mount → slide in
  useEffect(() => {
    const raf = requestAnimationFrame(() => setVisible(true))
    return () => cancelAnimationFrame(raf)
  }, [])

  // auto-dismiss
  useEffect(() => {
    const duration = toast.duration ?? 3500
    timerRef.current = setTimeout(() => dismiss(), duration)
    return () => { if (timerRef.current) clearTimeout(timerRef.current) }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const dismiss = () => {
    setLeaving(true)
    setTimeout(() => onRemove(toast.id), 300)
  }

  const icons: Record<ToastType, string> = {
    success: '✓',
    error:   '✕',
    info:    'i',
  }

  const colorMap: Record<ToastType, { bar: string; icon: string; bg: string }> = {
    success: { bar: 'bg-teal-500',  icon: 'bg-teal-500 text-white',  bg: 'bg-white' },
    error:   { bar: 'bg-red-500',   icon: 'bg-red-500 text-white',   bg: 'bg-white' },
    info:    { bar: 'bg-blue-500',  icon: 'bg-blue-500 text-white',  bg: 'bg-white' },
  }

  const { bar, icon, bg } = colorMap[toast.type]

  return (
    <div
      onClick={dismiss}
      style={{
        transform:  visible && !leaving ? 'translateX(0)' : 'translateX(120%)',
        opacity:    visible && !leaving ? 1 : 0,
        transition: 'transform 0.3s cubic-bezier(0.34,1.56,0.64,1), opacity 0.3s ease',
      }}
      className={`
        relative flex items-center gap-3 w-80 max-w-[calc(100vw-2rem)]
        ${bg} rounded-xl shadow-lg border border-gray-100
        px-4 py-3 cursor-pointer overflow-hidden select-none
      `}
    >
      {/* left colour bar */}
      <span className={`absolute left-0 top-0 bottom-0 w-1 rounded-l-xl ${bar}`} />

      {/* icon */}
      <span className={`
        flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center
        text-xs font-bold ${icon}
      `}>
        {icons[toast.type]}
      </span>

      {/* message */}
      <p className="flex-1 text-sm text-gray-800 font-medium leading-snug pr-2">
        {toast.message}
      </p>

      {/* dismiss × */}
      <span className="text-gray-300 text-xs hover:text-gray-500 transition-colors">✕</span>
    </div>
  )
}

// ─── Provider ─────────────────────────────────────────────────────────────────

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([])

  const remove = useCallback((id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id))
  }, [])

  const add = useCallback((message: string, type: ToastType, duration?: number) => {
    const id = Math.random().toString(36).slice(2)
    setToasts(prev => [...prev, { id, message, type, duration }])
  }, [])

  const toast = {
    success: (msg: string, duration?: number) => add(msg, 'success', duration),
    error:   (msg: string, duration?: number) => add(msg, 'error',   duration),
    info:    (msg: string, duration?: number) => add(msg, 'info',    duration),
  }

  return (
    <ToastContext.Provider value={{ toast }}>
      {children}

      {/* Portal-like fixed container */}
      <div className="fixed bottom-24 right-4 md:bottom-6 z-[9999] flex flex-col gap-2 items-end pointer-events-none">
        {toasts.map(t => (
          <div key={t.id} className="pointer-events-auto">
            <ToastItem toast={t} onRemove={remove} />
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  )
}
