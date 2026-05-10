import { DollarSign, TrendingUp, CreditCard, AlertCircle } from 'lucide-react'

function monthlyCost(sub) {
  if (sub.cycle === 'annual') return sub.cost / 12
  if (sub.cycle === 'weekly') return sub.cost * 4.33
  return sub.cost
}

export default function Dashboard({ subs }) {
  const active = subs.filter(s => s.status === 'active')
  const monthlyTotal = active.reduce((sum, s) => sum + monthlyCost(s), 0)
  const annualTotal = monthlyTotal * 12

  const byCategory = active.reduce((acc, s) => {
    acc[s.category] = (acc[s.category] || 0) + monthlyCost(s)
    return acc
  }, {})
  const topCategory = Object.entries(byCategory).sort((a, b) => b[1] - a[1])[0]

  const today = new Date()
  const soonRenewing = subs.filter(s => {
    if (!s.renewalDate || s.status !== 'active') return false
    const diff = (new Date(s.renewalDate) - today) / (1000 * 60 * 60 * 24)
    return diff >= 0 && diff <= 7
  })

  return (
    <div style={{ marginBottom: 32 }}>
      <h2 style={{ fontSize: 22, fontWeight: 700, marginBottom: 16, color: 'var(--text)' }}>Overview</h2>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 16 }}>
        <StatCard
          icon={<DollarSign size={20} />}
          label="Monthly Spend"
          value={`$${monthlyTotal.toFixed(2)}`}
          sub={`${active.length} active subscriptions`}
          color="var(--accent)"
        />
        <StatCard
          icon={<TrendingUp size={20} />}
          label="Annual Spend"
          value={`$${annualTotal.toFixed(2)}`}
          sub="Projected yearly cost"
          color="var(--success)"
        />
        <StatCard
          icon={<CreditCard size={20} />}
          label="Top Category"
          value={topCategory ? topCategory[0] : '—'}
          sub={topCategory ? `$${topCategory[1].toFixed(2)}/mo` : 'No data'}
          color="var(--warning)"
        />
        <StatCard
          icon={<AlertCircle size={20} />}
          label="Renewing Soon"
          value={soonRenewing.length}
          sub={soonRenewing.length ? soonRenewing.map(s => s.name).join(', ') : 'None in next 7 days'}
          color={soonRenewing.length ? 'var(--danger)' : 'var(--muted)'}
        />
      </div>
    </div>
  )
}

function StatCard({ icon, label, value, sub, color }) {
  return (
    <div style={{
      background: 'var(--surface)',
      border: '1px solid var(--border)',
      borderRadius: 'var(--radius)',
      padding: '20px 22px',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12, color }}>
        {icon}
        <span style={{ fontSize: 12, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--muted)' }}>{label}</span>
      </div>
      <div style={{ fontSize: 28, fontWeight: 700, marginBottom: 4, color: 'var(--text)' }}>{value}</div>
      <div style={{ fontSize: 13, color: 'var(--muted)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{sub}</div>
    </div>
  )
}
