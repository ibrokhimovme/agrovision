import { useEffect, useState } from 'react'
import { useAuthStore } from '@/store'
import { userService, type CreateUserPayload } from '@/services/userService'
import { useToastStore } from '@/components/ui/Toast'
import type { AdminUser, RoleDetail } from '@/types'

type ModalMode = 'create' | 'edit' | null

const EMPTY_CREATE: CreateUserPayload = {
  email: '',
  full_name: '',
  password: '',
  role_name: '',
  phone: '',
}

export default function UsersPage() {
  const currentUser = useAuthStore((s) => s.user)
  const showToast = useToastStore((s) => s.show)

  const [users, setUsers] = useState<AdminUser[]>([])
  const [roles, setRoles] = useState<RoleDetail[]>([])
  const [loading, setLoading] = useState(true)

  const [modal, setModal] = useState<ModalMode>(null)
  const [editTarget, setEditTarget] = useState<AdminUser | null>(null)

  const [createForm, setCreateForm] = useState(EMPTY_CREATE)
  const [editForm, setEditForm] = useState({ full_name: '', phone: '' })
  const [saving, setSaving] = useState(false)
  const [toggling, setToggling] = useState<string | null>(null)

  const farmId = currentUser?.farm_id ?? ''

  const load = () => {
    if (!farmId) return
    setLoading(true)
    userService
      .listUsers(farmId)
      .then((res) => setUsers(res.data))
      .catch(() => showToast('error', 'Foydalanuvchilar yuklanmadi'))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    if (!farmId) { setLoading(false); return }
    Promise.all([userService.listUsers(farmId), userService.listRoles()])
      .then(([usersRes, rolesRes]) => {
        setUsers(usersRes.data)
        setRoles(rolesRes.data)
      })
      .catch(() => showToast('error', "Ma'lumotlar yuklanmadi"))
      .finally(() => setLoading(false))
  }, [farmId]) // eslint-disable-line react-hooks/exhaustive-deps

  const openCreate = () => {
    setCreateForm({ ...EMPTY_CREATE, role_name: roles[0]?.name ?? '' })
    setModal('create')
  }

  const openEdit = (user: AdminUser) => {
    setEditTarget(user)
    setEditForm({ full_name: user.full_name, phone: user.phone ?? '' })
    setModal('edit')
  }

  const closeModal = () => { setModal(null); setEditTarget(null) }

  const handleCreate = async () => {
    if (!createForm.email.trim() || !createForm.full_name.trim() || !createForm.password || !createForm.role_name) return
    setSaving(true)
    try {
      await userService.createUser({
        ...createForm,
        farm_id: farmId || undefined,
        phone: createForm.phone || undefined,
      })
      showToast('success', 'Foydalanuvchi yaratildi')
      closeModal()
      load()
    } catch {
      showToast('error', 'Xatolik yuz berdi')
    } finally {
      setSaving(false)
    }
  }

  const handleEdit = async () => {
    if (!editTarget || !editForm.full_name.trim()) return
    setSaving(true)
    try {
      await userService.updateUser(editTarget.id, {
        full_name: editForm.full_name.trim(),
        phone: editForm.phone || undefined,
      })
      showToast('success', 'Foydalanuvchi yangilandi')
      closeModal()
      load()
    } catch {
      showToast('error', 'Xatolik yuz berdi')
    } finally {
      setSaving(false)
    }
  }

  const handleToggle = async (user: AdminUser) => {
    setToggling(user.id)
    try {
      await userService.updateUser(user.id, { is_active: !user.is_active })
      showToast('success', user.is_active ? "Foydalanuvchi o'chirildi" : 'Foydalanuvchi faollashtirildi')
      load()
    } catch {
      showToast('error', 'Xatolik yuz berdi')
    } finally {
      setToggling(null)
    }
  }

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Foydalanuvchilar</h1>
        <button
          onClick={openCreate}
          className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 transition-colors"
        >
          <span className="text-lg leading-none">+</span>
          Yangi foydalanuvchi
        </button>
      </div>

      {!farmId && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-sm text-yellow-800">
          Ferma aniqlanmadi. Foydalanuvchilarni ko'rish uchun fermaga bog'langan hisob bilan kiring.
        </div>
      )}

      {loading ? (
        <div className="flex justify-center items-center py-20">
          <div className="animate-spin rounded-full border-2 border-gray-200 border-t-green-600 h-8 w-8" />
        </div>
      ) : users.length === 0 ? (
        <div className="text-center py-20 text-gray-400">
          <p className="mb-4">Foydalanuvchilar topilmadi</p>
          <button onClick={openCreate} className="text-green-600 hover:underline text-sm">
            Birinchi foydalanuvchini yarating
          </button>
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-gray-600">F.I.O</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Email</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600 hidden sm:table-cell">Telefon</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Rol</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Holat</th>
                <th className="text-right px-4 py-3 font-medium text-gray-600">Amallar</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {users.map((user) => (
                <tr key={user.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3">
                    <p className="font-medium text-gray-900">{user.full_name}</p>
                    {user.is_superuser && (
                      <span className="text-xs text-purple-600">Super admin</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-gray-600">{user.email}</td>
                  <td className="px-4 py-3 text-gray-500 hidden sm:table-cell">
                    {user.phone ?? '—'}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex flex-wrap gap-1">
                      {user.roles.length === 0 ? (
                        <span className="text-gray-400 text-xs">Rol yo'q</span>
                      ) : (
                        user.roles.map((r) => (
                          <span
                            key={r.id}
                            className="inline-block px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full text-xs"
                          >
                            {r.display_name}
                          </span>
                        ))
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <button
                      onClick={() => handleToggle(user)}
                      disabled={toggling === user.id}
                      title={user.is_active ? "O'chirish" : 'Faollashtirish'}
                      className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors focus:outline-none disabled:opacity-50 ${
                        user.is_active ? 'bg-green-500' : 'bg-gray-300'
                      }`}
                    >
                      <span
                        className={`inline-block h-3.5 w-3.5 transform rounded-full bg-white shadow transition-transform ${
                          user.is_active ? 'translate-x-4' : 'translate-x-1'
                        }`}
                      />
                    </button>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <button
                      onClick={() => openEdit(user)}
                      className="text-xs px-3 py-1.5 border border-blue-200 text-blue-600 rounded-lg hover:bg-blue-50 transition-colors"
                    >
                      Tahrirlash
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Create Modal */}
      {modal === 'create' && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-md p-6 space-y-4">
            <h2 className="text-lg font-semibold text-gray-900">Yangi foydalanuvchi</h2>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                F.I.O <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={createForm.full_name}
                onChange={(e) => setCreateForm((f) => ({ ...f, full_name: e.target.value }))}
                placeholder="To'liq ism"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email <span className="text-red-500">*</span>
              </label>
              <input
                type="email"
                value={createForm.email}
                onChange={(e) => setCreateForm((f) => ({ ...f, email: e.target.value }))}
                placeholder="email@example.com"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Parol <span className="text-red-500">*</span>
              </label>
              <input
                type="password"
                value={createForm.password}
                onChange={(e) => setCreateForm((f) => ({ ...f, password: e.target.value }))}
                placeholder="Kamida 8 belgi"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Rol <span className="text-red-500">*</span>
              </label>
              <select
                value={createForm.role_name}
                onChange={(e) => setCreateForm((f) => ({ ...f, role_name: e.target.value }))}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                <option value="">Rol tanlang</option>
                {roles.map((r) => (
                  <option key={r.id} value={r.name}>
                    {r.display_name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Telefon</label>
              <input
                type="tel"
                value={createForm.phone}
                onChange={(e) => setCreateForm((f) => ({ ...f, phone: e.target.value }))}
                placeholder="+998 90 123 45 67"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>

            <div className="flex gap-3 pt-2">
              <button
                onClick={handleCreate}
                disabled={saving || !createForm.email.trim() || !createForm.full_name.trim() || !createForm.password || !createForm.role_name}
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

      {/* Edit Modal */}
      {modal === 'edit' && editTarget && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-md p-6 space-y-4">
            <h2 className="text-lg font-semibold text-gray-900">Foydalanuvchini tahrirlash</h2>
            <p className="text-sm text-gray-500">{editTarget.email}</p>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                F.I.O <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={editForm.full_name}
                onChange={(e) => setEditForm((f) => ({ ...f, full_name: e.target.value }))}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Telefon</label>
              <input
                type="tel"
                value={editForm.phone}
                onChange={(e) => setEditForm((f) => ({ ...f, phone: e.target.value }))}
                placeholder="+998 90 123 45 67"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>

            <div className="flex gap-3 pt-2">
              <button
                onClick={handleEdit}
                disabled={saving || !editForm.full_name.trim()}
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
    </div>
  )
}
