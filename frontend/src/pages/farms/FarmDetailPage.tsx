import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { farmService, type CreateBuildingPayload, type CreateSectionPayload } from '@/services/batchService'
import { useToastStore } from '@/components/ui/Toast'
import type { Farm, Building, Section, SectionType } from '@/types'

const SECTION_TYPE_LABELS: Record<SectionType, string> = {
  quarantine: 'Karantin',
  production: 'Ishlab chiqarish',
  isolation: 'Izolyatsiya',
  storage: 'Saqlash',
}

export default function FarmDetailPage() {
  const { id } = useParams<{ id: string }>()
  const showToast = useToastStore((s) => s.show)

  const [farm, setFarm] = useState<Farm | null>(null)
  const [buildings, setBuildings] = useState<Building[]>([])
  const [sections, setSections] = useState<Record<string, Section[]>>({})
  const [loading, setLoading] = useState(true)

  const [showBuildingForm, setShowBuildingForm] = useState(false)
  const [buildingForm, setBuildingForm] = useState({ name: '', capacity: '', notes: '' })
  const [savingBuilding, setSavingBuilding] = useState(false)

  const [sectionTarget, setSectionTarget] = useState<Building | null>(null)
  const [sectionForm, setSectionForm] = useState({ name: '', section_type: 'production' as SectionType, capacity: '' })
  const [savingSection, setSavingSection] = useState(false)

  const loadBuildings = async (farmId: string) => {
    const res = await farmService.listBuildings(farmId)
    const blds = res.data
    setBuildings(blds)
    const sectionMap: Record<string, Section[]> = {}
    await Promise.all(
      blds.map(async (b) => {
        const sRes = await farmService.listSections(b.id)
        sectionMap[b.id] = sRes.data
      })
    )
    setSections(sectionMap)
  }

  useEffect(() => {
    if (!id) return
    setLoading(true)
    Promise.all([farmService.getFarm(id), farmService.listBuildings(id)])
      .then(async ([farmRes, bldRes]) => {
        setFarm(farmRes.data)
        const blds = bldRes.data
        setBuildings(blds)
        const sectionMap: Record<string, Section[]> = {}
        await Promise.all(
          blds.map(async (b) => {
            const sRes = await farmService.listSections(b.id)
            sectionMap[b.id] = sRes.data
          })
        )
        setSections(sectionMap)
      })
      .catch(() => showToast('error', "Ferma ma'lumotlari yuklanmadi"))
      .finally(() => setLoading(false))
  }, [id]) // eslint-disable-line react-hooks/exhaustive-deps

  const handleAddBuilding = async () => {
    if (!id || !buildingForm.name.trim()) return
    setSavingBuilding(true)
    try {
      const payload: CreateBuildingPayload = {
        name: buildingForm.name.trim(),
        capacity: buildingForm.capacity ? Number(buildingForm.capacity) : undefined,
        notes: buildingForm.notes || undefined,
      }
      await farmService.createBuilding(id, payload)
      showToast('success', "Bino qo'shildi")
      setShowBuildingForm(false)
      setBuildingForm({ name: '', capacity: '', notes: '' })
      await loadBuildings(id)
    } catch {
      showToast('error', 'Xatolik yuz berdi')
    } finally {
      setSavingBuilding(false)
    }
  }

  const handleAddSection = async () => {
    if (!sectionTarget || !sectionForm.name.trim()) return
    setSavingSection(true)
    try {
      const payload: CreateSectionPayload = {
        name: sectionForm.name.trim(),
        section_type: sectionForm.section_type,
        capacity: sectionForm.capacity ? Number(sectionForm.capacity) : undefined,
      }
      await farmService.createSection(sectionTarget.id, payload)
      showToast('success', "Bo'lim qo'shildi")
      setSectionTarget(null)
      setSectionForm({ name: '', section_type: 'production', capacity: '' })
      if (id) await loadBuildings(id)
    } catch {
      showToast('error', 'Xatolik yuz berdi')
    } finally {
      setSavingSection(false)
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center py-20">
        <div className="animate-spin rounded-full border-2 border-gray-200 border-t-green-600 h-8 w-8" />
      </div>
    )
  }

  if (!farm) {
    return (
      <div className="p-6 text-center text-gray-500">
        Ferma topilmadi.{' '}
        <Link to="/farms" className="text-green-600 hover:underline">
          Orqaga
        </Link>
      </div>
    )
  }

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3 mb-2">
        <Link to="/farms" className="text-sm text-gray-500 hover:text-gray-700">
          ← Fermalar
        </Link>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{farm.name}</h1>
            <p className="text-sm text-gray-500 mt-1">
              {farm.farm_type === 'poultry'
                ? 'Parrandachilik'
                : farm.farm_type === 'livestock'
                ? 'Chorvachilik'
                : farm.farm_type === 'dairy'
                ? 'Sut ferma'
                : 'Aralash'}
            </p>
          </div>
          <span
            className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${
              farm.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'
            }`}
          >
            {farm.is_active ? 'Faol' : 'Nofaol'}
          </span>
        </div>

        {(farm.region || farm.address || farm.notes) && (
          <div className="mt-4 pt-4 border-t border-gray-100 grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm text-gray-600">
            {farm.region && (
              <div>
                <span className="text-xs text-gray-400 uppercase tracking-wide block">Viloyat</span>
                {farm.region}
              </div>
            )}
            {farm.address && (
              <div>
                <span className="text-xs text-gray-400 uppercase tracking-wide block">Manzil</span>
                {farm.address}
              </div>
            )}
            {farm.notes && (
              <div className="sm:col-span-2">
                <span className="text-xs text-gray-400 uppercase tracking-wide block">Izoh</span>
                {farm.notes}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Buildings */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold text-gray-900">Binolar</h2>
          <button
            onClick={() => setShowBuildingForm(true)}
            className="text-sm px-3 py-1.5 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            + Bino qo'shish
          </button>
        </div>

        {showBuildingForm && (
          <div className="bg-gray-50 border border-gray-200 rounded-xl p-4 mb-4 space-y-3">
            <h3 className="text-sm font-medium text-gray-700">Yangi bino</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="block text-xs text-gray-500 mb-1">
                  Nomi <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={buildingForm.name}
                  onChange={(e) => setBuildingForm((f) => ({ ...f, name: e.target.value }))}
                  placeholder="Masalan: A-bino"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">Sig'im (bosh)</label>
                <input
                  type="number"
                  min="0"
                  value={buildingForm.capacity}
                  onChange={(e) => setBuildingForm((f) => ({ ...f, capacity: e.target.value }))}
                  placeholder="0"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                />
              </div>
              <div className="sm:col-span-2">
                <label className="block text-xs text-gray-500 mb-1">Izoh</label>
                <input
                  type="text"
                  value={buildingForm.notes}
                  onChange={(e) => setBuildingForm((f) => ({ ...f, notes: e.target.value }))}
                  placeholder="Ixtiyoriy"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                />
              </div>
            </div>
            <div className="flex gap-2">
              <button
                onClick={handleAddBuilding}
                disabled={savingBuilding || !buildingForm.name.trim()}
                className="px-4 py-2 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors"
              >
                {savingBuilding ? 'Saqlanmoqda...' : 'Saqlash'}
              </button>
              <button
                onClick={() => { setShowBuildingForm(false); setBuildingForm({ name: '', capacity: '', notes: '' }) }}
                className="px-4 py-2 border border-gray-300 text-gray-700 text-sm rounded-lg hover:bg-gray-50 transition-colors"
              >
                Bekor qilish
              </button>
            </div>
          </div>
        )}

        {buildings.length === 0 ? (
          <div className="text-center py-10 text-gray-400 border border-dashed border-gray-200 rounded-xl">
            Hali binolar yo'q. Ferma tuzilmasini yaratish uchun bino qo'shing.
          </div>
        ) : (
          <div className="space-y-4">
            {buildings.map((building) => (
              <div key={building.id} className="bg-white rounded-xl border border-gray-200 p-5">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <h3 className="font-semibold text-gray-900">{building.name}</h3>
                    {building.capacity && (
                      <p className="text-xs text-gray-400 mt-0.5">Sig'im: {building.capacity.toLocaleString()} bosh</p>
                    )}
                  </div>
                  <button
                    onClick={() => {
                      setSectionTarget(building)
                      setSectionForm({ name: '', section_type: 'production', capacity: '' })
                    }}
                    className="text-xs px-3 py-1.5 border border-green-200 text-green-700 rounded-lg hover:bg-green-50 transition-colors"
                  >
                    + Bo'lim qo'shish
                  </button>
                </div>

                {/* Section inline form */}
                {sectionTarget?.id === building.id && (
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-3 mb-3 space-y-3">
                    <h4 className="text-xs font-medium text-gray-600">Yangi bo'lim</h4>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                      <div>
                        <label className="block text-xs text-gray-500 mb-1">
                          Nomi <span className="text-red-500">*</span>
                        </label>
                        <input
                          type="text"
                          value={sectionForm.name}
                          onChange={(e) => setSectionForm((f) => ({ ...f, name: e.target.value }))}
                          placeholder="Masalan: 1-sektor"
                          className="w-full border border-gray-300 rounded-lg px-2 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-green-500"
                        />
                      </div>
                      <div>
                        <label className="block text-xs text-gray-500 mb-1">Tur</label>
                        <select
                          value={sectionForm.section_type}
                          onChange={(e) => setSectionForm((f) => ({ ...f, section_type: e.target.value as SectionType }))}
                          className="w-full border border-gray-300 rounded-lg px-2 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-green-500"
                        >
                          <option value="production">Ishlab chiqarish</option>
                          <option value="quarantine">Karantin</option>
                          <option value="isolation">Izolyatsiya</option>
                          <option value="storage">Saqlash</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-xs text-gray-500 mb-1">Sig'im</label>
                        <input
                          type="number"
                          min="0"
                          value={sectionForm.capacity}
                          onChange={(e) => setSectionForm((f) => ({ ...f, capacity: e.target.value }))}
                          placeholder="0"
                          className="w-full border border-gray-300 rounded-lg px-2 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-green-500"
                        />
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={handleAddSection}
                        disabled={savingSection || !sectionForm.name.trim()}
                        className="px-3 py-1.5 bg-green-600 text-white text-xs rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors"
                      >
                        {savingSection ? 'Saqlanmoqda...' : 'Saqlash'}
                      </button>
                      <button
                        onClick={() => setSectionTarget(null)}
                        className="px-3 py-1.5 border border-gray-300 text-gray-600 text-xs rounded-lg hover:bg-gray-50 transition-colors"
                      >
                        Bekor
                      </button>
                    </div>
                  </div>
                )}

                {/* Section list */}
                {(sections[building.id] ?? []).length === 0 ? (
                  <p className="text-xs text-gray-400 italic">Bo'limlar yo'q</p>
                ) : (
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {(sections[building.id] ?? []).map((section) => (
                      <div
                        key={section.id}
                        className="flex items-center justify-between border border-gray-100 rounded-lg px-3 py-2 bg-gray-50"
                      >
                        <div>
                          <p className="text-sm font-medium text-gray-800">{section.name}</p>
                          <p className="text-xs text-gray-400">{SECTION_TYPE_LABELS[section.section_type]}</p>
                        </div>
                        <div className="text-right">
                          {section.capacity && (
                            <p className="text-xs text-gray-500">{section.capacity.toLocaleString()} bosh</p>
                          )}
                          <span
                            className={`inline-block text-xs px-1.5 py-0.5 rounded-full ${
                              section.is_active
                                ? 'bg-green-100 text-green-600'
                                : 'bg-gray-100 text-gray-400'
                            }`}
                          >
                            {section.is_active ? 'Faol' : 'Nofaol'}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
