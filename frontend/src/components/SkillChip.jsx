export default function SkillChip({ label, type, delay = 0 }) {
  const isHas = type === 'has'
  return (
    <div style={{
      padding: '6px 14px', borderRadius: 100, fontSize: '0.82rem', fontWeight: 500,
      display: 'inline-flex', alignItems: 'center', gap: 6,
      animationDelay: `${delay}s`, animation: 'chipPop 0.4s ease both',
      background: isHas ? 'rgba(74,240,196,0.1)' : 'rgba(255,107,107,0.1)',
      border: `1px solid ${isHas ? 'rgba(74,240,196,0.25)' : 'rgba(255,107,107,0.25)'}`,
      color: isHas ? 'var(--accent)' : 'var(--accent3)'
    }}>
      <span style={{ fontSize: '0.9rem' }}>{isHas ? '✓' : '+'}</span>
      {label}
    </div>
  )
}