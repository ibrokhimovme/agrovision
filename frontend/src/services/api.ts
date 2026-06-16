import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios'
import type { ErrorResponse } from '@/types'
import { useAuthStore } from '@/store'

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api/v1'

let isRefreshing = false
let refreshQueue: Array<(token: string) => void> = []

function drainQueue(newToken: string) {
  refreshQueue.forEach((cb) => cb(newToken))
  refreshQueue = []
}

function createApiClient(): AxiosInstance {
  const client = axios.create({
    baseURL: BASE_URL,
    timeout: 30_000,
    headers: { 'Content-Type': 'application/json' },
  })

  client.interceptors.request.use((config: InternalAxiosRequestConfig) => {
    const { accessToken } = useAuthStore.getState()
    if (accessToken) {
      config.headers['Authorization'] = `Bearer ${accessToken}`
    }
    return config
  })

  client.interceptors.response.use(
    (response) => response,
    async (error: AxiosError<ErrorResponse>) => {
      const original = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

      if (error.response?.status !== 401 || original._retry) {
        return Promise.reject(error)
      }

      const { refreshToken, user, setAuth, clearAuth } = useAuthStore.getState()

      if (!refreshToken) {
        clearAuth()
        window.location.href = '/login'
        return Promise.reject(error)
      }

      if (isRefreshing) {
        return new Promise<string>((resolve) => {
          refreshQueue.push(resolve)
        }).then((token) => {
          original.headers['Authorization'] = `Bearer ${token}`
          return client(original)
        })
      }

      original._retry = true
      isRefreshing = true

      try {
        const resp = await axios.post(`${BASE_URL}/auth/refresh`, {
          refresh_token: refreshToken,
        })
        const newAccessToken: string = resp.data.data.access_token

        setAuth(
          {
            access_token: newAccessToken,
            refresh_token: refreshToken,
            token_type: 'bearer',
            expires_in: 1800,
          },
          user!
        )

        drainQueue(newAccessToken)
        original.headers['Authorization'] = `Bearer ${newAccessToken}`
        return client(original)
      } catch {
        clearAuth()
        window.location.href = '/login'
        return Promise.reject(error)
      } finally {
        isRefreshing = false
      }
    }
  )

  return client
}

export const apiClient = createApiClient()
