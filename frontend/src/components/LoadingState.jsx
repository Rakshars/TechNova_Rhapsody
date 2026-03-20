export default function LoadingState({ message }) {
  return (
    <div style={{ textAlign: 'center', padding: '60px 24px' }}>
      <div style={{ display: 'flex', justifyContent: 'center', gap: 12, marginBottom: 20 }}>
        {['var(--accent)', 'var(--accent2)', 'var(--accent3)'].map((color, i) => (
          <div key={i} style={{
            width: 12, height: 12, borderRadius: '50%', background: color,
            animation: `orbBounce 1.4s ease-in-out ${i * 0.2}s infinite`
          }} />
        ))}
      </div>
      <div style={{ color: 'var(--muted)', fontSize: '0.9rem' }}>{message}</div>
    </div>
  )
}