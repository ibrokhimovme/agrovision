import { apiClient } from './api'
import type { APIResponse, Notification, PaginatedResponse } from '@/types'

export interface UnreadCountResponse {
  unread_count: number
}

export const notificationService = {
  async list(userId: string, page = 1, page_size = 20, unread_only = false): Promise<PaginatedResponse<Notification>> {
    const resp = await apiClient.get<PaginatedResponse<Notification>>('/notifications/', {
      params: { user_id: userId, page, page_size, unread_only },
    })
    return resp.data
  },

  async getUnreadCount(userId: string): Promise<number> {
    const resp = await apiClient.get<APIResponse<UnreadCountResponse>>('/notifications/unread-count', {
      params: { user_id: userId },
    })
    return resp.data.data.unread_count
  },

  async markAsRead(notificationId: string): Promise<APIResponse<Notification>> {
    const resp = await apiClient.patch<APIResponse<Notification>>(`/notifications/${notificationId}/read`)
    return resp.data
  },
}
