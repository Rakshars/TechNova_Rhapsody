export default function PathStep({ step }) {
  const priorityStyle = step.priority === 'High'
    ? { background: 'rgba(255,107,107,0.12)', color: 'var(--accent3)' }
    : { background: 'rgba(250,200,80,0.12)', color: '#fac850' }

  return (
    <div className="path-step" style={{ display: 'flex', gap: 20, marginBottom: 20, animation: `stepReveal 0.5s ${step.step * 0.1}s ease both` }}>
      <div
        style={{
          width: 42, height: 42, minWidth: 42, borderRadius: '50%',
          background: 'var(--bg2)', border: '1.5px solid var(--border)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontFamily: 'Syne, sans-serif', fontWeight: 800, fontSize: '0.85rem',
          color: 'var(--accent)', position: 'relative', zIndex: 1,
          transition: 'border-color 0.25s, transform 0.25s'
        }}
        onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--accent)'; e.currentTarget.style.transform = 'scale(1.1)' }}
        onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border)'; e.currentTarget.style.transform = 'scale(1)' }}
      >
        {step.step}
      </div>
      <div
        style={{
          flex: 1, background: 'var(--card)', border: '1px solid var(--border)',
          borderRadius: 14, padding: '18px 20px',
          transition: 'border-color 0.25s, transform 0.25s'
        }}
        onMouseEnter={e => { e.currentTarget.style.borderColor = 'rgba(74,240,196,0.2)'; e.currentTarget.style.transform = 'translateX(4px)' }}
        onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border)'; e.currentTarget.style.transform = 'translateX(0)' }}
      >
        <div style={{ fontFamily: 'Syne, sans-serif', fontWeight: 700, fontSize: '0.95rem', marginBottom: 4 }}>{step.title}</div>
        <div style={{ fontSize: '0.82rem', color: 'var(--muted)', lineHeight: 1.6, marginBottom: 10 }}>{step.description}</div>
        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
          <span style={{ fontSize: '0.72rem', padding: '3px 10px', borderRadius: 100, background: 'rgba(123,97,255,0.12)', color: 'var(--accent2)' }}>⏱ {step.duration}</span>
          <span style={{ fontSize: '0.72rem', padding: '3px 10px', borderRadius: 100, background: 'rgba(74,240,196,0.1)', color: 'var(--accent)' }}>{step.type}</span>
          <span style={{ fontSize: '0.72rem', padding: '3px 10px', borderRadius: 100, ...priorityStyle }}>{step.priority} Priority</span>
        </div>
      </div>
    </div>
  )
}