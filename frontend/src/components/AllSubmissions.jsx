import { useState, useEffect } from 'react'
import { api } from '../api.js'

function toCSV(profiles) {
  const cols = ['name','org','timestamp','areas','interests','expertise','collab_goals','description','deep_tech_contribution','deep_tech_examples']
  const esc  = v => `"${(Array.isArray(v) || (v && typeof v === 'object') ? JSON.stringify(v) : String(v ?? '')).replace(/"/g,'""')}"`
  const rows = profiles.map(p => cols.map(c => esc(p[c])).join(','))
  return [cols.join(','), ...rows].join('\n')
}

function download(profiles) {
  const blob = new Blob([toCSV(profiles)], { type: 'text/csv;charset=utf-8;' })
  const url  = URL.createObjectURL(blob)
  Object.assign(document.createElement('a'), { href: url, download: 'deep_tech_profiles.csv' }).click()
  URL.revokeObjectURL(url)
}

function fmtDate(v) {
  try { return new Date(v).toLocaleString('en-GB', { dateStyle: 'short', timeStyle: 'short' }) }
  catch { return v || '—' }
}

function fmtArr(v) { return Array.isArray(v) && v.length ? v.join(', ') : '—' }

export default function AllSubmissions() {
  const [profiles, setProfiles]   = useState([])
  const [status, setStatus]       = useState('')
  const [loading, setLoading]     = useState(false)
  const [expanded, setExpanded]   = useState(null)

  const [adminPwd, setAdminPwd]   = useState('')
  const [adminSt,  setAdminSt]    = useState('')
  const [clearing, setClearing]   = useState(false)

  const load = async () => {
    setLoading(true); setStatus('⏳ Loading…')
    try {
      const ps = await api.getAllProfiles()
      setProfiles(ps)
      setStatus(`✅ ${ps.length} profile${ps.length !== 1 ? 's' : ''} loaded`)
    } catch { setStatus('❌ Error loading.') }
    setLoading(false)
  }

  useEffect(() => { load() }, [])

  async function handleClear() {
    setClearing(true); setAdminSt('⏳ Clearing…')
    try {
      await api.clearProfiles(adminPwd)
      setAdminSt('✅ All profiles deleted.')
      setAdminPwd('')
      load()
    } catch (e) {
      setAdminSt(e.message.includes('403') ? '❌ Wrong password.' : `❌ ${e.message}`)
    }
    setClearing(false)
  }

  return (
    <div className="card col">

      {/* Header */}
      <div className="row-end">
        <button className="btn btn-secondary" onClick={load} disabled={loading}>🔄 Refresh</button>
        {profiles.length > 0 && (
          <button className="btn btn-ghost" onClick={() => download(profiles)}>⬇ Download CSV</button>
        )}
        {status && (
          <p className={`status ${status.startsWith('✅') ? 'ok' : status.startsWith('❌') ? 'error' : 'info'}`}>
            {status}
          </p>
        )}
      </div>

      {/* Table */}
      <div className="data-table-wrap">
        <table className="data-table">
          <thead>
            <tr>
              <th>Name</th><th>Org</th><th>Saved</th><th>Active Areas</th>
              <th>Deep Tech Contribution</th><th>Goals</th><th>Details</th>
            </tr>
          </thead>
          <tbody>
            {profiles.length === 0 ? (
              <tr className="empty-row"><td colSpan={7}>{loading ? 'Loading…' : 'No profiles submitted yet.'}</td></tr>
            ) : profiles.map(p => (
              <>
                <tr key={p.name} onClick={() => setExpanded(expanded === p.name ? null : p.name)} style={{ cursor: 'pointer' }}>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.55rem' }}>
                      <div style={{
                        width: 28, height: 28, borderRadius: '50%', flexShrink: 0,
                        background: 'linear-gradient(135deg,var(--blue),var(--purple))',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        fontFamily: 'var(--fc)', fontWeight: 700, fontSize: '0.8rem', color: '#fff',
                      }}>{p.name[0]}</div>
                      <span style={{ fontWeight: 600 }}>{p.name}</span>
                    </div>
                  </td>
                  <td style={{ color: 'var(--muted)', fontSize: '0.82rem' }}>{p.org || '—'}</td>
                  <td style={{ color: 'var(--muted)', fontSize: '0.8rem', whiteSpace: 'nowrap' }}>{fmtDate(p.timestamp)}</td>
                  <td>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.25rem', maxWidth: 220 }}>
                      {(p.areas || []).slice(0, 3).map(a => <span key={a} className="badge badge-blue" style={{ fontSize: '0.62rem' }}>{a}</span>)}
                      {(p.areas || []).length > 3 && <span className="badge badge-blue" style={{ fontSize: '0.62rem' }}>+{p.areas.length - 3}</span>}
                    </div>
                  </td>
                  <td style={{ fontSize: '0.82rem', color: 'var(--ink3)', maxWidth: 180 }}>
                    <span style={{ display: 'block', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {p.deep_tech_contribution || '—'}
                    </span>
                  </td>
                  <td>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.25rem' }}>
                      {(p.collab_goals || []).map(g => <span key={g} className="badge badge-cyan" style={{ fontSize: '0.62rem' }}>{g}</span>)}
                    </div>
                  </td>
                  <td style={{ color: 'var(--muted)', fontSize: '0.8rem' }}>
                    {expanded === p.name ? '▲ collapse' : '▼ expand'}
                  </td>
                </tr>
                {expanded === p.name && (
                  <tr key={`${p.name}-detail`} style={{ background: 'var(--surface2)' }}>
                    <td colSpan={7} style={{ padding: '1rem 1.1rem' }}>
                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                        {p.description && (
                          <div>
                            <div className="field-label" style={{ marginBottom: '0.3rem' }}>Current work / collaboration idea</div>
                            <p style={{ fontSize: '0.84rem', color: 'var(--ink3)', lineHeight: 1.55 }}>{p.description}</p>
                          </div>
                        )}
                        {p.deep_tech_contribution && (
                          <div>
                            <div className="field-label" style={{ marginBottom: '0.3rem' }}>How they will contribute to deep tech</div>
                            <p style={{ fontSize: '0.84rem', color: 'var(--ink3)', lineHeight: 1.55 }}>{p.deep_tech_contribution}</p>
                          </div>
                        )}
                        {p.deep_tech_examples && (
                          <div>
                            <div className="field-label" style={{ marginBottom: '0.3rem' }}>Deep tech examples</div>
                            <p style={{ fontSize: '0.84rem', color: 'var(--ink3)', lineHeight: 1.55 }}>{p.deep_tech_examples}</p>
                          </div>
                        )}
                      </div>
                    </td>
                  </tr>
                )}
              </>
            ))}
          </tbody>
        </table>
      </div>

      {/* Danger zone */}
      <div>
        <div className="section-label" style={{ marginTop: '0.5rem' }}>Danger zone</div>
        <div className="danger-zone">
          <h3>🔐 Admin Actions</h3>
          <div className="row-end" style={{ alignItems: 'flex-end' }}>
            <div className="field grow" style={{ maxWidth: 280 }}>
              <label className="field-label">Admin password</label>
              <input type="password" placeholder="Enter password…"
                value={adminPwd} onChange={e => setAdminPwd(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleClear()} />
            </div>
            <button className="btn btn-danger" onClick={handleClear} disabled={clearing || !adminPwd}>
              🗑 Clear All Data
            </button>
          </div>
          {adminSt && (
            <p className={`status ${adminSt.startsWith('✅') ? 'ok' : adminSt.startsWith('❌') ? 'error' : 'info'}`}
               style={{ marginTop: '0.6rem' }}>
              {adminSt}
            </p>
          )}
        </div>
      </div>
    </div>
  )
}
