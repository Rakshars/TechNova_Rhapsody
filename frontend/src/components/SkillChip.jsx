import { motion } from 'framer-motion'

export default function SkillChip({ label, type, delay = 0 }) {
  const isHas = type === 'has'
  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.7 }}
      whileInView={{ opacity: 1, scale: 1 }}
      viewport={{ once: true, margin: "-20px" }}
      transition={{ type: "spring", stiffness: 300, delay: delay * 0.5 }}
      whileHover={{ scale: 1.05 }}
      style={{
        padding: '6px 14px', borderRadius: 100, fontSize: '0.82rem', fontWeight: 500,
        display: 'inline-flex', alignItems: 'center', gap: 6,
        background: isHas ? 'rgba(74,240,196,0.1)' : 'rgba(255,107,107,0.1)',
        border: `1px solid ${isHas ? 'rgba(74,240,196,0.25)' : 'rgba(255,107,107,0.25)'}`,
        color: isHas ? 'var(--accent)' : 'var(--accent3)',
        cursor: 'default',
        transformOrigin: "center"
      }}
    >
      <span style={{ fontSize: '0.9rem' }}>{isHas ? '✓' : '+'}</span>
      {label}
    </motion.div>
  )
}