import { motion, useInView } from 'framer-motion'
import { useRef } from 'react'

export default function ReasoningBox({ text }) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: "-40px" })

  // Ensure content is an array
  const contentArray = Array.isArray(text) ? text : [text ?? '']

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
      
      <motion.ul 
        variants={container}
        initial="hidden"
        animate={isInView ? "visible" : "hidden"}
        style={{ 
          fontSize: '0.95rem', lineHeight: 1.8, fontWeight: 300, 
          position: 'relative', zIndex: 1, listStyleType: 'none',
          display: 'flex', flexDirection: 'column', gap: 16
        }}
      >
        {contentArray.map((sentence, sIdx) => {
          if (!sentence) return null
          return (
            <motion.li key={sIdx} style={{ display: 'flex', gap: 14, alignItems: 'flex-start' }}>
              <motion.span variants={child} style={{ color: 'var(--accent)', marginTop: 2, fontSize: '0.8rem' }}>✦</motion.span>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '2px 5px', flex: 1 }}>
                {sentence.split(" ").map((word, wIdx) => (
                  <motion.span key={wIdx} variants={child} style={{ display: 'inline-block', borderRadius: 3, padding: '0 1px' }}>
                    {word}
                  </motion.span>
                ))}
              </div>
            </motion.li>
          )
        })}
      </motion.ul>
    </div>
  )
}