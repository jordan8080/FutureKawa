import { apiRequest } from './client'
import { WAREHOUSES } from '../data/mockData'

const USE_MOCK = !import.meta.env.VITE_API_BASE_URL
const delay = (ms = 300) => new Promise(r => setTimeout(r, ms))

export const warehousesApi = {
  getAll: async () => {
    if (USE_MOCK) { await delay(); return WAREHOUSES }
    return apiRequest('/api/warehouses')
  },

  getByCountry: async (countryId) => {
    if (USE_MOCK) { await delay(); return WAREHOUSES.filter(w => w.country === countryId) }
    return apiRequest(`/api/countries/${countryId}/warehouses`)
  },

  getById: async (id) => {
    if (USE_MOCK) { await delay(150); return WAREHOUSES.find(w => w.id === id) ?? null }
    return apiRequest(`/api/warehouses/${id}`)
  },

  create: async (data) => {
    if (USE_MOCK) {
      await delay(500)
      const w = { ...data, id: `w-new-${Date.now()}`, currentTemp: 25, currentHumidity: 60 }
      WAREHOUSES.push(w)
      return w
    }
    return apiRequest('/api/warehouses', { method: 'POST', body: data })
  },

  remove: async (id) => {
    if (USE_MOCK) {
      await delay(400)
      const i = WAREHOUSES.findIndex(w => w.id === id)
      if (i >= 0) WAREHOUSES.splice(i, 1)
      return { ok: true, id }
    }
    return apiRequest(`/api/warehouses/${id}`, { method: 'DELETE' })
  },
}
