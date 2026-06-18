import { apiClient } from './api'
import type { APIResponse, PaginatedResponse, AdminUser, RoleDetail } from '@/types'

export interface CreateUserPayload {
  email: string
  full_name: string
  password: string
  role_name: string
  farm_id?: string
  phone?: string
}

export interface UpdateUserPayload {
  full_name?: string
  phone?: string
  is_active?: boolean
}

export const userService = {
  // EX-15 (execution-v2): farmId omitted lists account-wide (all farms in
  // the caller's account); the backend resolves the account from the
  // request's auth context, not a client-supplied value.
  async listUsers(farmId?: string, page = 1, pageSize = 50): Promise<PaginatedResponse<AdminUser>> {
    const resp = await apiClient.get<PaginatedResponse<AdminUser>>('/users/', {
      params: { farm_id: farmId || undefined, page, page_size: pageSize },
    })
    return resp.data
  },

  async createUser(payload: CreateUserPayload): Promise<APIResponse<AdminUser>> {
    const resp = await apiClient.post<APIResponse<AdminUser>>('/users/', payload)
    return resp.data
  },

  async updateUser(userId: string, payload: UpdateUserPayload): Promise<APIResponse<AdminUser>> {
    const resp = await apiClient.patch<APIResponse<AdminUser>>(`/users/${userId}`, payload)
    return resp.data
  },

  async listRoles(): Promise<APIResponse<RoleDetail[]>> {
    const resp = await apiClient.get<APIResponse<RoleDetail[]>>('/roles/')
    return resp.data
  },
}
