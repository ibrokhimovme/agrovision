import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { batchService, farmService } from '@/services/batchService'
import type { Batch, BatchStatus, Farm } from '@/types'

const STATUS_LABELS: Record<BatchStatus, string> = {
  quarantine: 'Karantin',
  active: 'Faol',
  closed: 'Yopilgan',
}

const STATUS_BADGE_CLASSES: Record<BatchStatus, string> = {
  quarantine: 'bg-yellow-100 text-yellow-800',
  active: 'bg-green-100 text-green-800',
  closed: 'bg-gray-100 text-gray-700',
}

const SPECIES_LABELS: Record<string, string> = {
  broiler: 'Broiler',
  layer: 'Tuxumchi',
}

type StatusFilter = BatchStatus | 'all'

const DEFAULT_FARM_ID = '11111111-1111-1111-1111-111111111111'

export default function BatchListPage() {
  const [batches, setBatches] = useState<Batch[]>([])
  const [farms, setFarms] = useState<Farm[]>([])
  const [selectedFarmId, setSelectedFarmId] = useState<string>(DEFAULT_FARM_ID)
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [total, setTotal] = useState(0)

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

  useEffect(() => {
    if (!selectedFarmId) return
    setLoading(true)
    setError(null)
    batchService
      .listBatches({
        farm_id: selectedFarmId,
        status: statusFilter !== 'all' ? statusFilter : undefined,
        page: 1,
        page_size: 50,
      })
      .then((res) => {
        setBatches(res.data)
        setTotal(res.pagination.total_items)
      })
      .catch(() => setError("Ma'lumotlarni yuklashda xatolik yuz berdi."))
      .finally(() => setLoading(false))
  }, [selectedFarmId, statusFilter])

  const statusOptions: { value: StatusFilter; label: string }[] = [
    { value: 'all', label: 'Barchasi' },
    { value: 'quarantine', label: 'Karantin' },
    { value: 'active', label: 'Faol' },
    { value: 'closed', label: 'Yopilgan' },
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
                    {batch.batch_code ?? '—'}
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
                  <td className="px-4 py-3">
                    <Link
                      to={`/livestock/${batch.id}`}
                      className="text-green-600 hover:text-green-800 font-medium"
                    >
                      Ko'rish
                    </Link>
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
