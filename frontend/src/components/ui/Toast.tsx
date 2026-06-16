import { create } from 'zustand'
import { useEffect } from 'react'

type ToastType = 'success' | 'error' | 'warning' | 'info'

interface Toast {
  id: string
  type: ToastType
  message: string
}

interface ToastState {
  toasts: Toast[]
  show: (type: ToastType, message: string) => void
  dismiss: (id: string) => void
}

export const useToastStore = create<ToastState>((set) => ({
  toasts: [],
  show: (type, message) => {
    const id = crypto.randomUUID()
    set((s) => ({ toasts: [...s.toasts, { id, type, message }] }))
    setTimeout(() => {
      set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) }))
    }, 4000)
  },
  dismiss: (id) => set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })),
}))

export function toast(type: ToastType, message: string) {
  useToastStore.getState().show(type, message)
}

const typeStyles: Record<ToastType, string> = {
  success: 'bg-green-600',
  error:   'bg-red-600',
  warning: 'bg-yellow-500',
  info:    'bg-blue-600',
}

const icons: Record<ToastType, string> = {
  success: '✓',
  error:   '✕',
  warning: '⚠',
  info:    'ℹ',
}

function ToastItem({ toast: t, onDismiss }: { toast: Toast; onDismiss: () => void }) {
  useEffect(() => {
    const timer = setTimeout(onDismiss, 4000)
    return () => clearTimeout(timer)
  }, [onDismiss])

  return (
    <div
      className={`flex items-center gap-3 px-4 py-3 rounded-lg text-white shadow-lg min-w-64 max-w-sm ${typeStyles[t.type]}`}
      role="alert"
    >
      <span className="font-bold text-lg leading-none">{icons[t.type]}</span>
      <p className="flex-1 text-sm">{t.message}</p>
      <button
        onClick={onDismiss}
        className="text-white/70 hover:text-white ml-2 text-lg leading-none"
        aria-label="Yopish"
      >
        ×
      </button>
    </div>
  )
}

export function ToastContainer() {
  const { toasts, dismiss } = useToastStore()

  if (toasts.length === 0) return null

  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-2" aria-live="polite">
      {toasts.map((t) => (
        <ToastItem key={t.id} toast={t} onDismiss={() => dismiss(t.id)} />
      ))}
    </div>
  )
}
