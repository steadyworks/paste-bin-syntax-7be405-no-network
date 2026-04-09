'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'

const API = 'http://localhost:3001'

export default function HomePage() {
  const router = useRouter()
  const [code, setCode] = useState('')
  const [language, setLanguage] = useState('python')
  const [expiryType, setExpiryType] = useState('time')
  const [expiryTime, setExpiryTime] = useState('never')
  const [expiryViews, setExpiryViews] = useState(10)
  const [password, setPassword] = useState('')
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setSubmitting(true)
    try {
      const body: Record<string, unknown> = {
        code,
        language,
        expiry_type: expiryType,
        password,
      }
      if (expiryType === 'time') {
        body.expiry_time = expiryTime
      } else {
        body.expiry_views = Number(expiryViews)
      }
      const res = await fetch(`${API}/api/pastes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      const data = await res.json()
      const id = data.id
      sessionStorage.setItem('just_created', id)
      router.push(`/p/${id}`)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main style={{ maxWidth: 800, margin: '0 auto', padding: 24 }}>
      <h1 style={{ marginBottom: 20 }}>Create Paste</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <textarea
            data-testid="code-input"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            rows={15}
            style={{
              width: '100%',
              fontFamily: 'monospace',
              fontSize: 14,
              background: '#161b22',
              color: '#c9d1d9',
              border: '1px solid #30363d',
              borderRadius: 6,
              padding: 12,
              resize: 'vertical',
            }}
            placeholder="Paste your code here..."
          />
        </div>

        <div style={{ marginTop: 12, display: 'flex', gap: 16, flexWrap: 'wrap' }}>
          <label>
            Language:{' '}
            <select
              data-testid="language-select"
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              style={{ background: '#161b22', color: '#c9d1d9', border: '1px solid #30363d', borderRadius: 4, padding: '4px 8px' }}
            >
              <option value="python">Python</option>
              <option value="javascript">JavaScript</option>
              <option value="go">Go</option>
              <option value="rust">Rust</option>
              <option value="sql">SQL</option>
            </select>
          </label>

          <label>
            Expiry:{' '}
            <select
              data-testid="expiry-type-select"
              value={expiryType}
              onChange={(e) => setExpiryType(e.target.value)}
              style={{ background: '#161b22', color: '#c9d1d9', border: '1px solid #30363d', borderRadius: 4, padding: '4px 8px' }}
            >
              <option value="time">Time</option>
              <option value="views">Views</option>
            </select>
          </label>

          {expiryType === 'views' && (
            <label>
              View limit:{' '}
              <input
                data-testid="expiry-views-input"
                type="number"
                min={1}
                max={100}
                value={expiryViews}
                onChange={(e) => setExpiryViews(Number(e.target.value))}
                style={{ width: 70, background: '#161b22', color: '#c9d1d9', border: '1px solid #30363d', borderRadius: 4, padding: '4px 8px' }}
              />
            </label>
          )}

          {expiryType === 'time' && (
            <label>
              Duration:{' '}
              <select
                data-testid="expiry-time-select"
                value={expiryTime}
                onChange={(e) => setExpiryTime(e.target.value)}
                style={{ background: '#161b22', color: '#c9d1d9', border: '1px solid #30363d', borderRadius: 4, padding: '4px 8px' }}
              >
                <option value="10s">10 seconds</option>
                <option value="1m">1 minute</option>
                <option value="1h">1 hour</option>
                <option value="1d">1 day</option>
                <option value="1w">1 week</option>
                <option value="never">Never</option>
              </select>
            </label>
          )}
        </div>

        <div style={{ marginTop: 12 }}>
          <label>
            Password (optional):{' '}
            <input
              data-testid="password-input"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{ background: '#161b22', color: '#c9d1d9', border: '1px solid #30363d', borderRadius: 4, padding: '4px 8px' }}
            />
          </label>
        </div>

        <div style={{ marginTop: 20 }}>
          <button
            data-testid="create-btn"
            type="submit"
            disabled={submitting}
            style={{
              background: '#238636',
              color: '#fff',
              border: 'none',
              borderRadius: 6,
              padding: '8px 20px',
              cursor: submitting ? 'not-allowed' : 'pointer',
              fontSize: 14,
            }}
          >
            {submitting ? 'Creating...' : 'Create Paste'}
          </button>
        </div>
      </form>
    </main>
  )
}
