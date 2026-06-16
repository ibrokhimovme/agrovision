import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import { apiClient } from '@/services/api'
import { useAuthStore } from '@/store'
import { toast } from '@/components/ui/Toast'
import { Spinner } from '@/components/ui/Spinner'
import type { AuthTokens, UserProfile } from '@/types'

const schema = z.object({
  email: z.string().min(1, "Email manzil kiritilishi shart").email("Noto'g'ri email format"),
  password: z.string().min(1, "Parol kiritilishi shart"),
})

type FormValues = z.infer<typeof schema>

export default function LoginPage() {
  const navigate = useNavigate()
  const setAuth = useAuthStore((s) => s.setAuth)
  const [loading, setLoading] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormValues>({ resolver: zodResolver(schema) })

  const onSubmit = async (data: FormValues) => {
    setLoading(true)
    try {
      const loginResp = await apiClient.post<{ data: AuthTokens }>('/auth/login', {
        email: data.email,
        password: data.password,
      })
      const tokens = loginResp.data.data

      const meResp = await apiClient.get<{ data: UserProfile }>('/users/me', {
        headers: { Authorization: `Bearer ${tokens.access_token}` },
      })
      const user = meResp.data.data

      setAuth(tokens, user)
      navigate('/', { replace: true })
    } catch (err: unknown) {
      const code = (err as { response?: { data?: { error_code?: string } } })?.response?.data?.error_code
      if (code === 'AUTH_001') {
        toast('error', "Email yoki parol noto'g'ri")
      } else if (code === 'BUSINESS_RULE') {
        toast('error', 'Hisob bloklangan. Administrator bilan bog\'laning.')
      } else {
        toast('error', 'Tizimga kirishda xatolik yuz berdi. Qayta urinib ko\'ring.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          {/* Logo / Brand */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-green-600 rounded-2xl mb-4">
              <svg className="w-9 h-9 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
              </svg>
            </div>
            <h1 className="text-2xl font-bold text-gray-900">AgroVision</h1>
            <p className="text-gray-500 text-sm mt-1">Qishloq xo'jaligi boshqaruv tizimi</p>
          </div>

          <h2 className="text-lg font-semibold text-gray-800 mb-6">Tizimga Kirish</h2>

          <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-5">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                Email manzil
              </label>
              <input
                id="email"
                type="email"
                autoComplete="email"
                {...register('email')}
                className={`w-full px-3 py-2.5 border rounded-lg text-sm outline-none transition-colors
                  focus:ring-2 focus:ring-green-500 focus:border-green-500
                  ${errors.email ? 'border-red-400 bg-red-50' : 'border-gray-300'}`}
                placeholder="misol@ferma.uz"
              />
              {errors.email && (
                <p className="mt-1 text-xs text-red-600">{errors.email.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                Parol
              </label>
              <input
                id="password"
                type="password"
                autoComplete="current-password"
                {...register('password')}
                className={`w-full px-3 py-2.5 border rounded-lg text-sm outline-none transition-colors
                  focus:ring-2 focus:ring-green-500 focus:border-green-500
                  ${errors.password ? 'border-red-400 bg-red-50' : 'border-gray-300'}`}
                placeholder="••••••••"
              />
              {errors.password && (
                <p className="mt-1 text-xs text-red-600">{errors.password.message}</p>
              )}
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 bg-green-600 hover:bg-green-700
                disabled:opacity-60 disabled:cursor-not-allowed text-white font-semibold
                py-2.5 px-4 rounded-lg transition-colors text-sm"
            >
              {loading ? <Spinner size="sm" /> : null}
              {loading ? 'Kirish...' : 'Kirish'}
            </button>
          </form>

          <p className="text-center text-xs text-gray-400 mt-6">
            AgroVision &copy; {new Date().getFullYear()}
          </p>
        </div>
      </div>
    </div>
  )
}
