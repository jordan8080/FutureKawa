import { clsx } from 'clsx'
import { COUNTRIES_CONFIG } from '../../data/mockData'

export function ConditionGauge({ type, value, country }) {
  const cfg = COUNTRIES_CONFIG[country]
  if (!cfg) return null

  const ideal = type === 'temp' ? cfg.idealTemp : cfg.idealHumidity
  const tol = type === 'temp' ? cfg.toleranceTemp : cfg.toleranceHumidity
  const unit = type === 'temp' ? '°C' : '%'
  const icon = type === 'temp' ? '🌡️' : '💧'
  const label = type === 'temp' ? 'Température' : 'Humidité'
  const min = ideal - tol - 5
  const max = ideal + tol + 5
  const pct = Math.max(0, Math.min(100, ((value - min) / (max - min)) * 100))
  const idealMinPct = ((ideal - tol - min) / (max - min)) * 100
  const idealMaxPct = ((ideal + tol - min) / (max - min)) * 100
  const inRange = Math.abs(value - ideal) <= tol

  return (
    <div className="bg-gray-800/60 border border-gray-700 rounded-xl p-4">
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-medium text-gray-400 flex items-center gap-1.5">
          <span>{icon}</span>
          {label}
        </span>
        <span className={clsx('text-lg font-bold', inRange ? 'text-white' : 'text-amber-400')}>
          {value}{unit}
        </span>
      </div>

      {/* Barre de progression */}
      <div className="relative h-2 bg-gray-700 rounded-full overflow-hidden mb-2">
        {/* Zone idéale en vert */}
        <div
          className="absolute top-0 h-full bg-emerald-500/30 rounded-full"
          style={{ left: `${idealMinPct}%`, width: `${idealMaxPct - idealMinPct}%` }}
        />
        {/* Curseur valeur actuelle */}
        <div
          className={clsx('absolute top-0 w-2.5 h-2.5 -mt-0.25 rounded-full shadow-lg border-2 border-gray-900 transition-all', inRange ? 'bg-emerald-400' : 'bg-amber-400')}
          style={{ left: `${Math.max(0, Math.min(95, pct))}%`, top: '-1px' }}
        />
      </div>

      <div className="flex justify-between text-xs text-gray-600">
        <span>Idéal: {ideal - tol}{unit}</span>
        <span className={clsx('font-medium text-xs', inRange ? 'text-emerald-400' : 'text-amber-400')}>
          {inRange ? '✓ Conforme' : '⚠ Hors plage'}
        </span>
        <span>{ideal + tol}{unit}</span>
      </div>
    </div>
  )
}
