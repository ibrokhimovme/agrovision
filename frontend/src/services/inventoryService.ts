import { apiClient } from './api'
import type { APIResponse, PaginatedResponse, ItemType } from '@/types'

export interface Warehouse {
  id: string
  farm_id: string
  name: string
  location?: string
  is_active: boolean
  notes?: string
  created_at: string
}

export interface StockItemDetail {
  id: string
  warehouse_id: string
  name: string
  item_type: ItemType
  unit: string
  current_quantity: number
  minimum_quantity: number
  unit_cost?: number
  sku?: string
  is_active: boolean
  is_below_minimum: boolean
  created_at: string
}

export interface StockBatch {
  id: string
  stock_item_id: string
  batch_number?: string
  quantity: number
  remaining_quantity: number
  unit_cost?: number
  received_at: string
  expiry_date?: string
  is_expired: boolean
}

export interface StockMovement {
  id: string
  stock_item_id: string
  warehouse_id: string
  movement_type: 'receipt' | 'dispatch' | 'transfer' | 'adjustment' | 'write_off'
  quantity: number
  unit: string
  unit_cost?: number
  purpose?: string
  reference_id?: string
  reference_type?: string
  notes?: string
  moved_at: string
  created_at: string
}

export interface CreateWarehousePayload {
  farm_id: string
  name: string
  location?: string
  notes?: string
}

export interface CreateStockItemPayload {
  warehouse_id: string
  name: string
  item_type: ItemType
  unit: string
  minimum_quantity?: number
  unit_cost?: number
  sku?: string
}

export interface ReceiveStockPayload {
  quantity: number
  unit_cost?: number
  batch_number?: string
  expiry_date?: string
  notes?: string
}

export interface DispatchStockPayload {
  quantity: number
  purpose?: string
  reference_id?: string
  reference_type?: string
  notes?: string
  use_fefo?: boolean
}

export const warehouseService = {
  async createWarehouse(payload: CreateWarehousePayload): Promise<APIResponse<Warehouse>> {
    const resp = await apiClient.post<APIResponse<Warehouse>>('/warehouses/', payload)
    return resp.data
  },

  async listWarehouses(farmId: string): Promise<APIResponse<Warehouse[]>> {
    const resp = await apiClient.get<APIResponse<Warehouse[]>>('/warehouses/', {
      params: { farm_id: farmId },
    })
    return resp.data
  },
}

export const stockService = {
  async createStockItem(payload: CreateStockItemPayload): Promise<APIResponse<StockItemDetail>> {
    const resp = await apiClient.post<APIResponse<StockItemDetail>>('/stock-items/', payload)
    return resp.data
  },

  async listStockItems(farmId: string, page = 1, page_size = 50): Promise<PaginatedResponse<StockItemDetail>> {
    const resp = await apiClient.get<PaginatedResponse<StockItemDetail>>('/stock-items/', {
      params: { farm_id: farmId, page, page_size },
    })
    return resp.data
  },

  async receiveStock(itemId: string, payload: ReceiveStockPayload): Promise<APIResponse<StockBatch>> {
    const resp = await apiClient.post<APIResponse<StockBatch>>(`/stock-items/${itemId}/receive`, payload)
    return resp.data
  },

  async dispatchStock(itemId: string, payload: DispatchStockPayload): Promise<APIResponse<{ dispatched_quantity: number; remaining_stock: number }>> {
    const resp = await apiClient.post<APIResponse<{ dispatched_quantity: number; remaining_stock: number }>>(`/stock-items/${itemId}/dispatch`, payload)
    return resp.data
  },

  async listMovements(itemId: string, page = 1, page_size = 20): Promise<PaginatedResponse<StockMovement>> {
    const resp = await apiClient.get<PaginatedResponse<StockMovement>>(`/stock-items/${itemId}/movements`, {
      params: { page, page_size },
    })
    return resp.data
  },
}
