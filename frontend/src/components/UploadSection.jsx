import UploadZone from './UploadZone'

export default function UploadSection({ files, onFile, onAnalyze, disabled }) {
  return (
    <div className="reveal" id="uploadSection">
      <div className="section-label">Step 01 — Upload Documents</div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, marginBottom: 28 }}>
        <UploadZone label="Resume" subLabel="Upload PDF file" accept=".pdf" file={files.resume} onFile={(f) => onFile('resume', f)} />
        <UploadZone label="Job Description" subLabel="Upload TXT or PDF" accept=".txt,.pdf" file={files.jd} onFile={(f) => onFile('jd', f)} />
      </div>
      <button
        onClick={onAnalyze}
        disabled={disabled}
        style={{
          width: '100%', padding: '18px 32px',
          background: 'linear-gradient(135deg, #4af0c4 0%, #2dd4a0 100%)',
          color: '#050a14', fontFamily: 'Syne, sans-serif', fontWeight: 700,
          fontSize: '1rem', letterSpacing: '0.03em', border: 'none',
          borderRadius: 14, cursor: disabled ? 'not-allowed' : 'pointer',
          opacity: disabled ? 0.5 : 1, marginBottom: 48,
          transition: 'transform 0.2s, box-shadow 0.2s'
        }}
        onMouseEnter={e => { if (!disabled) { e.currentTarget.style.transform = 'translateY(-2px)'; e.currentTarget.style.boxShadow = '0 12px 40px rgba(74,240,196,0.3)' }}}
        onMouseLeave={e => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = 'none' }}
      >
        <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10 }}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
          </svg>
          {disabled ? 'Analyzing...' : 'Analyze Skill Gap'}
        </span>
      </button>
    </div>
  )
}