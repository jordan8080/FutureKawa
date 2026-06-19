import { apiRequest } from './client'
import { LOTS, WAREHOUSES } from '../data/mockData'

const USE_MOCK = !import.meta.env.VITE_API_BASE_URL
const delay = (ms = 350) => new Promise(r => setTimeout(r, ms))

export const lotsApi = {
  getAll: async () => {
    if (USE_MOCK) { await delay(); return [...LOTS].sort((a, b) => new Date(a.storedAt) - new Date(b.storedAt)) }
    return apiRequest('/api/lots')
  },

  getByCountry: async (countryId) => {
    if (USE_MOCK) {
      await delay()
      const warehouseIds = WAREHOUSES.filter(w => w.country === countryId).map(w => w.id)
      return LOTS.filter(l => warehouseIds.includes(l.warehouseId)).sort((a, b) => new Date(a.storedAt) - new Date(b.storedAt))
    }
    return apiRequest(`/api/countries/${countryId}/lots`)
  },

  getByWarehouse: async (warehouseId) => {
    if (USE_MOCK) {
      await delay()
      return LOTS.filter(l => l.warehouseId === warehouseId).sort((a, b) => new Date(a.storedAt) - new Date(b.storedAt))
    }
    return apiRequest(`/api/warehouses/${warehouseId}/lots`)
  },

  getById: async (lotId) => {
    if (USE_MOCK) { await delay(200); return LOTS.find(l => l.id === lotId) ?? null }
    return apiRequest(`/api/lots/${lotId}`)
  },

  create: async (data) => {
    if (USE_MOCK) {
      await delay(600)
      const newLot = { ...data, id: `FK-NEW-${Date.now()}`, status: 'conforme', storedAt: new Date().toISOString() }
      LOTS.push(newLot)
      return newLot
    }
    return apiRequest('/api/lots', { method: 'POST', body: data })
  },

  updateStatus: async (lotId, status) => {
    if (USE_MOCK) {
      await delay(400)
      const lot = LOTS.find(l => l.id === lotId)
      if (lot) lot.status = status
      return lot
    }
    return apiRequest(`/api/lots/${lotId}/status`, { method: 'PATCH', body: { status } })
  },

  remove: async (lotId) => {
    if (USE_MOCK) {
      await delay(400)
      const i = LOTS.findIndex(l => l.id === lotId)
      if (i >= 0) LOTS.splice(i, 1)
      return { ok: true, id: lotId }
    }
    return apiRequest(`/api/lots/${lotId}`, { method: 'DELETE' })
  },
}
