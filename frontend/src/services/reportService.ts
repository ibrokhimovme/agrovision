import { apiClient } from './api'
import type { APIResponse } from '@/types'
import type { BatchReport, FarmComparisonRow } from '@/types'

export const reportService = {
  async getBatchReport(batchId: string): Promise<APIResponse<BatchReport>> {
    const resp = await apiClient.get<APIResponse<BatchReport>>(`/reports/batch/${batchId}`)
    return resp.data
  },

  getBatchReportPdfUrl(batchId: string): string {
    const base = (import.meta.env.VITE_API_BASE_URL ?? '/api/v1') as string
    return `${base}/reports/batch/${batchId}/pdf`
  },

  // EX-12 (execution-v2): Cross-Farm and Cross-Batch Trend Reporting.
  // EX-16 (execution-v2): archived defaults to 'false' (matches Dashboard's
  // reuse of this same call); ReportsPage explicitly passes 'all' to satisfy
  // "Reports must support both ACTIVE and ARCHIVED batches with archive filter support".
  async getFarmBatchPerformance(
    farmId: string,
    archived: 'true' | 'false' | 'all' = 'false'
  ): Promise<APIResponse<BatchReport[]>> {
    const resp = await apiClient.get<APIResponse<BatchReport[]>>(`/reports/farms/${farmId}/batch-performance`, {
      params: { archived },
    })
    return resp.data
  },

  async getFarmComparison(
    farmIds: string[],
    archived: 'true' | 'false' | 'all' = 'false'
  ): Promise<APIResponse<FarmComparisonRow[]>> {
    const resp = await apiClient.get<APIResponse<FarmComparisonRow[]>>('/reports/farm-comparison', {
      params: { farm_ids: farmIds.join(','), archived },
    })
    return resp.data
  },
}
