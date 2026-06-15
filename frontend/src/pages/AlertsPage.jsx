import { useState, useEffect } from 'react'
import { AlertItem } from '../components/alerts/AlertItem'
import { PageLoader } from '../components/ui/LoadingSpinner'
import { alertsApi } from '../api'
import { COUNTRIES_CONFIG } from '../data/mockData'

const countries = [{ id: 'all', name: 'Tous les pays', emoji: '🌍' }, ...Object.values(COUNTRIES_CONFIG)]
const TYPES = [
  { value: 'all', label: 'Tous les types' },
  { value: 'temperature', label: '🌡️ Température' },
  { value: 'humidity', label: '💧 Humidité' },
  { value: 'lot_age', label: '⏰ Lot périmé' },
]
const STATUSES = [
  { value: 'all', label: 'Tous les statuts' },
  { value: 'active', label: 'Actives' },
  { value: 'resolved', label: 'Résolues' },
]

export function AlertsPage() {
  const [loading, setLoading] = useState(true)
  const [alerts, setAlerts] = useState([])
  const [countryFilter, setCountryFilter] = useState('all')
  const [typeFilter, setTypeFilter] = useState('all')
  const [statusFilter, setStatusFilter] = useState('all')

  useEffect(() => {
    alertsApi.getAll().then(setAlerts).finally(() => setLoading(false))
  }, [])

  const handleResolve = async (alertId) => {
    await alertsApi.resolve(alertId)
    setAlerts(prev => prev.map(a => a.id === alertId ? { ...a, status: 'resolved' } : a))
  }

  const filtered = alerts.filter(a => {
    const cOk = countryFilter === 'all' || a.country === countryFilter
    const tOk = typeFilter === 'all' || a.type === typeFilter
    const sOk = statusFilter === 'all' || a.status === statusFilter
    return cOk && tOk && sOk
  })

  const activeCount = alerts.filter(a => a.status === 'active').length
  const criticalCount = alerts.filter(a => a.status === 'active' && a.severity === 'critical').length

  if (loading) return <PageLoader />

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">Alertes</h1>
        <p className="text-gray-500 text-sm mt-1">Surveillance des conditions et des lots à risque</p>
      </div>

      {/* Résumé */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-4 text-center">
          <p className="text-3xl font-bold text-amber-400">{activeCount}</p>
          <p className="text-xs text-gray-500 mt-1">Alertes actives</p>
        </div>
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-4 text-center">
          <p className="text-3xl font-bold text-red-400">{criticalCount}</p>
          <p className="text-xs text-gray-500 mt-1">Critiques</p>
        </div>
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-4 text-center">
          <p className="text-3xl font-bold text-gray-400">{alerts.filter(a => a.status === 'resolved').length}</p>
          <p className="text-xs text-gray-500 mt-1">Résolues</p>
        </div>
      </div>

      {/* Filtres */}
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-xs text-gray-500 mr-1">Filtrer :</span>
        <select
          value={countryFilter}
          onChange={e => setCountryFilter(e.target.value)}
          className="text-xs bg-gray-800 border border-gray-700 text-gray-300 rounded-lg px-3 py-1.5 focus:outline-none focus:border-amber-500"
        >
          {countries.map(c => (
            <option key={c.id} value={c.id}>{c.emoji} {c.name}</option>
          ))}
        </select>
        <select
          value={typeFilter}
          onChange={e => setTypeFilter(e.target.value)}
          className="text-xs bg-gray-800 border border-gray-700 text-gray-300 rounded-lg px-3 py-1.5 focus:outline-none focus:border-amber-500"
        >
          {TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
        </select>
        <select
          value={statusFilter}
          onChange={e => setStatusFilter(e.target.value)}
          className="text-xs bg-gray-800 border border-gray-700 text-gray-300 rounded-lg px-3 py-1.5 focus:outline-none focus:border-amber-500"
        >
          {STATUSES.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
        </select>
        <span className="text-xs text-gray-600 ml-auto">{filtered.length} résultat{filtered.length > 1 ? 's' : ''}</span>
      </div>

      {/* Liste */}
      {filtered.length === 0 ? (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-12 text-center">
          <span className="text-4xl">✅</span>
          <p className="text-gray-300 font-medium mt-4">Aucune alerte correspondante</p>
          <p className="text-gray-600 text-sm mt-1">Modifiez les filtres ou vérifiez plus tard</p>
        </div>
      ) : (
        <div className="space-y-3">
          {/* Séparation actives / résolues */}
          {statusFilter === 'all' && filtered.some(a => a.status === 'active') && (
            <>
              <p className="text-xs font-semibold text-gray-500 uppercase tracking-widest mb-1 mt-2">
                Alertes actives
              </p>
              {filtered.filter(a => a.status === 'active').map(alert => (
                <AlertItem key={alert.id} alert={alert} onResolve={handleResolve} />
              ))}
            </>
          )}
          {statusFilter === 'all' && filtered.some(a => a.status === 'resolved') && (
            <>
              <p className="text-xs font-semibold text-gray-600 uppercase tracking-widest mb-1 mt-6">
                Alertes résolues
              </p>
              {filtered.filter(a => a.status === 'resolved').map(alert => (
                <AlertItem key={alert.id} alert={alert} />
              ))}
            </>
          )}
          {statusFilter !== 'all' && filtered.map(alert => (
            <AlertItem key={alert.id} alert={alert} onResolve={handleResolve} />
          ))}
        </div>
      )}
    </div>
  )
}
