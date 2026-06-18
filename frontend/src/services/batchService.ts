import { apiClient } from './api'
import type {
  APIResponse,
  PaginatedResponse,
  Batch,
  Farm,
  Building,
  Section,
  FarmType,
  SectionType,
  BatchStatus,
  BatchCloseReason,
  PoultrySpecies,
  FeedRecord,
  FeedSummary,
  MortalityRecord,
  MortalitySummary,
  MedicationRecord,
  VaccinationRecord,
  VaccinationSchedule,
  WeightSampling,
  GrowthMetrics,
  Expense,
  BatchCostSummary,
  ExpenseCategory,
  BatchExpenseType,
  SaleRecord,
  BatchSalesSummary,
  SalePaymentStatus,
  BatchProfit,
  Supplier,
  DebtorCreditorSummary,
} from '@/types'

export interface CreateFarmPayload {
  name: string
  farm_type: FarmType
  address?: string
  region?: string
  notes?: string
}

export interface UpdateFarmPayload {
  name?: string
  farm_type?: FarmType
  address?: string
  region?: string
  notes?: string
}

export interface CreateBuildingPayload {
  name: string
  capacity?: number
  notes?: string
}

export interface CreateSectionPayload {
  name: string
  section_type: SectionType
  capacity?: number
}

export interface CreateBatchPayload {
  farm_id: string
  section_id: string
  species: PoultrySpecies
  initial_count: number
  placement_date: string
  supplier_name?: string
  chick_price_per_head?: number
  notes?: string
}

export interface UpdateBatchPayload {
  supplier_name?: string
  chick_price_per_head?: number
  notes?: string
}

export interface CloseBatchPayload {
  close_reason: BatchCloseReason
  notes?: string
}

export interface ListBatchesParams {
  farm_id: string
  status?: BatchStatus
  // EX-16 (execution-v2): 'false' (default, active views) excludes archived
  // batches; 'true' is the Archive view; 'all' is Reports' filter-supported view.
  archived?: 'true' | 'false' | 'all'
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

  async closeBatch(id: string, payload: CloseBatchPayload): Promise<APIResponse<Batch>> {
    const resp = await apiClient.post<APIResponse<Batch>>(`/batches/${id}/close`, payload)
    return resp.data
  },

  // EX-16 (execution-v2): manual-only archiving, restricted server-side to
  // Account Owner / Farm Director (decision_log.md BMD-018).
  async archiveBatch(id: string): Promise<APIResponse<Batch>> {
    const resp = await apiClient.post<APIResponse<Batch>>(`/batches/${id}/archive`, {})
    return resp.data
  },

  async unarchiveBatch(id: string): Promise<APIResponse<Batch>> {
    const resp = await apiClient.post<APIResponse<Batch>>(`/batches/${id}/unarchive`, {})
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

  async getFarm(farmId: string): Promise<APIResponse<Farm>> {
    const resp = await apiClient.get<APIResponse<Farm>>(`/farms/${farmId}`)
    return resp.data
  },

  async createFarm(payload: CreateFarmPayload): Promise<APIResponse<Farm>> {
    const resp = await apiClient.post<APIResponse<Farm>>('/farms/', payload)
    return resp.data
  },

  async updateFarm(farmId: string, payload: UpdateFarmPayload): Promise<APIResponse<Farm>> {
    const resp = await apiClient.patch<APIResponse<Farm>>(`/farms/${farmId}`, payload)
    return resp.data
  },

  async deleteFarm(farmId: string): Promise<void> {
    await apiClient.delete(`/farms/${farmId}`)
  },

  async listBuildings(farmId: string): Promise<APIResponse<Building[]>> {
    const resp = await apiClient.get<APIResponse<Building[]>>(`/farms/${farmId}/buildings`)
    return resp.data
  },

  async createBuilding(farmId: string, payload: CreateBuildingPayload): Promise<APIResponse<Building>> {
    const resp = await apiClient.post<APIResponse<Building>>(`/farms/${farmId}/buildings`, payload)
    return resp.data
  },

  async listSections(buildingId: string): Promise<APIResponse<Section[]>> {
    const resp = await apiClient.get<APIResponse<Section[]>>(`/buildings/${buildingId}/sections`)
    return resp.data
  },

  async createSection(buildingId: string, payload: CreateSectionPayload): Promise<APIResponse<Section>> {
    const resp = await apiClient.post<APIResponse<Section>>(`/buildings/${buildingId}/sections`, payload)
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

export interface RecordMedicationPayload {
  farm_id: string
  medicine_name: string
  medicine_inventory_item_id: string
  quantity_used: number
  unit: string
  reason?: string
  dosage_notes?: string
  administered_at?: string
  notes?: string
}

export const medicationService = {
  async recordMedication(batchId: string, payload: RecordMedicationPayload): Promise<APIResponse<MedicationRecord>> {
    const resp = await apiClient.post<APIResponse<MedicationRecord>>(`/batches/${batchId}/medication`, payload)
    return resp.data
  },

  async listMedication(batchId: string, page = 1, page_size = 20): Promise<PaginatedResponse<MedicationRecord>> {
    const resp = await apiClient.get<PaginatedResponse<MedicationRecord>>(`/batches/${batchId}/medication`, {
      params: { page, page_size },
    })
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

export interface RecordWeightPayload {
  farm_id: string
  sample_size: number
  total_sample_weight_kg: number
  notes?: string
}

export const weightService = {
  async recordWeight(batchId: string, payload: RecordWeightPayload): Promise<APIResponse<WeightSampling>> {
    const resp = await apiClient.post<APIResponse<WeightSampling>>(`/batches/${batchId}/weight/`, payload)
    return resp.data
  },

  async listWeight(batchId: string, page = 1, page_size = 20): Promise<PaginatedResponse<WeightSampling>> {
    const resp = await apiClient.get<PaginatedResponse<WeightSampling>>(`/batches/${batchId}/weight/`, {
      params: { page, page_size },
    })
    return resp.data
  },

  async getMetrics(batchId: string): Promise<APIResponse<GrowthMetrics>> {
    const resp = await apiClient.get<APIResponse<GrowthMetrics>>(`/batches/${batchId}/weight/metrics`)
    return resp.data
  },
}

export interface RecordExpensePayload {
  farm_id: string
  batch_id?: string
  category: ExpenseCategory
  expense_type?: BatchExpenseType
  description: string
  amount: number
  currency?: string
  // EX-11 (execution-v2): supplier debt / partial-payment tracking.
  supplier_id?: string
  amount_paid?: number
  notes?: string
}

export const expenseService = {
  async recordExpense(payload: RecordExpensePayload): Promise<APIResponse<Expense>> {
    const resp = await apiClient.post<APIResponse<Expense>>('/expenses/', payload)
    return resp.data
  },

  async listBatchExpenses(batchId: string, page = 1, page_size = 20): Promise<PaginatedResponse<Expense>> {
    const resp = await apiClient.get<PaginatedResponse<Expense>>(`/expenses/batch/${batchId}`, {
      params: { page, page_size },
    })
    return resp.data
  },

  async getBatchCostSummary(batchId: string): Promise<APIResponse<BatchCostSummary>> {
    const resp = await apiClient.get<APIResponse<BatchCostSummary>>(`/expenses/batch/${batchId}/cost-summary`)
    return resp.data
  },

  async recordExpensePayment(expenseId: string, amount: number): Promise<APIResponse<Expense>> {
    const resp = await apiClient.patch<APIResponse<Expense>>(`/expenses/${expenseId}/payment`, { amount })
    return resp.data
  },
}

export interface RecordSalePayload {
  farm_id: string
  customer_name: string
  customer_phone?: string
  head_count: number
  quantity_kg: number
  price_per_kg_uzs: number
  payment_status?: SalePaymentStatus
  // EX-11 (execution-v2): exact amount paid, for partial-payment tracking.
  amount_paid?: number
  notes?: string
}

export const saleService = {
  async recordSale(batchId: string, payload: RecordSalePayload): Promise<APIResponse<SaleRecord>> {
    const resp = await apiClient.post<APIResponse<SaleRecord>>(`/sales/batch/${batchId}`, payload)
    return resp.data
  },

  async listSales(batchId: string, page = 1, page_size = 20): Promise<PaginatedResponse<SaleRecord>> {
    const resp = await apiClient.get<PaginatedResponse<SaleRecord>>(`/sales/batch/${batchId}`, {
      params: { page, page_size },
    })
    return resp.data
  },

  async getSalesSummary(batchId: string): Promise<APIResponse<BatchSalesSummary>> {
    const resp = await apiClient.get<APIResponse<BatchSalesSummary>>(`/sales/batch/${batchId}/summary`)
    return resp.data
  },

  async recordSalePayment(saleId: string, amount: number): Promise<APIResponse<SaleRecord>> {
    const resp = await apiClient.patch<APIResponse<SaleRecord>>(`/sales/${saleId}/payment`, { amount })
    return resp.data
  },
}

export const profitService = {
  async getBatchProfit(batchId: string): Promise<APIResponse<BatchProfit>> {
    const resp = await apiClient.get<APIResponse<BatchProfit>>(`/profit/batch/${batchId}`)
    return resp.data
  },
}

export interface CreateSupplierPayload {
  farm_id: string
  name: string
  phone?: string
  address?: string
}

export const supplierService = {
  async createSupplier(payload: CreateSupplierPayload): Promise<APIResponse<Supplier>> {
    const resp = await apiClient.post<APIResponse<Supplier>>('/suppliers/', payload)
    return resp.data
  },

  async listSuppliers(farmId: string): Promise<APIResponse<Supplier[]>> {
    const resp = await apiClient.get<APIResponse<Supplier[]>>('/suppliers/', { params: { farm_id: farmId } })
    return resp.data
  },
}

export const debtService = {
  async getDebtorCreditorSummary(farmId: string): Promise<APIResponse<DebtorCreditorSummary>> {
    const resp = await apiClient.get<APIResponse<DebtorCreditorSummary>>('/debtors-creditors-summary', {
      params: { farm_id: farmId },
    })
    return resp.data
  },
}
