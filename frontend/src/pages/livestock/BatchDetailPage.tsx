import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { batchService, feedService } from '@/services/batchService'
import type { Batch, BatchCloseReason, FeedRecord, FeedSummary } from '@/types'

const STATUS_LABELS: Record<string, string> = {
  quarantine: 'Karantin',
  active: 'Faol',
  closed: 'Yopilgan',
}

const STATUS_BADGE_CLASSES: Record<string, string> = {
  quarantine: 'bg-yellow-100 text-yellow-800',
  active: 'bg-green-100 text-green-800',
  closed: 'bg-gray-100 text-gray-700',
}

const SPECIES_LABELS: Record<string, string> = {
  broiler: 'Broiler',
  layer: 'Tuxumchi',
}

const CLOSE_REASON_LABELS: Record<string, string> = {
  sale: "Sotish",
  slaughter: "So'yish",
  transfer: "Ko'chirish",
  disease: "Kasallik",
  other: "Boshqa",
}

const CLOSE_REASONS: BatchCloseReason[] = ['sale', 'slaughter', 'transfer', 'disease', 'other']

const today = () => new Date().toISOString().slice(0, 10)

export default function BatchDetailPage() {
  const { id } = useParams<{ id: string }>()
  const [batch, setBatch] = useState<Batch | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [actionLoading, setActionLoading] = useState(false)
  const [actionError, setActionError] = useState<string | null>(null)
  const [showCloseModal, setShowCloseModal] = useState(false)
  const [closeReason, setCloseReason] = useState<BatchCloseReason>('sale')

  // Feed state
  const [feedRecords, setFeedRecords] = useState<FeedRecord[]>([])
  const [feedSummary, setFeedSummary] = useState<FeedSummary | null>(null)
  const [feedLoading, setFeedLoading] = useState(false)
  const [feedError, setFeedError] = useState<string | null>(null)
  const [feedDate, setFeedDate] = useState(today())
  const [feedQty, setFeedQty] = useState('')
  const [waterQty, setWaterQty] = useState('')
  const [feedType, setFeedType] = useState('')

  useEffect(() => {
    if (!id) return
    batchService
      .getBatch(id)
      .then((res) => setBatch(res.data))
      .catch(() => setError("Partiya topilmadi yoki xatolik yuz berdi."))
      .finally(() => setLoading(false))
  }, [id])

  const loadFeedData = (batchId: string) => {
    feedService.listFeed(batchId, 1, 20).then((res) => setFeedRecords(res.data)).catch(() => {})
    feedService.getFeedSummary(batchId).then((res) => setFeedSummary(res.data)).catch(() => {})
  }

  useEffect(() => {
    if (id && batch?.status === 'active') loadFeedData(id)
  }, [id, batch?.status])

  const handleRecordFeed = async () => {
    if (!id || !batch || !feedQty) return
    setFeedLoading(true)
    setFeedError(null)
    try {
      await feedService.recordFeed(id, {
        farm_id: batch.farm_id,
        feed_date: feedDate,
        quantity_kg: parseFloat(feedQty),
        water_liters: waterQty ? parseFloat(waterQty) : undefined,
        feed_type: feedType || undefined,
      })
      setFeedQty('')
      setWaterQty('')
      setFeedType('')
      setFeedDate(today())
      loadFeedData(id)
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { message?: string } } }
      setFeedError(axiosError?.response?.data?.message ?? "Xatolik yuz berdi")
    } finally {
      setFeedLoading(false)
    }
  }

  const handleActivate = async () => {
    if (!id || !batch) return
    setActionLoading(true)
    setActionError(null)
    try {
      const res = await batchService.activateBatch(id)
      setBatch(res.data)
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { message?: string } } }
      setActionError(axiosError?.response?.data?.message ?? "Faollashtirish muvaffaqiyatsiz")
    } finally {
      setActionLoading(false)
    }
  }

  const handleClose = async () => {
    if (!id || !batch) return
    setActionLoading(true)
    setActionError(null)
    try {
      const res = await batchService.closeBatch(id, { close_reason: closeReason })
      setBatch(res.data)
      setShowCloseModal(false)
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { message?: string } } }
      setActionError(axiosError?.response?.data?.message ?? "Yopish muvaffaqiyatsiz")
    } finally {
      setActionLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center py-20">
        <div className="animate-spin rounded-full border-2 border-gray-200 border-t-green-600 h-8 w-8" />
      </div>
    )
  }

  if (error || !batch) {
    return (
      <div className="p-6 text-center text-red-600">
        <p>{error ?? "Partiya topilmadi"}</p>
        <Link to="/livestock" className="text-green-600 mt-3 inline-block hover:underline">
          ← Orqaga
        </Link>
      </div>
    )
  }

  return (
    <div className="p-6 max-w-3xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <Link to="/livestock" className="text-gray-500 hover:text-gray-700">
          ← Orqaga
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Partiya {batch.batch_code ?? batch.id.slice(0, 8)}
          </h1>
          <span
            className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${STATUS_BADGE_CLASSES[batch.status]}`}
          >
            {STATUS_LABELS[batch.status]}
          </span>
        </div>
      </div>

      {actionError && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-red-700 text-sm mb-4">
          {actionError}
        </div>
      )}

      {/* Info cards */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <InfoCard label="Tur" value={SPECIES_LABELS[batch.species] ?? batch.species} />
        <InfoCard label="Boshlang'ich soni" value={batch.initial_count.toLocaleString()} />
        <InfoCard label="Hozirgi soni" value={batch.current_count.toLocaleString()} />
        <InfoCard label="Jami nobud" value={batch.total_mortality.toLocaleString()} />
        <InfoCard label="Omon qolish darajasi" value={`${Number(batch.survival_rate).toFixed(2)}%`} />
        <InfoCard
          label="Joylashgan sana"
          value={new Date(batch.placement_date).toLocaleDateString('uz-UZ')}
        />
        {batch.quarantine_end_date && (
          <InfoCard
            label="Karantin tugash sanasi"
            value={new Date(batch.quarantine_end_date).toLocaleDateString('uz-UZ')}
          />
        )}
        {batch.supplier_name && (
          <InfoCard label="Ta'minotchi" value={batch.supplier_name} />
        )}
        {batch.chick_price_per_head != null && (
          <InfoCard
            label="Jo'ja narxi"
            value={`${Number(batch.chick_price_per_head).toLocaleString()} so'm`}
          />
        )}
        {batch.closed_at && (
          <InfoCard
            label="Yopilgan sana"
            value={new Date(batch.closed_at).toLocaleDateString('uz-UZ')}
          />
        )}
        {batch.close_reason && (
          <InfoCard
            label="Yopilish sababi"
            value={CLOSE_REASON_LABELS[batch.close_reason] ?? batch.close_reason}
          />
        )}
        {batch.notes && (
          <div className="col-span-2 bg-gray-50 rounded-xl p-4 border border-gray-100">
            <p className="text-xs text-gray-500 mb-1">Izoh</p>
            <p className="text-gray-700 text-sm">{batch.notes}</p>
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="flex gap-3 mb-6">
        {batch.status === 'quarantine' && (
          <button
            onClick={handleActivate}
            disabled={actionLoading}
            className="px-5 py-2.5 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors"
          >
            {actionLoading ? 'Kutilmoqda...' : 'Faollashtirish'}
          </button>
        )}
        {batch.status === 'active' && (
          <button
            onClick={() => setShowCloseModal(true)}
            disabled={actionLoading}
            className="px-5 py-2.5 bg-red-600 text-white text-sm font-medium rounded-lg hover:bg-red-700 disabled:opacity-50 transition-colors"
          >
            Yopish
          </button>
        )}
      </div>

      {/* Feed Consumption Section */}
      {batch.status === 'active' && (
        <div className="space-y-6">
          {/* Feed summary */}
          {feedSummary && feedSummary.record_count > 0 && (
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <SummaryCard label="Jami yem (kg)" value={Number(feedSummary.total_feed_kg).toFixed(1)} />
              {feedSummary.total_water_liters != null && (
                <SummaryCard label="Jami suv (L)" value={Number(feedSummary.total_water_liters).toFixed(0)} />
              )}
              <SummaryCard label="Kunlar soni" value={String(feedSummary.record_count)} />
              {feedSummary.fcr != null && (
                <SummaryCard label="FCR" value={Number(feedSummary.fcr).toFixed(3)} />
              )}
            </div>
          )}

          {/* Record feed form */}
          <div className="bg-white border border-gray-200 rounded-2xl p-5">
            <h2 className="text-base font-semibold text-gray-900 mb-4">Kunlik ozuqlantirish</h2>
            {feedError && (
              <div className="text-red-600 text-sm mb-3 bg-red-50 border border-red-100 rounded-lg px-3 py-2">
                {feedError}
              </div>
            )}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-3">
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Sana</label>
                <input
                  type="date"
                  value={feedDate}
                  onChange={(e) => setFeedDate(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Yem miqdori (kg) *</label>
                <input
                  type="number"
                  min="0"
                  step="0.1"
                  placeholder="masalan: 150.5"
                  value={feedQty}
                  onChange={(e) => setFeedQty(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Suv iste'moli (litr)</label>
                <input
                  type="number"
                  min="0"
                  step="1"
                  placeholder="masalan: 300"
                  value={waterQty}
                  onChange={(e) => setWaterQty(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Yem turi</label>
                <input
                  type="text"
                  placeholder="masalan: starter, grower"
                  value={feedType}
                  onChange={(e) => setFeedType(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                />
              </div>
            </div>
            <button
              onClick={handleRecordFeed}
              disabled={feedLoading || !feedQty}
              className="px-5 py-2.5 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors"
            >
              {feedLoading ? 'Saqlanmoqda...' : 'Saqlash'}
            </button>
          </div>

          {/* Feed history */}
          {feedRecords.length > 0 && (
            <div className="bg-white border border-gray-200 rounded-2xl overflow-hidden">
              <div className="px-5 py-3 border-b border-gray-100">
                <h2 className="text-base font-semibold text-gray-900">Ozuqlantirish tarixi</h2>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50 text-xs text-gray-500 uppercase">
                    <tr>
                      <th className="px-4 py-3 text-left">Sana</th>
                      <th className="px-4 py-3 text-right">Yem (kg)</th>
                      <th className="px-4 py-3 text-right">Suv (L)</th>
                      <th className="px-4 py-3 text-left">Tur</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {feedRecords.map((r) => (
                      <tr key={r.id} className="hover:bg-gray-50">
                        <td className="px-4 py-3 text-gray-700">{r.feed_date}</td>
                        <td className="px-4 py-3 text-right font-medium text-gray-900">
                          {Number(r.quantity_kg).toFixed(1)}
                        </td>
                        <td className="px-4 py-3 text-right text-gray-600">
                          {r.water_liters != null ? Number(r.water_liters).toFixed(0) : '—'}
                        </td>
                        <td className="px-4 py-3 text-gray-600">{r.feed_type ?? '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Close modal */}
      {showCloseModal && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-6 w-full max-w-sm shadow-xl">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Partiyani yopish</h2>
            <label className="block text-sm font-medium text-gray-700 mb-2">Yopilish sababi</label>
            <select
              value={closeReason}
              onChange={(e) => setCloseReason(e.target.value as BatchCloseReason)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm mb-4 focus:outline-none focus:ring-2 focus:ring-red-500"
            >
              {CLOSE_REASONS.map((r) => (
                <option key={r} value={r}>
                  {CLOSE_REASON_LABELS[r]}
                </option>
              ))}
            </select>
            <div className="flex gap-3">
              <button
                onClick={handleClose}
                disabled={actionLoading}
                className="flex-1 py-2.5 bg-red-600 text-white text-sm font-medium rounded-lg hover:bg-red-700 disabled:opacity-50"
              >
                {actionLoading ? 'Yopilmoqda...' : 'Tasdiqlash'}
              </button>
              <button
                onClick={() => setShowCloseModal(false)}
                className="flex-1 py-2.5 border border-gray-300 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50"
              >
                Bekor qilish
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function InfoCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-gray-50 rounded-xl p-4 border border-gray-100">
      <p className="text-xs text-gray-500 mb-1">{label}</p>
      <p className="text-gray-900 font-medium text-sm">{value}</p>
    </div>
  )
}

function SummaryCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-green-50 rounded-xl p-4 border border-green-100">
      <p className="text-xs text-green-600 mb-1">{label}</p>
      <p className="text-green-900 font-semibold text-lg">{value}</p>
    </div>
  )
}
