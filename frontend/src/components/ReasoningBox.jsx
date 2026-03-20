export default function ReasoningBox({ text }) {
  return (
    <div style={{
      background: 'linear-gradient(135deg, rgba(123,97,255,0.06), rgba(74,240,196,0.03))',
      border: '1px solid rgba(123,97,255,0.2)', borderRadius: 16,
      padding: 24, position: 'relative', overflow: 'hidden'
    }}>
      <div style={{
        position: 'absolute', top: -10, left: 16, fontSize: '6rem',
        color: 'rgba(123,97,255,0.1)', fontFamily: 'Syne, sans-serif',
        lineHeight: 1, pointerEvents: 'none'
      }}>"</div>
      <div style={{ fontSize: '0.9rem', lineHeight: 1.8, color: '#c0cce8', fontWeight: 300, position: 'relative' }}>
        {text}
      </div>
    </div>
  )
}