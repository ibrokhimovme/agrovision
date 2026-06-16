import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { batchService } from '@/services/batchService'
import type { Batch, BatchCloseReason } from '@/types'

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

export default function BatchDetailPage() {
  const { id } = useParams<{ id: string }>()
  const [batch, setBatch] = useState<Batch | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [actionLoading, setActionLoading] = useState(false)
  const [actionError, setActionError] = useState<string | null>(null)
  const [showCloseModal, setShowCloseModal] = useState(false)
  const [closeReason, setCloseReason] = useState<BatchCloseReason>('sale')

  useEffect(() => {
    if (!id) return
    batchService
      .getBatch(id)
      .then((res) => setBatch(res.data))
      .catch(() => setError("Partiya topilmadi yoki xatolik yuz berdi."))
      .finally(() => setLoading(false))
  }, [id])

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
      <div className="flex gap-3">
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
