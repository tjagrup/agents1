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

export default function SpendingChart({ subs }) {
  const active = subs.filter(s => s.status === 'active')
  if (active.length === 0) return null

  const byCategory = {}
  for (const s of active) {
    byCategory[s.category] = (byCategory[s.category] || 0) + monthlyCost(s)
  }

  const entries = Object.entries(byCategory).sort((a, b) => b[1] - a[1])
  const max = entries[0][1]
  const total = entries.reduce((s, [, v]) => s + v, 0)

  return (
    <div style={{ marginBottom: 32 }}>
      <h2 style={{ fontSize: 22, fontWeight: 700, marginBottom: 16, color: 'var(--text)' }}>Spend by Category</h2>
      <div className="chart-grid" style={{
        background: 'var(--surface)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius)',
        padding: '24px 28px',
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: 32,
        alignItems: 'center',
      }}>
        {/* Bar chart */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {entries.map(([cat, cost]) => {
            const color = CATEGORY_COLORS[cat] || CATEGORY_COLORS.Other
            const pct = (cost / max) * 100
            return (
              <div key={cat}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6, fontSize: 13 }}>
                  <span style={{ fontWeight: 600, color: 'var(--text)' }}>{cat}</span>
                  <span style={{ color: 'var(--muted)' }}>${cost.toFixed(2)}/mo</span>
                </div>
                <div style={{ height: 8, background: 'var(--surface2)', borderRadius: 4, overflow: 'hidden' }}>
                  <div style={{
                    height: '100%',
                    width: `${pct}%`,
                    background: color,
                    borderRadius: 4,
                    transition: 'width 0.4s ease',
                  }} />
                </div>
              </div>
            )
          })}
        </div>

        {/* Donut chart */}
        <DonutChart entries={entries} total={total} />
      </div>
    </div>
  )
}

function DonutChart({ entries, total }) {
  const size = 160
  const r = 60
  const cx = size / 2
  const cy = size / 2
  const stroke = 22
  const circumference = 2 * Math.PI * r

  let offset = 0
  const segments = entries.map(([cat, cost]) => {
    const color = CATEGORY_COLORS[cat] || CATEGORY_COLORS.Other
    const pct = cost / total
    const dash = pct * circumference
    const gap = circumference - dash
    const seg = { cat, cost, color, dash, gap, offset }
    offset += dash
    return seg
  })

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16 }}>
      <div style={{ position: 'relative', width: size, height: size }}>
        <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
          {/* background track */}
          <circle cx={cx} cy={cy} r={r} fill="none" stroke="var(--surface2)" strokeWidth={stroke} />
          {segments.map(({ cat, color, dash, gap, offset: off }) => (
            <circle
              key={cat}
              cx={cx} cy={cy} r={r}
              fill="none"
              stroke={color}
              strokeWidth={stroke}
              strokeDasharray={`${dash} ${gap}`}
              strokeDashoffset={-off}
              strokeLinecap="butt"
            />
          ))}
        </svg>
        <div style={{
          position: 'absolute', inset: 0,
          display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
        }}>
          <span style={{ fontSize: 20, fontWeight: 700 }}>${total.toFixed(0)}</span>
          <span style={{ fontSize: 11, color: 'var(--muted)' }}>/mo</span>
        </div>
      </div>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px 16px', justifyContent: 'center' }}>
        {entries.map(([cat, cost]) => {
          const color = CATEGORY_COLORS[cat] || CATEGORY_COLORS.Other
          const pct = ((cost / total) * 100).toFixed(0)
          return (
            <div key={cat} style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12 }}>
              <span style={{ width: 10, height: 10, borderRadius: 2, background: color, flexShrink: 0 }} />
              <span style={{ color: 'var(--muted)' }}>{cat} <strong style={{ color: 'var(--text)' }}>{pct}%</strong></span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
