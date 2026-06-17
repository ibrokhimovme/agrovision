import { apiClient } from './api'
import type {
  APIResponse,
  PaginatedResponse,
  Batch,
  Farm,
  BatchStatus,
  BatchCloseReason,
  PoultrySpecies,
  FeedRecord,
  FeedSummary,
  MortalityRecord,
  MortalitySummary,
  VaccinationRecord,
  VaccinationSchedule,
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

export interface RecordFeedPayload {
  farm_id: string
  feed_date: string
  quantity_kg: number
  water_liters?: number
  feed_type?: string
  age_days?: number
  notes?: string
}

export const feedService = {
  async recordFeed(batchId: string, payload: RecordFeedPayload): Promise<APIResponse<FeedRecord>> {
    const resp = await apiClient.post<APIResponse<FeedRecord>>(`/batches/${batchId}/feed`, payload)
    return resp.data
  },

  async listFeed(batchId: string, page = 1, page_size = 20): Promise<PaginatedResponse<FeedRecord>> {
    const resp = await apiClient.get<PaginatedResponse<FeedRecord>>(`/batches/${batchId}/feed`, {
      params: { page, page_size },
    })
    return resp.data
  },

  async getFeedSummary(batchId: string): Promise<APIResponse<FeedSummary>> {
    const resp = await apiClient.get<APIResponse<FeedSummary>>(`/batches/${batchId}/feed/summary`)
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

export interface RecordMortalityPayload {
  farm_id: string
  quantity: number
  deceased_at: string
  cause_category?: string
  cause_description?: string
  disposal_method?: string
}

export const mortalityService = {
  async recordMortality(batchId: string, payload: RecordMortalityPayload): Promise<APIResponse<MortalityRecord>> {
    const resp = await apiClient.post<APIResponse<MortalityRecord>>(`/batches/${batchId}/mortality`, payload)
    return resp.data
  },

  async listMortality(batchId: string, page = 1, page_size = 20): Promise<PaginatedResponse<MortalityRecord>> {
    const resp = await apiClient.get<PaginatedResponse<MortalityRecord>>(`/batches/${batchId}/mortality`, {
      params: { page, page_size },
    })
    return resp.data
  },

  async getMortalitySummary(batchId: string): Promise<APIResponse<MortalitySummary>> {
    const resp = await apiClient.get<APIResponse<MortalitySummary>>(`/batches/${batchId}/mortality/summary`)
    return resp.data
  },
}

export interface CreateSchedulePayload {
  farm_id: string
  species: string
  vaccine_name: string
  day_of_age: number
  is_mandatory?: boolean
  notes?: string
}

export interface RecordVaccinationPayload {
  vaccinated_at?: string
  quantity_used?: number
  unit?: string
  notes?: string
}

export const vaccinationService = {
  async createSchedule(payload: CreateSchedulePayload): Promise<APIResponse<VaccinationSchedule>> {
    const resp = await apiClient.post<APIResponse<VaccinationSchedule>>('/vaccination-schedules/', payload)
    return resp.data
  },

  async listSchedules(farmId: string, species?: string): Promise<APIResponse<VaccinationSchedule[]>> {
    const resp = await apiClient.get<APIResponse<VaccinationSchedule[]>>('/vaccination-schedules/', {
      params: { farm_id: farmId, ...(species ? { species } : {}) },
    })
    return resp.data
  },

  async generatePlan(batchId: string): Promise<APIResponse<VaccinationRecord[]>> {
    const resp = await apiClient.post<APIResponse<VaccinationRecord[]>>(`/batches/${batchId}/vaccinations/generate`)
    return resp.data
  },

  async listVaccinations(batchId: string, page = 1, page_size = 50): Promise<PaginatedResponse<VaccinationRecord>> {
    const resp = await apiClient.get<PaginatedResponse<VaccinationRecord>>(`/batches/${batchId}/vaccinations/`, {
      params: { page, page_size },
    })
    return resp.data
  },

  async completeVaccination(recordId: string, payload: RecordVaccinationPayload): Promise<APIResponse<VaccinationRecord>> {
    const resp = await apiClient.patch<APIResponse<VaccinationRecord>>(`/vaccinations/${recordId}/complete`, payload)
    return resp.data
  },
}
