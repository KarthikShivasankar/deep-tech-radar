import { useState, useRef, useEffect } from 'react'

const SUGGESTIONS = [
  'Which team members are open to collaborating on research papers?',
  'Who is working on privacy or cybersecurity topics?',
  'What deep tech areas does the team have the least coverage in?',
  'Who would be the best match for a project on digital twins?',
  'Summarise each person\'s deep tech contribution in one sentence.',
]

export default function AskAI() {
  const [question, setQuestion] = useState('')
  const [history, setHistory]   = useState([])
  const [loading, setLoading]   = useState(false)
  const [error, setError]       = useState('')
  const bottomRef               = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [history, loading])

  async function handleAsk(q) {
    const text = (q || question).trim()
    if (!text || loading) return
    setQuestion('')
    setError('')
    setLoading(true)

    // add entry with empty answer — will stream into it
    setHistory(h => [...h, { q: text, a: '' }])

    try {
      const resp = await fetch('/api/ask', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ question: text }),
      })

      if (!resp.ok) throw new Error(await resp.text())

      const reader  = resp.body.getReader()
      const decoder = new TextDecoder()

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        const chunk = decoder.decode(value, { stream: true })
        setHistory(h => {
          const next = [...h]
          next[next.length - 1] = { ...next[next.length - 1], a: next[next.length - 1].a + chunk }
          return next
        })
      }
    } catch (e) {
      setHistory(h => h.slice(0, -1))
      setError(e.message)
    }

    setLoading(false)
  }

  return (
    <div className="card col" style={{ gap: 0, padding: 0, overflow: 'hidden' }}>

      {/* Header */}
      <div style={{ padding: '1.2rem 1.4rem', borderBottom: '1px solid var(--border)', background: 'var(--surface)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span style={{ fontSize: '1.1rem' }}>💬</span>
          <span style={{ fontFamily: 'var(--fc)', fontWeight: 700, fontSize: '1rem', color: 'var(--ink2)', letterSpacing: '0.02em' }}>
            Ask the Data
          </span>
          <span style={{ marginLeft: 'auto', fontFamily: 'var(--fm)', fontSize: '0.65rem', color: 'var(--muted)', background: 'var(--surface2)', padding: '0.15rem 0.5rem', borderRadius: 'var(--r-pill)' }}>
            Ollama · qwen3
          </span>
        </div>
        <p style={{ margin: '0.4rem 0 0', fontSize: '0.82rem', color: 'var(--muted)' }}>
          Ask anything about the team's expertise, interests, and collaboration opportunities.
        </p>
      </div>

      {/* Chat area */}
      <div style={{ overflowY: 'auto', padding: '1.2rem 1.4rem', display: 'flex', flexDirection: 'column', gap: '1.2rem', minHeight: 320, maxHeight: 500, background: 'var(--bg)' }}>

        {history.length === 0 && !loading && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.8rem' }}>
            <p style={{ fontSize: '0.84rem', color: 'var(--muted)', textAlign: 'center', margin: 0 }}>
              Try one of these or type your own:
            </p>
            {SUGGESTIONS.map(s => (
              <button key={s} className="btn btn-ghost"
                style={{ textAlign: 'left', justifyContent: 'flex-start', fontSize: '0.83rem' }}
                onClick={() => handleAsk(s)}>
                {s}
              </button>
            ))}
          </div>
        )}

        {history.map((item, i) => (
          <div key={i} style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
            {/* Question */}
            <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
              <div style={{
                background: 'var(--blue)', color: '#fff',
                borderRadius: 'var(--r) var(--r) 4px var(--r)',
                padding: '0.6rem 0.9rem', maxWidth: '75%',
                fontSize: '0.86rem', lineHeight: 1.5,
              }}>
                {item.q}
              </div>
            </div>

            {/* Answer — streams in */}
            <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
              <div style={{
                background: 'var(--surface)',
                border: '1px solid var(--border)',
                borderRadius: '4px var(--r) var(--r) var(--r)',
                padding: '0.7rem 1rem', maxWidth: '85%',
                fontSize: '0.86rem', lineHeight: 1.65, color: 'var(--ink)',
                whiteSpace: 'pre-wrap', wordBreak: 'break-word',
              }}>
                {item.a || <span style={{ color: 'var(--muted)' }}>▍</span>}
              </div>
            </div>
          </div>
        ))}

        {loading && history[history.length - 1]?.a === '' && (
          <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
            <div style={{
              background: 'var(--surface)', border: '1px solid var(--border)',
              borderRadius: '4px var(--r) var(--r) var(--r)',
              padding: '0.7rem 1rem', display: 'flex', alignItems: 'center', gap: '0.5rem',
              fontSize: '0.84rem', color: 'var(--muted)',
            }}>
              <div className="spinner" style={{ width: 13, height: 13, borderWidth: 2 }} /> Thinking…
            </div>
          </div>
        )}

        {error && <p className="status error">{error}</p>}

        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div style={{
        padding: '0.9rem 1.2rem', borderTop: '1px solid var(--border)',
        background: 'var(--surface)', display: 'flex', gap: '0.6rem', alignItems: 'flex-end',
      }}>
        <textarea
          rows={2}
          style={{ flex: 1, resize: 'none', fontSize: '0.88rem' }}
          placeholder="Ask anything about the team… (Enter to send, Shift+Enter for newline)"
          value={question}
          onChange={e => setQuestion(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleAsk() } }}
        />
        <button className="btn btn-primary" onClick={() => handleAsk()}
          disabled={loading || !question.trim()} style={{ alignSelf: 'flex-end' }}>
          Ask
        </button>
      </div>
    </div>
  )
}
