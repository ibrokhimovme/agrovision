import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store'
import { apiClient } from '@/services/api'
import { toast } from '@/components/ui/Toast'

interface HeaderProps {
  onMenuClick: () => void
}

export function Header({ onMenuClick }: HeaderProps) {
  const navigate = useNavigate()
  const { user, clearAuth } = useAuthStore()

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

  const initials = user?.full_name
    ? user.full_name.split(' ').map((n) => n[0]).join('').toUpperCase().slice(0, 2)
    : '??'

  return (
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
  )
}
