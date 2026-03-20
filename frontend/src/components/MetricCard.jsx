import { motion } from 'framer-motion'

export default function MetricCard({ value, label, color }) {
  return (
    <motion.div
      className="metric-card"
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-50px" }}
      whileHover={{ y: -6, borderColor: 'rgba(74,240,196,0.3)', boxShadow: '0 8px 30px rgba(74,240,196,0.05)' }}
      style={{
        background: 'var(--card)', border: '1px solid var(--border)',
        borderRadius: 14, padding: 20, textAlign: 'center',
        transition: 'border-color 0.25s, box-shadow 0.25s'
      }}
    >
      <motion.span 
        initial={{ scale: 0.5, opacity: 0 }}
        whileInView={{ scale: 1, opacity: 1 }}
        viewport={{ once: true }}
        transition={{ type: 'spring', stiffness: 200, delay: 0.1 }}
        style={{ fontFamily: 'Syne, sans-serif', fontWeight: 800, fontSize: '2rem', color, display: 'block' }}
      >
        {value}
      </motion.span>
      <div style={{ fontSize: '0.78rem', color: 'var(--muted)', marginTop: 4, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
        {label}
      </div>
    </motion.div>
  )
}