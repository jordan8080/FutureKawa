// ─── Configuration pays ───────────────────────────────────────────────────────
export const COUNTRIES_CONFIG = {
  brazil: {
    id: 'brazil',
    name: 'Brésil',
    code: 'BR',
    emoji: '🇧🇷',
    idealTemp: 29,
    idealHumidity: 55,
    toleranceTemp: 3,
    toleranceHumidity: 2,
    manager: 'Carlos Oliveira',
    managerEmail: 'c.oliveira@futurekawa.com',
  },
  ecuador: {
    id: 'ecuador',
    name: 'Équateur',
    code: 'EC',
    emoji: '🇪🇨',
    idealTemp: 31,
    idealHumidity: 60,
    toleranceTemp: 3,
    toleranceHumidity: 2,
    manager: 'María García',
    managerEmail: 'm.garcia@futurekawa.com',
  },
  colombia: {
    id: 'colombia',
    name: 'Colombie',
    code: 'CO',
    emoji: '🇨🇴',
    idealTemp: 26,
    idealHumidity: 80,
    toleranceTemp: 3,
    toleranceHumidity: 2,
    manager: 'Andrés Martínez',
    managerEmail: 'a.martinez@futurekawa.com',
  },
}

// ─── Entrepôts ────────────────────────────────────────────────────────────────
export const WAREHOUSES = [
  { id: 'w-br-1', name: 'Entrepôt São Paulo', country: 'brazil', location: 'São Paulo', exploitation: 'Fazenda Aurora', currentTemp: 28.3, currentHumidity: 54.2 },
  { id: 'w-br-2', name: 'Entrepôt Minas Gerais', country: 'brazil', location: 'Minas Gerais', exploitation: 'Fazenda Verde', currentTemp: 32.7, currentHumidity: 56.1 },
  { id: 'w-ec-1', name: 'Entrepôt Quito', country: 'ecuador', location: 'Quito', exploitation: 'Hacienda del Sol', currentTemp: 30.8, currentHumidity: 60.5 },
  { id: 'w-ec-2', name: 'Entrepôt Guayaquil', country: 'ecuador', location: 'Guayaquil', exploitation: 'Finca La Esperanza', currentTemp: 27.9, currentHumidity: 59.4 },
  { id: 'w-co-1', name: 'Entrepôt Bogotá', country: 'colombia', location: 'Bogotá', exploitation: 'Finca Cafetera Nacional', currentTemp: 26.2, currentHumidity: 79.8 },
  { id: 'w-co-2', name: 'Entrepôt Medellín', country: 'colombia', location: 'Medellín', exploitation: 'Hacienda El Paraíso', currentTemp: 25.7, currentHumidity: 82.6 },
]

// ─── Helper dates ─────────────────────────────────────────────────────────────
const daysAgo = (days) => {
  const d = new Date()
  d.setDate(d.getDate() - days)
  return d.toISOString()
}

// ─── Lots ─────────────────────────────────────────────────────────────────────
export const LOTS = [
  // Brésil - São Paulo
  { id: 'FK-BR-SP-001', warehouseId: 'w-br-1', country: 'brazil', exploitation: 'Fazenda Aurora', storedAt: daysAgo(387), status: 'perime', weight: 2500, variety: 'Arabica', grade: 'Grade 2' },
  { id: 'FK-BR-SP-002', warehouseId: 'w-br-1', country: 'brazil', exploitation: 'Fazenda Aurora', storedAt: daysAgo(210), status: 'conforme', weight: 1800, variety: 'Arabica', grade: 'Grade 1' },
  { id: 'FK-BR-SP-003', warehouseId: 'w-br-1', country: 'brazil', exploitation: 'Fazenda Aurora', storedAt: daysAgo(145), status: 'conforme', weight: 3200, variety: 'Robusta', grade: 'Grade 1' },
  { id: 'FK-BR-SP-004', warehouseId: 'w-br-1', country: 'brazil', exploitation: 'Fazenda Aurora', storedAt: daysAgo(67), status: 'conforme', weight: 1500, variety: 'Arabica', grade: 'Grade 1' },
  { id: 'FK-BR-SP-005', warehouseId: 'w-br-1', country: 'brazil', exploitation: 'Fazenda Aurora', storedAt: daysAgo(12), status: 'conforme', weight: 2100, variety: 'Arabica', grade: 'Grade 2' },

  // Brésil - Minas Gerais (entrepôt en alerte température)
  { id: 'FK-BR-MG-001', warehouseId: 'w-br-2', country: 'brazil', exploitation: 'Fazenda Verde', storedAt: daysAgo(320), status: 'alerte', weight: 2800, variety: 'Arabica', grade: 'Grade 1' },
  { id: 'FK-BR-MG-002', warehouseId: 'w-br-2', country: 'brazil', exploitation: 'Fazenda Verde', storedAt: daysAgo(198), status: 'alerte', weight: 1600, variety: 'Robusta', grade: 'Grade 2' },
  { id: 'FK-BR-MG-003', warehouseId: 'w-br-2', country: 'brazil', exploitation: 'Fazenda Verde', storedAt: daysAgo(89), status: 'alerte', weight: 2200, variety: 'Arabica', grade: 'Grade 1' },
  { id: 'FK-BR-MG-004', warehouseId: 'w-br-2', country: 'brazil', exploitation: 'Fazenda Verde', storedAt: daysAgo(34), status: 'alerte', weight: 900, variety: 'Robusta', grade: 'Grade 2' },

  // Équateur - Quito
  { id: 'FK-EC-QT-001', warehouseId: 'w-ec-1', country: 'ecuador', exploitation: 'Hacienda del Sol', storedAt: daysAgo(290), status: 'conforme', weight: 3500, variety: 'Arabica', grade: 'Specialty' },
  { id: 'FK-EC-QT-002', warehouseId: 'w-ec-1', country: 'ecuador', exploitation: 'Hacienda del Sol', storedAt: daysAgo(178), status: 'conforme', weight: 2100, variety: 'Arabica', grade: 'Grade 1' },
  { id: 'FK-EC-QT-003', warehouseId: 'w-ec-1', country: 'ecuador', exploitation: 'Hacienda del Sol', storedAt: daysAgo(95), status: 'conforme', weight: 1800, variety: 'Arabica', grade: 'Specialty' },
  { id: 'FK-EC-QT-004', warehouseId: 'w-ec-1', country: 'ecuador', exploitation: 'Hacienda del Sol', storedAt: daysAgo(41), status: 'conforme', weight: 2700, variety: 'Arabica', grade: 'Grade 1' },
  { id: 'FK-EC-QT-005', warehouseId: 'w-ec-1', country: 'ecuador', exploitation: 'Hacienda del Sol', storedAt: daysAgo(8), status: 'conforme', weight: 1200, variety: 'Robusta', grade: 'Grade 2' },

  // Équateur - Guayaquil (alerte température basse)
  { id: 'FK-EC-GU-001', warehouseId: 'w-ec-2', country: 'ecuador', exploitation: 'Finca La Esperanza', storedAt: daysAgo(412), status: 'perime', weight: 1400, variety: 'Robusta', grade: 'Grade 2' },
  { id: 'FK-EC-GU-002', warehouseId: 'w-ec-2', country: 'ecuador', exploitation: 'Finca La Esperanza', storedAt: daysAgo(254), status: 'alerte', weight: 2000, variety: 'Arabica', grade: 'Grade 1' },
  { id: 'FK-EC-GU-003', warehouseId: 'w-ec-2', country: 'ecuador', exploitation: 'Finca La Esperanza', storedAt: daysAgo(120), status: 'alerte', weight: 3100, variety: 'Arabica', grade: 'Grade 1' },
  { id: 'FK-EC-GU-004', warehouseId: 'w-ec-2', country: 'ecuador', exploitation: 'Finca La Esperanza', storedAt: daysAgo(55), status: 'alerte', weight: 1700, variety: 'Robusta', grade: 'Grade 2' },

  // Colombie - Bogotá
  { id: 'FK-CO-BG-001', warehouseId: 'w-co-1', country: 'colombia', exploitation: 'Finca Cafetera Nacional', storedAt: daysAgo(340), status: 'conforme', weight: 4200, variety: 'Arabica', grade: 'Specialty' },
  { id: 'FK-CO-BG-002', warehouseId: 'w-co-1', country: 'colombia', exploitation: 'Finca Cafetera Nacional', storedAt: daysAgo(215), status: 'conforme', weight: 2800, variety: 'Arabica', grade: 'Specialty' },
  { id: 'FK-CO-BG-003', warehouseId: 'w-co-1', country: 'colombia', exploitation: 'Finca Cafetera Nacional', storedAt: daysAgo(130), status: 'conforme', weight: 1900, variety: 'Arabica', grade: 'Grade 1' },
  { id: 'FK-CO-BG-004', warehouseId: 'w-co-1', country: 'colombia', exploitation: 'Finca Cafetera Nacional', storedAt: daysAgo(72), status: 'conforme', weight: 3300, variety: 'Arabica', grade: 'Specialty' },
  { id: 'FK-CO-BG-005', warehouseId: 'w-co-1', country: 'colombia', exploitation: 'Finca Cafetera Nacional', storedAt: daysAgo(19), status: 'conforme', weight: 2100, variety: 'Robusta', grade: 'Grade 1' },

  // Colombie - Medellín (alerte humidité haute)
  { id: 'FK-CO-MD-001', warehouseId: 'w-co-2', country: 'colombia', exploitation: 'Hacienda El Paraíso', storedAt: daysAgo(298), status: 'alerte', weight: 2600, variety: 'Arabica', grade: 'Grade 1' },
  { id: 'FK-CO-MD-002', warehouseId: 'w-co-2', country: 'colombia', exploitation: 'Hacienda El Paraíso', storedAt: daysAgo(167), status: 'alerte', weight: 1500, variety: 'Arabica', grade: 'Specialty' },
  { id: 'FK-CO-MD-003', warehouseId: 'w-co-2', country: 'colombia', exploitation: 'Hacienda El Paraíso', storedAt: daysAgo(88), status: 'alerte', weight: 2900, variety: 'Robusta', grade: 'Grade 2' },
  { id: 'FK-CO-MD-004', warehouseId: 'w-co-2', country: 'colombia', exploitation: 'Hacienda El Paraíso', storedAt: daysAgo(23), status: 'alerte', weight: 1800, variety: 'Arabica', grade: 'Grade 1' },
]

// ─── Générateur de données capteurs (déterministe par seed) ───────────────────
function seededRng(seed) {
  let s = seed
  return () => {
    s = (s * 9301 + 49297) % 233280
    return s / 233280
  }
}

function generateReadings(warehouseId, baseTemp, baseHumidity, days = 7) {
  const readings = []
  const rng = seededRng(warehouseId.split('').reduce((a, c) => a + c.charCodeAt(0), 0))
  const now = new Date()

  const intervalHours = 3
  const points = Math.floor((days * 24) / intervalHours)

  for (let i = points; i >= 0; i--) {
    const ts = new Date(now.getTime() - i * intervalHours * 3600 * 1000)
    const r = rng()
    const spike = rng() < 0.08 ? (rng() - 0.5) * 9 : 0
    const tempNoise = (r - 0.5) * 5 + spike
    const humNoise = (rng() - 0.5) * 4 + spike * 0.4

    readings.push({
      timestamp: ts.toISOString(),
      temperature: Math.round((baseTemp + tempNoise) * 10) / 10,
      humidity: Math.max(0, Math.min(100, Math.round((baseHumidity + humNoise) * 10) / 10)),
    })
  }

  return readings
}

export const SENSOR_READINGS = {
  'w-br-1': generateReadings('w-br-1', 28.3, 54.2, 7),
  'w-br-2': generateReadings('w-br-2', 32.7, 56.1, 7),
  'w-ec-1': generateReadings('w-ec-1', 30.8, 60.5, 7),
  'w-ec-2': generateReadings('w-ec-2', 27.9, 59.4, 7),
  'w-co-1': generateReadings('w-co-1', 26.2, 79.8, 7),
  'w-co-2': generateReadings('w-co-2', 25.7, 82.6, 7),
}

// ─── Alertes ─────────────────────────────────────────────────────────────────
export const ALERTS = [
  {
    id: 'alert-001',
    type: 'temperature',
    severity: 'high',
    country: 'brazil',
    warehouseId: 'w-br-2',
    warehouseName: 'Entrepôt Minas Gerais',
    lotId: null,
    message: 'Température hors plage : 32.7°C (max autorisé : 32°C)',
    createdAt: daysAgo(1),
    status: 'active',
  },
  {
    id: 'alert-002',
    type: 'lot_age',
    severity: 'critical',
    country: 'brazil',
    warehouseId: 'w-br-1',
    warehouseName: 'Entrepôt São Paulo',
    lotId: 'FK-BR-SP-001',
    message: 'Lot FK-BR-SP-001 stocké depuis 387 jours (limite : 365 jours)',
    createdAt: daysAgo(22),
    status: 'active',
  },
  {
    id: 'alert-003',
    type: 'temperature',
    severity: 'medium',
    country: 'ecuador',
    warehouseId: 'w-ec-2',
    warehouseName: 'Entrepôt Guayaquil',
    lotId: null,
    message: 'Température hors plage : 27.9°C (min autorisé : 28°C)',
    createdAt: daysAgo(2),
    status: 'active',
  },
  {
    id: 'alert-004',
    type: 'lot_age',
    severity: 'critical',
    country: 'ecuador',
    warehouseId: 'w-ec-2',
    warehouseName: 'Entrepôt Guayaquil',
    lotId: 'FK-EC-GU-001',
    message: 'Lot FK-EC-GU-001 stocké depuis 412 jours (limite : 365 jours)',
    createdAt: daysAgo(47),
    status: 'active',
  },
  {
    id: 'alert-005',
    type: 'humidity',
    severity: 'medium',
    country: 'colombia',
    warehouseId: 'w-co-2',
    warehouseName: 'Entrepôt Medellín',
    lotId: null,
    message: 'Humidité hors plage : 82.6% (max autorisé : 82%)',
    createdAt: daysAgo(3),
    status: 'active',
  },
  {
    id: 'alert-006',
    type: 'temperature',
    severity: 'low',
    country: 'brazil',
    warehouseId: 'w-br-2',
    warehouseName: 'Entrepôt Minas Gerais',
    lotId: null,
    message: 'Pic de température détecté : 35.1°C à 02h00',
    createdAt: daysAgo(5),
    status: 'resolved',
  },
  {
    id: 'alert-007',
    type: 'humidity',
    severity: 'low',
    country: 'ecuador',
    warehouseId: 'w-ec-1',
    warehouseName: 'Entrepôt Quito',
    lotId: null,
    message: 'Humidité légèrement hors plage : 62.3%',
    createdAt: daysAgo(8),
    status: 'resolved',
  },
]
