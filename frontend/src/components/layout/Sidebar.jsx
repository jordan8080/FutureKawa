import { NavLink, useLocation } from 'react-router-dom'
import { COUNTRIES_CONFIG } from '../../data/mockData'
import { ALERTS, LOTS } from '../../data/mockData'
import { clsx } from 'clsx'

const countries = Object.values(COUNTRIES_CONFIG)
const activeAlertCount = ALERTS.filter(a => a.status === 'active').length

function NavItem({ to, children, badge }) {
  const location = useLocation()
  const isActive = to === '/' ? location.pathname === '/' : location.pathname.startsWith(to)

  return (
    <NavLink
      to={to}
      className={clsx(
        'flex items-center justify-between gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-150',
        isActive
          ? 'text-amber-400 bg-amber-400/10'
          : 'text-gray-400 hover:text-white hover:bg-gray-800'
      )}
    >
      <span>{children}</span>
      {badge != null && (
        <span className={clsx(
          'text-xs px-1.5 py-0.5 rounded-full font-bold min-w-[20px] text-center',
          isActive ? 'bg-amber-400/20 text-amber-300' : 'bg-gray-700 text-gray-400'
        )}>
          {badge}
        </span>
      )}
    </NavLink>
  )
}

export function Sidebar() {
  return (
    <aside className="fixed left-0 top-0 h-screen w-64 bg-gray-950 border-r border-gray-800 flex flex-col z-40">
      {/* Logo */}
      <div className="px-5 py-5 border-b border-gray-800">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-amber-500 rounded-xl flex items-center justify-center text-gray-950 font-black text-lg">
            FK
          </div>
          <div>
            <p className="text-white font-semibold text-sm leading-none">FutureKawa</p>
            <p className="text-gray-500 text-xs mt-0.5">Suivi des stocks</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
        <p className="text-xs font-semibold text-gray-600 uppercase tracking-widest px-3 mb-2">Vue globale</p>
        <NavItem to="/">
          <span className="flex items-center gap-2.5">
            <span>📊</span> Dashboard
          </span>
        </NavItem>
        <NavItem to="/alertes" badge={activeAlertCount > 0 ? activeAlertCount : undefined}>
          <span className="flex items-center gap-2.5">
            <span className={activeAlertCount > 0 ? 'animate-pulse-slow' : ''}>🔔</span> Alertes
          </span>
        </NavItem>

        <div className="pt-4">
          <p className="text-xs font-semibold text-gray-600 uppercase tracking-widest px-3 mb-2">Pays</p>
          {countries.map(c => {
            const countryLots = LOTS.filter(l => l.country === c.id)
            const alertLots = countryLots.filter(l => l.status === 'alerte' || l.status === 'perime').length
            return (
              <NavItem key={c.id} to={`/pays/${c.id}`} badge={alertLots > 0 ? alertLots : undefined}>
                <span className="flex items-center gap-2.5">
                  <span>{c.emoji}</span> {c.name}
                </span>
              </NavItem>
            )
          })}
        </div>
      </nav>

      {/* Footer */}
      <div className="px-4 py-4 border-t border-gray-800">
        <div className="flex items-center gap-2.5 px-2 py-2 rounded-lg">
          <div className="w-7 h-7 bg-gray-700 rounded-full flex items-center justify-center text-xs font-bold text-gray-300">
            HQ
          </div>
          <div>
            <p className="text-xs font-medium text-gray-300">Siège central</p>
            <p className="text-xs text-gray-600">Direction SI</p>
          </div>
          <span className="ml-auto w-2 h-2 bg-emerald-400 rounded-full" title="Connecté" />
        </div>
      </div>
    </aside>
  )
}
