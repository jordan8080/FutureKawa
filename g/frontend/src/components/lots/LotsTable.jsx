import { useNavigate } from 'react-router-dom'
import { StatusBadge } from '../ui/Badge'
import { formatDate, formatLotAge, getLotDays } from '../../utils/statusUtils'

export function LotsTable({ lots, showCountry = false, onDelete }) {
  const navigate = useNavigate()

  if (!lots?.length) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <span className="text-4xl mb-3">📦</span>
        <p className="text-gray-400 font-medium">Aucun lot trouvé</p>
        <p className="text-gray-600 text-sm mt-1">Les lots apparaîtront ici une fois créés</p>
      </div>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-800">
            <th className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider px-4 py-3">Lot ID</th>
            {showCountry && <th className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider px-4 py-3">Pays</th>}
            <th className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider px-4 py-3">Exploitation</th>
            <th className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider px-4 py-3">Date stockage</th>
            <th className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider px-4 py-3">Ancienneté</th>
            <th className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider px-4 py-3">Poids</th>
            <th className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider px-4 py-3">Statut</th>
            <th className="px-4 py-3" />
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-800/60">
          {lots.map((lot, idx) => {
            const days = getLotDays(lot.storedAt)
            const isUrgent = days >= 330 && lot.status !== 'expedie'
            return (
              <tr
                key={lot.id}
                onClick={() => navigate(`/lots/${lot.id}`)}
                className="hover:bg-gray-800/50 cursor-pointer transition-colors group"
              >
                {/* FIFO indicator: premier lot = plus urgent */}
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    {idx === 0 && lot.status !== 'expedie' && (
                      <span className="text-xs bg-amber-400/20 text-amber-400 border border-amber-400/30 px-1.5 py-0.5 rounded font-medium">FIFO</span>
                    )}
                    <span className="font-mono text-amber-400 text-sm group-hover:text-amber-300">{lot.id}</span>
                  </div>
                </td>
                {showCountry && (
                  <td className="px-4 py-3 text-gray-300 text-xs capitalize">{lot.country}</td>
                )}
                <td className="px-4 py-3 text-gray-300 text-sm">{lot.exploitation}</td>
                <td className="px-4 py-3 text-gray-400 text-sm">{formatDate(lot.storedAt)}</td>
                <td className="px-4 py-3">
                  <span className={`text-sm font-medium ${isUrgent ? 'text-amber-400' : 'text-gray-400'}`}>
                    {formatLotAge(lot.storedAt)}
                    {isUrgent && <span className="ml-1.5 text-xs">⚠</span>}
                  </span>
                </td>
                <td className="px-4 py-3 text-gray-400 text-sm">{lot.weight?.toLocaleString('fr-FR')} kg</td>
                <td className="px-4 py-3"><StatusBadge status={lot.status} /></td>
                <td className="px-4 py-3 text-right">
                  {onDelete ? (
                    <button
                      onClick={(e) => { e.stopPropagation(); onDelete(lot.id) }}
                      className="text-gray-600 hover:text-red-400 transition-colors"
                      title="Supprimer le lot"
                    >🗑</button>
                  ) : (
                    <span className="text-gray-600 group-hover:text-gray-400">›</span>
                  )}
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
