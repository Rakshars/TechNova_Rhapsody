export default function MetricCard({ value, label, color }) {
  return (
    <div
      className="metric-card"
      style={{
        background: 'var(--card)', border: '1px solid var(--border)',
        borderRadius: 14, padding: 20, textAlign: 'center',
        transition: 'transform 0.25s, border-color 0.25s'
      }}
      onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-3px)'; e.currentTarget.style.borderColor = 'rgba(74,240,196,0.2)' }}
      onMouseLeave={e => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.borderColor = 'var(--border)' }}
    >
      <span style={{ fontFamily: 'Syne, sans-serif', fontWeight: 800, fontSize: '2rem', color, display: 'block' }}>
        {value}
      </span>
      <div style={{ fontSize: '0.78rem', color: 'var(--muted)', marginTop: 4, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
        {label}
      </div>
    </div>
  )
}