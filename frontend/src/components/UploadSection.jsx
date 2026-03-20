import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion'
import UploadZone from './UploadZone'

export default function UploadSection({ files, onFile, onAnalyze, disabled }) {
  const x = useMotionValue(0)
  const y = useMotionValue(0)
  const xSpring = useSpring(x, { stiffness: 150, damping: 15, mass: 0.1 })
  const ySpring = useSpring(y, { stiffness: 150, damping: 15, mass: 0.1 })

  const isMissingFiles = !files.resume || !files.jd
  const isButtonDisabled = disabled || isMissingFiles

  const handleMouseMove = (e) => {
    if (isButtonDisabled) return
    const rect = e.currentTarget.getBoundingClientRect()
    const centerX = rect.left + rect.width / 2
    const centerY = rect.top + rect.height / 2
    x.set(e.clientX - centerX)
    y.set(e.clientY - centerY)
  }

  const handleMouseLeave = () => {
    x.set(0)
    y.set(0)
  }

  const xMove = useTransform(xSpring, v => v * 0.15)
  const yMove = useTransform(ySpring, v => v * 0.15)

  return (
    <motion.div 
      initial={{ opacity: 0, y: 50 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-100px" }}
      transition={{ duration: 0.7, ease: "easeOut" }}
      id="uploadSection"
    >
      <div className="section-label">Step 01 — Upload Documents</div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginBottom: 28 }}>
        <UploadZone label="Resume" subLabel="Upload PDF file" accept=".pdf" file={files.resume} onFile={(f) => onFile('resume', f)} />
        <UploadZone label="Job Description" subLabel="Upload TXT or PDF" accept=".txt,.pdf" file={files.jd} onFile={(f) => onFile('jd', f)} />
      </div>
      
      <motion.button
        onClick={onAnalyze}
        disabled={isButtonDisabled}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
        whileHover={{ scale: isButtonDisabled ? 1 : 1.02 }}
        whileTap={{ scale: isButtonDisabled ? 1 : 0.98 }}
        style={{
          x: isButtonDisabled ? 0 : xMove,
          y: isButtonDisabled ? 0 : yMove,
          width: '100%', padding: '18px 32px',
          background: 'linear-gradient(135deg, #4af0c4 0%, #2dd4a0 100%)',
          color: '#050a14', fontFamily: 'Syne, sans-serif', fontWeight: 700,
          fontSize: '1rem', letterSpacing: '0.03em', border: 'none',
          borderRadius: 14, cursor: isButtonDisabled ? 'not-allowed' : 'pointer',
          opacity: isButtonDisabled ? 0.5 : 1, marginBottom: 48,
          boxShadow: isButtonDisabled ? 'none' : '0 8px 30px rgba(74,240,196,0.15)',
        }}
      >
        <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10 }}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
          </svg>
          {disabled ? 'Analyzing...' : 'Analyze Skill Gap'}
        </span>
      </motion.button>
    </motion.div>
  )
}