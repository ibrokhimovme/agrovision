import { useEffect, useState } from 'react'
import { farmService } from '@/services/batchService'
import type { Farm } from '@/types'

export default function FarmListPage() {
  const [farms, setFarms] = useState<Farm[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    farmService
      .listFarms()
      .then((res) => setFarms(res.data))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="flex justify-center items-center py-20">
        <div className="animate-spin rounded-full border-2 border-gray-200 border-t-green-600 h-8 w-8" />
      </div>
    )
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Fermalar</h1>
      {farms.length === 0 ? (
        <div className="text-center py-20 text-gray-400">Fermalar topilmadi</div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {farms.map((farm) => (
            <div key={farm.id} className="bg-white rounded-xl border border-gray-200 p-5">
              <h2 className="font-semibold text-gray-900">{farm.name}</h2>
              <p className="text-sm text-gray-500 mt-1">{farm.farm_type}</p>
              {farm.region && <p className="text-xs text-gray-400 mt-1">{farm.region}</p>}
              <span
                className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium mt-2 ${
                  farm.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'
                }`}
              >
                {farm.is_active ? 'Faol' : 'Nofaol'}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
