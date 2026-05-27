import { SeverityBadge, AlertTypeBadge } from '../ui/Badge'
import { COUNTRIES_CONFIG } from '../../data/mockData'
import { formatDateTime } from '../../utils/statusUtils'
import { Button } from '../ui/Button'

export function AlertItem({ alert, onResolve }) {
  const country = COUNTRIES_CONFIG[alert.country]
  const isActive = alert.status === 'active'

  return (
    <div className={`bg-gray-900 border rounded-xl p-4 transition-all ${isActive ? 'border-gray-700' : 'border-gray-800 opacity-60'}`}>
      <div className="flex items-start gap-3">
        <div className={`flex-shrink-0 w-9 h-9 rounded-lg flex items-center justify-center text-lg ${isActive ? 'bg-amber-400/10' : 'bg-gray-800'}`}>
          {alert.type === 'temperature' ? '🌡️' : alert.type === 'humidity' ? '💧' : '⏰'}
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex flex-wrap items-center gap-2 mb-1.5">
            <SeverityBadge severity={alert.severity} />
            <AlertTypeBadge type={alert.type} />
            {country && (
              <span className="text-xs text-gray-500 flex items-center gap-1">
                {country.emoji} {country.name}
              </span>
            )}
          </div>

          <p className="text-sm text-gray-200 font-medium mb-1">{alert.message}</p>

          <div className="flex flex-wrap items-center gap-3 text-xs text-gray-500 mt-2">
            <span>📍 {alert.warehouseName}</span>
            {alert.lotId && <span>📦 Lot <span className="font-mono text-amber-400/70">{alert.lotId}</span></span>}
            <span>🕐 {formatDateTime(alert.createdAt)}</span>
          </div>
        </div>

        <div className="flex-shrink-0 flex items-center gap-2">
          {isActive ? (
            <span className="flex items-center gap-1.5 text-xs font-medium text-amber-400">
              <span className="w-1.5 h-1.5 bg-amber-400 rounded-full animate-pulse-slow" />
              Active
            </span>
          ) : (
            <span className="text-xs text-gray-600 font-medium">Résolue</span>
          )}
          {isActive && onResolve && (
            <Button variant="ghost" size="sm" onClick={() => onResolve(alert.id)}>
              Résoudre
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}
