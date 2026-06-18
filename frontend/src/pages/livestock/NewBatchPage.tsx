import { useEffect, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { batchService, farmService } from '@/services/batchService'
import type { Farm, Building, Section } from '@/types'

const schema = z.object({
  farm_id: z.string().min(1, "Ferma tanlang"),
  section_id: z.string().min(1, "Bo'lim tanlang"),
  species: z.enum(['broiler', 'layer']),
  initial_count: z.coerce.number().int().min(1, "Kamida 1 ta qush kerak"),
  placement_date: z.string().min(1, "Sana kiritilsin"),
  supplier_name: z.string().optional(),
  chick_price_per_head: z.coerce.number().positive().optional().or(z.literal('')),
  notes: z.string().optional(),
})

type FormData = z.infer<typeof schema>

export default function NewBatchPage() {
  const navigate = useNavigate()
  const [farms, setFarms] = useState<Farm[]>([])
  const [buildings, setBuildings] = useState<Building[]>([])
  const [sections, setSections] = useState<Section[]>([])
  const [selectedBuildingId, setSelectedBuildingId] = useState('')
  const [loadingBuildings, setLoadingBuildings] = useState(false)
  const [loadingSections, setLoadingSections] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [serverError, setServerError] = useState<string | null>(null)

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      species: 'broiler',
      farm_id: '',
      section_id: '',
    },
  })

  const watchedFarmId = watch('farm_id')

  useEffect(() => {
    farmService.listFarms().then((res) => setFarms(res.data)).catch(() => {})
  }, [])

  useEffect(() => {
    if (!watchedFarmId) {
      setBuildings([])
      setSections([])
      setSelectedBuildingId('')
      setValue('section_id', '')
      return
    }
    setLoadingBuildings(true)
    setBuildings([])
    setSections([])
    setSelectedBuildingId('')
    setValue('section_id', '')
    farmService
      .listBuildings(watchedFarmId)
      .then((res) => setBuildings(res.data))
      .catch(() => {})
      .finally(() => setLoadingBuildings(false))
  }, [watchedFarmId, setValue])

  const handleBuildingChange = (buildingId: string) => {
    setSelectedBuildingId(buildingId)
    setSections([])
    setValue('section_id', '')
    if (!buildingId) return
    setLoadingSections(true)
    farmService
      .listSections(buildingId)
      .then((res) => setSections(res.data))
      .catch(() => {})
      .finally(() => setLoadingSections(false))
  }

  const onSubmit = async (data: FormData) => {
    setSubmitting(true)
    setServerError(null)
    try {
      await batchService.createBatch({
        farm_id: data.farm_id,
        section_id: data.section_id,
        species: data.species,
        initial_count: data.initial_count,
        placement_date: new Date(data.placement_date).toISOString(),
        supplier_name: data.supplier_name || undefined,
        chick_price_per_head:
          data.chick_price_per_head !== '' && data.chick_price_per_head != null
            ? Number(data.chick_price_per_head)
            : undefined,
        notes: data.notes || undefined,
      })
      navigate('/livestock')
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { message?: string } } }
      setServerError(axiosError?.response?.data?.message ?? "Xatolik yuz berdi. Qaytadan urinib ko'ring.")
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <div className="flex items-center gap-3 mb-6">
        <Link to="/livestock" className="text-gray-500 hover:text-gray-700">
          ← Orqaga
        </Link>
        <h1 className="text-2xl font-bold text-gray-900">Yangi partiya</h1>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
        {serverError && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-red-700 text-sm">
            {serverError}
          </div>
        )}

        {/* Farm */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Ferma <span className="text-red-500">*</span>
          </label>
          <select
            {...register('farm_id')}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <option value="">Fermani tanlang</option>
            {farms.map((f) => (
              <option key={f.id} value={f.id}>
                {f.name}
              </option>
            ))}
          </select>
          {errors.farm_id && (
            <p className="text-red-500 text-xs mt-1">{errors.farm_id.message}</p>
          )}
        </div>

        {/* Building — appears after farm selected */}
        {watchedFarmId && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Bino <span className="text-red-500">*</span>
            </label>
            <select
              value={selectedBuildingId}
              onChange={(e) => handleBuildingChange(e.target.value)}
              disabled={loadingBuildings}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500 disabled:bg-gray-50"
            >
              <option value="">
                {loadingBuildings ? 'Yuklanmoqda...' : buildings.length === 0 ? "Binolar yo'q — avval ferma sahifasida bino qo'shing" : 'Binoni tanlang'}
              </option>
              {buildings.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.name}
                  {b.capacity ? ` (${b.capacity.toLocaleString()} bosh)` : ''}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Section — appears after building selected */}
        {selectedBuildingId && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Bo'lim <span className="text-red-500">*</span>
            </label>
            <select
              {...register('section_id')}
              disabled={loadingSections}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500 disabled:bg-gray-50"
            >
              <option value="">
                {loadingSections ? 'Yuklanmoqda...' : sections.length === 0 ? "Bo'limlar yo'q — binoga bo'lim qo'shing" : "Bo'limni tanlang"}
              </option>
              {sections.filter((s) => s.is_active).map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                  {s.section_type === 'isolation'
                    ? ' — Izolyatsiya'
                    : s.section_type === 'storage'
                    ? ' — Saqlash'
                    : ''}
                  {s.capacity ? ` (${s.capacity.toLocaleString()} bosh)` : ''}
                </option>
              ))}
            </select>
            {errors.section_id && (
              <p className="text-red-500 text-xs mt-1">{errors.section_id.message}</p>
            )}
          </div>
        )}

        {/* Species */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Tur <span className="text-red-500">*</span>
          </label>
          <select
            {...register('species')}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <option value="broiler">Broiler</option>
            <option value="layer">Tuxumchi</option>
          </select>
        </div>

        {/* Initial count */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Boshlang'ich soni <span className="text-red-500">*</span>
          </label>
          <input
            type="number"
            {...register('initial_count')}
            placeholder="Masalan: 5000"
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
          />
          {errors.initial_count && (
            <p className="text-red-500 text-xs mt-1">{errors.initial_count.message}</p>
          )}
        </div>

        {/* Placement date */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Joylashgan sana <span className="text-red-500">*</span>
          </label>
          <input
            type="date"
            {...register('placement_date')}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
          />
          {errors.placement_date && (
            <p className="text-red-500 text-xs mt-1">{errors.placement_date.message}</p>
          )}
        </div>

        {/* Supplier name */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Ta'minotchi</label>
          <input
            type="text"
            {...register('supplier_name')}
            placeholder="Ta'minotchi nomi"
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
          />
        </div>

        {/* Price per head */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Jo'ja narxi (so'm)
          </label>
          <input
            type="number"
            step="0.01"
            {...register('chick_price_per_head')}
            placeholder="Masalan: 8500.00"
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
          />
        </div>

        {/* Notes */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Izoh</label>
          <textarea
            {...register('notes')}
            rows={3}
            placeholder="Qo'shimcha ma'lumot..."
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500 resize-none"
          />
        </div>

        <div className="flex gap-3 pt-2">
          <button
            type="submit"
            disabled={submitting}
            className="flex-1 py-2.5 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors"
          >
            {submitting ? 'Saqlanmoqda...' : 'Saqlash'}
          </button>
          <Link
            to="/livestock"
            className="flex-1 py-2.5 border border-gray-300 text-gray-700 text-sm font-medium rounded-lg text-center hover:bg-gray-50 transition-colors"
          >
            Bekor qilish
          </Link>
        </div>
      </form>
    </div>
  )
}
