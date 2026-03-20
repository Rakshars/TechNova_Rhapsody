import { motion } from 'framer-motion'

export default function PathStep({ step }) {
  const priorityStyle = step.priority === 'High'
    ? { background: 'rgba(255,107,107,0.12)', color: 'var(--accent3)' }
    : { background: 'rgba(250,200,80,0.12)', color: '#fac850' }

  return (
    <motion.div 
      className="path-step" 
      initial={{ x: -25, opacity: 0 }}
      whileInView={{ x: 0, opacity: 1 }}
      viewport={{ once: true, margin: "-40px" }}
      transition={{ type: "spring", stiffness: 200, damping: 20 }}
      style={{ display: 'flex', gap: 20, marginBottom: 20 }}
    >
      <motion.div
        whileHover={{ scale: 1.15, borderColor: 'var(--accent)', backgroundColor: 'var(--bg)' }}
        transition={{ type: "spring" }}
        style={{
          width: 42, height: 42, minWidth: 42, borderRadius: '50%',
          background: 'var(--bg2)', border: '1.5px solid var(--border)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontFamily: 'Syne, sans-serif', fontWeight: 800, fontSize: '0.85rem',
          color: 'var(--accent)', position: 'relative', zIndex: 1,
          transition: 'border-color 0.25s, background-color 0.25s'
        }}
      >
        {step.step}
      </motion.div>
      <motion.div
        whileHover={{ x: 6, borderColor: 'rgba(74,240,196,0.2)' }}
        style={{
          flex: 1, background: 'var(--card)', border: '1px solid var(--border)',
          borderRadius: 14, padding: '18px 20px',
          transition: 'border-color 0.25s'
        }}
      >
        <div style={{ fontFamily: 'Syne, sans-serif', fontWeight: 700, fontSize: '0.95rem', marginBottom: 4 }}>{step.title}</div>
        <div style={{ fontSize: '0.82rem', color: 'var(--muted)', lineHeight: 1.6, marginBottom: 10 }}>{step.description}</div>
        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
          <span style={{ fontSize: '0.72rem', padding: '3px 10px', borderRadius: 100, background: 'rgba(123,97,255,0.12)', color: 'var(--accent2)' }}>⏱ {step.duration}</span>
          <span style={{ fontSize: '0.72rem', padding: '3px 10px', borderRadius: 100, background: 'rgba(74,240,196,0.1)', color: 'var(--accent)' }}>{step.type}</span>
          <span style={{ fontSize: '0.72rem', padding: '3px 10px', borderRadius: 100, ...priorityStyle }}>{step.priority} Priority</span>
        </div>
      </motion.div>
    </motion.div>
  )
}