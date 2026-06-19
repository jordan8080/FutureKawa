import { useState } from 'react'
import { Button } from '../ui/Button'

const inputCls =
  'w-full text-sm bg-gray-800 border border-gray-700 text-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:border-amber-500'

const VARIETIES = ['Arabica', 'Robusta']
const GRADES = ['Grade 1', 'Grade 2', 'Specialty']

export function NewLotForm({ warehouses, onSubmit, onCancel }) {
  const [form, setForm] = useState({
    warehouseId: warehouses[0]?.id ?? '',
    exploitation: warehouses[0]?.exploitation ?? '',
    weight: 1000,
    variety: 'Arabica',
    grade: 'Grade 1',
  })
  const [saving, setSaving] = useState(false)
  const set = (k, v) => setForm(f => ({ ...f, [k]: v }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.warehouseId) return
    setSaving(true)
    try {
      await onSubmit({ ...form, weight: Number(form.weight) })
    } finally {
      setSaving(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="bg-gray-800/40 border border-gray-700 rounded-xl p-4 mb-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
      <label className="text-xs text-gray-400 space-y-1">
        Entrepôt
        <select className={inputCls} value={form.warehouseId}
          onChange={e => {
            const w = warehouses.find(x => x.id === e.target.value)
            set('warehouseId', e.target.value)
            if (w) set('exploitation', w.exploitation)
          }}>
          {warehouses.map(w => <option key={w.id} value={w.id}>{w.name}</option>)}
        </select>
      </label>
      <label className="text-xs text-gray-400 space-y-1">
        Exploitation
        <input className={inputCls} value={form.exploitation}
          onChange={e => set('exploitation', e.target.value)} required />
      </label>
      <label className="text-xs text-gray-400 space-y-1">
        Poids (kg)
        <input type="number" min="1" className={inputCls} value={form.weight}
          onChange={e => set('weight', e.target.value)} required />
      </label>
      <label className="text-xs text-gray-400 space-y-1">
        Variété
        <select className={inputCls} value={form.variety} onChange={e => set('variety', e.target.value)}>
          {VARIETIES.map(v => <option key={v} value={v}>{v}</option>)}
        </select>
      </label>
      <label className="text-xs text-gray-400 space-y-1">
        Grade
        <select className={inputCls} value={form.grade} onChange={e => set('grade', e.target.value)}>
          {GRADES.map(g => <option key={g} value={g}>{g}</option>)}
        </select>
      </label>
      <div className="flex items-end gap-2">
        <Button type="submit" variant="primary" size="sm" disabled={saving}>
          {saving ? 'Création…' : 'Créer le lot'}
        </Button>
        <Button type="button" variant="ghost" size="sm" onClick={onCancel}>Annuler</Button>
      </div>
    </form>
  )
}
