import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { batchService, farmService } from '@/services/batchService'
import { useAuthStore } from '@/store'
import { useToastStore } from '@/components/ui/Toast'
import type { Batch, BatchStatus, Farm } from '@/types'

// EX-16 (execution-v2): archive/un-archive authority — Account Owner and
// Farm Director per decision_log.md BMD-018; maps onto the existing
// `farm_owner` role (no separate roles exist for those exact titles, and
// adding them would be RBAC redesign, out of scope per EX-15), same
// convention as the backend's `_can_archive` in batches.py.
function canArchive(roles: string[]): boolean {
  return roles.includes('super_admin') || roles.includes('farm_owner')
}

// EX-04 (execution-v2): 'quarantine'/'closed' replaced by the 2-state
// ACTIVE/COMPLETED model per decision_log.md BMD-002/BMD-003.
const STATUS_LABELS: Record<BatchStatus, string> = {
  active: 'Faol',
  completed: 'Yakunlangan',
}

const STATUS_BADGE_CLASSES: Record<BatchStatus, string> = {
  active: 'bg-green-100 text-green-800',
  completed: 'bg-gray-100 text-gray-700',
}

const SPECIES_LABELS: Record<string, string> = {
  broiler: 'Broiler',
  layer: 'Tuxumchi',
}

type StatusFilter = BatchStatus | 'all'
type ArchiveTab = 'current' | 'archive'

const DEFAULT_FARM_ID = '11111111-1111-1111-1111-111111111111'

export default function BatchListPage() {
  const currentUser = useAuthStore((s) => s.user)
  const showToast = useToastStore((s) => s.show)
  const allowedToArchive = canArchive(currentUser?.roles ?? [])

  const [batches, setBatches] = useState<Batch[]>([])
  const [farms, setFarms] = useState<Farm[]>([])
  const [selectedFarmId, setSelectedFarmId] = useState<string>(DEFAULT_FARM_ID)
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all')
  // EX-16 (execution-v2): "Joriy" (current, non-archived) vs "Arxiv" tab.
  const [archiveTab, setArchiveTab] = useState<ArchiveTab>('current')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [total, setTotal] = useState(0)
  const [actioningId, setActioningId] = useState<string | null>(null)

  useEffect(() => {
    farmService
      .listFarms()
      .then((res) => {
        setFarms(res.data)
        if (res.data.length > 0) {
          setSelectedFarmId(res.data[0].id)
        }
      })
      .catch(() => {
        // keep default farm id
      })
  }, [])

  const load = () => {
    if (!selectedFarmId) return
    setLoading(true)
    setError(null)
    batchService
      .listBatches({
        farm_id: selectedFarmId,
        status: statusFilter !== 'all' ? statusFilter : undefined,
        archived: archiveTab === 'archive' ? 'true' : 'false',
        page: 1,
        page_size: 50,
      })
      .then((res) => {
        setBatches(res.data)
        setTotal(res.pagination.total_items)
      })
      .catch(() => setError("Ma'lumotlarni yuklashda xatolik yuz berdi."))
      .finally(() => setLoading(false))
  }

  useEffect(load, [selectedFarmId, statusFilter, archiveTab]) // eslint-disable-line react-hooks/exhaustive-deps

  const handleArchive = async (batch: Batch) => {
    setActioningId(batch.id)
    try {
      await batchService.archiveBatch(batch.id)
      showToast('success', 'Partiya arxivlandi')
      load()
    } catch {
      showToast('error', 'Arxivlashda xatolik yuz berdi')
    } finally {
      setActioningId(null)
    }
  }

  const handleUnarchive = async (batch: Batch) => {
    setActioningId(batch.id)
    try {
      await batchService.unarchiveBatch(batch.id)
      showToast('success', 'Partiya arxivdan chiqarildi')
      load()
    } catch {
      showToast('error', 'Arxivdan chiqarishda xatolik yuz berdi')
    } finally {
      setActioningId(null)
    }
  }

  const statusOptions: { value: StatusFilter; label: string }[] = [
    { value: 'all', label: 'Barchasi' },
    { value: 'active', label: 'Faol' },
    { value: 'completed', label: 'Yakunlangan' },
  ]

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Partiyalar</h1>
          <p className="text-sm text-gray-500 mt-1">Jami: {total} ta partiya</p>
        </div>
        <Link
          to="/livestock/new"
          className="inline-flex items-center px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 transition-colors"
        >
          + Yangi partiya
        </Link>
      </div>

      {/* Joriy / Arxiv tabs — EX-16 (execution-v2) */}
      <div className="flex gap-1 mb-4 bg-gray-100 p-1 rounded-lg w-fit">
        {([
          { value: 'current', label: 'Joriy' },
          { value: 'archive', label: 'Arxiv' },
        ] as { value: ArchiveTab; label: string }[]).map((t) => (
          <button
            key={t.value}
            onClick={() => setArchiveTab(t.value)}
            className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
              archiveTab === t.value ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 mb-4">
        {farms.length > 0 && (
          <select
            value={selectedFarmId}
            onChange={(e) => setSelectedFarmId(e.target.value)}
            className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            {farms.map((f) => (
              <option key={f.id} value={f.id}>
                {f.name}
              </option>
            ))}
          </select>
        )}
        <div className="flex gap-2">
          {statusOptions.map((opt) => (
            <button
              key={opt.value}
              onClick={() => setStatusFilter(opt.value)}
              className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                statusFilter === opt.value
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      {loading ? (
        <div className="flex justify-center items-center py-20">
          <div className="animate-spin rounded-full border-2 border-gray-200 border-t-green-600 h-8 w-8" />
        </div>
      ) : error ? (
        <div className="text-red-600 text-center py-10">{error}</div>
      ) : batches.length === 0 ? (
        <div className="text-center py-20 text-gray-400">
          <p className="text-lg">Partiyalar topilmadi</p>
          <p className="text-sm mt-1">Yangi partiya qo'shing</p>
        </div>
      ) : (
        <div className="overflow-x-auto rounded-xl border border-gray-200">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 text-left text-gray-600">
                <th className="px-4 py-3 font-medium">Kod</th>
                <th className="px-4 py-3 font-medium">Tur</th>
                <th className="px-4 py-3 font-medium">Holat</th>
                <th className="px-4 py-3 font-medium">Boshlang'ich soni</th>
                <th className="px-4 py-3 font-medium">Hozirgi soni</th>
                <th className="px-4 py-3 font-medium">Joylashgan sana</th>
                <th className="px-4 py-3 font-medium">Amallar</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {batches.map((batch) => (
                <tr key={batch.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3 font-mono text-gray-700">
                    {batch.batch_code}
                  </td>
                  <td className="px-4 py-3 text-gray-700">
                    {SPECIES_LABELS[batch.species] ?? batch.species}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${STATUS_BADGE_CLASSES[batch.status]}`}
                    >
                      {STATUS_LABELS[batch.status]}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-700">
                    {batch.initial_count.toLocaleString()}
                  </td>
                  <td className="px-4 py-3 text-gray-700">
                    {batch.current_count.toLocaleString()}
                  </td>
                  <td className="px-4 py-3 text-gray-500">
                    {new Date(batch.placement_date).toLocaleDateString('uz-UZ')}
                  </td>
                  <td className="px-4 py-3 space-x-3">
                    <Link
                      to={`/livestock/${batch.id}`}
                      className="text-green-600 hover:text-green-800 font-medium"
                    >
                      Ko'rish
                    </Link>
                    {allowedToArchive && batch.status === 'completed' && (
                      archiveTab === 'current' ? (
                        <button
                          onClick={() => handleArchive(batch)}
                          disabled={actioningId === batch.id}
                          className="text-gray-500 hover:text-gray-800 font-medium disabled:opacity-50"
                        >
                          Arxivlash
                        </button>
                      ) : (
                        <button
                          onClick={() => handleUnarchive(batch)}
                          disabled={actioningId === batch.id}
                          className="text-gray-500 hover:text-gray-800 font-medium disabled:opacity-50"
                        >
                          Arxivdan chiqarish
                        </button>
                      )
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
