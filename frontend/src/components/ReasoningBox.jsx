import { motion, useInView } from 'framer-motion'
import { useRef } from 'react'

export default function ReasoningBox({ text }) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: "-40px" })

  // Accept either a plain string or an array of {skill, status, reason} objects
  const content = Array.isArray(text)
    ? text.map(r => r.reason ?? '').filter(Boolean).join(' ')
    : (text ?? '')

  const container = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.04, delayChildren: 0.1 },
    },
  }

  // The redacted effect: Block renders solid, then wiped away into transparent revealing text
  const child = {
    hidden: { 
      color: "transparent", 
      backgroundColor: "var(--muted)",
    },
    visible: {
      color: "#c0cce8", 
      backgroundColor: "transparent",
      transition: { duration: 0.4, ease: "easeOut" }
    },
  }

  return (
    <div ref={ref} style={{
      background: 'linear-gradient(135deg, rgba(123,97,255,0.06), rgba(74,240,196,0.03))',
      border: '1px solid rgba(123,97,255,0.2)', borderRadius: 16,
      padding: '24px 30px', position: 'relative', overflow: 'hidden'
    }}>
      <div style={{
        position: 'absolute', top: -14, left: 16, fontSize: '7rem',
        color: 'rgba(123,97,255,0.1)', fontFamily: 'Syne, sans-serif',
        lineHeight: 1, pointerEvents: 'none', zIndex: 0
      }}>"</div>
      
      <motion.div 
        variants={container}
        initial="hidden"
        animate={isInView ? "visible" : "hidden"}
        style={{ 
          fontSize: '0.95rem', lineHeight: 1.8, fontWeight: 300, 
          position: 'relative', display: 'flex', flexWrap: 'wrap', 
          gap: '2px 5px', zIndex: 1 
        }}
      >
        {content.split(" ").map((word, index) => (
          <motion.span key={index} variants={child} style={{ display: 'inline-block', borderRadius: 3, padding: '0 1px' }}>
            {word}
          </motion.span>
        ))}
      </motion.div>
    </div>
  )
}