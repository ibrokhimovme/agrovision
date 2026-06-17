import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { farmService, batchService } from '@/services/batchService'
import type { Farm, Batch } from '@/types'

function statusBadge(status: string) {
  const classes: Record<string, string> = {
    active: 'bg-green-100 text-green-700',
    quarantine: 'bg-yellow-100 text-yellow-700',
    closed: 'bg-gray-100 text-gray-500',
  }
  const labels: Record<string, string> = {
    active: 'Faol',
    quarantine: 'Karantin',
    closed: 'Yopiq',
  }
  return (
    <span className={`text-xs px-2 py-1 rounded-full font-medium ${classes[status] ?? 'bg-gray-100 text-gray-600'}`}>
      {labels[status] ?? status}
    </span>
  )
}

export default function ReportsPage() {
  const [farms, setFarms] = useState<Farm[]>([])
  const [selectedFarmId, setSelectedFarmId] = useState<string>('')
  const [batches, setBatches] = useState<Batch[]>([])
  const [loading, setLoading] = useState(false)

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

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Hisobotlar</h1>
        <p className="text-sm text-gray-500 mt-1">
          Partiya bo'yicha ishlash ko'rsatkichlari va PDF eksport
        </p>
      </div>

      {farms.length > 1 && (
        <select
          value={selectedFarmId}
          onChange={(e) => setSelectedFarmId(e.target.value)}
          className="mb-6 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
        >
          {farms.map((f) => (
            <option key={f.id} value={f.id}>{f.name}</option>
          ))}
        </select>
      )}

      {loading ? (
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
                    {batch.batch_code ?? batch.id.slice(0, 8)}
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
      )}
    </div>
  )
}
