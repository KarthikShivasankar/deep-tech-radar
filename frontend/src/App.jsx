import { useState, useEffect } from 'react'
import { api } from './api.js'
import SubmitProfile from './components/SubmitProfile.jsx'
import TeamRadar from './components/TeamRadar.jsx'
import FindCollaborators from './components/FindCollaborators.jsx'
import AllSubmissions from './components/AllSubmissions.jsx'
import AskAI from './components/AskAI.jsx'

const TABS = [
  { id: 'submit',      icon: '📡', label: 'Submit Profile' },
  { id: 'radar',       icon: '🎯', label: 'Team Radar' },
  { id: 'find',        icon: '🔍', label: 'Find Synergy' },
  { id: 'submissions', icon: '📊', label: 'All Profiles' },
  { id: 'ask',         icon: '💬', label: 'Ask the Data' },
]

export default function App() {
  const [activeTab, setActiveTab] = useState('submit')
  const [appConfig, setAppConfig] = useState(null)
  const [profileCount, setProfileCount] = useState(0)
  const [configError, setConfigError] = useState(null)

  useEffect(() => {
    api.getConfig()
      .then(cfg => {
        setAppConfig(cfg)
        return api.getAllProfiles()
      })
      .then(ps => setProfileCount(ps.length))
      .catch(e => setConfigError(e.message))
  }, [])

  if (configError) {
    return (
      <div className="app-error">
        <p>⚠️ Could not reach the API server.</p>
        <pre>{configError}</pre>
        <p>Make sure <code>python server.py</code> is running on port 8000.</p>
      </div>
    )
  }

  if (!appConfig) {
    return (
      <div className="app-loading">
        <div className="spinner" />
        <span>Connecting to server…</span>
      </div>
    )
  }

  return (
    <div className="app">
      {/* Hero */}
      <header className="hero">
        <div className="hero-bg" />
        <div className="hero-inner">
          <div className="hero-text">
            <div className="hero-badge">◈ SINTEF Research Group</div>
            <h1>{appConfig.app_title}</h1>
            <p>{appConfig.app_subtitle}</p>
          </div>
          <div className="hero-stats">
            <div className="hero-stat">
              <span className="hero-stat-num">{profileCount}</span>
              <span className="hero-stat-label">Profiles</span>
            </div>
            <div className="hero-stat">
              <span className="hero-stat-num">{appConfig.tech_areas.length}</span>
              <span className="hero-stat-label">Areas</span>
            </div>
            <div className="hero-stat">
              <span className="hero-stat-num">{appConfig.team_members.length}</span>
              <span className="hero-stat-label">Members</span>
            </div>
          </div>
        </div>
      </header>

      {/* Tab navigation */}
      <nav className="tab-bar">
        {TABS.map(t => (
          <button
            key={t.id}
            className={`tab-btn${activeTab === t.id ? ' active' : ''}`}
            onClick={() => setActiveTab(t.id)}
          >
            <span className="tab-icon">{t.icon}</span>
            <span className="tab-label">{t.label}</span>
          </button>
        ))}
      </nav>

      {/* Tab content */}
      <main>
        {activeTab === 'submit'      && <SubmitProfile     config={appConfig} onSaved={() => setProfileCount(c => c + 1)} />}
        {activeTab === 'radar'       && <TeamRadar         config={appConfig} />}
        {activeTab === 'find'        && <FindCollaborators config={appConfig} />}
        {activeTab === 'submissions' && <AllSubmissions    config={appConfig} />}
        {activeTab === 'ask'         && <AskAI             config={appConfig} />}
      </main>
    </div>
  )
}
