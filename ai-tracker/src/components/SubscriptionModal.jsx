import { useState } from 'react'
import { X } from 'lucide-react'

const EMPTY = {
  name: '', provider: '', plan: '', cost: '', cycle: 'monthly',
  category: 'LLM', status: 'active', renewalDate: '', notes: '',
}

const CATEGORIES = ['LLM', 'Image', 'Audio', 'Code', 'Video', 'Other']
const CYCLES = ['monthly', 'annual', 'weekly']

export default function SubscriptionModal({ sub, onSave, onClose }) {
  const [form, setForm] = useState(sub ? { ...sub, cost: String(sub.cost) } : EMPTY)
  const [errors, setErrors] = useState({})

  function set(field, value) {
    setForm(f => ({ ...f, [field]: value }))
    setErrors(e => ({ ...e, [field]: undefined }))
  }

  function validate() {
    const e = {}
    if (!form.name.trim()) e.name = 'Name is required'
    if (!form.provider.trim()) e.provider = 'Provider is required'
    if (!form.cost || isNaN(Number(form.cost)) || Number(form.cost) < 0) e.cost = 'Enter a valid cost'
    return e
  }

  function handleSubmit(ev) {
    ev.preventDefault()
    const e = validate()
    if (Object.keys(e).length) { setErrors(e); return }
    onSave({ ...form, cost: Number(form.cost), id: sub?.id || null })
  }

  return (
    <div style={overlayStyle} onClick={e => { if (e.target === e.currentTarget) onClose() }}>
      <div style={modalStyle}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24 }}>
          <h3 style={{ fontSize: 18, fontWeight: 700 }}>{sub ? 'Edit Subscription' : 'Add Subscription'}</h3>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: 'var(--muted)', padding: 4 }}><X size={20} /></button>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <Field label="Name" error={errors.name}>
              <input style={inp(errors.name)} value={form.name} onChange={e => set('name', e.target.value)} placeholder="e.g. ChatGPT Plus" />
            </Field>
            <Field label="Provider" error={errors.provider}>
              <input style={inp(errors.provider)} value={form.provider} onChange={e => set('provider', e.target.value)} placeholder="e.g. OpenAI" />
            </Field>
            <Field label="Plan">
              <input style={inp()} value={form.plan} onChange={e => set('plan', e.target.value)} placeholder="e.g. Pro" />
            </Field>
            <Field label="Category">
              <select style={inp()} value={form.category} onChange={e => set('category', e.target.value)}>
                {CATEGORIES.map(c => <option key={c}>{c}</option>)}
              </select>
            </Field>
            <Field label="Cost ($)" error={errors.cost}>
              <input style={inp(errors.cost)} type="number" min="0" step="0.01" value={form.cost} onChange={e => set('cost', e.target.value)} placeholder="0.00" />
            </Field>
            <Field label="Billing Cycle">
              <select style={inp()} value={form.cycle} onChange={e => set('cycle', e.target.value)}>
                {CYCLES.map(c => <option key={c} value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</option>)}
              </select>
            </Field>
            <Field label="Status">
              <select style={inp()} value={form.status} onChange={e => set('status', e.target.value)}>
                <option value="active">Active</option>
                <option value="paused">Paused</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </Field>
            <Field label="Renewal Date">
              <input style={inp()} type="date" value={form.renewalDate} onChange={e => set('renewalDate', e.target.value)} />
            </Field>
          </div>
          <Field label="Notes">
            <textarea style={{ ...inp(), resize: 'vertical', minHeight: 72 }} value={form.notes} onChange={e => set('notes', e.target.value)} placeholder="Optional notes..." />
          </Field>

          <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end', marginTop: 8 }}>
            <button type="button" onClick={onClose} style={cancelBtn}>Cancel</button>
            <button type="submit" style={saveBtn}>{sub ? 'Save Changes' : 'Add Subscription'}</button>
          </div>
        </form>
      </div>
    </div>
  )
}

function Field({ label, children, error }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
      <label style={{ fontSize: 13, fontWeight: 600, color: 'var(--muted)' }}>{label}</label>
      {children}
      {error && <span style={{ fontSize: 12, color: 'var(--danger)' }}>{error}</span>}
    </div>
  )
}

const inp = (err) => ({
  background: 'var(--surface2)',
  border: `1px solid ${err ? 'var(--danger)' : 'var(--border)'}`,
  borderRadius: 8,
  padding: '9px 12px',
  color: 'var(--text)',
  fontSize: 14,
  outline: 'none',
  width: '100%',
})

const overlayStyle = {
  position: 'fixed', inset: 0,
  background: 'rgba(0,0,0,0.65)',
  display: 'flex', alignItems: 'center', justifyContent: 'center',
  zIndex: 100, padding: 20,
}

const modalStyle = {
  background: 'var(--surface)',
  border: '1px solid var(--border)',
  borderRadius: 'var(--radius)',
  padding: 28,
  width: '100%',
  maxWidth: 580,
  maxHeight: '90vh',
  overflowY: 'auto',
}

const saveBtn = {
  background: 'var(--accent)', color: '#fff', border: 'none',
  borderRadius: 8, padding: '10px 22px', fontSize: 14, fontWeight: 600,
}

const cancelBtn = {
  background: 'transparent', color: 'var(--muted)',
  border: '1px solid var(--border)', borderRadius: 8,
  padding: '10px 22px', fontSize: 14, fontWeight: 500,
}
