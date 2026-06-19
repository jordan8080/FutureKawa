import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { SensorChart } from '../components/charts/SensorChart'
import { StatusBadge } from '../components/ui/Badge'
import { PageLoader } from '../components/ui/LoadingSpinner'
import { lotsApi, sensorsApi, warehousesApi } from '../api'
import { COUNTRIES_CONFIG } from '../data/mockData'
import { formatDate, formatLotAge, getLotDays } from '../utils/statusUtils'

function InfoRow({ label, value, mono = false }) {
  return (
    <div className="flex items-start justify-between py-2.5 border-b border-gray-800 last:border-0">
      <span className="text-xs text-gray-500 w-36 flex-shrink-0">{label}</span>
      <span className={`text-sm text-right ${mono ? 'font-mono text-amber-400' : 'text-gray-200'}`}>{value}</span>
    </div>
  )
}

export function LotDetailPage() {
  const { lotId } = useParams()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [lot, setLot] = useState(null)
  const [warehouse, setWarehouse] = useState(null)
  const [readings, setReadings] = useState([])

  useEffect(() => {
    lotsApi.getById(lotId)
      .then(lotData => {
        setLot(lotData)
        if (lotData) {
          return Promise.all([
            warehousesApi.getById(lotData.warehouseId),
            sensorsApi.getReadings(lotData.warehouseId),
          ])
        }
        return [null, []]
      })
      .then(([warehouseData, readingsData]) => {
        setWarehouse(warehouseData)
        setReadings(readingsData)
      })
      .finally(() => setLoading(false))
  }, [lotId])

  // Rafraîchissement live de l'entrepôt + historique capteurs
  useEffect(() => {
    if (!lot) return
    const id = setInterval(() => {
      Promise.all([
        warehousesApi.getById(lot.warehouseId),
        sensorsApi.getReadings(lot.warehouseId),
      ])
        .then(([warehouseData, readingsData]) => {
          setWarehouse(warehouseData)
          setReadings(readingsData)
        })
        .catch(() => {})
    }, 8000)
    return () => clearInterval(id)
  }, [lot])

  if (loading) return <PageLoader />

  if (!lot) {
    return (
      <div className="flex flex-col items-center justify-center py-24">
        <span className="text-5xl mb-4">📦</span>
        <p className="text-gray-300 text-lg font-medium">Lot introuvable</p>
        <button onClick={() => navigate(-1)} className="mt-4 text-amber-400 text-sm hover:underline">
          ← Retour
        </button>
      </div>
    )
  }

  const country = COUNTRIES_CONFIG[lot.country]
  const days = getLotDays(lot.storedAt)
  const ageWarning = days >= 330

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between flex-wrap gap-4">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <button
              onClick={() => navigate(-1)}
              className="text-gray-500 hover:text-gray-300 transition-colors text-sm flex items-center gap-1"
            >
              ← Retour
            </button>
          </div>
          <div className="flex items-center gap-3 flex-wrap">
            <h1 className="text-2xl font-bold font-mono text-amber-400">{lot.id}</h1>
            <StatusBadge status={lot.status} />
          </div>
          <p className="text-gray-500 text-sm mt-1">
            {country?.emoji} {country?.name} · {warehouse?.name ?? lot.warehouseId}
          </p>
        </div>

        {ageWarning && lot.status !== 'expedie' && (
          <div className="bg-amber-400/10 border border-amber-400/30 rounded-xl px-4 py-3 text-sm text-amber-400 flex items-start gap-2 max-w-xs">
            <span className="text-lg flex-shrink-0">⚠️</span>
            <div>
              <p className="font-semibold">Lot ancien</p>
              <p className="text-xs text-amber-400/80 mt-0.5">{days} jours de stockage. Expédition prioritaire recommandée.</p>
            </div>
          </div>
        )}
      </div>

      {/* Info lot */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <h2 className="text-sm font-semibold text-gray-300 mb-3">Informations du lot</h2>
          <InfoRow label="Identifiant" value={lot.id} mono />
          <InfoRow label="Statut" value={<StatusBadge status={lot.status} />} />
          <InfoRow label="Pays" value={`${country?.emoji ?? ''} ${country?.name ?? lot.country}`} />
          <InfoRow label="Exploitation" value={lot.exploitation} />
          <InfoRow label="Entrepôt" value={warehouse?.name ?? lot.warehouseId} />
          <InfoRow label="Variété" value={lot.variety} />
          <InfoRow label="Grade" value={lot.grade} />
          <InfoRow label="Poids" value={`${lot.weight?.toLocaleString('fr-FR')} kg`} />
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <h2 className="text-sm font-semibold text-gray-300 mb-3">Stockage & conditions</h2>
          <InfoRow label="Date de stockage" value={formatDate(lot.storedAt)} />
          <InfoRow label="Ancienneté" value={
            <span className={ageWarning ? 'text-amber-400 font-semibold' : 'text-gray-200'}>
              {formatLotAge(lot.storedAt)} ({days} jours)
            </span>
          } />
          <InfoRow label="Limite FIFO" value={`${365 - days > 0 ? `${365 - days} jours restants` : 'Dépassée'}`} />
          {warehouse && country && (
            <>
              <InfoRow label="Temp. actuelle" value={`${warehouse.currentTemp}°C (idéal: ${country.idealTemp}°C ±${country.toleranceTemp})`} />
              <InfoRow label="Humidité actuelle" value={`${warehouse.currentHumidity}% (idéal: ${country.idealHumidity}% ±${country.toleranceHumidity})`} />
            </>
          )}
        </div>
      </div>

      {/* Graphiques capteurs */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl">
        <div className="px-5 py-4 border-b border-gray-800">
          <h2 className="text-base font-semibold text-white">Historique des conditions (7 derniers jours)</h2>
          <p className="text-xs text-gray-500 mt-0.5">
            Relevés IoT depuis l'entrepôt {warehouse?.name ?? lot.warehouseId} · {readings.length} mesures
          </p>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 divide-y lg:divide-y-0 lg:divide-x divide-gray-800">
          <div className="p-5">
            <SensorChart readings={readings} type="temperature" country={lot.country} height={220} />
          </div>
          <div className="p-5">
            <SensorChart readings={readings} type="humidity" country={lot.country} height={220} />
          </div>
        </div>
      </div>

      {/* Paramètres idéaux du pays */}
      {country && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <h2 className="text-sm font-semibold text-gray-300 mb-3">Référentiel qualité — {country.emoji} {country.name}</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-gray-800/60 rounded-xl p-3 text-center">
              <p className="text-xs text-gray-500 mb-1">Température idéale</p>
              <p className="text-lg font-bold text-white">{country.idealTemp}°C</p>
            </div>
            <div className="bg-gray-800/60 rounded-xl p-3 text-center">
              <p className="text-xs text-gray-500 mb-1">Tolérance temp.</p>
              <p className="text-lg font-bold text-amber-400">±{country.toleranceTemp}°C</p>
            </div>
            <div className="bg-gray-800/60 rounded-xl p-3 text-center">
              <p className="text-xs text-gray-500 mb-1">Humidité idéale</p>
              <p className="text-lg font-bold text-white">{country.idealHumidity}%</p>
            </div>
            <div className="bg-gray-800/60 rounded-xl p-3 text-center">
              <p className="text-xs text-gray-500 mb-1">Tolérance hum.</p>
              <p className="text-lg font-bold text-amber-400">±{country.toleranceHumidity}%</p>
            </div>
          </div>
          <p className="text-xs text-gray-600 mt-3">Contact responsable : {country.managerEmail}</p>
        </div>
      )}
    </div>
  )
}
