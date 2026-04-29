export const api = {
  async getConfig() {
    return fetch('/api/config').then(r => r.json())
  },

  async getProfile(name) {
    const r = await fetch(`/api/profiles/${encodeURIComponent(name)}`)
    if (r.status === 404) return null
    if (!r.ok) throw new Error(await r.text())
    return r.json()
  },

  async getAllProfiles() {
    return fetch('/api/profiles').then(r => r.json())
  },

  async saveProfile(profile) {
    const r = await fetch('/api/profiles', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(profile),
    })
    if (!r.ok) throw new Error(await r.text())
    return r.json()
  },

  async clearProfiles(password) {
    const r = await fetch('/api/profiles', {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password }),
    })
    if (!r.ok) throw new Error(await r.text())
    return r.json()
  },

  async askQuestion(question) {
    const r = await fetch('/api/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
    })
    if (!r.ok) throw new Error(await r.text())
    return r.json()
  },
}
