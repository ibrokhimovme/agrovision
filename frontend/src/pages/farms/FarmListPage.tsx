import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { farmService, type CreateFarmPayload, type UpdateFarmPayload } from '@/services/batchService'
import { useToastStore } from '@/components/ui/Toast'
import type { Farm, FarmType } from '@/types'

const FARM_TYPE_LABELS: Record<FarmType, string> = {
  poultry: 'Parrandachilik',
  livestock: 'Chorvachilik',
  dairy: 'Sut ferma',
  mixed: 'Aralash',
}

type ModalMode = 'create' | 'edit' | null

const EMPTY_FORM = { name: '', farm_type: 'poultry' as FarmType, region: '', address: '', notes: '' }

export default function FarmListPage() {
  const [farms, setFarms] = useState<Farm[]>([])
  const [loading, setLoading] = useState(true)
  const [modal, setModal] = useState<ModalMode>(null)
  const [editTarget, setEditTarget] = useState<Farm | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<Farm | null>(null)
  const [form, setForm] = useState(EMPTY_FORM)
  const [saving, setSaving] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const showToast = useToastStore((s) => s.show)

  const load = () => {
    setLoading(true)
    farmService
      .listFarms()
      .then((res) => setFarms(res.data))
      .catch(() => showToast('error', 'Fermalar yuklanmadi'))
      .finally(() => setLoading(false))
  }

  useEffect(() => { load() }, []) // eslint-disable-line react-hooks/exhaustive-deps

  const openCreate = () => {
    setForm(EMPTY_FORM)
    setEditTarget(null)
    setModal('create')
  }

  const openEdit = (farm: Farm) => {
    setForm({
      name: farm.name,
      farm_type: farm.farm_type,
      region: farm.region ?? '',
      address: farm.address ?? '',
      notes: farm.notes ?? '',
    })
    setEditTarget(farm)
    setModal('edit')
  }

  const closeModal = () => { setModal(null); setEditTarget(null) }

  const handleSave = async () => {
    if (!form.name.trim()) return
    setSaving(true)
    try {
      const payload: CreateFarmPayload | UpdateFarmPayload = {
        name: form.name.trim(),
        farm_type: form.farm_type,
        region: form.region || undefined,
        address: form.address || undefined,
        notes: form.notes || undefined,
      }
      if (modal === 'create') {
        await farmService.createFarm(payload as CreateFarmPayload)
        showToast('success', 'Ferma yaratildi')
      } else if (modal === 'edit' && editTarget) {
        await farmService.updateFarm(editTarget.id, payload)
        showToast('success', 'Ferma yangilandi')
      }
      closeModal()
      load()
    } catch {
      showToast('error', 'Xatolik yuz berdi')
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async () => {
    if (!deleteTarget) return
    setDeleting(true)
    try {
      await farmService.deleteFarm(deleteTarget.id)
      showToast('success', `"${deleteTarget.name}" o'chirildi`)
      setDeleteTarget(null)
      load()
    } catch {
      showToast('error', "O'chirishda xatolik. Faol partiyalar mavjud bo'lishi mumkin.")
    } finally {
      setDeleting(false)
    }
  }

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Fermalar</h1>
        <button
          onClick={openCreate}
          className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 transition-colors"
        >
          <span className="text-lg leading-none">+</span>
          Yangi ferma
        </button>
      </div>

      {loading ? (
        <div className="flex justify-center items-center py-20">
          <div className="animate-spin rounded-full border-2 border-gray-200 border-t-green-600 h-8 w-8" />
        </div>
      ) : farms.length === 0 ? (
        <div className="text-center py-20 text-gray-400">
          <p className="mb-4">Fermalar topilmadi</p>
          <button onClick={openCreate} className="text-green-600 hover:underline text-sm">
            Birinchi fermani yarating
          </button>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {farms.map((farm) => (
            <div key={farm.id} className="bg-white rounded-xl border border-gray-200 p-5 flex flex-col gap-3">
              <div className="flex items-start justify-between">
                <div>
                  <h2 className="font-semibold text-gray-900">{farm.name}</h2>
                  <p className="text-sm text-gray-500 mt-0.5">{FARM_TYPE_LABELS[farm.farm_type]}</p>
                  {farm.region && <p className="text-xs text-gray-400 mt-0.5">{farm.region}</p>}
                </div>
                <span
                  className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                    farm.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'
                  }`}
                >
                  {farm.is_active ? 'Faol' : 'Nofaol'}
                </span>
              </div>

              <div className="flex gap-2 mt-auto pt-2 border-t border-gray-100">
                <Link
                  to={`/farms/${farm.id}`}
                  className="flex-1 text-center text-xs py-1.5 border border-gray-200 rounded-lg text-gray-600 hover:bg-gray-50 transition-colors"
                >
                  Batafsil
                </Link>
                <button
                  onClick={() => openEdit(farm)}
                  className="flex-1 text-xs py-1.5 border border-blue-200 rounded-lg text-blue-600 hover:bg-blue-50 transition-colors"
                >
                  Tahrirlash
                </button>
                <button
                  onClick={() => setDeleteTarget(farm)}
                  className="flex-1 text-xs py-1.5 border border-red-200 rounded-lg text-red-600 hover:bg-red-50 transition-colors"
                >
                  O'chirish
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create / Edit Modal */}
      {modal !== null && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-md p-6 space-y-4">
            <h2 className="text-lg font-semibold text-gray-900">
              {modal === 'create' ? 'Yangi ferma qo\'shish' : 'Fermani tahrirlash'}
            </h2>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Ferma nomi <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={form.name}
                onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
                placeholder="Masalan: Asosiy ferma"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Tur</label>
              <select
                value={form.farm_type}
                onChange={(e) => setForm((f) => ({ ...f, farm_type: e.target.value as FarmType }))}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                <option value="poultry">Parrandachilik</option>
                <option value="livestock">Chorvachilik</option>
                <option value="dairy">Sut ferma</option>
                <option value="mixed">Aralash</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Viloyat / Hudud</label>
              <input
                type="text"
                value={form.region}
                onChange={(e) => setForm((f) => ({ ...f, region: e.target.value }))}
                placeholder="Masalan: Toshkent viloyati"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Manzil</label>
              <input
                type="text"
                value={form.address}
                onChange={(e) => setForm((f) => ({ ...f, address: e.target.value }))}
                placeholder="To'liq manzil"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Izoh</label>
              <textarea
                value={form.notes}
                onChange={(e) => setForm((f) => ({ ...f, notes: e.target.value }))}
                rows={2}
                placeholder="Qo'shimcha ma'lumot..."
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500 resize-none"
              />
            </div>

            <div className="flex gap-3 pt-2">
              <button
                onClick={handleSave}
                disabled={saving || !form.name.trim()}
                className="flex-1 py-2.5 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors"
              >
                {saving ? 'Saqlanmoqda...' : 'Saqlash'}
              </button>
              <button
                onClick={closeModal}
                className="flex-1 py-2.5 border border-gray-300 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50 transition-colors"
              >
                Bekor qilish
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirm Modal */}
      {deleteTarget !== null && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-sm p-6 space-y-4">
            <h2 className="text-lg font-semibold text-gray-900">Fermani o'chirish</h2>
            <p className="text-sm text-gray-600">
              <span className="font-medium">"{deleteTarget.name}"</span> fermasini o'chirishni tasdiqlaysizmi?
              Agar faol partiyalar mavjud bo'lsa, bu amal bloklanadi.
            </p>
            <div className="flex gap-3">
              <button
                onClick={handleDelete}
                disabled={deleting}
                className="flex-1 py-2.5 bg-red-600 text-white text-sm font-medium rounded-lg hover:bg-red-700 disabled:opacity-50 transition-colors"
              >
                {deleting ? 'O\'chirilmoqda...' : 'O\'chirish'}
              </button>
              <button
                onClick={() => setDeleteTarget(null)}
                className="flex-1 py-2.5 border border-gray-300 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50 transition-colors"
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
