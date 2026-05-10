import { useState } from 'react'
import { Pencil, Trash2, Plus, ChevronUp, ChevronDown, Download } from 'lucide-react'

function exportCSV(subs) {
  const headers = ['Name', 'Provider', 'Plan', 'Category', 'Cost', 'Cycle', 'Monthly Cost', 'Status', 'Renewal Date', 'Notes']
  const rows = subs.map(s => [
    s.name, s.provider, s.plan, s.category, s.cost, s.cycle,
    monthlyCost(s).toFixed(2), s.status, s.renewalDate || '', s.notes || '',
  ])
  const csv = [headers, ...rows].map(r => r.map(v => `"${String(v).replace(/"/g, '""')}"`).join(',')).join('\n')
  const a = document.createElement('a')
  a.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv' }))
  a.download = 'ai-subscriptions.csv'
  a.click()
}

const CATEGORY_COLORS = {
  LLM: '#7c6af7',
  Image: '#ed8936',
  Audio: '#48bb78',
  Code: '#4299e1',
  Video: '#ed64a6',
  Other: '#718096',
}

function monthlyCost(sub) {
  if (sub.cycle === 'annual') return sub.cost / 12
  if (sub.cycle === 'weekly') return sub.cost * 4.33
  return sub.cost
}

function daysUntil(dateStr) {
  if (!dateStr) return null
  const diff = (new Date(dateStr) - new Date()) / (1000 * 60 * 60 * 24)
  return Math.ceil(diff)
}

export default function SubscriptionList({ subs, onEdit, onDelete, onAdd }) {

  const [filter, setFilter] = useState('all')
  const [sort, setSort] = useState({ key: 'name', dir: 'asc' })
  const [search, setSearch] = useState('')

  const categories = ['all', ...new Set(subs.map(s => s.category))]

  const filtered = subs
    .filter(s => filter === 'all' || s.category === filter)
    .filter(s => !search || s.name.toLowerCase().includes(search.toLowerCase()) || s.provider.toLowerCase().includes(search.toLowerCase()))
    .sort((a, b) => {
      let va = sort.key === 'cost' ? monthlyCost(a) : (a[sort.key] || '').toString().toLowerCase()
      let vb = sort.key === 'cost' ? monthlyCost(b) : (b[sort.key] || '').toString().toLowerCase()
      if (va < vb) return sort.dir === 'asc' ? -1 : 1
      if (va > vb) return sort.dir === 'asc' ? 1 : -1
      return 0
    })

  function toggleSort(key) {
    setSort(s => s.key === key ? { key, dir: s.dir === 'asc' ? 'desc' : 'asc' } : { key, dir: 'asc' })
  }

  function SortIcon({ col }) {
    if (sort.key !== col) return <ChevronUp size={13} color="var(--border)" />
    return sort.dir === 'asc' ? <ChevronUp size={13} /> : <ChevronDown size={13} />
  }

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16, flexWrap: 'wrap' }}>
        <h2 style={{ fontSize: 22, fontWeight: 700, color: 'var(--text)', marginRight: 'auto' }}>Subscriptions</h2>
        {subs.length > 0 && (
          <button onClick={() => exportCSV(subs)} title="Export CSV" style={{ display: 'flex', alignItems: 'center', gap: 6, background: 'transparent', border: '1px solid var(--border)', borderRadius: 8, padding: '7px 12px', color: 'var(--muted)', fontSize: 13 }}>
            <Download size={14} /> Export CSV
          </button>
        )}
        <input
          type="text"
          placeholder="Search..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          style={inputStyle}
        />
        <div style={{ display: 'flex', gap: 8 }}>
          {categories.map(cat => (
            <button
              key={cat}
              onClick={() => setFilter(cat)}
              style={{
                padding: '6px 12px',
                borderRadius: 20,
                border: '1px solid',
                fontSize: 13,
                fontWeight: 500,
                borderColor: filter === cat ? 'var(--accent)' : 'var(--border)',
                background: filter === cat ? 'var(--accent)' : 'transparent',
                color: filter === cat ? '#fff' : 'var(--muted)',
              }}
            >{cat}</button>
          ))}
        </div>
      </div>

      {filtered.length === 0 ? (
        <EmptyState onAdd={onAdd} />
      ) : (
        <div className="table-wrap" style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 'var(--radius)' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: 700 }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border)' }}>
                {[['name', 'Name'], ['provider', 'Provider'], ['category', 'Category'], ['cost', 'Monthly Cost'], ['cycle', 'Billing'], ['renewalDate', 'Renews'], ['status', 'Status']].map(([key, label]) => (
                  <th
                    key={key}
                    onClick={() => toggleSort(key)}
                    style={{ padding: '12px 16px', textAlign: 'left', fontSize: 12, fontWeight: 600, color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '0.05em', cursor: 'pointer', userSelect: 'none', whiteSpace: 'nowrap' }}
                  >
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}>
                      {label} <SortIcon col={key} />
                    </span>
                  </th>
                ))}
                <th style={{ padding: '12px 16px', width: 80 }} />
              </tr>
            </thead>
            <tbody>
              {filtered.map((sub, i) => (
                <SubRow
                  key={sub.id}
                  sub={sub}
                  onEdit={onEdit}
                  onDelete={onDelete}
                  last={i === filtered.length - 1}
                />
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

function SubRow({ sub, onEdit, onDelete, last }) {
  const days = daysUntil(sub.renewalDate)
  const catColor = CATEGORY_COLORS[sub.category] || CATEGORY_COLORS.Other

  return (
    <tr style={{ borderBottom: last ? 'none' : '1px solid var(--border)', transition: 'background 0.15s' }}
      onMouseEnter={e => e.currentTarget.style.background = 'var(--surface2)'}
      onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
    >
      <td style={tdStyle}>
        <span style={{ fontWeight: 600 }}>{sub.name}</span>
      </td>
      <td style={tdStyle}><span style={{ color: 'var(--muted)', fontSize: 14 }}>{sub.provider}</span></td>
      <td style={tdStyle}>
        <span style={{ background: catColor + '22', color: catColor, borderRadius: 6, padding: '2px 8px', fontSize: 12, fontWeight: 600 }}>
          {sub.category}
        </span>
      </td>
      <td style={tdStyle}>
        <span style={{ fontWeight: 700, color: 'var(--accent-light)' }}>${monthlyCost(sub).toFixed(2)}</span>
        <span style={{ color: 'var(--muted)', fontSize: 12 }}>/mo</span>
      </td>
      <td style={tdStyle}><span style={{ color: 'var(--muted)', fontSize: 13, textTransform: 'capitalize' }}>{sub.cycle}</span></td>
      <td style={tdStyle}>
        {days !== null ? (
          <span style={{ color: days <= 3 ? 'var(--danger)' : days <= 7 ? 'var(--warning)' : 'var(--muted)', fontSize: 13 }}>
            {days < 0 ? 'Overdue' : days === 0 ? 'Today' : `${days}d`}
          </span>
        ) : <span style={{ color: 'var(--muted)' }}>—</span>}
      </td>
      <td style={tdStyle}>
        <span style={{
          background: sub.status === 'active' ? 'var(--success)22' : 'var(--muted)22',
          color: sub.status === 'active' ? 'var(--success)' : 'var(--muted)',
          borderRadius: 6,
          padding: '2px 8px',
          fontSize: 12,
          fontWeight: 600,
          textTransform: 'capitalize',
        }}>{sub.status}</span>
      </td>
      <td style={{ ...tdStyle, display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
        <IconBtn onClick={() => onEdit(sub)} title="Edit"><Pencil size={15} /></IconBtn>
        <IconBtn onClick={() => onDelete(sub.id)} title="Delete" danger><Trash2 size={15} /></IconBtn>
      </td>
    </tr>
  )
}

function IconBtn({ onClick, children, title, danger }) {
  return (
    <button
      onClick={onClick}
      title={title}
      style={{
        background: 'transparent',
        border: '1px solid var(--border)',
        borderRadius: 6,
        padding: '5px 7px',
        color: danger ? 'var(--danger)' : 'var(--muted)',
        display: 'flex',
        alignItems: 'center',
      }}
    >{children}</button>
  )
}

function EmptyState({ onAdd }) {
  return (
    <div style={{ textAlign: 'center', padding: '64px 20px', background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 'var(--radius)' }}>
      <p style={{ color: 'var(--muted)', marginBottom: 16 }}>No subscriptions yet. Add your first one!</p>
      <button onClick={onAdd} style={{ display: 'inline-flex', alignItems: 'center', gap: 6, background: 'var(--accent)', color: '#fff', border: 'none', borderRadius: 8, padding: '10px 20px', fontSize: 14, fontWeight: 600 }}>
        <Plus size={16} /> Add Subscription
      </button>
    </div>
  )
}

const tdStyle = { padding: '14px 16px', fontSize: 14 }
const inputStyle = {
  background: 'var(--surface)',
  border: '1px solid var(--border)',
  borderRadius: 8,
  padding: '7px 12px',
  color: 'var(--text)',
  fontSize: 14,
  outline: 'none',
  width: 180,
}
