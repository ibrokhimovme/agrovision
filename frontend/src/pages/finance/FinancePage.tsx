import { useEffect, useState } from 'react'
import { farmService } from '@/services/batchService'
import {
  batchService,
  expenseService,
  saleService,
  profitService,
  supplierService,
  debtService,
  type RecordExpensePayload,
  type RecordSalePayload,
} from '@/services/batchService'
import type {
  Farm,
  Batch,
  Expense,
  SaleRecord,
  BatchCostSummary,
  BatchProfit,
  ExpenseCategory,
  Supplier,
  DebtorCreditorSummary,
  SalePaymentStatus,
} from '@/types'

// ── Helpers ───────────────────────────────────────────────────────────────────

function fmt(n: number | null | undefined, decimals = 0): string {
  if (n == null) return '—'
  return Number(n).toLocaleString('uz-UZ', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  })
}

const EXPENSE_CATEGORY_LABELS: Record<string, string> = {
  feed: 'Yem',
  veterinary: 'Veterinariya',
  labor: 'Mehnat haqi',
  transport: 'Transport',
  equipment: 'Uskunalar',
  utilities: 'Kommunal',
  depreciation: 'Amortizatsiya',
  other: 'Boshqa',
}

const PAYMENT_LABELS: Record<string, string> = {
  paid: "To'langan",
  pending: 'Kutilmoqda',
  partial: 'Qisman to\'langan',
}

const PAYMENT_BADGE: Record<string, string> = {
  paid: 'bg-green-100 text-green-700',
  pending: 'bg-yellow-100 text-yellow-700',
  partial: 'bg-orange-100 text-orange-700',
}

const CATEGORY_BADGE: Record<string, string> = {
  feed: 'bg-yellow-100 text-yellow-700',
  veterinary: 'bg-blue-100 text-blue-700',
  labor: 'bg-purple-100 text-purple-700',
  transport: 'bg-orange-100 text-orange-700',
  equipment: 'bg-gray-100 text-gray-700',
  utilities: 'bg-cyan-100 text-cyan-700',
  depreciation: 'bg-red-100 text-red-700',
  other: 'bg-gray-100 text-gray-500',
}

function SummaryCard({
  label,
  value,
  sub,
  color,
}: {
  label: string
  value: string
  sub?: string
  color?: string
}) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">{label}</p>
      <p className={`text-2xl font-bold ${color ?? 'text-gray-900'}`}>{value}</p>
      {sub && <p className="text-xs text-gray-400 mt-0.5">{sub}</p>}
    </div>
  )
}

// ── Main component ────────────────────────────────────────────────────────────

type ModalType = 'expense' | 'sale' | 'supplier' | 'salePayment' | 'expensePayment' | null
type Tab = 'expenses' | 'sales' | 'debts'

export default function FinancePage() {
  const [farms, setFarms] = useState<Farm[]>([])
  const [selectedFarmId, setSelectedFarmId] = useState<string>('')
  const [batches, setBatches] = useState<Batch[]>([])
  const [selectedBatchId, setSelectedBatchId] = useState<string>('')
  const [profit, setProfit] = useState<BatchProfit | null>(null)
  const [costSummary, setCostSummary] = useState<BatchCostSummary | null>(null)
  const [expenses, setExpenses] = useState<Expense[]>([])
  const [sales, setSales] = useState<SaleRecord[]>([])
  const [suppliers, setSuppliers] = useState<Supplier[]>([])
  const [debtSummary, setDebtSummary] = useState<DebtorCreditorSummary | null>(null)
  const [loading, setLoading] = useState(false)
  const [tab, setTab] = useState<Tab>('expenses')
  const [modal, setModal] = useState<ModalType>(null)
  const [saving, setSaving] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)

  // Expense form
  const [expCategory, setExpCategory] = useState<ExpenseCategory>('feed')
  const [expDescription, setExpDescription] = useState('')
  const [expAmount, setExpAmount] = useState('')
  const [expSupplierId, setExpSupplierId] = useState('')
  const [expAmountPaid, setExpAmountPaid] = useState('')
  const [expNotes, setExpNotes] = useState('')

  // Sale form
  const [saleCustomer, setSaleCustomer] = useState('')
  const [salePhone, setSalePhone] = useState('')
  const [saleHeads, setSaleHeads] = useState('')
  const [saleKg, setSaleKg] = useState('')
  const [salePricePerKg, setSalePricePerKg] = useState('')
  const [salePayment, setSalePayment] = useState<SalePaymentStatus>('paid')
  const [saleAmountPaid, setSaleAmountPaid] = useState('')

  // Supplier form
  const [supplierName, setSupplierName] = useState('')
  const [supplierPhone, setSupplierPhone] = useState('')

  // Payment-recording form (shared by sale/expense partial payments)
  const [paymentTargetId, setPaymentTargetId] = useState<string>('')
  const [paymentAmount, setPaymentAmount] = useState('')

  // Load farms on mount
  useEffect(() => {
    farmService.listFarms().then((res) => {
      setFarms(res.data)
      if (res.data.length > 0) setSelectedFarmId(res.data[0].id)
    })
  }, [])

  // Load batches when farm changes
  useEffect(() => {
    if (!selectedFarmId) return
    batchService
      .listBatches({ farm_id: selectedFarmId, page_size: 100 })
      .then((res) => {
        setBatches(res.data)
        setSelectedBatchId(res.data.length > 0 ? res.data[0].id : '')
      })
  }, [selectedFarmId])

  // Load finance data when batch changes
  useEffect(() => {
    if (!selectedBatchId) {
      setProfit(null)
      setCostSummary(null)
      setExpenses([])
      setSales([])
      return
    }
    setLoading(true)
    Promise.all([
      profitService.getBatchProfit(selectedBatchId),
      expenseService.getBatchCostSummary(selectedBatchId),
      expenseService.listBatchExpenses(selectedBatchId, 1, 100),
      saleService.listSales(selectedBatchId, 1, 100),
    ])
      .then(([profitRes, costRes, expRes, salesRes]) => {
        setProfit(profitRes.data)
        setCostSummary(costRes.data)
        setExpenses(expRes.data)
        setSales(salesRes.data)
      })
      .finally(() => setLoading(false))
  }, [selectedBatchId])

  // EX-11 (execution-v2): suppliers and debtor/creditor summary are farm-scoped, not batch-scoped.
  async function refreshDebtData() {
    if (!selectedFarmId) return
    const [supplierRes, debtRes] = await Promise.all([
      supplierService.listSuppliers(selectedFarmId),
      debtService.getDebtorCreditorSummary(selectedFarmId),
    ])
    setSuppliers(supplierRes.data)
    setDebtSummary(debtRes.data)
  }

  useEffect(() => {
    if (!selectedFarmId) {
      setSuppliers([])
      setDebtSummary(null)
      return
    }
    refreshDebtData()
  }, [selectedFarmId])

  async function refreshFinance() {
    if (!selectedBatchId) return
    const [profitRes, costRes, expRes, salesRes] = await Promise.all([
      profitService.getBatchProfit(selectedBatchId),
      expenseService.getBatchCostSummary(selectedBatchId),
      expenseService.listBatchExpenses(selectedBatchId, 1, 100),
      saleService.listSales(selectedBatchId, 1, 100),
    ])
    setProfit(profitRes.data)
    setCostSummary(costRes.data)
    setExpenses(expRes.data)
    setSales(salesRes.data)
    await refreshDebtData()
  }

  async function handleAddExpense(e: React.FormEvent) {
    e.preventDefault()
    if (!selectedBatchId || !selectedFarmId) return
    setSaving(true)
    setFormError(null)
    try {
      const payload: RecordExpensePayload = {
        farm_id: selectedFarmId,
        batch_id: selectedBatchId,
        category: expCategory,
        description: expDescription,
        amount: parseFloat(expAmount),
        supplier_id: expSupplierId || undefined,
        amount_paid: expAmountPaid !== '' ? parseFloat(expAmountPaid) : undefined,
        notes: expNotes || undefined,
      }
      await expenseService.recordExpense(payload)
      await refreshFinance()
      setModal(null)
      setExpDescription('')
      setExpAmount('')
      setExpSupplierId('')
      setExpAmountPaid('')
      setExpNotes('')
    } catch {
      setFormError("Xarajat qo'shishda xatolik yuz berdi")
    } finally {
      setSaving(false)
    }
  }

  async function handleAddSupplier(e: React.FormEvent) {
    e.preventDefault()
    if (!selectedFarmId) return
    setSaving(true)
    setFormError(null)
    try {
      await supplierService.createSupplier({
        farm_id: selectedFarmId,
        name: supplierName,
        phone: supplierPhone || undefined,
      })
      await refreshDebtData()
      setModal(null)
      setSupplierName('')
      setSupplierPhone('')
    } catch {
      setFormError("Ta'minotchi qo'shishda xatolik yuz berdi")
    } finally {
      setSaving(false)
    }
  }

  async function handleRecordSalePayment(e: React.FormEvent) {
    e.preventDefault()
    setSaving(true)
    setFormError(null)
    try {
      await saleService.recordSalePayment(paymentTargetId, parseFloat(paymentAmount))
      await refreshFinance()
      setModal(null)
      setPaymentAmount('')
    } catch {
      setFormError("To'lovni saqlashda xatolik yuz berdi")
    } finally {
      setSaving(false)
    }
  }

  async function handleRecordExpensePayment(e: React.FormEvent) {
    e.preventDefault()
    setSaving(true)
    setFormError(null)
    try {
      await expenseService.recordExpensePayment(paymentTargetId, parseFloat(paymentAmount))
      await refreshFinance()
      setModal(null)
      setPaymentAmount('')
    } catch {
      setFormError("To'lovni saqlashda xatolik yuz berdi")
    } finally {
      setSaving(false)
    }
  }

  async function handleAddSale(e: React.FormEvent) {
    e.preventDefault()
    if (!selectedBatchId || !selectedFarmId) return
    setSaving(true)
    setFormError(null)
    try {
      const payload: RecordSalePayload = {
        farm_id: selectedFarmId,
        customer_name: saleCustomer,
        customer_phone: salePhone || undefined,
        head_count: parseInt(saleHeads),
        quantity_kg: parseFloat(saleKg),
        price_per_kg_uzs: parseFloat(salePricePerKg),
        payment_status: salePayment,
        amount_paid: salePayment === 'partial' ? parseFloat(saleAmountPaid) : undefined,
      }
      await saleService.recordSale(selectedBatchId, payload)
      await refreshFinance()
      setModal(null)
      setSaleCustomer('')
      setSalePhone('')
      setSaleHeads('')
      setSaleKg('')
      setSalePricePerKg('')
      setSaleAmountPaid('')
    } catch {
      setFormError('Sotuv qo\'shishda xatolik yuz berdi')
    } finally {
      setSaving(false)
    }
  }

  const profitColor =
    profit && profit.gross_profit_uzs >= 0 ? 'text-green-700' : 'text-red-600'

  const selectedBatch = batches.find((b) => b.id === selectedBatchId)

  return (
    <div className="p-6 max-w-5xl">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Moliya</h1>
        <p className="text-sm text-gray-500 mt-1">Partiya bo'yicha xarajatlar, sotuvlar va foyda tahlili</p>
      </div>

      {/* Selectors */}
      <div className="flex flex-wrap gap-3 mb-6">
        {farms.length > 1 && (
          <select
            value={selectedFarmId}
            onChange={(e) => setSelectedFarmId(e.target.value)}
            className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            {farms.map((f) => (
              <option key={f.id} value={f.id}>{f.name}</option>
            ))}
          </select>
        )}
        <select
          value={selectedBatchId}
          onChange={(e) => setSelectedBatchId(e.target.value)}
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
          disabled={batches.length === 0}
        >
          {batches.length === 0 && <option value="">Partiyalar yo'q</option>}
          {batches.map((b) => (
            <option key={b.id} value={b.id}>
              {b.batch_code} — {b.current_count} bosh ({b.status})
            </option>
          ))}
        </select>
      </div>

      {!selectedBatchId ? (
        <div className="text-center py-16 text-gray-400">Partiya tanlang</div>
      ) : loading ? (
        <div className="flex justify-center py-16">
          <div className="w-8 h-8 border-4 border-green-500 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : (
        <>
          {/* Profit summary cards */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
            <SummaryCard
              label="Jami daromad"
              value={profit ? fmt(profit.total_revenue_uzs) + ' UZS' : '—'}
            />
            <SummaryCard
              label="Jami xarajat"
              value={profit ? fmt(profit.total_cost_uzs) + ' UZS' : '—'}
            />
            <SummaryCard
              label="Sof foyda"
              value={profit ? fmt(profit.gross_profit_uzs) + ' UZS' : '—'}
              color={profit ? profitColor : undefined}
            />
            <SummaryCard
              label="Foyda marjasi"
              value={profit ? fmt(profit.profit_margin_pct, 1) + '%' : '—'}
              color={profit ? profitColor : undefined}
              sub={profit ? `${profit.sale_count} sotuv · ${profit.expense_count} xarajat` : undefined}
            />
          </div>

          {/* Cost breakdown */}
          {costSummary && Object.keys(costSummary.breakdown).length > 0 && (
            <div className="bg-white rounded-xl border border-gray-200 p-4 mb-6">
              <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-3">
                Xarajat tarkibi
              </h2>
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
                {Object.entries(costSummary.breakdown).map(([cat, amount]) => (
                  <div key={cat}>
                    <p className="text-xs text-gray-500 mb-0.5">
                      {EXPENSE_CATEGORY_LABELS[cat] ?? cat}
                    </p>
                    <p className="text-sm font-semibold text-gray-900">{fmt(amount)} UZS</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Tabs */}
          <div className="flex gap-1 mb-4 bg-gray-100 p-1 rounded-lg w-fit">
            {(['expenses', 'sales', 'debts'] as Tab[]).map((t) => (
              <button
                key={t}
                onClick={() => setTab(t)}
                className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
                  tab === t
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                {t === 'expenses'
                  ? `Xarajatlar (${expenses.length})`
                  : t === 'sales'
                  ? `Sotuvlar (${sales.length})`
                  : "Qarzlar"}
              </button>
            ))}
          </div>

          {tab === 'expenses' && (
            <>
              <div className="flex justify-end mb-3">
                <button
                  onClick={() => {
                    setFormError(null)
                    setModal('expense')
                  }}
                  className="px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 transition-colors"
                >
                  + Xarajat qo'shish
                </button>
              </div>
              {expenses.length === 0 ? (
                <div className="text-center py-12 text-gray-400">Xarajatlar yo'q</div>
              ) : (
                <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
                  <table className="min-w-full divide-y divide-gray-100">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Sana</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Kategoriya</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tavsif</th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Miqdor</th>
                        <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">To'lov</th>
                        <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase"></th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-50">
                      {expenses.map((exp) => (
                        <tr key={exp.id} className="hover:bg-gray-50">
                          <td className="px-4 py-3 text-sm text-gray-500 whitespace-nowrap">
                            {new Date(exp.expense_date ?? exp.created_at).toLocaleDateString('uz-UZ')}
                          </td>
                          <td className="px-4 py-3">
                            <span className={`text-xs px-2 py-1 rounded-full font-medium ${CATEGORY_BADGE[exp.category] ?? 'bg-gray-100 text-gray-600'}`}>
                              {EXPENSE_CATEGORY_LABELS[exp.category] ?? exp.category}
                            </span>
                          </td>
                          <td className="px-4 py-3 text-sm text-gray-900">{exp.description}</td>
                          <td className="px-4 py-3 text-sm font-medium text-gray-900 text-right whitespace-nowrap">
                            {fmt(exp.amount)} {exp.currency}
                          </td>
                          <td className="px-4 py-3 text-center">
                            <span className={`text-xs px-2 py-1 rounded-full font-medium ${PAYMENT_BADGE[exp.payment_status]}`}>
                              {PAYMENT_LABELS[exp.payment_status]}
                            </span>
                          </td>
                          <td className="px-4 py-3 text-center">
                            {exp.outstanding_amount > 0 && (
                              <button
                                onClick={() => {
                                  setFormError(null)
                                  setPaymentTargetId(exp.id)
                                  setPaymentAmount('')
                                  setModal('expensePayment')
                                }}
                                className="text-xs text-green-700 hover:underline whitespace-nowrap"
                              >
                                To'lov qo'shish
                              </button>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </>
          )}

          {tab === 'sales' && (
            <>
              <div className="flex justify-end mb-3">
                <button
                  onClick={() => {
                    setFormError(null)
                    setModal('sale')
                  }}
                  className="px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 transition-colors"
                  disabled={selectedBatch?.status === 'completed'}
                >
                  + Sotuv qo'shish
                </button>
              </div>
              {sales.length === 0 ? (
                <div className="text-center py-12 text-gray-400">Sotuvlar yo'q</div>
              ) : (
                <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
                  <table className="min-w-full divide-y divide-gray-100">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Sana</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Xaridor</th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Bosh</th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Kg</th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Narx/kg</th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Jami</th>
                        <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">To'lov</th>
                        <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase"></th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-50">
                      {sales.map((sale) => (
                        <tr key={sale.id} className="hover:bg-gray-50">
                          <td className="px-4 py-3 text-sm text-gray-500 whitespace-nowrap">
                            {new Date(sale.sold_at).toLocaleDateString('uz-UZ')}
                          </td>
                          <td className="px-4 py-3 text-sm text-gray-900">
                            {sale.customer_name}
                            {sale.customer_phone && (
                              <span className="ml-2 text-xs text-gray-400">{sale.customer_phone}</span>
                            )}
                          </td>
                          <td className="px-4 py-3 text-sm text-right text-gray-900">{fmt(sale.head_count)}</td>
                          <td className="px-4 py-3 text-sm text-right text-gray-900">{fmt(sale.quantity_kg, 1)}</td>
                          <td className="px-4 py-3 text-sm text-right text-gray-900">{fmt(sale.price_per_kg_uzs)}</td>
                          <td className="px-4 py-3 text-sm text-right font-medium text-gray-900">
                            {fmt(sale.total_revenue_uzs)} UZS
                            {sale.outstanding_amount > 0 && (
                              <span className="block text-xs text-orange-600 font-normal">
                                Qarz: {fmt(sale.outstanding_amount)}
                              </span>
                            )}
                          </td>
                          <td className="px-4 py-3 text-center">
                            <span className={`text-xs px-2 py-1 rounded-full font-medium ${PAYMENT_BADGE[sale.payment_status]}`}>
                              {PAYMENT_LABELS[sale.payment_status]}
                            </span>
                          </td>
                          <td className="px-4 py-3 text-center">
                            {sale.outstanding_amount > 0 && (
                              <button
                                onClick={() => {
                                  setFormError(null)
                                  setPaymentTargetId(sale.id)
                                  setPaymentAmount('')
                                  setModal('salePayment')
                                }}
                                className="text-xs text-green-700 hover:underline whitespace-nowrap"
                              >
                                To'lov qo'shish
                              </button>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </>
          )}

          {tab === 'debts' && (
            <>
              <div className="flex justify-end mb-3">
                <button
                  onClick={() => {
                    setFormError(null)
                    setModal('supplier')
                  }}
                  className="px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 transition-colors"
                >
                  + Ta'minotchi qo'shish
                </button>
              </div>

              <div className="grid grid-cols-2 gap-4 mb-6">
                <SummaryCard
                  label="Mijozlardan qarzlar (debitor)"
                  value={debtSummary ? fmt(debtSummary.total_receivable_uzs) + ' UZS' : '—'}
                  color="text-orange-600"
                />
                <SummaryCard
                  label="Ta'minotchilarga qarzlar (kreditor)"
                  value={debtSummary ? fmt(debtSummary.total_payable_uzs) + ' UZS' : '—'}
                  color="text-red-600"
                />
              </div>

              <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-3">
                Mijozlar qarzi (farm bo'yicha)
              </h2>
              {!debtSummary || debtSummary.debtors.length === 0 ? (
                <div className="text-center py-8 text-gray-400 mb-6">Qarzdor mijozlar yo'q</div>
              ) : (
                <div className="bg-white rounded-xl border border-gray-200 overflow-hidden mb-6">
                  <table className="min-w-full divide-y divide-gray-100">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Mijoz</th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Sotuvlar</th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Qarz</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-50">
                      {debtSummary.debtors.map((d, i) => (
                        <tr key={i} className="hover:bg-gray-50">
                          <td className="px-4 py-3 text-sm text-gray-900">
                            {d.customer_name}
                            {d.customer_phone && (
                              <span className="ml-2 text-xs text-gray-400">{d.customer_phone}</span>
                            )}
                          </td>
                          <td className="px-4 py-3 text-sm text-right text-gray-900">{d.sale_count}</td>
                          <td className="px-4 py-3 text-sm text-right font-medium text-orange-600">
                            {fmt(d.outstanding_amount)} UZS
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-3">
                Ta'minotchilarga qarzlar (farm bo'yicha)
              </h2>
              {!debtSummary || debtSummary.creditors.length === 0 ? (
                <div className="text-center py-8 text-gray-400">Qarzlar yo'q</div>
              ) : (
                <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
                  <table className="min-w-full divide-y divide-gray-100">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Ta'minotchi</th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Xarajatlar</th>
                        <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Qarz</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-50">
                      {debtSummary.creditors.map((c) => (
                        <tr key={c.supplier_id} className="hover:bg-gray-50">
                          <td className="px-4 py-3 text-sm text-gray-900">{c.supplier_name}</td>
                          <td className="px-4 py-3 text-sm text-right text-gray-900">{c.expense_count}</td>
                          <td className="px-4 py-3 text-sm text-right font-medium text-red-600">
                            {fmt(c.outstanding_amount)} UZS
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </>
          )}
        </>
      )}

      {/* Modals */}
      {modal && (
        <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl shadow-xl p-6 w-full max-w-md">
            {modal === 'expense' && (
              <>
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Xarajat qo'shish</h2>
                <form onSubmit={handleAddExpense} className="space-y-3">
                  <select
                    value={expCategory}
                    onChange={(e) => setExpCategory(e.target.value as ExpenseCategory)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                  >
                    {Object.entries(EXPENSE_CATEGORY_LABELS).map(([v, l]) => (
                      <option key={v} value={v}>{l}</option>
                    ))}
                  </select>
                  <input
                    required
                    placeholder="Tavsif *"
                    value={expDescription}
                    onChange={(e) => setExpDescription(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                  />
                  <div>
                    <label className="text-xs text-gray-500 block mb-1">Miqdor (UZS) *</label>
                    <input
                      required
                      type="number"
                      min="0"
                      step="1"
                      placeholder="0"
                      value={expAmount}
                      onChange={(e) => setExpAmount(e.target.value)}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-gray-500 block mb-1">Ta'minotchi (ixtiyoriy)</label>
                    <select
                      value={expSupplierId}
                      onChange={(e) => setExpSupplierId(e.target.value)}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                    >
                      <option value="">— Yo'q —</option>
                      {suppliers.map((s) => (
                        <option key={s.id} value={s.id}>{s.name}</option>
                      ))}
                    </select>
                  </div>
                  {expSupplierId && (
                    <div>
                      <label className="text-xs text-gray-500 block mb-1">
                        To'langan summa (bo'sh = to'liq to'langan)
                      </label>
                      <input
                        type="number"
                        min="0"
                        step="1"
                        placeholder={expAmount || '0'}
                        value={expAmountPaid}
                        onChange={(e) => setExpAmountPaid(e.target.value)}
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                      />
                    </div>
                  )}
                  <input
                    placeholder="Izoh (ixtiyoriy)"
                    value={expNotes}
                    onChange={(e) => setExpNotes(e.target.value)}
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

            {modal === 'sale' && (
              <>
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Sotuv qo'shish</h2>
                <form onSubmit={handleAddSale} className="space-y-3">
                  <input
                    required
                    placeholder="Xaridor nomi *"
                    value={saleCustomer}
                    onChange={(e) => setSaleCustomer(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                  />
                  <input
                    placeholder="Telefon (ixtiyoriy)"
                    value={salePhone}
                    onChange={(e) => setSalePhone(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                  />
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="text-xs text-gray-500 block mb-1">Bosh soni *</label>
                      <input
                        required
                        type="number"
                        min="1"
                        placeholder="0"
                        value={saleHeads}
                        onChange={(e) => setSaleHeads(e.target.value)}
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                      />
                    </div>
                    <div>
                      <label className="text-xs text-gray-500 block mb-1">Og'irlik (kg) *</label>
                      <input
                        required
                        type="number"
                        min="0.01"
                        step="0.01"
                        placeholder="0.00"
                        value={saleKg}
                        onChange={(e) => setSaleKg(e.target.value)}
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="text-xs text-gray-500 block mb-1">Narx 1 kg (UZS) *</label>
                    <input
                      required
                      type="number"
                      min="0"
                      step="1"
                      placeholder="0"
                      value={salePricePerKg}
                      onChange={(e) => setSalePricePerKg(e.target.value)}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-gray-500 block mb-1">To'lov holati</label>
                    <select
                      value={salePayment}
                      onChange={(e) => setSalePayment(e.target.value as SalePaymentStatus)}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                    >
                      <option value="paid">To'langan</option>
                      <option value="pending">Kutilmoqda</option>
                      <option value="partial">Qisman to'langan</option>
                    </select>
                  </div>
                  {salePayment === 'partial' && (
                    <div>
                      <label className="text-xs text-gray-500 block mb-1">To'langan summa (UZS) *</label>
                      <input
                        required
                        type="number"
                        min="0"
                        step="1"
                        placeholder="0"
                        value={saleAmountPaid}
                        onChange={(e) => setSaleAmountPaid(e.target.value)}
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                      />
                    </div>
                  )}
                  {salePricePerKg && saleKg && (
                    <p className="text-sm text-green-700 font-medium bg-green-50 p-2 rounded-lg">
                      Jami: {fmt(parseFloat(salePricePerKg) * parseFloat(saleKg))} UZS
                    </p>
                  )}
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

            {modal === 'supplier' && (
              <>
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Ta'minotchi qo'shish</h2>
                <form onSubmit={handleAddSupplier} className="space-y-3">
                  <input
                    required
                    placeholder="Ta'minotchi nomi *"
                    value={supplierName}
                    onChange={(e) => setSupplierName(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                  />
                  <input
                    placeholder="Telefon (ixtiyoriy)"
                    value={supplierPhone}
                    onChange={(e) => setSupplierPhone(e.target.value)}
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

            {(modal === 'salePayment' || modal === 'expensePayment') && (
              <>
                <h2 className="text-lg font-semibold text-gray-900 mb-4">To'lov qo'shish</h2>
                <form
                  onSubmit={modal === 'salePayment' ? handleRecordSalePayment : handleRecordExpensePayment}
                  className="space-y-3"
                >
                  <div>
                    <label className="text-xs text-gray-500 block mb-1">Summa (UZS) *</label>
                    <input
                      required
                      autoFocus
                      type="number"
                      min="0"
                      step="1"
                      placeholder="0"
                      value={paymentAmount}
                      onChange={(e) => setPaymentAmount(e.target.value)}
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
          </div>
        </div>
      )}
    </div>
  )
}
