import { STATUS_CONFIG, ALERT_SEVERITY, ALERT_TYPE } from '../../utils/statusUtils'

export function StatusBadge({ status }) {
  const cfg = STATUS_CONFIG[status] ?? STATUS_CONFIG.conforme
  return (
    <span className={`inline-flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-full border ${cfg.color} ${cfg.bg} ${cfg.border}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${cfg.dot}`} />
      {cfg.label}
    </span>
  )
}

export function SeverityBadge({ severity }) {
  const cfg = ALERT_SEVERITY[severity] ?? ALERT_SEVERITY.low
  return (
    <span className={`inline-flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-full border ${cfg.color} ${cfg.bg} ${cfg.border}`}>
      {cfg.label}
    </span>
  )
}

export function AlertTypeBadge({ type }) {
  const cfg = ALERT_TYPE[type] ?? { label: type, icon: '⚠️' }
  return (
    <span className="inline-flex items-center gap-1.5 text-xs font-medium text-gray-300 bg-gray-800 border border-gray-700 px-2.5 py-1 rounded-full">
      <span>{cfg.icon}</span>
      {cfg.label}
    </span>
  )
}
