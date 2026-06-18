import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  Bar,
  BarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { farmService, batchService } from '@/services/batchService'
import { reportService } from '@/services/reportService'
import type { Farm, Batch, BatchReport, FarmComparisonRow } from '@/types'

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
    <span className={`text-xs px-2 py-1 rounded-full font-medium ${classes[status] ?? 'bg-gray-100 text-gray-600'}`}>
      {labels[status] ?? status}
    </span>
  )
}

function fmt(n: number | null | undefined, decimals = 0): string {
  if (n == null) return '—'
  return Number(n).toLocaleString('uz-UZ', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  })
}

type Tab = 'batches' | 'trends'

export default function ReportsPage() {
  const [farms, setFarms] = useState<Farm[]>([])
  const [selectedFarmId, setSelectedFarmId] = useState<string>('')
  const [batches, setBatches] = useState<Batch[]>([])
  const [loading, setLoading] = useState(false)
  const [tab, setTab] = useState<Tab>('batches')

  // EX-12 (execution-v2): Cross-Farm and Cross-Batch Trend Reporting
  const [performance, setPerformance] = useState<BatchReport[]>([])
  const [performanceLoading, setPerformanceLoading] = useState(false)
  const [comparison, setComparison] = useState<FarmComparisonRow[]>([])
  const [comparisonLoading, setComparisonLoading] = useState(false)
  // EX-16 (execution-v2): Reports must support both ACTIVE and ARCHIVED
  // batches with archive filter support (decision_log.md BMD-018).
  const [archivedFilter, setArchivedFilter] = useState<'false' | 'true' | 'all'>('all')

  useEffect(() => {
    farmService.listFarms().then((res) => {
      setFarms(res.data)
      if (res.data.length > 0) setSelectedFarmId(res.data[0].id)
    })
  }, [])

  useEffect(() => {
    if (!selectedFarmId) return
    setLoading(true)
    batchService
      .listBatches({ farm_id: selectedFarmId, page_size: 100 })
      .then((res) => setBatches(res.data))
      .finally(() => setLoading(false))
  }, [selectedFarmId])

  useEffect(() => {
    if (tab !== 'trends' || !selectedFarmId) return
    setPerformanceLoading(true)
    reportService
      .getFarmBatchPerformance(selectedFarmId, archivedFilter)
      .then((res) => setPerformance(res.data))
      .finally(() => setPerformanceLoading(false))
  }, [tab, selectedFarmId, archivedFilter])

  useEffect(() => {
    if (tab !== 'trends' || farms.length === 0) return
    setComparisonLoading(true)
    reportService
      .getFarmComparison(farms.map((f) => f.id), archivedFilter)
      .then((res) => setComparison(res.data))
      .finally(() => setComparisonLoading(false))
  }, [tab, farms, archivedFilter])

  const chartData = performance.map((r) => ({
    label: r.batch_code ?? r.batch_id.slice(0, 8),
    mortality_rate_pct: r.mortality_rate_pct,
    latest_avg_weight_kg: r.latest_avg_weight_kg,
    adg_grams: r.adg_grams,
    total_feed_kg: r.total_feed_kg,
    fcr: r.fcr,
    total_revenue_uzs: r.total_revenue_uzs,
    gross_profit_uzs: r.gross_profit_uzs,
  }))

  const farmNameById = Object.fromEntries(farms.map((f) => [f.id, f.name]))
  const comparisonChartData = comparison
    .filter((c) => c.batch_count > 0)
    .map((c) => ({
      label: farmNameById[c.farm_id] ?? c.farm_id.slice(0, 8),
      avg_fcr: c.avg_fcr,
      avg_mortality_rate_pct: c.avg_mortality_rate_pct,
      total_profit_uzs: c.total_profit_uzs,
    }))

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Hisobotlar</h1>
        <p className="text-sm text-gray-500 mt-1">
          Partiya bo'yicha ishlash ko'rsatkichlari, tendensiyalar va PDF eksport
        </p>
      </div>

      <div className="flex items-center justify-between mb-6 flex-wrap gap-3">
        <div className="flex gap-1 bg-gray-100 p-1 rounded-lg w-fit">
          {(['batches', 'trends'] as Tab[]).map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
                tab === t ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              {t === 'batches' ? 'Partiyalar' : 'Tendensiyalar'}
            </button>
          ))}
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

      {tab === 'batches' && (
        loading ? (
          <div className="flex justify-center py-16">
            <div className="w-8 h-8 border-4 border-green-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : batches.length === 0 ? (
          <div className="text-center py-16 text-gray-400">Partiyalar topilmadi</div>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {batches.map((batch) => (
              <div key={batch.id} className="bg-white rounded-xl border border-gray-200 p-5 flex flex-col gap-3">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-semibold text-gray-900">
                      {batch.batch_code}
                    </p>
                    <p className="text-xs text-gray-400 mt-0.5 capitalize">{batch.species}</p>
                  </div>
                  {statusBadge(batch.status)}
                </div>

                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div>
                    <p className="text-xs text-gray-400">Joriy soni</p>
                    <p className="font-medium text-gray-900">{batch.current_count.toLocaleString('uz-UZ')} bosh</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-400">Omon qolish</p>
                    <p className="font-medium text-gray-900">{Number(batch.survival_rate).toFixed(1)}%</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-400">Joylashtirilgan</p>
                    <p className="font-medium text-gray-900">
                      {new Date(batch.placement_date).toLocaleDateString('uz-UZ')}
                    </p>
                  </div>
                  {batch.closed_at && (
                    <div>
                      <p className="text-xs text-gray-400">Yopilgan</p>
                      <p className="font-medium text-gray-900">
                        {new Date(batch.closed_at).toLocaleDateString('uz-UZ')}
                      </p>
                    </div>
                  )}
                </div>

                <Link
                  to={`/reports/batch/${batch.id}`}
                  className="mt-auto flex items-center justify-center gap-2 px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 transition-colors"
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                      d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  Hisobotni ko'rish
                </Link>
              </div>
            ))}
          </div>
        )
      )}

      {tab === 'trends' && (
        <div className="space-y-8">
          {/* EX-16 (execution-v2): archive filter — Reports must show
              ACTIVE and ARCHIVED batches with filter support. */}
          <div className="flex items-center gap-2">
            <span className="text-xs font-medium text-gray-500 uppercase">Arxiv filtri:</span>
            {([
              { value: 'false', label: 'Faol' },
              { value: 'true', label: 'Arxivlangan' },
              { value: 'all', label: 'Barchasi' },
            ] as { value: 'false' | 'true' | 'all'; label: string }[]).map((opt) => (
              <button
                key={opt.value}
                onClick={() => setArchivedFilter(opt.value)}
                className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                  archivedFilter === opt.value ? 'bg-green-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>

          {/* Batch performance comparison */}
          <section>
            <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-3">
              Partiyalarni solishtirish
            </h2>
            {performanceLoading ? (
              <div className="flex justify-center py-10">
                <div className="w-6 h-6 border-4 border-green-500 border-t-transparent rounded-full animate-spin" />
              </div>
            ) : performance.length === 0 ? (
              <div className="text-center py-10 text-gray-400">Ma'lumot yo'q</div>
            ) : (
              <div className="bg-white rounded-xl border border-gray-200 overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-100">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Partiya</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Holat</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">FCR</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">O'lim %</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">O'rtacha vazn (kg)</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Yem (kg)</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Daromad</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Foyda</th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Marja %</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-50">
                    {performance.map((r) => (
                      <tr key={r.batch_id} className="hover:bg-gray-50">
                        <td className="px-4 py-3 text-sm text-gray-900 whitespace-nowrap">
                          <Link to={`/reports/batch/${r.batch_id}`} className="text-green-700 hover:underline">
                            {r.batch_code ?? r.batch_id.slice(0, 8)}
                          </Link>
                        </td>
                        <td className="px-4 py-3 space-x-1">
                          {statusBadge(r.status)}
                          {r.is_archived && (
                            <span className="text-xs px-2 py-1 rounded-full font-medium bg-amber-100 text-amber-700">
                              Arxivlangan
                            </span>
                          )}
                        </td>
                        <td className="px-4 py-3 text-sm text-right text-gray-900">{fmt(r.fcr, 2)}</td>
                        <td className="px-4 py-3 text-sm text-right text-gray-900">{fmt(r.mortality_rate_pct, 2)}</td>
                        <td className="px-4 py-3 text-sm text-right text-gray-900">{fmt(r.latest_avg_weight_kg, 2)}</td>
                        <td className="px-4 py-3 text-sm text-right text-gray-900">{fmt(r.total_feed_kg)}</td>
                        <td className="px-4 py-3 text-sm text-right text-gray-900">{fmt(r.total_revenue_uzs)}</td>
                        <td className="px-4 py-3 text-sm text-right font-medium text-gray-900">{fmt(r.gross_profit_uzs)}</td>
                        <td className="px-4 py-3 text-sm text-right text-gray-900">{fmt(r.profit_margin_pct, 1)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>

          {performance.length > 0 && (
            <>
              {/* Mortality trend */}
              <section>
                <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-3">
                  O'lim tendensiyasi
                </h2>
                <div className="bg-white rounded-xl border border-gray-200 p-4">
                  <ResponsiveContainer width="100%" height={260}>
                    <LineChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="label" tick={{ fontSize: 12 }} />
                      <YAxis tick={{ fontSize: 12 }} unit="%" />
                      <Tooltip />
                      <Line type="monotone" dataKey="mortality_rate_pct" name="O'lim %" stroke="#dc2626" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </section>

              {/* Weight growth trend */}
              <section>
                <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-3">
                  Vazn o'sishi tendensiyasi
                </h2>
                <div className="bg-white rounded-xl border border-gray-200 p-4">
                  <ResponsiveContainer width="100%" height={260}>
                    <LineChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="label" tick={{ fontSize: 12 }} />
                      <YAxis tick={{ fontSize: 12 }} />
                      <Tooltip />
                      <Legend />
                      <Line type="monotone" dataKey="latest_avg_weight_kg" name="O'rtacha vazn (kg)" stroke="#16a34a" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </section>

              {/* Feed consumption trend */}
              <section>
                <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-3">
                  Yem sarfi tendensiyasi
                </h2>
                <div className="bg-white rounded-xl border border-gray-200 p-4">
                  <ResponsiveContainer width="100%" height={260}>
                    <LineChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="label" tick={{ fontSize: 12 }} />
                      <YAxis tick={{ fontSize: 12 }} />
                      <Tooltip />
                      <Legend />
                      <Line type="monotone" dataKey="total_feed_kg" name="Yem (kg)" stroke="#ca8a04" strokeWidth={2} />
                      <Line type="monotone" dataKey="fcr" name="FCR" stroke="#9333ea" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </section>

              {/* Revenue & profit trend */}
              <section>
                <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-3">
                  Daromad va foyda tendensiyasi
                </h2>
                <div className="bg-white rounded-xl border border-gray-200 p-4">
                  <ResponsiveContainer width="100%" height={260}>
                    <LineChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="label" tick={{ fontSize: 12 }} />
                      <YAxis tick={{ fontSize: 12 }} />
                      <Tooltip />
                      <Legend />
                      <Line type="monotone" dataKey="total_revenue_uzs" name="Daromad (UZS)" stroke="#2563eb" strokeWidth={2} />
                      <Line type="monotone" dataKey="gross_profit_uzs" name="Foyda (UZS)" stroke="#16a34a" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </section>
            </>
          )}

          {/* Farm-to-farm comparison */}
          <section>
            <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-3">
              Fermalarni solishtirish
            </h2>
            {comparisonLoading ? (
              <div className="flex justify-center py-10">
                <div className="w-6 h-6 border-4 border-green-500 border-t-transparent rounded-full animate-spin" />
              </div>
            ) : comparisonChartData.length === 0 ? (
              <div className="text-center py-10 text-gray-400">Ma'lumot yo'q</div>
            ) : (
              <>
                <div className="bg-white rounded-xl border border-gray-200 p-4 mb-4">
                  <ResponsiveContainer width="100%" height={260}>
                    <BarChart data={comparisonChartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="label" tick={{ fontSize: 12 }} />
                      <YAxis tick={{ fontSize: 12 }} />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="avg_fcr" name="O'rtacha FCR" fill="#9333ea" />
                      <Bar dataKey="avg_mortality_rate_pct" name="O'rtacha o'lim %" fill="#dc2626" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                <div className="bg-white rounded-xl border border-gray-200 overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-100">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Ferma</th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Partiyalar</th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">O'rtacha FCR</th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">O'rtacha o'lim %</th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Jami daromad</th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Jami foyda</th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">O'rtacha marja %</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-50">
                      {comparison.filter((c) => c.batch_count > 0).map((c) => (
                        <tr key={c.farm_id} className="hover:bg-gray-50">
                          <td className="px-4 py-3 text-sm text-gray-900">{farmNameById[c.farm_id] ?? c.farm_id}</td>
                          <td className="px-4 py-3 text-sm text-right text-gray-900">{c.batch_count}</td>
                          <td className="px-4 py-3 text-sm text-right text-gray-900">{fmt(c.avg_fcr, 2)}</td>
                          <td className="px-4 py-3 text-sm text-right text-gray-900">{fmt(c.avg_mortality_rate_pct, 2)}</td>
                          <td className="px-4 py-3 text-sm text-right text-gray-900">{fmt(c.total_revenue_uzs)}</td>
                          <td className="px-4 py-3 text-sm text-right font-medium text-gray-900">{fmt(c.total_profit_uzs)}</td>
                          <td className="px-4 py-3 text-sm text-right text-gray-900">{fmt(c.avg_profit_margin_pct, 1)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </>
            )}
          </section>
        </div>
      )}
    </div>
  )
}
