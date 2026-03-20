export default function Navbar() {
  return (
    <nav style={{
      position: 'fixed', top: 0, left: 0, right: 0, zIndex: 100,
      padding: '20px 48px', display: 'flex', alignItems: 'center',
      justifyContent: 'space-between', backdropFilter: 'blur(16px)',
      borderBottom: '1px solid var(--border)', background: 'rgba(5,10,20,0.6)'
    }}>
      <div style={{
        fontFamily: 'Syne, sans-serif', fontWeight: 800,
        fontSize: '1.3rem', letterSpacing: '-0.02em',
        display: 'flex', alignItems: 'center', gap: 8
      }}>
        <div style={{
          width: 8, height: 8, background: 'var(--accent)',
          borderRadius: '50%', animation: 'pulse 2s ease-in-out infinite'
        }} />
        SkillBridge
      </div>
      <div style={{
        fontSize: '0.72rem', padding: '4px 12px',
        border: '1px solid var(--border)', borderRadius: 100,
        color: 'var(--muted)', letterSpacing: '0.05em'
      }}>
        ARTPARK × CodeForge
      </div>
    </nav>
  )
}