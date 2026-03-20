import { motion } from 'framer-motion'

export default function AvatarScanner({ matchedSkills = [], missingSkills = [], level }) {
  const stagger = 1.8
  const travelDuration = 2.5
  const totalCycle = Math.max(missingSkills.length * stagger, travelDuration + 1)
  const repeatDelay = totalCycle - travelDuration

  return (
    <div style={{
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', gap: 0,
      marginTop: 20, marginBottom: 60,
      position: 'relative'
    }}>
      {/* Matched Skills — natural flex-wrap cloud above avatar */}
      <div style={{
        display: 'flex', flexWrap: 'wrap', justifyContent: 'center',
        gap: '10px 10px', maxWidth: 700, marginBottom: 28,
        position: 'relative', zIndex: 3
      }}>
        {matchedSkills.map((skill, i) => (
          <motion.div
            key={`matched-${skill}`}
            initial={{ opacity: 0, scale: 0.5, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            whileHover={{ y: -5, scale: 1.1, boxShadow: '0 6px 24px rgba(74,240,196,0.35)', transition: { duration: 0.15 } }}
            transition={{ type: 'spring', stiffness: 120, damping: 14, delay: 0.3 + i * 0.07 }}
            style={{
              background: 'rgba(74,240,196,0.1)', border: '1px solid rgba(74,240,196,0.35)',
              color: 'var(--accent)', padding: '5px 14px', borderRadius: 100,
              fontSize: '0.78rem', fontWeight: 600,
              whiteSpace: 'nowrap', boxShadow: '0 0 12px rgba(74,240,196,0.08)',
              cursor: 'default', userSelect: 'none'
            }}
          >
            ✓ {skill}
          </motion.div>
        ))}
      </div>

      {/* Avatar group */}
      <div style={{ position: 'relative', width: 180, height: 180, zIndex: 10, flexShrink: 0 }}>
        {/* Background radial glow */}
        <motion.div
          animate={{ scale: [1, 1.2, 1], opacity: [0.1, 0.25, 0.1] }}
          transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
          style={{
            position: 'absolute', width: 260, height: 260,
            background: 'radial-gradient(circle, var(--accent) 0%, transparent 70%)',
            filter: 'blur(40px)', borderRadius: '50%', zIndex: 0,
            top: '50%', left: '50%', transform: 'translate(-50%, -50%)'
          }}
        />

        {/* Base Geometric Silhouette */}
        <svg viewBox="0 0 100 100" fill="none" style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', stroke: '#7a8aaa', strokeWidth: 1.5 }}>
          <circle cx="50" cy="35" r="18" fill="rgba(255,255,255,0.02)" />
          <path d="M20 90 Q 50 60 80 90" strokeLinecap="round" fill="rgba(255,255,255,0.02)" />
        </svg>

        {/* AR Visor */}
        <motion.div
          initial={{ y: -30, opacity: 0, scale: 1.2 }}
          animate={{ y: 0, opacity: 1, scale: 1 }}
          transition={{ duration: 1, type: 'spring', stiffness: 200, delay: 0.2 }}
          style={{ position: 'absolute', top: 52, left: '50%', x: '-50%', zIndex: 2 }}
        >
          <svg width="60" height="24" viewBox="0 0 60 24" fill="none">
            <path d="M 4 4 L 56 4 L 60 16 L 35 16 L 30 10 L 25 16 L 0 16 Z" fill="rgba(74,240,196,0.2)" stroke="var(--accent)" strokeWidth="1.5" />
            <motion.line
              x1="0" y1="4" x2="60" y2="4"
              stroke="#fff" strokeWidth="2"
              animate={{ y: [0, 10, 0] }}
              transition={{ repeat: Infinity, duration: 2, ease: 'linear' }}
            />
          </svg>
        </motion.div>

        {/* Missing Skills streaming in from left */}
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
              delay: i * stagger + 1
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

      {/* Level badge below the avatar */}
      {level && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.2, duration: 0.5 }}
          style={{
            marginTop: 16, fontSize: '0.78rem', fontWeight: 700,
            letterSpacing: '0.08em', textTransform: 'uppercase',
            padding: '6px 18px', borderRadius: 100,
            background: level === 'advanced' ? 'rgba(123,97,255,0.18)' : level === 'intermediate' ? 'rgba(74,240,196,0.12)' : 'rgba(250,200,80,0.12)',
            color:  level === 'advanced' ? 'var(--accent2)' : level === 'intermediate' ? 'var(--accent)' : '#fac850',
            border: level === 'advanced' ? '1px solid rgba(123,97,255,0.3)' : level === 'intermediate' ? '1px solid rgba(74,240,196,0.25)' : '1px solid rgba(250,200,80,0.25)',
            boxShadow: level === 'advanced' ? '0 0 20px rgba(123,97,255,0.15)' : level === 'intermediate' ? '0 0 20px rgba(74,240,196,0.1)' : '0 0 20px rgba(250,200,80,0.1)',
          }}
        >
          {level === 'advanced' ? '🏆 Advanced' : level === 'intermediate' ? '⚡ Intermediate' : '🌱 Beginner'}
        </motion.div>
      )}
    </div>
  )
}
