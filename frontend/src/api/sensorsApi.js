import { apiRequest } from './client'
import { SENSOR_READINGS, WAREHOUSES } from '../data/mockData'

const USE_MOCK = !import.meta.env.VITE_API_BASE_URL
const delay = (ms = 400) => new Promise(r => setTimeout(r, ms))

export const sensorsApi = {
  getReadings: async (warehouseId, options = {}) => {
    if (USE_MOCK) {
      await delay()
      const readings = SENSOR_READINGS[warehouseId] ?? []
      const { limit } = options
      return limit ? readings.slice(-limit) : readings
    }
    const params = new URLSearchParams(options).toString()
    return apiRequest(`/api/warehouses/${warehouseId}/sensors?${params}`)
  },

  getLatestByCountry: async (countryId) => {
    if (USE_MOCK) {
      await delay(250)
      const warehouses = WAREHOUSES.filter(w => w.country === countryId)
      return warehouses.map(w => {
        const readings = SENSOR_READINGS[w.id] ?? []
        const latest = readings[readings.length - 1] ?? null
        return { warehouseId: w.id, warehouseName: w.name, ...latest }
      })
    }
    return apiRequest(`/api/countries/${countryId}/sensors/latest`)
  },

  getCurrentAll: async () => {
    if (USE_MOCK) {
      await delay(200)
      return WAREHOUSES.map(w => {
        const readings = SENSOR_READINGS[w.id] ?? []
        const latest = readings[readings.length - 1] ?? {}
        return {
          warehouseId: w.id,
          warehouseName: w.name,
          country: w.country,
          temperature: w.currentTemp,
          humidity: w.currentHumidity,
          lastUpdated: latest.timestamp ?? new Date().toISOString(),
        }
      })
    }
    return apiRequest('/api/sensors/current')
  },
}
