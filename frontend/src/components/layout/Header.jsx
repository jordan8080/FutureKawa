import { useLocation, Link } from 'react-router-dom'
import { COUNTRIES_CONFIG } from '../../data/mockData'
import { ALERTS } from '../../data/mockData'

function useBreadcrumb() {
  const { pathname } = useLocation()
  const parts = [{ label: 'Dashboard', to: '/' }]

  if (pathname === '/') return parts
  if (pathname === '/alertes') {
    parts.push({ label: 'Alertes' })
    return parts
  }

  const payMatch = pathname.match(/^\/pays\/([^/]+)/)
  if (payMatch) {
    const cfg = COUNTRIES_CONFIG[payMatch[1]]
    parts.push({ label: 'Pays', to: null })
    if (cfg) parts.push({ label: `${cfg.emoji} ${cfg.name}` })
    return parts
  }

  const lotMatch = pathname.match(/^\/lots\/([^/]+)/)
  if (lotMatch) {
    parts.push({ label: 'Lots', to: null })
    parts.push({ label: lotMatch[1] })
    return parts
  }

  return parts
}

export function Header() {
  const crumbs = useBreadcrumb()
  const activeAlerts = ALERTS.filter(a => a.status === 'active').length
  const now = new Date().toLocaleString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })

  return (
    <header className="h-14 bg-gray-950 border-b border-gray-800 flex items-center justify-between px-6 flex-shrink-0">
      {/* Breadcrumb */}
      <nav className="flex items-center gap-1.5 text-sm">
        {crumbs.map((c, i) => (
          <span key={i} className="flex items-center gap-1.5">
            {i > 0 && <span className="text-gray-700">/</span>}
            {c.to !== undefined && i < crumbs.length - 1 ? (
              <Link to={c.to ?? '#'} className="text-gray-500 hover:text-gray-300 transition-colors">{c.label}</Link>
            ) : (
              <span className="text-white font-medium">{c.label}</span>
            )}
          </span>
        ))}
      </nav>

      {/* Right side */}
      <div className="flex items-center gap-4">
        <span className="text-xs text-gray-600 hidden md:block capitalize">{now}</span>

        <Link
          to="/alertes"
          className="relative flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-gray-900 border border-gray-800 hover:border-gray-700 transition-colors text-xs text-gray-400 hover:text-white"
        >
          <span>🔔</span>
          {activeAlerts > 0 && (
            <>
              <span className="text-amber-400 font-semibold">{activeAlerts} alertes</span>
              <span className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-amber-400 rounded-full border-2 border-gray-950 animate-pulse-slow" />
            </>
          )}
          {activeAlerts === 0 && <span>Aucune alerte</span>}
        </Link>
      </div>
    </header>
  )
}
