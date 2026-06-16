import { apiClient } from './api'
import type {
  APIResponse,
  PaginatedResponse,
  Batch,
  Farm,
  BatchStatus,
  BatchCloseReason,
  PoultrySpecies,
} from '@/types'

export interface CreateBatchPayload {
  farm_id: string
  section_id: string
  species: PoultrySpecies
  initial_count: number
  placement_date: string
  batch_code?: string
  supplier_name?: string
  chick_price_per_head?: number
  notes?: string
  quarantine_end_date?: string
}

export interface UpdateBatchPayload {
  batch_code?: string
  supplier_name?: string
  chick_price_per_head?: number
  notes?: string
  quarantine_end_date?: string
}

export interface CloseBatchPayload {
  close_reason: BatchCloseReason
  notes?: string
}

export interface ListBatchesParams {
  farm_id: string
  status?: BatchStatus
  page?: number
  page_size?: number
}

export const batchService = {
  async createBatch(payload: CreateBatchPayload): Promise<APIResponse<Batch>> {
    const resp = await apiClient.post<APIResponse<Batch>>('/batches/', payload)
    return resp.data
  },

  async listBatches(params: ListBatchesParams): Promise<PaginatedResponse<Batch>> {
    const resp = await apiClient.get<PaginatedResponse<Batch>>('/batches/', { params })
    return resp.data
  },

  async getBatch(id: string): Promise<APIResponse<Batch>> {
    const resp = await apiClient.get<APIResponse<Batch>>(`/batches/${id}`)
    return resp.data
  },

  async updateBatch(id: string, payload: UpdateBatchPayload): Promise<APIResponse<Batch>> {
    const resp = await apiClient.patch<APIResponse<Batch>>(`/batches/${id}`, payload)
    return resp.data
  },

  async activateBatch(id: string): Promise<APIResponse<Batch>> {
    const resp = await apiClient.post<APIResponse<Batch>>(`/batches/${id}/activate`)
    return resp.data
  },

  async closeBatch(id: string, payload: CloseBatchPayload): Promise<APIResponse<Batch>> {
    const resp = await apiClient.post<APIResponse<Batch>>(`/batches/${id}/close`, payload)
    return resp.data
  },
}

export const farmService = {
  async listFarms(page = 1, page_size = 100): Promise<PaginatedResponse<Farm>> {
    const resp = await apiClient.get<PaginatedResponse<Farm>>('/farms/', {
      params: { page, page_size },
    })
    return resp.data
  },
}
