import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { reportService } from '@/services/reportService'
import type { BatchReport } from '@/types'

function Metric({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div className="bg-white rounded-xl border border-gray-100 p-4 shadow-sm">
      <p className="text-xs text-gray-500 mb-1">{label}</p>
      <p className="text-lg font-semibold text-gray-900">{value}</p>
      {sub && <p className="text-xs text-gray-400 mt-0.5">{sub}</p>}
    </div>
  )
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="mb-6">
      <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-3">{title}</h2>
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">{children}</div>
    </div>
  )
}

function fmt(val: number | null | undefined, decimals = 2, suffix = ''): string {
  if (val == null) return '—'
  return `${Number(val).toLocaleString('uz-UZ', { minimumFractionDigits: decimals, maximumFractionDigits: decimals })}${suffix}`
}

function fmtInt(val: number | null | undefined): string {
  if (val == null) return '—'
  return Number(val).toLocaleString('uz-UZ')
}

export default function BatchReportPage() {
  const { id } = useParams<{ id: string }>()
  const [report, setReport] = useState<BatchReport | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!id) return
    reportService.getBatchReport(id)
      .then((res) => setReport(res.data))
      .catch(() => setError('Hisobot yuklanmadi. Partiya mavjud emas yoki xatolik yuz berdi.'))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="w-8 h-8 border-4 border-green-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  if (error || !report) {
    return (
      <div className="max-w-lg mx-auto mt-16 text-center">
        <p className="text-red-500 mb-4">{error}</p>
        <Link to="/livestock" className="text-green-600 hover:underline text-sm">← Partiyalar ro'yxatiga</Link>
      </div>
    )
  }

  const code = report.batch_code ?? report.batch_id.slice(0, 8)
  const pdfUrl = reportService.getBatchReportPdfUrl(report.batch_id)
  const profit = report.gross_profit_uzs ?? 0
  const profitColor = profit >= 0 ? 'text-green-700' : 'text-red-600'

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Page header */}
      <div className="flex items-start justify-between flex-wrap gap-3">
        <div>
          <Link to={`/livestock/${report.batch_id}`} className="text-sm text-gray-400 hover:text-green-600 flex items-center gap-1 mb-1">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Partiya sahifasiga qaytish
          </Link>
          <h1 className="text-xl font-bold text-gray-900">Partiya hisoboti — {code}</h1>
          <p className="text-sm text-gray-500 mt-0.5">
            {report.species.toUpperCase()} · {report.status} · Yaratildi: {new Date(report.generated_at).toLocaleString('uz-UZ')}
          </p>
        </div>
        <a
          href={pdfUrl}
          target="_blank"
          rel="noreferrer"
          className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 transition-colors"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          PDF yuklab olish
        </a>
      </div>

      {/* Batch info */}
      <Section title="Umumiy ma'lumot">
        <Metric label="Boshlang'ich soni" value={fmtInt(report.initial_count) + ' bosh'} />
        <Metric label="Joriy soni" value={fmtInt(report.current_count) + ' bosh'} />
        <Metric label="Joylashtirilgan sana" value={report.placement_date} />
        <Metric label="Yosh" value={report.age_days != null ? `${report.age_days} kun` : '—'} />
      </Section>

      {/* Growth */}
      <Section title="O'sish ko'rsatkichlari">
        <Metric label="FCR" value={fmt(report.fcr, 3)} sub="Yem konversiya" />
        <Metric label="ADG" value={fmt(report.adg_grams, 1, ' g/kun')} sub="Kunlik o'sish" />
        <Metric label="O'rtacha vazn" value={fmt(report.latest_avg_weight_kg, 3, ' kg')} />
        <Metric label="Jami yem" value={fmt(report.total_feed_kg, 1, ' kg')} />
        <Metric label="Jami suv" value={fmt(report.total_water_liters, 1, ' L')} />
      </Section>

      {/* Mortality */}
      <Section title="O'lim ko'rsatkichlari">
        <Metric label="Nobud bo'lganlar" value={fmtInt(report.total_deaths) + ' bosh'} />
        <Metric label="O'lim darajasi" value={fmt(report.mortality_rate_pct, 2, '%')} />
        <Metric label="Omon qolish" value={fmt(report.survival_rate_pct, 2, '%')} />
      </Section>

      {/* Financial */}
      <div className="mb-6">
        <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-3">Moliyaviy ko'rsatkichlar</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
          <Metric label="Jami xarajat" value={fmt(report.total_cost_uzs, 0, ' UZS')} />
          <Metric label="Jami daromad" value={fmt(report.total_revenue_uzs, 0, ' UZS')} />
          <div className="bg-white rounded-xl border border-gray-100 p-4 shadow-sm">
            <p className="text-xs text-gray-500 mb-1">Sof foyda</p>
            <p className={`text-lg font-semibold ${profitColor}`}>{fmt(report.gross_profit_uzs, 0, ' UZS')}</p>
          </div>
          <div className="bg-white rounded-xl border border-gray-100 p-4 shadow-sm">
            <p className="text-xs text-gray-500 mb-1">Foyda marjasi</p>
            <p className={`text-lg font-semibold ${profitColor}`}>{fmt(report.profit_margin_pct, 2, '%')}</p>
          </div>
          <Metric label="Sotuvlar soni" value={fmtInt(report.sale_count)} />
          <Metric label="Xarajatlar soni" value={fmtInt(report.expense_count)} />
        </div>
      </div>
    </div>
  )
}
