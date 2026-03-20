import { useEffect } from 'react'
import { motion, useScroll, useTransform, useMotionValue, useSpring } from 'framer-motion'
import TerminalText from './TerminalText'

export default function Hero() {
  const mouseX = useMotionValue(0)
  const mouseY = useMotionValue(0)

  // Spring physics for smooth following
  const glowX = useSpring(mouseX, { damping: 30, stiffness: 200 })
  const glowY = useSpring(mouseY, { damping: 30, stiffness: 200 })

  // Parallax for background
  const { scrollY } = useScroll()
  const yParallax = useTransform(scrollY, [0, 1000], [0, 300])

  // Mascot 3D transforms based on mouse
  const headRotateX = useTransform(glowY, [-120, 120], [15, -15])
  const headRotateY = useTransform(glowX, [-120, 120], [-25, 25])
  const pupilX = useTransform(glowX, [-120, 120], [-10, 10])
  const pupilY = useTransform(glowY, [-120, 120], [-12, 12])
  const faceTranslateX = useTransform(glowX, [-120, 120], [-5, 5])
  const faceTranslateY = useTransform(glowY, [-120, 120], [-5, 5])

  useEffect(() => {
    const onMove = (e) => {
      const x = (e.clientX / window.innerWidth - 0.5) * 240
      const y = (e.clientY / window.innerHeight - 0.5) * 240
      mouseX.set(x)
      mouseY.set(y)
    }
    window.addEventListener('mousemove', onMove)
    return () => window.removeEventListener('mousemove', onMove)
  }, [mouseX, mouseY])

  return (
    <section style={{
      minHeight: '100vh', display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      textAlign: 'center', padding: '100px 24px 60px',
      position: 'relative', overflow: 'hidden',
      perspective: 1200 // Allows 3D tilting child elements
    }}>
      <motion.div style={{
        position: 'absolute', inset: 0,
        y: yParallax,
        backgroundImage: `linear-gradient(rgba(74,240,196,0.04) 1px, transparent 1px),
                          linear-gradient(90deg, rgba(74,240,196,0.04) 1px, transparent 1px)`,
        backgroundSize: '60px 60px',
        animation: 'gridFloat 20s linear infinite'
      }} />
      <motion.div style={{
        position: 'absolute', width: 600, height: 600,
        background: 'radial-gradient(circle, rgba(74,240,196,0.08) 0%, transparent 70%)',
        borderRadius: '50%', left: '50%', top: '50%',
        x: '-50%', y: '-50%',
        translateX: glowX, translateY: glowY,
        pointerEvents: 'none'
      }} />

      {/* 3D Interactive Cute AI Mascot */}
      <motion.div 
        initial={{ opacity: 0, y: 50, scale: 0.8 }}
        animate={{ opacity: 1, y: [0, -12, 0], scale: 1 }}
        transition={{ 
          opacity: { duration: 1 }, 
          scale: { duration: 1, type: "spring", stiffness: 100 },
          y: { duration: 4, repeat: Infinity, ease: 'easeInOut' } // Cute continuous floating bob
        }}
        style={{
          width: 220, height: 140, marginBottom: 50, position: 'relative', zIndex: 3,
          borderRadius: 80, background: 'linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.02))',
          backdropFilter: 'blur(20px)', border: '1.5px solid rgba(255,255,255,0.1)', 
          boxShadow: '0 20px 40px rgba(0,0,0,0.5), inset 0 4px 15px rgba(255,255,255,0.1)',
          rotateX: headRotateX, rotateY: headRotateY, transformStyle: 'preserve-3d',
          display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center'
        }}
      >
        {/* Soft Inner Glow */}
        <div style={{ position: 'absolute', inset: 30, background: 'var(--accent)', filter: 'blur(40px)', opacity: 0.25, borderRadius: '50%' }} />

        {/* The Black Glass Face/Screen (pops forward in 3D) */}
        <motion.div style={{
          width: 170, height: 96, background: '#050a14', borderRadius: 48,
          border: '2px solid rgba(74,240,196,0.15)',
          display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
          transform: 'translateZ(30px)', x: faceTranslateX, y: faceTranslateY,
          boxShadow: 'inset 0 0 20px rgba(74,240,196,0.1)'
        }}>
          
          {/* Eyes Container */}
          <div style={{ display: 'flex', gap: 24, marginTop: 12 }}>
            {/* Left Eye Socket */}
            <div style={{ width: 32, height: 38, background: 'rgba(74,240,196,0.08)', borderRadius: '50%', position: 'relative', overflow: 'hidden' }}>
              <motion.div style={{ 
                width: 24, height: 30, background: 'var(--accent)', borderRadius: '50%', 
                position: 'absolute', top: 4, left: 4, 
                boxShadow: '0 0 15px var(--accent)', x: pupilX, y: pupilY 
              }} />
            </div>
            {/* Right Eye Socket */}
            <div style={{ width: 32, height: 38, background: 'rgba(74,240,196,0.08)', borderRadius: '50%', position: 'relative', overflow: 'hidden' }}>
              <motion.div style={{ 
                width: 24, height: 30, background: 'var(--accent)', borderRadius: '50%', 
                position: 'absolute', top: 4, left: 4, 
                boxShadow: '0 0 15px var(--accent)', x: pupilX, y: pupilY 
              }} />
            </div>
          </div>

          {/* Cute Glowing Smile */}
          <motion.svg width="30" height="15" viewBox="0 0 30 15" style={{ marginTop: 8, transform: 'translateZ(10px)' }}>
            <path d="M 5 5 Q 15 15 25 5" fill="none" stroke="var(--accent)" strokeWidth="3" strokeLinecap="round" />
          </motion.svg>
        </motion.div>

        {/* Floating Little Hands/Ears detached from body */}
        <motion.div style={{
          position: 'absolute', left: -26, top: '45%', width: 20, height: 36,
          background: 'linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.02))',
          backdropFilter: 'blur(10px)', border: '1px solid rgba(255,255,255,0.1)',
          borderRadius: 20, transform: 'translateZ(15px)', y: faceTranslateY, x: faceTranslateX
        }} />
        <motion.div style={{
          position: 'absolute', right: -26, top: '45%', width: 20, height: 36,
          background: 'linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.02))',
          backdropFilter: 'blur(10px)', border: '1px solid rgba(255,255,255,0.1)',
          borderRadius: 20, transform: 'translateZ(15px)', y: faceTranslateY, x: faceTranslateX
        }} />
      </motion.div>

      <motion.div 
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.2, ease: "easeOut" }}
        style={{
          display: 'inline-flex', alignItems: 'center', gap: 8,
          padding: '6px 16px', border: '1px solid rgba(74,240,196,0.3)',
          borderRadius: 100, fontSize: '0.78rem', color: 'var(--accent)',
          letterSpacing: '0.08em', textTransform: 'uppercase',
          marginBottom: 28, position: 'relative', zIndex: 2
        }}
      >
        <div style={{ width: 20, height: 1, background: 'var(--accent)' }} />
        AI-Powered Adaptive Learning
        <div style={{ width: 20, height: 1, background: 'var(--accent)' }} />
      </motion.div>

      <motion.h1 
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.9, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
        style={{
          fontFamily: 'Syne, sans-serif', fontWeight: 800,
          fontSize: 'clamp(2.8rem, 7vw, 5.5rem)', lineHeight: 1.05,
          letterSpacing: '-0.03em', position: 'relative', zIndex: 2
        }}
      >
        <TerminalText text="Close your" delay={0.4} /><br />
        <span style={{ color: 'var(--accent)' }}><TerminalText text="skill gap" delay={0.7} /></span>,<br />
        <span style={{ color: 'var(--accent2)' }}><TerminalText text="faster" delay={1.0} /></span>
      </motion.h1>

      <motion.p 
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.9, delay: 0.5, ease: "easeOut" }}
        style={{
          maxWidth: 560, margin: '20px auto 0', fontSize: '1.1rem',
          color: 'var(--muted)', lineHeight: 1.7, fontWeight: 300,
          position: 'relative', zIndex: 2
        }}
      >
        Upload your resume and a job description. Our engine maps exactly what you know,
        what you don't, and how to get there — in seconds.
      </motion.p>
    </section>
  )
}