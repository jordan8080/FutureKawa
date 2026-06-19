import { apiRequest } from './client'
import { COUNTRIES_CONFIG } from '../data/mockData'

const USE_MOCK = !import.meta.env.VITE_API_BASE_URL
const delay = (ms = 300) => new Promise(r => setTimeout(r, ms))

export const countriesApi = {
  getAll: async () => {
    if (USE_MOCK) {
      await delay()
      return Object.values(COUNTRIES_CONFIG).map(c => ({
        id: c.id, name: c.name, code: c.code, emoji: c.emoji,
      }))
    }
    return apiRequest('/api/countries')
  },

  create: async (data) => {
    if (USE_MOCK) { await delay(); return data }
    return apiRequest('/api/countries', { method: 'POST', body: data })
  },

  remove: async (id) => {
    if (USE_MOCK) { await delay(); return { ok: true, id } }
    return apiRequest(`/api/countries/${id}`, { method: 'DELETE' })
  },
}
