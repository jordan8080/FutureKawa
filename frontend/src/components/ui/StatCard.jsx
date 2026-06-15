import { clsx } from 'clsx'

export function StatCard({ label, value, sublabel, icon, trend, accentColor = 'amber' }) {
  const colorMap = {
    amber: 'text-amber-400 bg-amber-400/10',
    emerald: 'text-emerald-400 bg-emerald-400/10',
    red: 'text-red-400 bg-red-400/10',
    blue: 'text-blue-400 bg-blue-400/10',
    violet: 'text-violet-400 bg-violet-400/10',
  }

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <p className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-1">{label}</p>
          <p className="text-3xl font-bold text-white leading-none mb-1">{value}</p>
          {sublabel && <p className="text-xs text-gray-500 mt-1">{sublabel}</p>}
          {trend && (
            <p className={clsx('text-xs mt-2 font-medium', trend.positive ? 'text-emerald-400' : 'text-red-400')}>
              {trend.positive ? '↑' : '↓'} {trend.label}
            </p>
          )}
        </div>
        {icon && (
          <div className={clsx('flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center text-xl', colorMap[accentColor] ?? colorMap.amber)}>
            {icon}
          </div>
        )}
      </div>
    </div>
  )
}
