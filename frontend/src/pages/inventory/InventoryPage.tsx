import { useEffect, useState } from 'react'
import { farmService } from '@/services/batchService'
import { warehouseService, stockService } from '@/services/inventoryService'
import type { Farm } from '@/types'
import type {
  Warehouse,
  StockItemDetail,
  CreateWarehousePayload,
  CreateStockItemPayload,
  ReceiveStockPayload,
} from '@/services/inventoryService'

const DEFAULT_FARM_ID = '11111111-1111-1111-1111-111111111111'

const ITEM_TYPE_LABELS: Record<string, string> = {
  feed: 'Yem',
  vaccine: 'Vaktsina',
  medicine: 'Dori',
  equipment: 'Asbob-uskuna',
  packaging: 'Qadoqlash',
  other: 'Boshqa',
}

const ITEM_TYPE_BADGE: Record<string, string> = {
  feed: 'bg-yellow-100 text-yellow-700',
  vaccine: 'bg-blue-100 text-blue-700',
  medicine: 'bg-purple-100 text-purple-700',
  equipment: 'bg-gray-100 text-gray-700',
  packaging: 'bg-orange-100 text-orange-700',
  other: 'bg-gray-100 text-gray-600',
}

type ModalType = 'warehouse' | 'stockItem' | 'receive' | null

export default function InventoryPage() {
  const [farms, setFarms] = useState<Farm[]>([])
  const [selectedFarmId, setSelectedFarmId] = useState<string>(DEFAULT_FARM_ID)
  const [warehouses, setWarehouses] = useState<Warehouse[]>([])
  const [items, setItems] = useState<StockItemDetail[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [modal, setModal] = useState<ModalType>(null)
  const [selectedItemId, setSelectedItemId] = useState<string | null>(null)
  const [formError, setFormError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  // warehouse form
  const [whName, setWhName] = useState('')
  const [whLocation, setWhLocation] = useState('')

  // stock item form
  const [siWarehouseId, setSiWarehouseId] = useState('')
  const [siName, setSiName] = useState('')
  const [siType, setSiType] = useState('feed')
  const [siUnit, setSiUnit] = useState('')
  const [siMinQty, setSiMinQty] = useState('0')

  // receive stock form
  const [rcQty, setRcQty] = useState('')
  const [rcCost, setRcCost] = useState('')
  const [rcBatchNo, setRcBatchNo] = useState('')
  const [rcExpiry, setRcExpiry] = useState('')
  const [rcNotes, setRcNotes] = useState('')

  useEffect(() => {
    farmService
      .listFarms()
      .then((res) => {
        setFarms(res.data)
        if (res.data.length > 0) setSelectedFarmId(res.data[0].id)
      })
      .catch(() => {})
  }, [])

  useEffect(() => {
    if (!selectedFarmId) return
    setLoading(true)
    setError(null)
    Promise.all([
      warehouseService.listWarehouses(selectedFarmId),
      stockService.listStockItems(selectedFarmId),
    ])
      .then(([whRes, siRes]) => {
        setWarehouses(whRes.data)
        setItems(siRes.data)
      })
      .catch(() => setError("Ma'lumotlarni yuklashda xatolik yuz berdi."))
      .finally(() => setLoading(false))
  }, [selectedFarmId])

  function openReceive(itemId: string) {
    setSelectedItemId(itemId)
    setRcQty('')
    setRcCost('')
    setRcBatchNo('')
    setRcExpiry('')
    setRcNotes('')
    setFormError(null)
    setModal('receive')
  }

  async function handleCreateWarehouse(e: React.FormEvent) {
    e.preventDefault()
    setSaving(true)
    setFormError(null)
    try {
      const payload: CreateWarehousePayload = {
        farm_id: selectedFarmId,
        name: whName,
        location: whLocation || undefined,
      }
      await warehouseService.createWarehouse(payload)
      const res = await warehouseService.listWarehouses(selectedFarmId)
      setWarehouses(res.data)
      setModal(null)
      setWhName('')
      setWhLocation('')
    } catch {
      setFormError('Ombor yaratishda xatolik')
    } finally {
      setSaving(false)
    }
  }

  async function handleCreateStockItem(e: React.FormEvent) {
    e.preventDefault()
    setSaving(true)
    setFormError(null)
    try {
      const payload: CreateStockItemPayload = {
        warehouse_id: siWarehouseId,
        name: siName,
        item_type: siType as any,
        unit: siUnit,
        minimum_quantity: parseFloat(siMinQty) || 0,
      }
      await stockService.createStockItem(payload)
      const res = await stockService.listStockItems(selectedFarmId)
      setItems(res.data)
      setModal(null)
      setSiName('')
      setSiUnit('')
      setSiMinQty('0')
    } catch {
      setFormError('Mahsulot qo\'shishda xatolik')
    } finally {
      setSaving(false)
    }
  }

  async function handleReceive(e: React.FormEvent) {
    e.preventDefault()
    if (!selectedItemId) return
    setSaving(true)
    setFormError(null)
    try {
      const payload: ReceiveStockPayload = {
        quantity: parseFloat(rcQty),
        unit_cost: rcCost ? parseFloat(rcCost) : undefined,
        batch_number: rcBatchNo || undefined,
        expiry_date: rcExpiry ? new Date(rcExpiry).toISOString() : undefined,
        notes: rcNotes || undefined,
      }
      await stockService.receiveStock(selectedItemId, payload)
      const res = await stockService.listStockItems(selectedFarmId)
      setItems(res.data)
      setModal(null)
    } catch {
      setFormError('Kirim qilishda xatolik')
    } finally {
      setSaving(false)
    }
  }

  const warehouseMap = Object.fromEntries(warehouses.map((w) => [w.id, w.name]))
  const belowMin = items.filter((i) => i.is_below_minimum)

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Ombor</h1>
          <p className="text-sm text-gray-500 mt-1">{items.length} ta mahsulot</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => { setFormError(null); setModal('warehouse') }}
            className="px-4 py-2 border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50 transition-colors"
          >
            + Ombor
          </button>
          <button
            onClick={() => {
              if (warehouses.length > 0) setSiWarehouseId(warehouses[0].id)
              setFormError(null)
              setModal('stockItem')
            }}
            className="px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 transition-colors"
          >
            + Mahsulot
          </button>
        </div>
      </div>

      {/* Farm selector */}
      {farms.length > 0 && (
        <select
          value={selectedFarmId}
          onChange={(e) => setSelectedFarmId(e.target.value)}
          className="mb-4 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
        >
          {farms.map((f) => (
            <option key={f.id} value={f.id}>{f.name}</option>
          ))}
        </select>
      )}

      {/* Low stock alert */}
      {belowMin.length > 0 && (
        <div className="mb-4 p-3 bg-red-50 border border-red-100 rounded-lg text-sm text-red-700">
          ⚠ {belowMin.length} ta mahsulot minimal miqdordan past: {belowMin.map((i) => i.name).join(', ')}
        </div>
      )}

      {error && <p className="text-red-500 text-sm mb-4">{error}</p>}

      {loading ? (
        <div className="text-center py-12 text-gray-400">Yuklanmoqda...</div>
      ) : (
        <>
          {/* Warehouses */}
          {warehouses.length > 0 && (
            <div className="mb-6">
              <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">Omborlar</h2>
              <div className="flex flex-wrap gap-2">
                {warehouses.map((w) => (
                  <div key={w.id} className="px-3 py-1 bg-white border border-gray-200 rounded-lg text-sm text-gray-700">
                    {w.name}{w.location ? ` — ${w.location}` : ''}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Stock items table */}
          {items.length === 0 ? (
            <div className="text-center py-12 text-gray-400">
              Hali mahsulot yo'q. Yangi mahsulot qo'shing.
            </div>
          ) : (
            <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
              <table className="min-w-full divide-y divide-gray-100">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nomi</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tur</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Ombor</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Mavjud</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Minimal</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Holati</th>
                    <th className="px-4 py-3" />
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {items.map((item) => (
                    <tr key={item.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 text-sm font-medium text-gray-900">
                        {item.name}
                        {item.sku && <span className="ml-2 text-xs text-gray-400">{item.sku}</span>}
                      </td>
                      <td className="px-4 py-3">
                        <span className={`text-xs px-2 py-1 rounded-full font-medium ${ITEM_TYPE_BADGE[item.item_type] ?? 'bg-gray-100 text-gray-600'}`}>
                          {ITEM_TYPE_LABELS[item.item_type] ?? item.item_type}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-500">{warehouseMap[item.warehouse_id] ?? '—'}</td>
                      <td className="px-4 py-3 text-sm text-right font-medium text-gray-900">
                        {Number(item.current_quantity).toFixed(2)} {item.unit}
                      </td>
                      <td className="px-4 py-3 text-sm text-right text-gray-500">
                        {Number(item.minimum_quantity).toFixed(2)} {item.unit}
                      </td>
                      <td className="px-4 py-3 text-right">
                        {item.is_below_minimum ? (
                          <span className="text-xs px-2 py-1 rounded-full bg-red-100 text-red-700 font-medium">Kam</span>
                        ) : (
                          <span className="text-xs px-2 py-1 rounded-full bg-green-100 text-green-700 font-medium">OK</span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-right">
                        <button
                          onClick={() => openReceive(item.id)}
                          className="text-xs px-3 py-1 bg-green-50 text-green-700 rounded-lg hover:bg-green-100 transition-colors"
                        >
                          Kirim
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}

      {/* Modal overlay */}
      {modal && (
        <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl shadow-xl p-6 w-full max-w-md">
            {modal === 'warehouse' && (
              <>
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Yangi ombor</h2>
                <form onSubmit={handleCreateWarehouse} className="space-y-3">
                  <input
                    required
                    placeholder="Ombor nomi"
                    value={whName}
                    onChange={(e) => setWhName(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                  />
                  <input
                    placeholder="Joylashuv (ixtiyoriy)"
                    value={whLocation}
                    onChange={(e) => setWhLocation(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                  />
                  {formError && <p className="text-red-500 text-xs">{formError}</p>}
                  <div className="flex gap-2 pt-2">
                    <button type="button" onClick={() => setModal(null)} className="flex-1 py-2 border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50">Bekor</button>
                    <button type="submit" disabled={saving} className="flex-1 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 disabled:opacity-50">
                      {saving ? 'Saqlanmoqda...' : 'Saqlash'}
                    </button>
                  </div>
                </form>
              </>
            )}

            {modal === 'stockItem' && (
              <>
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Yangi mahsulot</h2>
                <form onSubmit={handleCreateStockItem} className="space-y-3">
                  <select
                    required
                    value={siWarehouseId}
                    onChange={(e) => setSiWarehouseId(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                  >
                    <option value="">Ombor tanlang</option>
                    {warehouses.map((w) => (
                      <option key={w.id} value={w.id}>{w.name}</option>
                    ))}
                  </select>
                  <input
                    required
                    placeholder="Mahsulot nomi"
                    value={siName}
                    onChange={(e) => setSiName(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                  />
                  <select
                    value={siType}
                    onChange={(e) => setSiType(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                  >
                    {Object.entries(ITEM_TYPE_LABELS).map(([v, l]) => (
                      <option key={v} value={v}>{l}</option>
                    ))}
                  </select>
                  <input
                    required
                    placeholder="O'lchov birligi (kg, dona, litr...)"
                    value={siUnit}
                    onChange={(e) => setSiUnit(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                  />
                  <div>
                    <label className="text-xs text-gray-500 block mb-1">Minimal miqdor</label>
                    <input
                      type="number"
                      min="0"
                      step="0.01"
                      value={siMinQty}
                      onChange={(e) => setSiMinQty(e.target.value)}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                    />
                  </div>
                  {formError && <p className="text-red-500 text-xs">{formError}</p>}
                  <div className="flex gap-2 pt-2">
                    <button type="button" onClick={() => setModal(null)} className="flex-1 py-2 border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50">Bekor</button>
                    <button type="submit" disabled={saving} className="flex-1 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 disabled:opacity-50">
                      {saving ? 'Saqlanmoqda...' : 'Saqlash'}
                    </button>
                  </div>
                </form>
              </>
            )}

            {modal === 'receive' && (
              <>
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Kirim</h2>
                <form onSubmit={handleReceive} className="space-y-3">
                  <div>
                    <label className="text-xs text-gray-500 block mb-1">Miqdor *</label>
                    <input
                      required
                      type="number"
                      min="0.01"
                      step="0.01"
                      placeholder="0.00"
                      value={rcQty}
                      onChange={(e) => setRcQty(e.target.value)}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-gray-500 block mb-1">Narx (ixtiyoriy)</label>
                    <input
                      type="number"
                      min="0"
                      step="0.01"
                      placeholder="0.00"
                      value={rcCost}
                      onChange={(e) => setRcCost(e.target.value)}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                    />
                  </div>
                  <input
                    placeholder="Partiya raqami (ixtiyoriy)"
                    value={rcBatchNo}
                    onChange={(e) => setRcBatchNo(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                  />
                  <div>
                    <label className="text-xs text-gray-500 block mb-1">Yaroqlilik muddati (ixtiyoriy)</label>
                    <input
                      type="date"
                      value={rcExpiry}
                      onChange={(e) => setRcExpiry(e.target.value)}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                    />
                  </div>
                  <input
                    placeholder="Izoh (ixtiyoriy)"
                    value={rcNotes}
                    onChange={(e) => setRcNotes(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                  />
                  {formError && <p className="text-red-500 text-xs">{formError}</p>}
                  <div className="flex gap-2 pt-2">
                    <button type="button" onClick={() => setModal(null)} className="flex-1 py-2 border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50">Bekor</button>
                    <button type="submit" disabled={saving} className="flex-1 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 disabled:opacity-50">
                      {saving ? 'Saqlanmoqda...' : 'Kirim qilish'}
                    </button>
                  </div>
                </form>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
