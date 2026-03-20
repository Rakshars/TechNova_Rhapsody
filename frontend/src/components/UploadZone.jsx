import { useRef, useState } from 'react'
import { motion } from 'framer-motion'

export default function UploadZone({ label, subLabel, accept, file, onFile }) {
  const inputRef = useRef(null)
  const [isDragging, setIsDragging] = useState(false)

  const handleChange = (e) => { if (e.target.files[0]) onFile(e.target.files[0]) }
  const handleDrop = (e) => { 
    e.preventDefault()
    setIsDragging(false)
    const f = e.dataTransfer.files[0]
    if (f) onFile(f) 
  }

  return (
    <motion.div
      className="upload-zone"
      onDragEnter={() => setIsDragging(true)}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
      onDragOver={e => e.preventDefault()}
      onClick={() => inputRef.current.click()}
      animate={{
        scale: isDragging ? 1.02 : 1,
        borderColor: isDragging || file ? 'rgba(74,240,196,0.8)' : 'rgba(255,255,255,0.07)',
        backgroundColor: file ? 'rgba(74,240,196,0.05)' : isDragging ? 'rgba(74,240,196,0.03)' : 'rgba(255,255,255,0.04)'
      }}
      transition={{ type: "spring", stiffness: 300, damping: 20 }}
      whileHover={{ y: -4 }}
      whileTap={{ scale: 0.98 }}
      style={{
        borderWidth: 1.5, borderStyle: 'dashed', borderRadius: 16, 
        padding: '36px 24px', textAlign: 'center', cursor: 'pointer',
      }}
    >
      <input ref={inputRef} type="file" accept={accept} onChange={handleChange} style={{ display: 'none' }} />
      <motion.div 
        animate={{ y: isDragging ? -5 : 0, scale: isDragging ? 1.1 : 1 }}
        style={{ fontSize: '2.2rem', marginBottom: 10, color: file ? 'var(--accent)' : 'var(--muted)' }}
      >
        {label === 'Resume' ? '📄' : '📋'}
      </motion.div>
      <div style={{ fontFamily: 'Syne, sans-serif', fontWeight: 700, fontSize: '0.95rem', marginBottom: 4 }}>
        {label}
      </div>
      <div style={{ fontSize: '0.78rem', color: 'var(--muted)' }}>{subLabel}</div>
      {file && (
        <motion.div 
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          style={{
            marginTop: 10, fontSize: '0.78rem', color: 'var(--accent)',
            background: 'rgba(74,240,196,0.1)', padding: '4px 10px',
            borderRadius: 100, display: 'inline-block',
            maxWidth: '100%', overflow: 'hidden',
            textOverflow: 'ellipsis', whiteSpace: 'nowrap'
          }}
        >
          {file.name}
        </motion.div>
      )}
    </motion.div>
  )
}