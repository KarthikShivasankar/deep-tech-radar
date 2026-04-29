import { useState, useEffect } from 'react'
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis,
  PolarRadiusAxis, Legend, Tooltip, ResponsiveContainer,
} from 'recharts'
import { api } from '../api.js'

function buildChartData(profiles, areas) {
  if (!profiles.length) return []
  return areas
    .map(area => {
      const avgI = profiles.reduce((s, p) => s + (p.interests?.[area] || 0), 0) / profiles.length
      const avgE = profiles.reduce((s, p) => s + (p.expertise?.[area] || 0), 0) / profiles.length
      if (avgI === 0 && avgE === 0) return null
      return {
        subject: area.length > 20 ? area.slice(0, 20) + '…' : area,
        interest: Math.round(avgI * 10) / 10,
        expertise: Math.round(avgE * 10) / 10,
      }
    })
    .filter(Boolean)
}

const TT = {
  background: '#fff',
  border: '1px solid #D4DCF0',
  borderRadius: '8px',
  fontSize: '12px',
  fontFamily: 'Inter, sans-serif',
  boxShadow: '0 4px 16px rgba(15,23,42,0.10)',
  padding: '8px 12px',
}

export default function TeamRadar({ config }) {
  const { team_members, tech_areas } = config

  const [allProfiles, setAll]    = useState([])
  const [filter, setFilter]      = useState([])
  const [status, setStatus]      = useState('')
  const [loading, setLoading]    = useState(false)

  const load = async () => {
    setLoading(true); setStatus('⏳ Fetching profiles…')
    try {
      const ps = await api.getAllProfiles()
      setAll(ps)
      setStatus(`✅ ${ps.length} profile${ps.length !== 1 ? 's' : ''} loaded`)
    } catch { setStatus('❌ Error loading profiles.') }
    setLoading(false)
  }

  useEffect(() => { load() }, [])

  const visible = filter.length ? allProfiles.filter(p => filter.includes(p.name)) : allProfiles
  const data    = buildChartData(visible, tech_areas)

  const toggle = name => setFilter(prev => prev.includes(name) ? prev.filter(n => n !== name) : [...prev, name])

  return (
    <div className="card col">

      {/* Controls */}
      <div className="row-end">
        <button className="btn btn-secondary" onClick={load} disabled={loading}>🔄 Refresh</button>
        {filter.length > 0 && (
          <button className="btn btn-ghost" onClick={() => setFilter([])}>
            ✕ Clear filter ({filter.length})
          </button>
        )}
        {status && (
          <p className={`status ${status.startsWith('✅') ? 'ok' : status.startsWith('❌') ? 'error' : 'info'}`}>
            {status}
          </p>
        )}
      </div>

      {/* Member filter pills */}
      <div>
        <div className="section-label">Filter by member</div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
          {team_members.map(m => (
            <button
              key={m}
              className={`member-pill${filter.includes(m) ? ' active' : ''}`}
              onClick={() => toggle(m)}
            >
              {m}
            </button>
          ))}
        </div>
      </div>

      {/* Chart */}
      <div className="chart-wrap">
        {data.length === 0 ? (
          <div className="chart-empty">
            {loading
              ? <><div className="spinner" /><span>Loading…</span></>
              : <><span style={{ fontSize: '2rem' }}>📡</span><span>No data yet — submit profiles first</span></>
            }
          </div>
        ) : (
          <>
            <p style={{
              fontFamily: 'var(--fc)', fontSize: '0.78rem', fontWeight: 600,
              color: 'var(--ink3)', textAlign: 'center', marginBottom: '0.25rem',
              letterSpacing: '0.06em', textTransform: 'uppercase',
            }}>
              Team Deep Tech Radar &nbsp;·&nbsp; {data.length} active area{data.length !== 1 ? 's' : ''}
              {filter.length > 0 && ` · ${visible.length} member${visible.length !== 1 ? 's' : ''}`}
            </p>
            <ResponsiveContainer width="100%" height={490}>
              <RadarChart data={data} margin={{ top: 12, right: 35, bottom: 12, left: 35 }}>
                <PolarGrid gridType="polygon" stroke="rgba(37,99,235,0.09)" />
                <PolarAngleAxis
                  dataKey="subject"
                  tick={{ fontSize: 10, fontFamily: 'Inter, sans-serif', fill: '#334155' }}
                  tickLine={false}
                />
                <PolarRadiusAxis
                  domain={[0, 5]} tickCount={6} angle={90} axisLine={false}
                  tick={{ fontSize: 9, fontFamily: 'JetBrains Mono, monospace', fill: '#94A3B8' }}
                />
                <Radar name="Interest (avg)"  dataKey="interest"  stroke="#2563EB" fill="#2563EB" fillOpacity={0.11} strokeWidth={2} dot={{ fill: '#2563EB', r: 3 }} />
                <Radar name="Expertise (avg)" dataKey="expertise" stroke="#0D9488" fill="#0D9488" fillOpacity={0.09} strokeWidth={2} dot={{ fill: '#0D9488', r: 3 }} />
                <Legend wrapperStyle={{ fontSize: '12px', fontFamily: 'Inter, sans-serif', color: '#1E293B', paddingTop: '8px' }} />
                <Tooltip formatter={(v, n) => [v.toFixed(1), n]} contentStyle={TT} />
              </RadarChart>
            </ResponsiveContainer>
          </>
        )}
      </div>
    </div>
  )
}
