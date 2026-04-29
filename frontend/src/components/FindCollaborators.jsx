import { useState, useEffect, useMemo } from 'react'
import { api } from '../api.js'

function scoreProfile(profile, selectedAreas, minScore) {
  const sharedAreas = selectedAreas.filter(
    a => (profile.interests?.[a] || 0) >= minScore || (profile.expertise?.[a] || 0) >= minScore
  )
  if (!sharedAreas.length) return null

  const corpus = [profile.description, profile.deep_tech_contribution, profile.deep_tech_examples]
    .filter(Boolean).join(' ').toLowerCase()

  const keywordHits = selectedAreas.flatMap(a =>
    a.toLowerCase().split(/[\s/&+]+/).filter(w => w.length > 3)
  ).filter(w => corpus.includes(w)).length

  return {
    ...profile,
    _sharedAreas: sharedAreas,
    _score: sharedAreas.reduce((s, a) =>
      s + (profile.interests?.[a] || 0) + (profile.expertise?.[a] || 0), 0
    ) + keywordHits * 1.5,
  }
}

function ResultCard({ p }) {
  return (
    <div className="synergy-card">
      <div className="synergy-card-header">
        <div className="avatar">{p.name[0]}</div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div className="synergy-name">{p.name}</div>
          <div className="synergy-org">{p.org || 'SINTEF'}</div>
        </div>
      </div>

      <div className="synergy-card-body">
        {p._sharedAreas.length > 0 && (
          <div>
            <div className="card-micro-label">Shared areas</div>
            <div className="chips-row">
              {p._sharedAreas.map(a => <span key={a} className="badge badge-blue">{a}</span>)}
            </div>
          </div>
        )}

        {(p.deep_tech_contribution || p.description) && (
          <p className="synergy-quote">
            {(p.deep_tech_contribution || p.description).slice(0, 160)}
            {(p.deep_tech_contribution || p.description).length > 160 ? '…' : ''}
          </p>
        )}
      </div>
    </div>
  )
}

export default function FindCollaborators({ config }) {
  const { tech_areas } = config

  const [profiles, setProfiles]   = useState([])
  const [selectedAreas, setAreas] = useState([])
  const [minScore, setMinScore]   = useState(3)
  const [loadStatus, setLoadSt]   = useState('')

  useEffect(() => {
    setLoadSt('⏳ Loading profiles…')
    api.getAllProfiles()
      .then(ps => { setProfiles(ps); setLoadSt('') })
      .catch(() => setLoadSt('❌ Error loading profiles.'))
  }, [])

  const toggleArea = a =>
    setAreas(prev => prev.includes(a) ? prev.filter(x => x !== a) : [...prev, a])

  const results = useMemo(() => {
    if (!selectedAreas.length) return []
    return profiles
      .map(p => scoreProfile(p, selectedAreas, minScore))
      .filter(Boolean)
      .sort((a, b) => b._score - a._score)
  }, [profiles, selectedAreas, minScore])

  const hasQuery = selectedAreas.length > 0

  return (
    <div className="card col">

      {/* Filters */}
      <div className="card-section col" style={{ gap: '0.9rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span style={{ fontSize: '1rem' }}>🎯</span>
          <span style={{ fontFamily: 'var(--fc)', fontWeight: 700, fontSize: '0.9rem', color: 'var(--ink2)' }}>
            What are you looking to work on?
          </span>
        </div>

        <div>
          <label className="field-label" style={{ display: 'block', marginBottom: '0.5rem' }}>Tech areas</label>
          <div className="cb-grid">
            {tech_areas.map(area => (
              <label key={area} className={`cb-item${selectedAreas.includes(area) ? ' checked' : ''}`}>
                <input type="checkbox" checked={selectedAreas.includes(area)} onChange={() => toggleArea(area)} />
                <span>{area}</span>
              </label>
            ))}
          </div>
        </div>

        <div className="field" style={{ maxWidth: 260 }}>
          <label className="field-label">Min. score threshold</label>
          <div className="slider-row" style={{ marginTop: '0.35rem' }}>
            <input type="range" min={1} max={5} step={1} value={minScore}
              onChange={e => setMinScore(+e.target.value)}
              style={{ flex: 1, accentColor: 'var(--blue)' }} />
            <span className="slider-val">{minScore}</span>
          </div>
        </div>
      </div>

      {/* Status */}
      <div className="row-end">
        {loadStatus && <p className="status info">{loadStatus}</p>}
        {hasQuery && (
          <p className="status ok" style={{ marginRight: 'auto' }}>
            {results.length} person{results.length !== 1 ? 's' : ''} with overlap found
          </p>
        )}
      </div>

      {/* Results */}
      {!hasQuery ? (
        <div style={{ textAlign: 'center', padding: '2.5rem 1rem', color: 'var(--muted)', fontSize: '0.9rem' }}>
          <div style={{ fontSize: '2.5rem', marginBottom: '0.6rem' }}>🔭</div>
          Select tech areas to discover who you can build deep tech with.
        </div>
      ) : results.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--muted)', fontSize: '0.88rem' }}>
          No one matches — try lowering the score threshold or selecting different areas.
        </div>
      ) : (
        <>
          <div className="section-label">
            {results.length} researcher{results.length !== 1 ? 's' : ''} with overlapping areas
          </div>
          <div className="synergy-grid">
            {results.map(p => <ResultCard key={p.name} p={p} />)}
          </div>
        </>
      )}
    </div>
  )
}
