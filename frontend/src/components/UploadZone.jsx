import { useRef } from 'react'

export default function UploadZone({ label, subLabel, accept, file, onFile }) {
  const inputRef = useRef(null)

  const handleChange = (e) => { if (e.target.files[0]) onFile(e.target.files[0]) }
  const handleDrop = (e) => { e.preventDefault(); const f = e.dataTransfer.files[0]; if (f) onFile(f) }

  return (
    <div
      className="upload-zone"
      onDrop={handleDrop}
      onDragOver={e => e.preventDefault()}
      onClick={() => inputRef.current.click()}
      style={{
        border: `1.5px dashed ${file ? 'rgba(74,240,196,0.6)' : 'var(--border)'}`,
        borderRadius: 16, padding: '36px 24px', textAlign: 'center',
        cursor: 'pointer',
        background: file ? 'rgba(74,240,196,0.05)' : 'var(--card)',
        transition: 'all 0.25s'
      }}
    >
      <input ref={inputRef} type="file" accept={accept} onChange={handleChange} style={{ display: 'none' }} />
      <div style={{ fontSize: '2.2rem', marginBottom: 10, color: file ? 'var(--accent)' : 'var(--muted)' }}>
        {label === 'Resume' ? '📄' : '📋'}
      </div>
      <div style={{ fontFamily: 'Syne, sans-serif', fontWeight: 700, fontSize: '0.95rem', marginBottom: 4 }}>
        {label}
      </div>
      <div style={{ fontSize: '0.78rem', color: 'var(--muted)' }}>{subLabel}</div>
      {file && (
        <div style={{
          marginTop: 10, fontSize: '0.78rem', color: 'var(--accent)',
          background: 'rgba(74,240,196,0.1)', padding: '4px 10px',
          borderRadius: 100, display: 'inline-block',
          maxWidth: '100%', overflow: 'hidden',
          textOverflow: 'ellipsis', whiteSpace: 'nowrap'
        }}>
          {file.name}
        </div>
      )}
    </div>
  )
}