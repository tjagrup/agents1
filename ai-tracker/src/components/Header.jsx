import { Plus, Bot } from 'lucide-react'

export default function Header({ onAdd }) {
  return (
    <header style={{
      background: 'var(--surface)',
      borderBottom: '1px solid var(--border)',
      padding: '16px 0',
      position: 'sticky',
      top: 0,
      zIndex: 10,
    }}>
      <div className="container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <Bot size={24} color="var(--accent)" />
          <span style={{ fontSize: 18, fontWeight: 700, letterSpacing: '-0.3px' }}>AI Spend Tracker</span>
        </div>
        <button onClick={onAdd} style={btnStyle}>
          <Plus size={16} />
          Add Subscription
        </button>
      </div>
    </header>
  )
}

const btnStyle = {
  display: 'flex',
  alignItems: 'center',
  gap: 6,
  background: 'var(--accent)',
  color: '#fff',
  border: 'none',
  borderRadius: 8,
  padding: '8px 16px',
  fontSize: 14,
  fontWeight: 600,
}
