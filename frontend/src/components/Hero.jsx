import { useEffect, useRef } from 'react'

export default function Hero() {
  const glowRef = useRef(null)

  useEffect(() => {
    const onMove = (e) => {
      if (!glowRef.current) return
      const x = (e.clientX / window.innerWidth - 0.5) * 60
      const y = (e.clientY / window.innerHeight - 0.5) * 60
      glowRef.current.style.transform = `translate(calc(-50% + ${x}px), calc(-50% + ${y}px))`
    }
    window.addEventListener('mousemove', onMove)
    return () => window.removeEventListener('mousemove', onMove)
  }, [])

  return (
    <section style={{
      minHeight: '100vh', display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      textAlign: 'center', padding: '100px 24px 60px',
      position: 'relative', overflow: 'hidden'
    }}>
      <div style={{
        position: 'absolute', inset: 0,
        backgroundImage: `linear-gradient(rgba(74,240,196,0.04) 1px, transparent 1px),
                          linear-gradient(90deg, rgba(74,240,196,0.04) 1px, transparent 1px)`,
        backgroundSize: '60px 60px',
        animation: 'gridFloat 20s linear infinite'
      }} />
      <div ref={glowRef} style={{
        position: 'absolute', width: 600, height: 600,
        background: 'radial-gradient(circle, rgba(74,240,196,0.08) 0%, transparent 70%)',
        borderRadius: '50%', left: '50%', top: '50%',
        transform: 'translate(-50%, -50%)', pointerEvents: 'none'
      }} />
      <div style={{
        display: 'inline-flex', alignItems: 'center', gap: 8,
        padding: '6px 16px', border: '1px solid rgba(74,240,196,0.3)',
        borderRadius: 100, fontSize: '0.78rem', color: 'var(--accent)',
        letterSpacing: '0.08em', textTransform: 'uppercase',
        marginBottom: 28, position: 'relative', zIndex: 2,
        animation: 'fadeUp 0.8s ease both'
      }}>
        <div style={{ width: 20, height: 1, background: 'var(--accent)' }} />
        AI-Powered Adaptive Learning
        <div style={{ width: 20, height: 1, background: 'var(--accent)' }} />
      </div>
      <h1 style={{
        fontFamily: 'Syne, sans-serif', fontWeight: 800,
        fontSize: 'clamp(2.8rem, 7vw, 5.5rem)', lineHeight: 1.05,
        letterSpacing: '-0.03em', position: 'relative', zIndex: 2,
        animation: 'fadeUp 0.8s 0.1s ease both'
      }}>
        Close your<br />
        <span style={{ color: 'var(--accent)' }}>skill gap</span>,<br />
        <span style={{ color: 'var(--accent2)' }}>faster</span>
      </h1>
      <p style={{
        maxWidth: 560, margin: '20px auto 0', fontSize: '1.1rem',
        color: 'var(--muted)', lineHeight: 1.7, fontWeight: 300,
        position: 'relative', zIndex: 2,
        animation: 'fadeUp 0.8s 0.2s ease both'
      }}>
        Upload your resume and a job description. Our engine maps exactly what you know,
        what you don't, and how to get there — in seconds.
      </p>
    </section>
  )
}