import { apiRequest } from './client'
import { ALERTS } from '../data/mockData'

const USE_MOCK = !import.meta.env.VITE_API_BASE_URL
const delay = (ms = 300) => new Promise(r => setTimeout(r, ms))

export const alertsApi = {
  getAll: async (filters = {}) => {
    if (USE_MOCK) {
      await delay()
      let alerts = [...ALERTS]
      if (filters.country) alerts = alerts.filter(a => a.country === filters.country)
      if (filters.type) alerts = alerts.filter(a => a.type === filters.type)
      if (filters.status) alerts = alerts.filter(a => a.status === filters.status)
      return alerts.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
    }
    const params = new URLSearchParams(filters).toString()
    return apiRequest(`/api/alerts?${params}`)
  },

  getActive: async () => {
    if (USE_MOCK) {
      await delay(200)
      return ALERTS.filter(a => a.status === 'active').sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
    }
    return apiRequest('/api/alerts?status=active')
  },

  resolve: async (alertId) => {
    if (USE_MOCK) {
      await delay(400)
      const alert = ALERTS.find(a => a.id === alertId)
      if (alert) alert.status = 'resolved'
      return alert
    }
    return apiRequest(`/api/alerts/${alertId}/resolve`, { method: 'POST' })
  },

  getCount: async () => {
    if (USE_MOCK) {
      await delay(150)
      return { active: ALERTS.filter(a => a.status === 'active').length, total: ALERTS.length }
    }
    return apiRequest('/api/alerts/count')
  },
}
