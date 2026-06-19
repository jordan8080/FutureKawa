import { useState, useEffect, useCallback } from 'react'
import { countriesApi } from '../../api'
import { Button } from '../ui/Button'

const inputCls =
  'w-full text-sm bg-gray-800 border border-gray-700 text-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:border-amber-500'

const EMPTY = { id: '', name: '', code: '', emoji: '🏳️', url: '' }

export function CountriesPanel() {
  const [countries, setCountries] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState(EMPTY)
  const [error, setError] = useState('')
  const set = (k, v) => setForm(f => ({ ...f, [k]: v }))

  const reload = useCallback(() => countriesApi.getAll().then(setCountries).catch(() => {}), [])
  useEffect(() => { reload() }, [reload])

  const handleAdd = async (e) => {
    e.preventDefault()
    setError('')
    try {
      await countriesApi.create(form)
      setForm(EMPTY)
      setShowForm(false)
      await reload()
    } catch (err) {
      setError(err.message)
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm(`Retirer le pays « ${id} » du registre central ?`)) return
    try {
      await countriesApi.remove(id)
      await reload()
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
      <div className="flex items-center justify-between mb-3">
        <div>
          <h2 className="text-base font-semibold text-white">Registre des pays (central)</h2>
          <p className="text-xs text-gray-600 mt-0.5">
            Ajout/suppression dans le routage du central. N'instancie pas de backend/base :
            l'URL doit pointer vers un backend pays déjà déployé.
          </p>
        </div>
        <Button size="sm" variant="secondary" onClick={() => setShowForm(s => !s)}>
          {showForm ? 'Fermer' : '+ Pays'}
        </Button>
      </div>

      {error && <p className="text-xs text-red-400 mb-3">{error}</p>}

      {showForm && (
        <form onSubmit={handleAdd} className="grid grid-cols-2 md:grid-cols-5 gap-2 mb-4">
          <input className={inputCls} placeholder="id (ex: peru)" value={form.id} onChange={e => set('id', e.target.value)} required />
          <input className={inputCls} placeholder="Nom" value={form.name} onChange={e => set('name', e.target.value)} required />
          <input className={inputCls} placeholder="Code (PE)" value={form.code} onChange={e => set('code', e.target.value)} required />
          <input className={inputCls} placeholder="🏳️" value={form.emoji} onChange={e => set('emoji', e.target.value)} />
          <input className={inputCls} placeholder="http://backend-peru:8000" value={form.url} onChange={e => set('url', e.target.value)} required />
          <div className="col-span-2 md:col-span-5">
            <Button type="submit" variant="primary" size="sm">Enregistrer le pays</Button>
          </div>
        </form>
      )}

      <div className="flex flex-wrap gap-2">
        {countries.map(c => (
          <span key={c.id} className="inline-flex items-center gap-2 bg-gray-800/60 border border-gray-700 rounded-lg px-3 py-1.5 text-sm text-gray-200">
            <span>{c.emoji}</span>{c.name}
            <span className="text-xs text-gray-500">({c.code})</span>
            <button onClick={() => handleDelete(c.id)} className="text-gray-500 hover:text-red-400 ml-1" title="Retirer">✕</button>
          </span>
        ))}
      </div>
    </div>
  )
}
