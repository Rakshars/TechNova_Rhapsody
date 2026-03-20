import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import TerminalText from './TerminalText'

export default function LoadingState({ message }) {
  const logs = [
    "[SYS] INITIALIZING COGNITIVE ENGINE...",
    "[SYS] PARSING PDF EXTRACT TOKENS...",
    "[AI] MAPPING DOCUMENT EMBEDDINGS...",
    "[AI] ANALYZING JOB DESCRIPTION VECTORS...",
    "[CALC] IDENTIFYING KILOBYTE-LEVEL GAP DELTAS...",
    "[DONE] GENERATING PATHWAY SYNTHESIS PROTOCOL..."
  ]
  const [logIndex, setLogIndex] = useState(0)

  useEffect(() => {
    // Reveal a new terminal log line every 600ms
    const interval = setInterval(() => {
      setLogIndex(prev => (prev < logs.length - 1 ? prev + 1 : prev))
    }, 600)
    return () => clearInterval(interval)
  }, [])

  return (
    <div style={{ textAlign: 'center', padding: '60px 24px', fontFamily: '"DM Mono", monospace' }}>
      
      {/* Hacker rotating radar / loading spinner */}
      <motion.div 
        animate={{ rotate: 360 }} 
        transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
        style={{ 
          width: 50, height: 50, borderTop: '2.5px solid var(--accent)', 
          borderRight: '2.5px solid transparent', borderBottom: '2.5px solid rgba(74,240,196,0.3)',
          borderLeft: '2.5px solid transparent', borderRadius: '50%', 
          margin: '0 auto 24px', position: 'relative' 
        }}
      >
        <div style={{ position: 'absolute', top: 6, left: 6, right: 6, bottom: 6, border: '1px dashed var(--accent)', borderRadius: '50%', opacity: 0.5 }} />
      </motion.div>

      <div style={{ color: 'var(--accent)', fontSize: '0.9rem', marginBottom: 16, fontWeight: 700, letterSpacing: '0.1em' }}>
        <TerminalText text={message} delay={0} />
      </div>

      {/* Scrolling Output Logs */}
      <div style={{ 
        height: 80, overflow: 'hidden', display: 'flex', flexDirection: 'column', 
        justifyContent: 'flex-end', alignItems: 'center', color: 'var(--muted)', 
        fontSize: '0.72rem', letterSpacing: '0.05em'
      }}>
        {logs.slice(0, logIndex + 1).map((log, i) => (
          <motion.div 
            key={i} 
            initial={{ opacity: 0, x: -10 }} 
            animate={{ opacity: 1, x: 0 }} 
            transition={{ type: "spring", stiffness: 200, damping: 20 }}
            style={{ marginBottom: 4 }}
          >
            {log}
          </motion.div>
        ))}
      </div>
    </div>
  )
}