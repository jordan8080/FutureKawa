import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Card } from '../components/ui/Card'
import { LotsTable } from '../components/lots/LotsTable'
import { ConditionGauge } from '../components/ui/ConditionGauge'
import { StatusBadge } from '../components/ui/Badge'
import { PageLoader } from '../components/ui/LoadingSpinner'
import { lotsApi, warehousesApi } from '../api'
import { COUNTRIES_CONFIG } from '../data/mockData'
import { getWarehouseStatus } from '../utils/statusUtils'

const STATUS_FILTER_OPTIONS = [
  { value: 'all', label: 'Tous les statuts' },
  { value: 'conforme', label: 'Conformes' },
  { value: 'alerte', label: 'En alerte' },
  { value: 'perime', label: 'Périmés' },
  { value: 'expedie', label: 'Expédiés' },
]

export function CountryPage() {
  const { countryId } = useParams()
  const navigate = useNavigate()
  const country = COUNTRIES_CONFIG[countryId]

  const [loading, setLoading] = useState(true)
  const [lots, setLots] = useState([])
  const [warehouses, setWarehouses] = useState([])
  const [selectedWarehouse, setSelectedWarehouse] = useState('all')
  const [statusFilter, setStatusFilter] = useState('all')

  useEffect(() => {
    if (!country) return
    setLoading(true)
    Promise.all([lotsApi.getByCountry(countryId), warehousesApi.getByCountry(countryId)])
      .then(([lotsData, warehousesData]) => {
        setLots(lotsData)
        setWarehouses(warehousesData)
      })
      .finally(() => setLoading(false))
  }, [countryId])

  if (!country) {
    return (
      <div className="flex flex-col items-center justify-center py-24">
        <span className="text-5xl mb-4">🌍</span>
        <p className="text-gray-300 text-lg font-medium">Pays non trouvé</p>
        <button onClick={() => navigate('/')} className="mt-4 text-amber-400 text-sm hover:underline">
          Retour au dashboard
        </button>
      </div>
    )
  }

  if (loading) return <PageLoader />

  const filteredLots = lots.filter(l => {
    const warehouseOk = selectedWarehouse === 'all' || l.warehouseId === selectedWarehouse
    const statusOk = statusFilter === 'all' || l.status === statusFilter
    return warehouseOk && statusOk
  })

  const alertLots = lots.filter(l => l.status === 'alerte' || l.status === 'perime').length
  const conformeLots = lots.filter(l => l.status === 'conforme').length

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header pays */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="flex items-start justify-between flex-wrap gap-4">
          <div className="flex items-center gap-4">
            <span className="text-5xl">{country.emoji}</span>
            <div>
              <h1 className="text-2xl font-bold text-white">{country.name}</h1>
              <p className="text-gray-500 text-sm mt-0.5">
                {warehouses.length} entrepôt{warehouses.length > 1 ? 's' : ''} · {lots.length} lots
              </p>
            </div>
          </div>
          <div className="flex items-center gap-6 text-sm">
            <div className="text-center">
              <p className="text-gray-500 text-xs">Idéal température</p>
              <p className="text-white font-semibold">{country.idealTemp}°C ± {country.toleranceTemp}</p>
            </div>
            <div className="text-center">
              <p className="text-gray-500 text-xs">Idéal humidité</p>
              <p className="text-white font-semibold">{country.idealHumidity}% ± {country.toleranceHumidity}</p>
            </div>
            <div className="text-center">
              <p className="text-gray-500 text-xs">Responsable</p>
              <p className="text-white font-semibold text-sm">{country.manager}</p>
            </div>
          </div>
        </div>

        {/* Stats rapides */}
        <div className="grid grid-cols-3 gap-4 mt-5 pt-5 border-t border-gray-800">
          <div>
            <p className="text-xs text-gray-500">Lots conformes</p>
            <p className="text-xl font-bold text-emerald-400">{conformeLots}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500">En alerte / périmés</p>
            <p className={`text-xl font-bold ${alertLots > 0 ? 'text-amber-400' : 'text-gray-600'}`}>{alertLots}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Total lots</p>
            <p className="text-xl font-bold text-white">{lots.length}</p>
          </div>
        </div>
      </div>

      {/* Entrepôts + conditions */}
      <div>
        <h2 className="text-base font-semibold text-white mb-3">Conditions actuelles par entrepôt</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {warehouses.map(w => {
            const status = getWarehouseStatus(w)
            const warehouseLots = lots.filter(l => l.warehouseId === w.id)
            return (
              <div
                key={w.id}
                onClick={() => navigate(`/entrepot/${w.id}`)}
                className="bg-gray-900 border border-gray-800 hover:border-gray-700 rounded-xl p-4 cursor-pointer transition-all"
              >
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="text-sm font-semibold text-white">{w.name}</h3>
                    <p className="text-xs text-gray-500 mt-0.5">{w.exploitation} · {w.location}</p>
                  </div>
                  <StatusBadge status={status} />
                </div>
                <div className="space-y-2">
                  <ConditionGauge type="temp" value={w.currentTemp} country={countryId} />
                  <ConditionGauge type="humidity" value={w.currentHumidity} country={countryId} />
                </div>
                <p className="text-xs text-gray-600 mt-3">{warehouseLots.length} lots stockés</p>
              </div>
            )
          })}
        </div>
      </div>

      {/* Lots section */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl">
        <div className="px-5 py-4 border-b border-gray-800 flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-base font-semibold text-white">Lots stockés</h2>
            <p className="text-xs text-gray-500 mt-0.5">Triés par date de stockage (FIFO — les plus anciens en premier)</p>
          </div>

          {/* Filtres */}
          <div className="flex items-center gap-2 flex-wrap">
            <select
              value={selectedWarehouse}
              onChange={e => setSelectedWarehouse(e.target.value)}
              className="text-xs bg-gray-800 border border-gray-700 text-gray-300 rounded-lg px-3 py-1.5 focus:outline-none focus:border-amber-500"
            >
              <option value="all">Tous les entrepôts</option>
              {warehouses.map(w => <option key={w.id} value={w.id}>{w.name}</option>)}
            </select>
            <select
              value={statusFilter}
              onChange={e => setStatusFilter(e.target.value)}
              className="text-xs bg-gray-800 border border-gray-700 text-gray-300 rounded-lg px-3 py-1.5 focus:outline-none focus:border-amber-500"
            >
              {STATUS_FILTER_OPTIONS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
            </select>
            <span className="text-xs text-gray-500">{filteredLots.length} résultat{filteredLots.length > 1 ? 's' : ''}</span>
          </div>
        </div>

        <LotsTable lots={filteredLots} />
      </div>
    </div>
  )
}
