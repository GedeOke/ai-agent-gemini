import type { FormEvent } from 'react'
import { useEffect, useMemo, useState } from 'react'
import './App.css'

type Config = {
  baseUrl: string
  apiKey: string
  tenantId: string
}

type TenantSettings = {
  tenant_id: string
  persona: {
    persona: string
    style_prompt: string
    tone: string
    language: string
  }
  sop: {
    steps: { name: string; description: string; order: number }[]
  }
  working_hours: string
  timezone: string
  followup_enabled: boolean
  followup_interval_minutes: number
  api_key?: string
}

type FollowUpRow = {
  id: string
  user_id: string
  reason: string
  scheduled_at: string
  channel: string
  metadata: Record<string, unknown>
  status: string
  sent_at?: string | null
  last_error?: string | null
}

const STORAGE_KEY = 'agent_dashboard_config'

function loadConfig(): Config {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) return JSON.parse(raw)
  } catch (err) {
    console.warn('Failed to load config', err)
  }
  return { baseUrl: 'http://localhost:8000', apiKey: '', tenantId: '' }
}

function saveConfig(cfg: Config) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(cfg))
}

function App() {
  const [config, setConfig] = useState<Config>(loadConfig)
  const [settings, setSettings] = useState<TenantSettings | null>(null)
  const [loadingSettings, setLoadingSettings] = useState(false)
  const [settingsMessage, setSettingsMessage] = useState<string | null>(null)
  const [kbTitle, setKbTitle] = useState('')
  const [kbContent, setKbContent] = useState('')
  const [kbTags, setKbTags] = useState('')
  const [kbMessage, setKbMessage] = useState<string | null>(null)
  const [followups, setFollowups] = useState<FollowUpRow[]>([])
  const [followupStatus, setFollowupStatus] = useState('pending')
  const [health, setHealth] = useState<string | null>(null)
  const [toast, setToast] = useState<string | null>(null)

  const headers = useMemo(
    () => ({
      'Content-Type': 'application/json',
      'X-API-Key': config.apiKey,
      'X-Tenant-Id': config.tenantId,
    }),
    [config]
  )

  useEffect(() => {
    saveConfig(config)
  }, [config])

  const handleConfigSubmit = (e: FormEvent) => {
    e.preventDefault()
    setToast('Config saved locally')
    setTimeout(() => setToast(null), 2000)
  }

  async function fetchSettings() {
    if (!config.baseUrl || !config.tenantId || !config.apiKey) {
      setSettingsMessage('Isi base URL, tenant ID, dan API key dulu.')
      return
    }
    setLoadingSettings(true)
    setSettingsMessage(null)
    try {
      const res = await fetch(
        `${config.baseUrl}/tenants/${config.tenantId}/settings`,
        { headers }
      )
      if (!res.ok) throw new Error(await res.text())
      const data = (await res.json()) as TenantSettings
      setSettings(data)
      setSettingsMessage('Loaded.')
    } catch (err: unknown) {
      setSettingsMessage('Gagal load settings: ' + String(err))
    } finally {
      setLoadingSettings(false)
    }
  }

  async function saveSettings(e: FormEvent) {
    e.preventDefault()
    if (!settings) return
    setSettingsMessage(null)
    try {
      const res = await fetch(
        `${config.baseUrl}/tenants/${config.tenantId}/settings`,
        {
          method: 'PUT',
          headers,
          body: JSON.stringify(settings),
        }
      )
      if (!res.ok) throw new Error(await res.text())
      const data = (await res.json()) as TenantSettings
      setSettings(data)
      setSettingsMessage('Settings disimpan.')
    } catch (err: unknown) {
      setSettingsMessage('Gagal simpan: ' + String(err))
    }
  }

  async function upsertKb(e: FormEvent) {
    e.preventDefault()
    setKbMessage(null)
    if (!kbTitle || !kbContent) {
      setKbMessage('Title dan content wajib.')
      return
    }
    try {
      const payload = {
        tenant_id: config.tenantId,
        items: [
          {
            title: kbTitle,
            content: kbContent,
            tags: kbTags
              .split(',')
              .map((t) => t.trim())
              .filter(Boolean),
          },
        ],
      }
      const res = await fetch(`${config.baseUrl}/kb/upsert`, {
        method: 'POST',
        headers,
        body: JSON.stringify(payload),
      })
      if (!res.ok) throw new Error(await res.text())
      setKbMessage('KB item disimpan.')
      setKbTitle('')
      setKbContent('')
      setKbTags('')
    } catch (err: unknown) {
      setKbMessage('Gagal upsert KB: ' + String(err))
    }
  }

  async function loadFollowups() {
    try {
      const res = await fetch(
        `${config.baseUrl}/followup?status=${followupStatus}`,
        { headers }
      )
      if (!res.ok) throw new Error(await res.text())
      const data = (await res.json()) as FollowUpRow[]
      setFollowups(data)
    } catch (err: unknown) {
      setToast('Gagal load follow-up: ' + String(err))
    }
  }

  async function checkHealth() {
    try {
      const res = await fetch(`${config.baseUrl}/health`)
      if (!res.ok) throw new Error(await res.text())
      setHealth('OK')
    } catch (err: unknown) {
      setHealth('DOWN: ' + String(err))
    }
  }

  return (
    <div className="app">
      <header>
        <h1>AI Agent Dashboard</h1>
        <p>Konfigurasi tenant, KB, dan follow-up.</p>
      </header>

      {toast && <div className="toast">{toast}</div>}

      <section>
        <h2>Konfigurasi API</h2>
        <form className="card" onSubmit={handleConfigSubmit}>
          <label>
            Base URL
            <input
              value={config.baseUrl}
              onChange={(e) =>
                setConfig((c) => ({ ...c, baseUrl: e.target.value }))
              }
              placeholder="http://localhost:8000"
            />
          </label>
          <label>
            Tenant ID
            <input
              value={config.tenantId}
              onChange={(e) =>
                setConfig((c) => ({ ...c, tenantId: e.target.value }))
              }
              placeholder="demo"
            />
          </label>
          <label>
            API Key
            <input
              value={config.apiKey}
              onChange={(e) =>
                setConfig((c) => ({ ...c, apiKey: e.target.value }))
              }
              placeholder="tenant api key"
            />
          </label>
          <div className="actions">
            <button type="submit">Simpan</button>
            <button type="button" onClick={checkHealth}>
              Cek Health
            </button>
            {health && <span className="muted">Health: {health}</span>}
          </div>
        </form>
      </section>

      <section>
        <div className="section-head">
          <h2>Tenant Settings</h2>
          <button onClick={fetchSettings} disabled={loadingSettings}>
            {loadingSettings ? 'Loading...' : 'Load Settings'}
          </button>
        </div>
        {settingsMessage && <div className="muted">{settingsMessage}</div>}
        {settings && (
          <form className="card grid" onSubmit={saveSettings}>
            <label>
              Persona
              <input
                value={settings.persona.persona}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    persona: { ...settings.persona, persona: e.target.value },
                  })
                }
              />
            </label>
            <label>
              Style Prompt
              <input
                value={settings.persona.style_prompt}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    persona: { ...settings.persona, style_prompt: e.target.value },
                  })
                }
              />
            </label>
            <label>
              Tone
              <input
                value={settings.persona.tone}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    persona: { ...settings.persona, tone: e.target.value },
                  })
                }
              />
            </label>
            <label>
              Language
              <input
                value={settings.persona.language}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    persona: { ...settings.persona, language: e.target.value },
                  })
                }
              />
            </label>
            <label>
              Working Hours
              <input
                value={settings.working_hours}
                onChange={(e) =>
                  setSettings({ ...settings, working_hours: e.target.value })
                }
              />
            </label>
            <label>
              Timezone
              <input
                value={settings.timezone}
                onChange={(e) =>
                  setSettings({ ...settings, timezone: e.target.value })
                }
              />
            </label>
            <label>
              Follow-up Enabled
              <select
                value={settings.followup_enabled ? 'true' : 'false'}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    followup_enabled: e.target.value === 'true',
                  })
                }
              >
                <option value="true">Yes</option>
                <option value="false">No</option>
              </select>
            </label>
            <label>
              Follow-up Interval (minutes)
              <input
                type="number"
                value={settings.followup_interval_minutes}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    followup_interval_minutes: Number(e.target.value),
                  })
                }
              />
            </label>
            <div className="actions">
              <button type="submit">Simpan Settings</button>
              {settings.api_key && (
                <span className="muted">Tenant API Key: {settings.api_key}</span>
              )}
            </div>
          </form>
        )}
      </section>

      <section>
        <h2>Knowledge Base</h2>
        <form className="card grid" onSubmit={upsertKb}>
          <label>
            Title
            <input
              value={kbTitle}
              onChange={(e) => setKbTitle(e.target.value)}
              placeholder="Produk A"
            />
          </label>
          <label className="full">
            Content
            <textarea
              value={kbContent}
              onChange={(e) => setKbContent(e.target.value)}
              rows={4}
              placeholder="Deskripsi dan harga produk..."
            />
          </label>
          <label>
            Tags (comma)
            <input
              value={kbTags}
              onChange={(e) => setKbTags(e.target.value)}
              placeholder="produk,harga"
            />
          </label>
          <div className="actions">
            <button type="submit">Simpan KB Item</button>
            {kbMessage && <span className="muted">{kbMessage}</span>}
          </div>
        </form>
      </section>

      <section>
        <div className="section-head">
          <h2>Follow-up</h2>
          <div className="inline">
            <label>
              Status
              <select
                value={followupStatus}
                onChange={(e) => setFollowupStatus(e.target.value)}
              >
                <option value="pending">pending</option>
                <option value="sent">sent</option>
                <option value="failed">failed</option>
              </select>
            </label>
            <button onClick={loadFollowups}>Refresh</button>
          </div>
        </div>
        <div className="card">
          {followups.length === 0 ? (
            <p className="muted">Tidak ada data untuk status ini.</p>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>User</th>
                  <th>Reason</th>
                  <th>Scheduled</th>
                  <th>Status</th>
                  <th>Channel</th>
                  <th>Metadata</th>
                  <th>Sent at</th>
                  <th>Error</th>
                </tr>
              </thead>
              <tbody>
                {followups.map((f) => (
                  <tr key={f.id}>
                    <td>{f.user_id}</td>
                    <td>{f.reason}</td>
                    <td>{new Date(f.scheduled_at).toLocaleString()}</td>
                    <td>{f.status}</td>
                    <td>{f.channel}</td>
                    <td>
                      <code>{JSON.stringify(f.metadata || {})}</code>
                    </td>
                    <td>
                      {f.sent_at ? new Date(f.sent_at).toLocaleString() : '-'}
                    </td>
                    <td>{f.last_error || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </section>
    </div>
  )
}

export default App
