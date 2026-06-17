import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore, useNotificationStore } from '@/store'
import { apiClient } from '@/services/api'
import { notificationService } from '@/services/notificationService'
import { toast } from '@/components/ui/Toast'
import { useNotifications } from '@/hooks/useNotifications'

interface HeaderProps {
  onMenuClick: () => void
}

const SEVERITY_CONFIG = {
  info:     { cls: 'bg-blue-50 border-blue-100',   dot: 'bg-blue-400',   label: 'Ma\'lumot' },
  warning:  { cls: 'bg-yellow-50 border-yellow-100', dot: 'bg-yellow-400', label: 'Ogohlantirish' },
  critical: { cls: 'bg-red-50 border-red-100',      dot: 'bg-red-500',    label: 'Kritik' },
}

export function Header({ onMenuClick }: HeaderProps) {
  const navigate = useNavigate()
  const { user, clearAuth } = useAuthStore()
  const { notifications, unreadCount, markRead } = useNotificationStore()
  const [drawerOpen, setDrawerOpen] = useState(false)

  useNotifications()

  const handleLogout = async () => {
    try {
      await apiClient.post('/auth/logout')
    } catch {
      // Ignore errors — we clear local state regardless
    }
    clearAuth()
    toast('success', 'Tizimdan chiqildi')
    navigate('/login', { replace: true })
  }

  const handleMarkRead = async (id: string) => {
    try {
      await notificationService.markAsRead(id)
      markRead(id)
    } catch {
      // silently fail
    }
  }

  const initials = user?.full_name
    ? user.full_name.split(' ').map((n) => n[0]).join('').toUpperCase().slice(0, 2)
    : '??'

  return (
    <>
      <header className="h-14 bg-white border-b border-gray-200 flex items-center px-4 gap-4">
        {/* Hamburger — mobile only */}
        <button
          className="lg:hidden flex items-center justify-center w-9 h-9 rounded-lg hover:bg-gray-100 transition-colors"
          onClick={onMenuClick}
          aria-label="Menyu ochish"
        >
          <svg className="w-5 h-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>

        {/* Spacer */}
        <div className="flex-1" />

        {/* Notification bell */}
        <button
          onClick={() => setDrawerOpen(true)}
          className="relative flex items-center justify-center w-9 h-9 rounded-lg hover:bg-gray-100 transition-colors"
          aria-label="Bildirishnomalar"
        >
          <svg className="w-5 h-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
          </svg>
          {unreadCount > 0 && (
            <span className="absolute -top-0.5 -right-0.5 flex items-center justify-center w-4 h-4 bg-red-500 text-white text-[10px] font-bold rounded-full">
              {unreadCount > 9 ? '9+' : unreadCount}
            </span>
          )}
        </button>

        {/* User info + logout */}
        <div className="flex items-center gap-3">
          <div className="text-right hidden sm:block">
            <p className="text-sm font-medium text-gray-900 leading-none">{user?.full_name ?? 'Foydalanuvchi'}</p>
            <p className="text-xs text-gray-500 mt-0.5">{user?.email}</p>
          </div>
          <div className="flex items-center justify-center w-9 h-9 bg-green-100 rounded-full text-green-700 font-bold text-sm">
            {initials}
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-1.5 px-3 py-1.5 text-sm text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
            title="Chiqish"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            <span className="hidden sm:inline">Chiqish</span>
          </button>
        </div>
      </header>

      {/* Notification drawer */}
      {drawerOpen && (
        <div className="fixed inset-0 z-50 flex">
          {/* Backdrop */}
          <div
            className="flex-1 bg-black/30"
            onClick={() => setDrawerOpen(false)}
          />
          {/* Panel */}
          <div className="w-80 bg-white shadow-xl flex flex-col">
            <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100">
              <h2 className="text-sm font-semibold text-gray-900">
                Bildirishnomalar
                {unreadCount > 0 && (
                  <span className="ml-2 px-1.5 py-0.5 bg-red-100 text-red-600 text-xs font-bold rounded-full">
                    {unreadCount}
                  </span>
                )}
              </h2>
              <button
                onClick={() => setDrawerOpen(false)}
                className="w-7 h-7 flex items-center justify-center rounded-lg hover:bg-gray-100 text-gray-500"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="flex-1 overflow-y-auto">
              {notifications.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-16 text-gray-400">
                  <svg className="w-10 h-10 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                      d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                  </svg>
                  <p className="text-sm">Bildirishnoma yo'q</p>
                </div>
              ) : (
                <ul className="divide-y divide-gray-50">
                  {notifications.map((n) => {
                    const cfg = SEVERITY_CONFIG[n.severity] ?? SEVERITY_CONFIG.info
                    return (
                      <li
                        key={n.id}
                        className={`px-4 py-3 ${cfg.cls} border-l-2 ${n.is_read ? 'opacity-60' : ''} cursor-pointer hover:brightness-95 transition-all`}
                        onClick={() => !n.is_read && handleMarkRead(n.id)}
                      >
                        <div className="flex items-start gap-2">
                          <span className={`mt-1.5 w-2 h-2 rounded-full flex-shrink-0 ${cfg.dot}`} />
                          <div className="flex-1 min-w-0">
                            <p className="text-xs font-semibold text-gray-900 truncate">{n.title}</p>
                            <p className="text-xs text-gray-600 mt-0.5 line-clamp-2">{n.body}</p>
                            <p className="text-[10px] text-gray-400 mt-1">
                              {new Date(n.created_at).toLocaleString('uz-UZ')}
                            </p>
                          </div>
                          {!n.is_read && (
                            <span className="w-2 h-2 bg-blue-500 rounded-full flex-shrink-0 mt-1.5" />
                          )}
                        </div>
                      </li>
                    )
                  })}
                </ul>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  )
}
