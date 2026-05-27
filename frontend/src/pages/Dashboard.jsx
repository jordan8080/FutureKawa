import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { StatCard } from '../components/ui/StatCard'
import { Card } from '../components/ui/Card'
import { StatusBadge } from '../components/ui/Badge'
import { AlertItem } from '../components/alerts/AlertItem'
import { PageLoader } from '../components/ui/LoadingSpinner'
import { lotsApi, alertsApi, warehousesApi } from '../api'
import { COUNTRIES_CONFIG } from '../data/mockData'
import { getWarehouseStatus } from '../utils/statusUtils'

const countries = Object.values(COUNTRIES_CONFIG)

function CountryCard({ country, warehouses, lots }) {
  const navigate = useNavigate()
  const alertCount = lots.filter(l => l.status === 'alerte' || l.status === 'perime').length
  const conformCount = lots.filter(l => l.status === 'conforme').length
  const conformPct = lots.length > 0 ? Math.round((conformCount / lots.length) * 100) : 100

  const warehouseStatuses = warehouses.map(w => getWarehouseStatus(w))
  const hasWarehouseAlert = warehouseStatuses.some(s => s === 'alerte')
  const avgTemp = warehouses.length
    ? (warehouses.reduce((s, w) => s + w.currentTemp, 0) / warehouses.length).toFixed(1)
    : '—'
  const avgHumidity = warehouses.length
    ? (warehouses.reduce((s, w) => s + w.currentHumidity, 0) / warehouses.length).toFixed(1)
    : '—'

  return (
    <div
      onClick={() => navigate(`/pays/${country.id}`)}
      className="bg-gray-900 border border-gray-800 hover:border-gray-700 hover:bg-gray-800/60 rounded-xl p-5 cursor-pointer transition-all duration-200 group"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <span className="text-3xl">{country.emoji}</span>
          <div>
            <h3 className="text-white font-semibold text-base group-hover:text-amber-300 transition-colors">{country.name}</h3>
            <p className="text-gray-500 text-xs">{warehouses.length} entrepôt{warehouses.length > 1 ? 's' : ''}</p>
          </div>
        </div>
        <StatusBadge status={hasWarehouseAlert ? 'alerte' : 'conforme'} />
      </div>

      {/* Conditions */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="bg-gray-800/60 rounded-xl p-3">
          <p className="text-xs text-gray-500 mb-0.5">Température moy.</p>
          <p className="text-xl font-bold text-white">{avgTemp}°C</p>
          <p className="text-xs text-gray-600">Idéal: {country.idealTemp}°C ±{country.toleranceTemp}</p>
        </div>
        <div className="bg-gray-800/60 rounded-xl p-3">
          <p className="text-xs text-gray-500 mb-0.5">Humidité moy.</p>
          <p className="text-xl font-bold text-white">{avgHumidity}%</p>
          <p className="text-xs text-gray-600">Idéal: {country.idealHumidity}% ±{country.toleranceHumidity}</p>
        </div>
      </div>

      {/* Stats lots */}
      <div className="flex items-center justify-between pt-3 border-t border-gray-800">
        <div className="flex items-center gap-4">
          <div>
            <p className="text-xs text-gray-500">Lots</p>
            <p className="text-sm font-semibold text-white">{lots.length}</p>
          </div>
          {alertCount > 0 && (
            <div>
              <p className="text-xs text-gray-500">En alerte</p>
              <p className="text-sm font-semibold text-amber-400">{alertCount}</p>
            </div>
          )}
          <div>
            <p className="text-xs text-gray-500">Conformes</p>
            <p className="text-sm font-semibold text-emerald-400">{conformPct}%</p>
          </div>
        </div>
        <span className="text-gray-600 group-hover:text-amber-400 transition-colors text-lg">›</span>
      </div>
    </div>
  )
}

export function Dashboard() {
  const [loading, setLoading] = useState(true)
  const [lots, setLots] = useState([])
  const [alerts, setAlerts] = useState([])
  const [warehouses, setWarehouses] = useState([])

  useEffect(() => {
    Promise.all([lotsApi.getAll(), alertsApi.getActive(), warehousesApi.getAll()])
      .then(([lotsData, alertsData, warehousesData]) => {
        setLots(lotsData)
        setAlerts(alertsData)
        setWarehouses(warehousesData)
      })
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <PageLoader />

  const totalLots = lots.length
  const activeAlerts = alerts.length
  const perimeLots = lots.filter(l => l.status === 'perime').length
  const conformeLots = lots.filter(l => l.status === 'conforme').length
  const conformePct = totalLots > 0 ? Math.round((conformeLots / totalLots) * 100) : 100

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Page title */}
      <div>
        <h1 className="text-2xl font-bold text-white">Tableau de bord</h1>
        <p className="text-gray-500 text-sm mt-1">Vue consolidée de toutes les exploitations</p>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Lots en stock" value={totalLots} sublabel="Tous pays confondus" icon="📦" accentColor="amber" />
        <StatCard
          label="Alertes actives"
          value={activeAlerts}
          sublabel={activeAlerts > 0 ? 'Action requise' : 'Aucune alerte'}
          icon="🔔"
          accentColor={activeAlerts > 0 ? 'red' : 'emerald'}
        />
        <StatCard
          label="Lots périmés"
          value={perimeLots}
          sublabel="> 365 jours de stockage"
          icon="⏰"
          accentColor={perimeLots > 0 ? 'red' : 'emerald'}
        />
        <StatCard
          label="Taux de conformité"
          value={`${conformePct}%`}
          sublabel={`${conformeLots} lots conformes`}
          icon="✅"
          accentColor="emerald"
        />
      </div>

      {/* Countries */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-base font-semibold text-white">Pays & Exploitations</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {countries.map(country => (
            <CountryCard
              key={country.id}
              country={country}
              warehouses={warehouses.filter(w => w.country === country.id)}
              lots={lots.filter(l => l.country === country.id)}
            />
          ))}
        </div>
      </div>

      {/* Dernières alertes */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-base font-semibold text-white">Alertes récentes</h2>
          <a href="/alertes" className="text-xs text-amber-400 hover:text-amber-300 transition-colors">
            Voir toutes →
          </a>
        </div>
        {alerts.length === 0 ? (
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-8 text-center">
            <span className="text-4xl">✅</span>
            <p className="text-gray-300 font-medium mt-3">Aucune alerte active</p>
            <p className="text-gray-600 text-sm mt-1">Toutes les conditions sont dans les plages acceptables</p>
          </div>
        ) : (
          <div className="space-y-3">
            {alerts.slice(0, 4).map(alert => (
              <AlertItem key={alert.id} alert={alert} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
