import { apiClient } from './api'
import type { APIResponse } from '@/types'
import type { BatchReport } from '@/types'

export const reportService = {
  async getBatchReport(batchId: string): Promise<APIResponse<BatchReport>> {
    const resp = await apiClient.get<APIResponse<BatchReport>>(`/reports/batch/${batchId}`)
    return resp.data
  },

  getBatchReportPdfUrl(batchId: string): string {
    const base = (import.meta.env.VITE_API_BASE_URL ?? '/api/v1') as string
    return `${base}/reports/batch/${batchId}/pdf`
  },
}
