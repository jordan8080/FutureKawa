import { useState } from 'react'
import { Button } from '../ui/Button'

const inputCls =
  'w-full text-sm bg-gray-800 border border-gray-700 text-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:border-amber-500'

export function NewWarehouseForm({ onSubmit, onCancel }) {
  const [form, setForm] = useState({ name: '', location: '', exploitation: '' })
  const [saving, setSaving] = useState(false)
  const set = (k, v) => setForm(f => ({ ...f, [k]: v }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      await onSubmit(form)
    } finally {
      setSaving(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="bg-gray-800/40 border border-gray-700 rounded-xl p-4 mb-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
      <label className="text-xs text-gray-400 space-y-1">
        Nom
        <input className={inputCls} value={form.name}
          onChange={e => set('name', e.target.value)} placeholder="Entrepôt …" required />
      </label>
      <label className="text-xs text-gray-400 space-y-1">
        Localisation
        <input className={inputCls} value={form.location}
          onChange={e => set('location', e.target.value)} placeholder="Ville" required />
      </label>
      <label className="text-xs text-gray-400 space-y-1">
        Exploitation
        <input className={inputCls} value={form.exploitation}
          onChange={e => set('exploitation', e.target.value)} placeholder="Fazenda / Finca …" required />
      </label>
      <div className="flex items-end gap-2">
        <Button type="submit" variant="primary" size="sm" disabled={saving}>
          {saving ? 'Création…' : 'Créer'}
        </Button>
        <Button type="button" variant="ghost" size="sm" onClick={onCancel}>Annuler</Button>
      </div>
    </form>
  )
}
