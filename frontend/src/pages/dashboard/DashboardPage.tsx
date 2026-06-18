import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { farmService, batchService } from '@/services/batchService'
import { stockService } from '@/services/inventoryService'
import { reportService } from '@/services/reportService'
import type { Farm, Batch, BatchReport, FarmComparisonRow } from '@/types'
import type { StockItemDetail } from '@/services/inventoryService'

function fmt(n: number | null | undefined, decimals = 0): string {
  if (n == null) return '—'
  return Number(n).toLocaleString('uz-UZ', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  })
}

function StatCard({
  label,
  value,
  sub,
  color,
}: {
  label: string
  value: string | number
  sub?: string
  color?: string
}) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">{label}</p>
      <p className={`text-2xl font-bold ${color ?? 'text-gray-900'}`}>{value}</p>
      {sub && <p className="text-xs text-gray-400 mt-0.5">{sub}</p>}
    </div>
  )
}

// EX-04 (execution-v2): 'quarantine'/'closed' replaced by the 2-state
// ACTIVE/COMPLETED model per decision_log.md BMD-002/BMD-003.
function statusBadge(status: string) {
  const classes: Record<string, string> = {
    active: 'bg-green-100 text-green-700',
    completed: 'bg-gray-100 text-gray-500',
  }
  const labels: Record<string, string> = {
    active: 'Faol',
    completed: 'Yakunlangan',
  }
  return (
    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${classes[status] ?? 'bg-gray-100 text-gray-600'}`}>
      {labels[status] ?? status}
    </span>
  )
}

export default function DashboardPage() {
  const [farms, setFarms] = useState<Farm[]>([])
  const [selectedFarmId, setSelectedFarmId] = useState<string>('')
  const [activeBatches, setActiveBatches] = useState<Batch[]>([])
  const [lowStockItems, setLowStockItems] = useState<StockItemDetail[]>([])
  const [loading, setLoading] = useState(false)

  // EX-14 (execution-v2): analytics — reuses EX-12's reporting aggregation,
  // per decision_log.md. Dashboard stays read-only/analytical (BMD-005);
  // full drill-down lives in the Reports section.
  const [performance, setPerformance] = useState<BatchReport[]>([])
  const [comparison, setComparison] = useState<FarmComparisonRow[]>([])

  useEffect(() => {
    farmService.listFarms().then((res) => {
      setFarms(res.data)
      if (res.data.length > 0) setSelectedFarmId(res.data[0].id)
    })
  }, [])

  useEffect(() => {
    if (!selectedFarmId) return
    setLoading(true)
    Promise.all([
      batchService.listBatches({ farm_id: selectedFarmId, status: 'active', page_size: 50 }),
      stockService.listStockItems(selectedFarmId, 1, 100),
    ])
      .then(([activeRes, stockRes]) => {
        setActiveBatches(activeRes.data)
        setLowStockItems(stockRes.data.filter((i) => i.is_below_minimum))
      })
      .finally(() => setLoading(false))
  }, [selectedFarmId])

  useEffect(() => {
    if (!selectedFarmId) return
    reportService.getFarmBatchPerformance(selectedFarmId).then((res) => setPerformance(res.data))
  }, [selectedFarmId])

  useEffect(() => {
    if (farms.length < 2) {
      setComparison([])
      return
    }
    reportService.getFarmComparison(farms.map((f) => f.id)).then((res) => setComparison(res.data))
  }, [farms])

  const totalBirdsActive = activeBatches.reduce((sum, b) => sum + b.current_count, 0)
  // EX-04 (execution-v2): quarantine removed; the "current batches" table
  // is just the active batches now. Full analytics redesign (trends,
  // multi-farm rollups) is EX-14 scope, not this mechanical status-model fix.
  const allCurrentBatches = activeBatches

  const selectedFarm = farms.find((f) => f.id === selectedFarmId)

  const trendData = performance.map((r) => ({
    label: r.batch_code ?? r.batch_id.slice(0, 8),
    fcr: r.fcr,
    mortality_rate_pct: r.mortality_rate_pct,
    gross_profit_uzs: r.gross_profit_uzs,
  }))

  const farmNameById = Object.fromEntries(farms.map((f) => [f.id, f.name]))
  const comparisonRows = comparison.filter((c) => c.batch_count > 0)

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-start justify-between flex-wrap gap-3 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Bosh sahifa</h1>
          {selectedFarm && (
            <p className="text-sm text-gray-500 mt-0.5">{selectedFarm.name}</p>
          )}
        </div>
        {farms.length > 1 && (
          <select
            value={selectedFarmId}
            onChange={(e) => setSelectedFarmId(e.target.value)}
            className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            {farms.map((f) => (
              <option key={f.id} value={f.id}>{f.name}</option>
            ))}
          </select>
        )}
      </div>

      {!selectedFarmId ? (
        <div className="text-center py-16 text-gray-400">
          Ferma topilmadi.{' '}
          <Link to="/farms" className="text-green-600 hover:underline">Ferma yarating</Link>
        </div>
      ) : loading ? (
        <div className="flex justify-center py-16">
          <div className="w-8 h-8 border-4 border-green-500 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : (
        <>
          {/* Low stock alert */}
          {lowStockItems.length > 0 && (
            <div className="mb-5 flex items-start gap-3 p-4 bg-red-50 border border-red-100 rounded-xl">
              <svg className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <div>
                <p className="text-sm font-medium text-red-700">
                  {lowStockItems.length} ta mahsulot kam — ombor to'ldirish kerak
                </p>
                <p className="text-xs text-red-500 mt-0.5">
                  {lowStockItems.map((i) => i.name).join(', ')}
                </p>
              </div>
              <Link
                to="/inventory"
                className="ml-auto text-xs text-red-600 hover:underline whitespace-nowrap"
              >
                Omborga o'tish →
              </Link>
            </div>
          )}

          {/* Stats */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
            <StatCard
              label="Faol partiyalar"
              value={activeBatches.length}
              sub="Hozirda faol"
              color="text-green-700"
            />
            <StatCard
              label="Faol parrandalar"
              value={totalBirdsActive.toLocaleString('uz-UZ')}
              sub="Faol partiyalarda"
            />
          </div>

          {/* Trend analytics — EX-14 (execution-v2), reuses EX-12's aggregation */}
          {trendData.length > 0 && (
            <div className="mb-6">
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">
                  FCR va foyda tendensiyasi
                </h2>
                <Link to="/reports" className="text-xs text-green-600 hover:underline">
                  To'liq hisobot →
                </Link>
              </div>
              <div className="bg-white rounded-xl border border-gray-200 p-4">
                <ResponsiveContainer width="100%" height={220}>
                  <LineChart data={trendData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="label" tick={{ fontSize: 12 }} />
                    <YAxis tick={{ fontSize: 12 }} />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="fcr" name="FCR" stroke="#9333ea" strokeWidth={2} />
                    <Line type="monotone" dataKey="gross_profit_uzs" name="Foyda (UZS)" stroke="#16a34a" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {/* Multi-farm KPI rollup — EX-14 (execution-v2), reuses EX-12's farm-comparison aggregation */}
          {comparisonRows.length > 0 && (
            <div className="mb-6">
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">
                  Fermalar bo'yicha xulosa
                </h2>
                <Link to="/reports" className="text-xs text-green-600 hover:underline">
                  To'liq hisobot →
                </Link>
              </div>
              <div className="bg-white rounded-xl border border-gray-200 overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-100">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Ferma</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Partiyalar</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">O'rtacha FCR</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">O'rtacha o'lim %</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Jami foyda</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-50">
                    {comparisonRows.map((c) => (
                      <tr key={c.farm_id} className="hover:bg-gray-50">
                        <td className="px-4 py-3 text-sm text-gray-900">{farmNameById[c.farm_id] ?? c.farm_id}</td>
                        <td className="px-4 py-3 text-sm text-right text-gray-900">{c.batch_count}</td>
                        <td className="px-4 py-3 text-sm text-right text-gray-900">{fmt(c.avg_fcr, 2)}</td>
                        <td className="px-4 py-3 text-sm text-right text-gray-900">{fmt(c.avg_mortality_rate_pct, 2)}</td>
                        <td className="px-4 py-3 text-sm text-right font-medium text-gray-900">{fmt(c.total_profit_uzs)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Active batches */}
          {allCurrentBatches.length === 0 ? (
            <div className="text-center py-12 bg-white rounded-xl border border-gray-200">
              <p className="text-gray-400 mb-3">Faol partiyalar yo'q</p>
              <Link
                to="/livestock/new"
                className="inline-flex items-center gap-2 px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 transition-colors"
              >
                + Yangi partiya
              </Link>
            </div>
          ) : (
            <div>
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">
                  Joriy partiyalar
                </h2>
                <Link to="/livestock" className="text-xs text-green-600 hover:underline">
                  Barchasi →
                </Link>
              </div>
              <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
                <table className="min-w-full divide-y divide-gray-100">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Partiya</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Holat</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Joriy soni</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Omon qolish</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Joylashtirilgan</th>
                      <th className="px-4 py-3" />
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-50">
                    {allCurrentBatches.map((batch) => (
                      <tr key={batch.id} className="hover:bg-gray-50">
                        <td className="px-4 py-3">
                          <p className="text-sm font-medium text-gray-900">
                            {batch.batch_code}
                          </p>
                          <p className="text-xs text-gray-400 capitalize">{batch.species}</p>
                        </td>
                        <td className="px-4 py-3">{statusBadge(batch.status)}</td>
                        <td className="px-4 py-3 text-sm text-right font-medium text-gray-900">
                          {batch.current_count.toLocaleString('uz-UZ')} bosh
                        </td>
                        <td className="px-4 py-3 text-sm text-right text-gray-700">
                          {Number(batch.survival_rate).toFixed(1)}%
                        </td>
                        <td className="px-4 py-3 text-sm text-right text-gray-500">
                          {new Date(batch.placement_date).toLocaleDateString('uz-UZ')}
                        </td>
                        <td className="px-4 py-3 text-right">
                          <Link
                            to={`/livestock/${batch.id}`}
                            className="text-xs px-3 py-1 bg-green-50 text-green-700 rounded-lg hover:bg-green-100 transition-colors"
                          >
                            Ko'rish
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Quick links */}
          <div className="mt-6 grid grid-cols-2 sm:grid-cols-3 gap-3">
            <Link
              to="/livestock/new"
              className="flex items-center gap-3 p-4 bg-white border border-gray-200 rounded-xl hover:border-green-300 hover:bg-green-50 transition-colors"
            >
              <div className="w-8 h-8 rounded-lg bg-green-100 flex items-center justify-center flex-shrink-0">
                <svg className="w-4 h-4 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
              </div>
              <span className="text-sm font-medium text-gray-700">Yangi partiya</span>
            </Link>
            <Link
              to="/inventory"
              className="flex items-center gap-3 p-4 bg-white border border-gray-200 rounded-xl hover:border-green-300 hover:bg-green-50 transition-colors"
            >
              <div className="w-8 h-8 rounded-lg bg-blue-100 flex items-center justify-center flex-shrink-0">
                <svg className="w-4 h-4 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                </svg>
              </div>
              <span className="text-sm font-medium text-gray-700">Ombor</span>
            </Link>
            <Link
              to="/finance"
              className="flex items-center gap-3 p-4 bg-white border border-gray-200 rounded-xl hover:border-green-300 hover:bg-green-50 transition-colors"
            >
              <div className="w-8 h-8 rounded-lg bg-purple-100 flex items-center justify-center flex-shrink-0">
                <svg className="w-4 h-4 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <span className="text-sm font-medium text-gray-700">Moliya</span>
            </Link>
          </div>
        </>
      )}
    </div>
  )
}
