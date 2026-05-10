import { useState, useEffect } from 'react'
import Dashboard from './components/Dashboard'
import SubscriptionList from './components/SubscriptionList'
import SubscriptionModal from './components/SubscriptionModal'
import Header from './components/Header'
import './index.css'

const STORAGE_KEY = 'ai-subscriptions'

const DEFAULT_SUBS = [
  { id: 1, name: 'ChatGPT Plus', provider: 'OpenAI', plan: 'Plus', cost: 20, cycle: 'monthly', category: 'LLM', status: 'active', renewalDate: '2026-06-01', notes: '' },
  { id: 2, name: 'Claude Pro', provider: 'Anthropic', plan: 'Pro', cost: 20, cycle: 'monthly', category: 'LLM', status: 'active', renewalDate: '2026-06-05', notes: '' },
  { id: 3, name: 'Midjourney', provider: 'Midjourney', plan: 'Basic', cost: 10, cycle: 'monthly', category: 'Image', status: 'active', renewalDate: '2026-06-10', notes: '' },
]

export default function App() {
  const [subs, setSubs] = useState(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY)
      return saved ? JSON.parse(saved) : DEFAULT_SUBS
    } catch {
      return DEFAULT_SUBS
    }
  })
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState(null)

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(subs))
  }, [subs])

  function handleSave(sub) {
    if (sub.id) {
      setSubs(prev => prev.map(s => s.id === sub.id ? sub : s))
    } else {
      setSubs(prev => [...prev, { ...sub, id: Date.now() }])
    }
    setModalOpen(false)
    setEditing(null)
  }

  function handleDelete(id) {
    setSubs(prev => prev.filter(s => s.id !== id))
  }

  function handleEdit(sub) {
    setEditing(sub)
    setModalOpen(true)
  }

  function handleAdd() {
    setEditing(null)
    setModalOpen(true)
  }

  return (
    <>
      <Header onAdd={handleAdd} />
      <main style={{ flex: 1, padding: '24px 0 48px' }}>
        <div className="container">
          <Dashboard subs={subs} />
          <SubscriptionList subs={subs} onEdit={handleEdit} onDelete={handleDelete} onAdd={handleAdd} />
        </div>
      </main>
      {modalOpen && (
        <SubscriptionModal
          sub={editing}
          onSave={handleSave}
          onClose={() => { setModalOpen(false); setEditing(null) }}
        />
      )}
    </>
  )
}
