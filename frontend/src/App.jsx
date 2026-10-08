import { useEffect, useState } from 'react'

const API_URL = 'http://localhost:5000/api/requests'
const EMPTY_FORM = { applicant_name: '', document_type: '', document_number: '', request_date: '' }
const STATUS_OPTIONS = ['pendiente', 'aprobada', 'rechazada']

async function readResponse(response) {
  const body = await response.json()
  if (!response.ok) throw new Error(body.error || 'No se pudo completar la operación.')
  return body
}

export default function App() {
  const [requests, setRequests] = useState([])
  const [form, setForm] = useState(EMPTY_FORM)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  // La carga inicial y las mutaciones usan el mismo endpoint de listado como fuente de verdad.
  async function loadRequests() {
    try {
      const result = await readResponse(await fetch(API_URL))
      setRequests(result)
      setError('')
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadRequests()
  }, [])

  function updateField(event) {
    const fieldName = event.target.name
    const fieldValue = fieldName === 'applicant_name'
      ? event.target.value.replace(/[^\p{L}\s'’-]/gu, '')
      : fieldName === 'document_number'
        ? event.target.value.replace(/\D/g, '')
        : event.target.value
    setForm((current) => ({ ...current, [fieldName]: fieldValue }))
  }

  async function submitRequest(event) {
    event.preventDefault()
    setSaving(true)
    setError('')
    try {
      await readResponse(await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      }))
      setForm(EMPTY_FORM)
      await loadRequests()
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setSaving(false)
    }
  }

  async function updateStatus(id, status) {
    setError('')
    try {
      await readResponse(await fetch(`${API_URL}/${id}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status }),
      }))
      await loadRequests()
    } catch (requestError) {
      setError(requestError.message)
    }
  }

  const pendingCount = requests.filter((item) => item.status === 'pendiente').length

  return (
    <main className="page-shell">
      <header className="topbar">
        <a className="wordmark" href="#inicio" aria-label="Mesa de gestión, inicio">
          <span className="brand-mark">MG</span>
          <span>Mesa de gestión</span>
        </a>
        <span className="environment-label"><span className="live-dot" /> Operación local</span>
      </header>

      <section className="intro" id="inicio">
        <div>
          <p className="eyebrow">CONTROL DE TRÁMITES <span> / </span> 01</p>
          <h1>Solicitudes</h1>
          <p className="intro-copy">Registro y seguimiento en un solo lugar.</p>
        </div>
        <div className="summary" aria-label="Resumen de solicitudes">
          <div className="summary-item"><span>Total</span><strong>{requests.length}</strong></div>
          <div className="summary-item"><span>Pendientes</span><strong>{pendingCount}</strong></div>
        </div>
      </section>

      {error && <div className="alert" role="alert">{error}</div>}

      <section className="form-section" aria-labelledby="form-title">
        <div className="section-heading">
          <div><p className="eyebrow">NUEVO REGISTRO</p><h2 id="form-title">Crear solicitud</h2></div>
          <span className="section-index">01 — 02</span>
        </div>
        <form className="request-form" onSubmit={submitRequest}>
          <label className="field field-name">
            <span>Nombre del solicitante</span>
            <input name="applicant_name" value={form.applicant_name} onChange={updateField} placeholder="Ej. Camila Torres" required maxLength="120" />
          </label>
          <label className="field">
            <span>Tipo de documento</span>
            <select name="document_type" value={form.document_type} onChange={updateField} required>
              <option value="" disabled>Seleccionar tipo</option>
              <option value="Cédula">Cédula</option>
              <option value="Pasaporte">Pasaporte</option>
              <option value="DNI">DNI</option>
              <option value="Otro">Otro</option>
            </select>
          </label>
          <label className="field">
            <span>Número de documento</span>
            <input type="text" inputMode="numeric" pattern="[0-9]+" title="Ingresa solo números." name="document_number" value={form.document_number} onChange={updateField} placeholder="Ej. 00123456" required maxLength="40" />
          </label>
          <label className="field">
            <span>Fecha de solicitud</span>
            <input type="date" name="request_date" value={form.request_date} onChange={updateField} required />
          </label>
          <button className="primary-button" type="submit" disabled={saving}>
            <span>{saving ? 'Guardando…' : 'Registrar solicitud'}</span><span aria-hidden="true">↗</span>
          </button>
        </form>
      </section>

      <section className="list-section" aria-labelledby="list-title">
        <div className="section-heading list-heading">
          <div><p className="eyebrow">SEGUIMIENTO</p><h2 id="list-title">Solicitudes registradas</h2></div>
          <span className="record-count">{requests.length} {requests.length === 1 ? 'registro' : 'registros'}</span>
        </div>
        <div className="table-wrap">
          <table>
            <thead><tr><th>Solicitante</th><th>Tipo de documento</th><th>Número</th><th>Fecha</th><th>Estado</th><th className="action-heading">Actualizar estado</th></tr></thead>
            <tbody>
              {loading ? (
                <tr><td colSpan="6" className="empty-state">Cargando solicitudes…</td></tr>
              ) : requests.length === 0 ? (
                <tr><td colSpan="6" className="empty-state">Todavía no hay solicitudes registradas.</td></tr>
              ) : requests.map((item) => (
                <tr key={item.id}>
                  <td className="applicant-cell"><span className="row-marker" />{item.applicant_name}</td>
                  <td>{item.document_type}</td>
                  <td>{item.document_number || '—'}</td>
                  <td>{new Intl.DateTimeFormat('es', { dateStyle: 'medium', timeZone: 'UTC' }).format(new Date(`${item.request_date}T00:00:00Z`))}</td>
                  <td><span className={`status status-${item.status}`}>{item.status}</span></td>
                  <td><select className="status-select" aria-label={`Cambiar estado de ${item.applicant_name}`} value={item.status} onChange={(event) => updateStatus(item.id, event.target.value)}>
                    {STATUS_OPTIONS.map((status) => <option key={status} value={status}>{status.charAt(0).toUpperCase() + status.slice(1)}</option>)}
                  </select></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
      <footer className="footer"><span>GESTIÓN DE SOLICITUDES</span><span>REGISTROS EN BASE LOCAL</span></footer>
    </main>
  )
}