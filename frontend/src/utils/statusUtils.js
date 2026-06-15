import { COUNTRIES_CONFIG } from '../data/mockData'

export const STATUS_CONFIG = {
  conforme: { label: 'Conforme', color: 'text-emerald-400', bg: 'bg-emerald-400/10', border: 'border-emerald-400/20', dot: 'bg-emerald-400' },
  alerte: { label: 'En alerte', color: 'text-amber-400', bg: 'bg-amber-400/10', border: 'border-amber-400/20', dot: 'bg-amber-400' },
  perime: { label: 'Périmé', color: 'text-red-400', bg: 'bg-red-400/10', border: 'border-red-400/20', dot: 'bg-red-400' },
  expedie: { label: 'Expédié', color: 'text-gray-400', bg: 'bg-gray-400/10', border: 'border-gray-400/20', dot: 'bg-gray-400' },
}

export const ALERT_SEVERITY = {
  critical: { label: 'Critique', color: 'text-red-400', bg: 'bg-red-400/10', border: 'border-red-400/30', icon: '🔴' },
  high: { label: 'Haute', color: 'text-orange-400', bg: 'bg-orange-400/10', border: 'border-orange-400/30', icon: '🟠' },
  medium: { label: 'Moyenne', color: 'text-amber-400', bg: 'bg-amber-400/10', border: 'border-amber-400/30', icon: '🟡' },
  low: { label: 'Faible', color: 'text-blue-400', bg: 'bg-blue-400/10', border: 'border-blue-400/30', icon: '🔵' },
}

export const ALERT_TYPE = {
  temperature: { label: 'Température', icon: '🌡️' },
  humidity: { label: 'Humidité', icon: '💧' },
  lot_age: { label: 'Lot périmé', icon: '⏰' },
}

export function getWarehouseStatus(warehouse) {
  const country = COUNTRIES_CONFIG[warehouse.country]
  if (!country) return 'conforme'
  const tempOk = Math.abs(warehouse.currentTemp - country.idealTemp) <= country.toleranceTemp
  const humOk = Math.abs(warehouse.currentHumidity - country.idealHumidity) <= country.toleranceHumidity
  if (!tempOk || !humOk) return 'alerte'
  return 'conforme'
}

export function formatLotAge(storedAt) {
  const days = Math.floor((Date.now() - new Date(storedAt).getTime()) / 86400000)
  if (days === 0) return "Aujourd'hui"
  if (days === 1) return '1 jour'
  if (days < 30) return `${days} jours`
  if (days < 365) {
    const months = Math.floor(days / 30)
    return `${months} mois`
  }
  const years = Math.floor(days / 365)
  const remainingMonths = Math.floor((days % 365) / 30)
  return remainingMonths > 0 ? `${years} an${years > 1 ? 's' : ''} ${remainingMonths} mois` : `${years} an${years > 1 ? 's' : ''}`
}

export function getLotDays(storedAt) {
  return Math.floor((Date.now() - new Date(storedAt).getTime()) / 86400000)
}

export function formatDate(isoString) {
  return new Date(isoString).toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
}

export function formatDateTime(isoString) {
  return new Date(isoString).toLocaleString('fr-FR', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })
}
