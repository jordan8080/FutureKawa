import { useState, useRef } from 'react'
import { COUNTRIES_CONFIG } from '../../data/mockData'

const VW = 560
const VH = 200
const PAD = { top: 16, right: 16, bottom: 32, left: 48 }
const CHART_W = VW - PAD.left - PAD.right
const CHART_H = VH - PAD.top - PAD.bottom

function mapX(i, total) {
  return PAD.left + (i / Math.max(total - 1, 1)) * CHART_W
}
function mapY(val, yMin, yMax) {
  return PAD.top + (1 - (val - yMin) / (yMax - yMin)) * CHART_H
}
function buildPath(pts) {
  return pts.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' ')
}
function fmtDate(iso) {
  const d = new Date(iso)
  return d.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit' })
}
function fmtDateTime(iso) {
  const d = new Date(iso)
  return d.toLocaleDateString('fr-FR', { weekday: 'short', day: '2-digit', month: '2-digit' }) +
    ' ' + d.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
}

export function SensorChart({ readings, type, country }) {
  const [hovered, setHovered] = useState(null)
  const svgRef = useRef(null)

  const cfg = COUNTRIES_CONFIG[country]
  if (!cfg || !readings?.length) {
    return (
      <div className="flex items-center justify-center h-40 text-gray-600 text-sm">
        Aucune donnée disponible
      </div>
    )
  }

  const isTemp = type === 'temperature'
  const ideal = isTemp ? cfg.idealTemp : cfg.idealHumidity
  const tol = isTemp ? cfg.toleranceTemp : cfg.toleranceHumidity
  const unit = isTemp ? '°C' : '%'
  const label = isTemp ? 'Température' : 'Humidité'
  const lineColor = isTemp ? '#3b82f6' : '#8b5cf6'

  const vals = readings.map(r => (isTemp ? r.temperature : r.humidity))
  const pad = Math.max(tol + 2, 4)
  const yMin = Math.min(...vals, ideal - tol) - pad
  const yMax = Math.max(...vals, ideal + tol) + pad

  const pts = readings.map((r, i) => {
    const val = isTemp ? r.temperature : r.humidity
    return {
      x: mapX(i, readings.length),
      y: mapY(val, yMin, yMax),
      val,
      ts: r.timestamp,
      out: Math.abs(val - ideal) > tol,
    }
  })

  // Y ticks
  const range = yMax - yMin
  const step = range <= 10 ? 2 : range <= 20 ? 5 : 10
  const yticks = []
  const first = Math.ceil(yMin / step) * step
  for (let v = first; v <= yMax; v += step) yticks.push(v)

  // X ticks: ~7 evenly spaced
  const xInterval = Math.max(1, Math.floor(readings.length / 7))
  const xticks = readings
    .map((r, i) => ({ r, i }))
    .filter(({ i }) => i % xInterval === 0)

  const yBandTop = mapY(ideal + tol, yMin, yMax)
  const yBandBot = mapY(ideal - tol, yMin, yMax)
  const xL = PAD.left
  const xR = VW - PAD.right

  const linePath = buildPath(pts)
  const fillPath = pts.length > 1
    ? `${linePath} L${pts[pts.length - 1].x.toFixed(1)},${(PAD.top + CHART_H).toFixed(1)} L${pts[0].x.toFixed(1)},${(PAD.top + CHART_H).toFixed(1)} Z`
    : ''

  // Handle mouse move on SVG to find nearest point
  const handleMouseMove = (e) => {
    const svg = svgRef.current
    if (!svg) return
    const rect = svg.getBoundingClientRect()
    const svgX = ((e.clientX - rect.left) / rect.width) * VW
    let best = null
    let bestDist = Infinity
    pts.forEach(p => {
      const d = Math.abs(p.x - svgX)
      if (d < bestDist) { bestDist = d; best = p }
    })
    if (best && bestDist < 30) setHovered(best)
    else setHovered(null)
  }

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-sm font-semibold text-gray-300">
          {isTemp ? '🌡️' : '💧'} {label}
        </h4>
        <div className="flex items-center gap-1.5 text-xs text-gray-500">
          <span className="inline-block w-3 h-2 bg-emerald-500/20 border border-emerald-500/40 rounded-sm" />
          Zone idéale {ideal - tol}{unit} – {ideal + tol}{unit}
        </div>
      </div>

      {/* Tooltip info bar */}
      <div className="h-9 mb-1 flex items-center">
        {hovered ? (
          <div className="flex items-center gap-3 text-xs">
            <span className="text-gray-400">{fmtDateTime(hovered.ts)}</span>
            <span className={`font-bold text-sm ${hovered.out ? 'text-amber-400' : 'text-white'}`}>
              {hovered.val}{unit}
            </span>
            <span className={`text-xs ${hovered.out ? 'text-amber-400' : 'text-emerald-400'}`}>
              {hovered.out ? '⚠ Hors plage' : '✓ Conforme'}
            </span>
          </div>
        ) : (
          <span className="text-xs text-gray-600">Survolez le graphique pour voir les valeurs</span>
        )}
      </div>

      {/* SVG Chart */}
      <svg
        ref={svgRef}
        viewBox={`0 0 ${VW} ${VH}`}
        className="w-full"
        style={{ height: '200px' }}
        onMouseMove={handleMouseMove}
        onMouseLeave={() => setHovered(null)}
      >
        {/* Grid lines (horizontal only) */}
        {yticks.map(v => {
          const y = mapY(v, yMin, yMax)
          return (
            <g key={v}>
              <line x1={xL} y1={y} x2={xR} y2={y} stroke="#1f2937" strokeWidth="1" />
              <text x={xL - 5} y={y} textAnchor="end" dominantBaseline="middle" fill="#4b5563" fontSize="10">
                {v}{unit}
              </text>
            </g>
          )
        })}

        {/* Ideal zone band */}
        <rect
          x={xL} y={yBandTop}
          width={xR - xL} height={Math.max(0, yBandBot - yBandTop)}
          fill="#10b981" fillOpacity="0.07"
          stroke="#10b981" strokeOpacity="0.2" strokeWidth="1" strokeDasharray="4 3"
        />

        {/* Fill under line */}
        {fillPath && (
          <path d={fillPath} fill={lineColor} fillOpacity="0.05" />
        )}

        {/* Data line */}
        <path
          d={linePath}
          fill="none"
          stroke={lineColor}
          strokeWidth="2"
          strokeLinejoin="round"
          strokeLinecap="round"
        />

        {/* Out-of-range dots */}
        {pts.filter(p => p.out).map((p, i) => (
          <circle key={i} cx={p.x} cy={p.y} r="3" fill="#f59e0b" stroke="#030712" strokeWidth="1.5" />
        ))}

        {/* Hovered dot + vertical guide */}
        {hovered && (
          <g>
            <line
              x1={hovered.x} y1={PAD.top}
              x2={hovered.x} y2={PAD.top + CHART_H}
              stroke="#374151" strokeWidth="1" strokeDasharray="3 2"
            />
            <circle
              cx={hovered.x} cy={hovered.y} r="5"
              fill={hovered.out ? '#f59e0b' : lineColor}
              stroke="#030712" strokeWidth="2"
            />
          </g>
        )}

        {/* X axis labels */}
        {xticks.map(({ r, i }) => (
          <text key={i} x={mapX(i, readings.length)} y={VH - 6} textAnchor="middle" fill="#4b5563" fontSize="9">
            {fmtDate(r.timestamp)}
          </text>
        ))}

        {/* Bottom axis line */}
        <line x1={xL} y1={PAD.top + CHART_H} x2={xR} y2={PAD.top + CHART_H} stroke="#1f2937" strokeWidth="1" />
      </svg>
    </div>
  )
}
