import { useState, useEffect, useCallback } from 'react'
import { api } from '../api.js'

export default function SubmitProfile({ config, onSaved }) {
  const { team_members, tech_areas, collab_goals } = config

  const [name, setName]           = useState(team_members[0])
  const [org, setOrg]             = useState('')
  const [selectedAreas, setAreas] = useState([])
  const [interests, setInterests] = useState({})
  const [expertise, setExpertise] = useState({})
  const [collabGoals, setGoals]   = useState([])
  const [description, setDesc]    = useState('')
  const [contribution, setContrib] = useState('')
  const [examples, setExamples]   = useState('')

  const [profileStatus, setProSt] = useState('')
  const [saveStatus, setSaveSt]   = useState('')
  const [saving, setSaving]       = useState(false)

  const resetForm = useCallback(() => {
    setAreas([]); setInterests({}); setExpertise({})
    setGoals([]); setDesc(''); setContrib(''); setExamples('')
    setSaveSt('')
  }, [])

  const loadProfile = useCallback(async n => {
    if (n === 'External Collaborator') { resetForm(); setProSt(''); return }
    setProSt('⏳ Loading profile…')
    try {
      const p = await api.getProfile(n)
      if (!p) {
        resetForm()
        setProSt('🆕 No profile yet — fill in your details and save.')
      } else {
        setAreas(p.areas || [])
        setInterests(p.interests || {})
        setExpertise(p.expertise || {})
        setGoals(p.collab_goals || [])
        setDesc(p.description || '')
        setContrib(p.deep_tech_contribution || '')
        setExamples(p.deep_tech_examples || '')
        setProSt('✅ Profile loaded — update any field and save.')
      }
    } catch { setProSt('❌ Error loading profile.') }
  }, [resetForm])

  useEffect(() => { loadProfile(name) }, [name, loadProfile])

  const toggleArea = a =>
    setAreas(prev => prev.includes(a) ? prev.filter(x => x !== a) : [...prev, a])

  const toggleGoal = g =>
    setGoals(prev => prev.includes(g) ? prev.filter(x => x !== g) : [...prev, g])

  async function handleSave() {
    setSaving(true); setSaveSt('⏳ Saving…')
    const effName = name === 'External Collaborator' ? (org.trim() || 'Anonymous') : name
    const filtI = Object.fromEntries(Object.entries(interests).filter(([k]) => selectedAreas.includes(k)))
    const filtE = Object.fromEntries(Object.entries(expertise).filter(([k]) => selectedAreas.includes(k)))
    try {
      await api.saveProfile({
        name: effName,
        org: name === 'External Collaborator' ? org : 'SINTEF',
        areas: selectedAreas,
        interests: filtI,
        expertise: filtE,
        collab_goals: collabGoals,
        description,
        deep_tech_contribution: contribution,
        deep_tech_examples: examples,
      })
      setSaveSt('✅ Profile saved successfully!')
      onSaved?.()
    } catch (e) { setSaveSt(`❌ ${e.message}`) }
    setSaving(false)
  }

  return (
    <div className="card col">

      {/* ── Identity ── */}
      <div className="row">
        <div className="field grow">
          <label className="field-label">Your name</label>
          <select value={name} onChange={e => setName(e.target.value)}>
            {team_members.map(m => <option key={m}>{m}</option>)}
            <option>External Collaborator</option>
          </select>
        </div>
        {name === 'External Collaborator' && (
          <div className="field grow">
            <label className="field-label">Organisation</label>
            <input type="text" placeholder="Your organisation…" value={org} onChange={e => setOrg(e.target.value)} />
          </div>
        )}
      </div>

      {profileStatus && (
        <p className={`status ${profileStatus.startsWith('✅') ? 'ok' : profileStatus.startsWith('❌') ? 'error' : 'info'}`}>
          {profileStatus}
        </p>
      )}

      {/* ── Tech area selection ── */}
      <div>
        <div className="section-label">Select your active tech areas</div>
        <div className="cb-grid">
          {tech_areas.map(area => (
            <label key={area} className={`cb-item${selectedAreas.includes(area) ? ' checked' : ''}`}>
              <input type="checkbox" checked={selectedAreas.includes(area)} onChange={() => toggleArea(area)} />
              <span>{area}</span>
            </label>
          ))}
        </div>
      </div>

      {/* ── Ratings ── */}
      {selectedAreas.length > 0 && (
        <div>
          <div className="section-label">
            Rate selected areas
            <span className="hint-pill">0 = not applicable · 5 = leading expert</span>
          </div>
          <div className="area-sliders-wrap">
            {selectedAreas.map(area => (
              <div key={area} className="area-slider-row">
                <div className="area-name">{area}</div>
                <div className="slider-field">
                  <div className="slider-field-label">Interest</div>
                  <div className="slider-row">
                    <input type="range" min={0} max={5} step={1}
                      value={interests[area] ?? 0}
                      onChange={e => setInterests(p => ({ ...p, [area]: +e.target.value }))} />
                    <span className="slider-val">{interests[area] ?? 0}</span>
                  </div>
                </div>
                <div className="slider-field">
                  <div className="slider-field-label">Expertise</div>
                  <div className="slider-row">
                    <input type="range" min={0} max={5} step={1}
                      value={expertise[area] ?? 0}
                      onChange={e => setExpertise(p => ({ ...p, [area]: +e.target.value }))} />
                    <span className="slider-val">{expertise[area] ?? 0}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── Collaboration ── */}
      <div className="card-section col" style={{ gap: '0.9rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span style={{ fontSize: '1rem' }}>🤝</span>
          <span style={{ fontFamily: 'var(--fc)', fontWeight: 700, fontSize: '0.9rem', color: 'var(--ink2)', letterSpacing: '0.02em' }}>Collaboration Goals</span>
        </div>

        <div>
          <label className="field-label" style={{ display: 'block', marginBottom: '0.4rem' }}>I am open to</label>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem' }}>
            {collab_goals.map(g => (
              <label key={g} className={`cb-item${collabGoals.includes(g) ? ' checked' : ''}`} style={{ flexShrink: 0 }}>
                <input type="checkbox" checked={collabGoals.includes(g)} onChange={() => toggleGoal(g)} />
                <span>{g}</span>
              </label>
            ))}
          </div>
        </div>

        <div className="field">
          <label className="field-label">Current work / collaboration idea</label>
          <textarea
            placeholder="What are you currently building or researching? What kind of collaborations are you looking for?"
            value={description}
            onChange={e => setDesc(e.target.value)}
          />
        </div>

        <div className="field">
          <label className="field-label">How will you contribute to deep tech?</label>
          <textarea
            placeholder="What unique skills, methods, or perspectives do you bring? How do you see yourself contributing to deep tech initiatives?"
            value={contribution}
            onChange={e => setContrib(e.target.value)}
          />
        </div>

        <div className="field">
          <label className="field-label">Deep tech examples — work done &amp; areas you want to explore</label>
          <textarea
            placeholder="Describe deep tech you have worked on (projects, prototypes, papers) and areas you are excited to explore next…"
            value={examples}
            onChange={e => setExamples(e.target.value)}
          />
        </div>
      </div>

      {/* ── Save ── */}
      <div className="row-end">
        <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
          ⬆ Save Profile
        </button>
        {saveStatus && (
          <p className={`status ${saveStatus.startsWith('✅') ? 'ok' : saveStatus.startsWith('❌') ? 'error' : 'info'}`}>
            {saveStatus}
          </p>
        )}
      </div>

    </div>
  )
}
