import { motion } from 'framer-motion'

export default function AvatarScanner({ matchedSkills = [], missingSkills = [] }) {
  // Spreads skills in an arch over the avatar
  const spreadAroundTop = (index, total) => {
    const angle = (Math.PI / (total + 1)) * (index + 1)
    const radius = 120
    return {
      x: -Math.cos(angle) * radius,
      y: -Math.sin(angle) * (radius * 0.6) - 30
    }
  }

  const stagger = 1.8
  const travelDuration = 2.5
  const totalCycle = Math.max(missingSkills.length * stagger, travelDuration + 1)
  const repeatDelay = totalCycle - travelDuration

  return (
    <div style={{
      position: 'relative', width: '100%', height: 350,
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      marginTop: 20, marginBottom: 80, overflow: 'hidden'
    }}>
      {/* Background radial glow */}
      <motion.div 
        animate={{ scale: [1, 1.2, 1], opacity: [0.1, 0.25, 0.1] }}
        transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
        style={{
          position: 'absolute', width: 260, height: 260, 
          background: 'radial-gradient(circle, var(--accent) 0%, transparent 70%)',
          filter: 'blur(40px)', borderRadius: '50%', zIndex: 0, 
          top: '50%', left: '50%', transform: 'translate(-50%, -50%)'
        }}
      />

      {/* Main Avatar Group */}
      <div style={{ position: 'relative', width: 180, height: 180, zIndex: 10 }}>
        {/* Base Geometric Silhouette */}
        <svg viewBox="0 0 100 100" fill="none" style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', stroke: '#7a8aaa', strokeWidth: 1.5 }}>
          <circle cx="50" cy="35" r="18" fill="rgba(255,255,255,0.02)" />
          <path d="M20 90 Q 50 60 80 90" strokeLinecap="round" fill="rgba(255,255,255,0.02)" />
        </svg>

        {/* Locked-on AR Visor */}
        <motion.div
          initial={{ y: -30, opacity: 0, scale: 1.2 }}
          animate={{ y: 0, opacity: 1, scale: 1 }}
          transition={{ duration: 1, type: "spring", stiffness: 200, delay: 0.2 }}
          style={{ position: 'absolute', top: 52, left: '50%', x: '-50%', zIndex: 2 }}
        >
          {/* Cyberpunk glasses (Upright orientation) */}
          <svg width="60" height="24" viewBox="0 0 60 24" fill="none">
            <path d="M 4 4 L 56 4 L 60 16 L 35 16 L 30 10 L 25 16 L 0 16 Z" fill="rgba(74,240,196,0.2)" stroke="var(--accent)" strokeWidth="1.5" />
            <motion.line 
               x1="0" y1="4" x2="60" y2="4" 
               stroke="#fff" strokeWidth="2"
               animate={{ y: [0, 10, 0] }}
               transition={{ repeat: Infinity, duration: 2, ease: "linear" }}
            />
          </svg>
        </motion.div>

        {/* Matched Skills floating above */}
        {matchedSkills.map((skill, i) => {
          const pos = spreadAroundTop(i, matchedSkills.length)
          return (
            <motion.div
              key={`matched-${skill}`}
              initial={{ opacity: 0, scale: 0, x: 0, y: 0 }}
              animate={{ opacity: 1, scale: 1, x: pos.x, y: pos.y }}
              transition={{ 
                type: "spring", stiffness: 100, damping: 15,
                delay: 0.5 + i * 0.15
              }}
              style={{
                position: 'absolute', top: '50%', left: '50%',
                background: 'rgba(74,240,196,0.1)', border: '1px solid rgba(74,240,196,0.3)',
                color: 'var(--accent)', padding: '6px 14px', borderRadius: 100,
                fontSize: '0.8rem', fontWeight: 600, zIndex: 3, 
                whiteSpace: 'nowrap', boxShadow: '0 0 15px rgba(74,240,196,0.1)'
              }}
            >
              ✓ {skill}
            </motion.div>
          )
        })}

        {/* Missing Skills streaming into the head from left */}
        {missingSkills.map((skill, i) => (
          <motion.div
            key={`missing-${skill}`}
            initial={{ opacity: 0, x: -300, y: 20, scale: 0.8 }}
            animate={{ 
              x: [-300, 0],
              y: [20, -10],
              opacity: [0, 1, 1, 0],
              scale: [0.8, 1.1, 0.4]
            }}
            transition={{
              duration: travelDuration,
              ease: 'easeInOut',
              repeat: Infinity,
              repeatDelay: repeatDelay,
              delay: i * stagger + 1 // Add a small initial delay before starting stream
            }}
            style={{
              position: 'absolute', top: '50%', left: '50%',
              background: 'rgba(255,107,107,0.1)', border: '1px solid rgba(255,107,107,0.4)',
              color: 'var(--accent3)', padding: '6px 14px', borderRadius: 100,
              fontSize: '0.8rem', fontWeight: 600, zIndex: 4, 
              whiteSpace: 'nowrap', boxShadow: '0 0 15px rgba(255,107,107,0.15)'
            }}
          >
            + {skill}
          </motion.div>
        ))}
        
      </div>
    </div>
  )
}
