import { useState, useEffect, useRef } from 'react'
import Navbar from './components/Navbar'
import Hero from './components/Hero'
import UploadSection from './components/UploadSection'
import LoadingState from './components/LoadingState'
import ResultsSection from './components/ResultsSection'
import { MOCK_RESPONSE } from './mockData'

const LOADING_MESSAGES = [
  'Parsing resume...', 'Extracting skills...', 'Scanning job description...',
  'Mapping skill graph...', 'Running gap analysis...', 'Generating your pathway...'
]

export default function App() {
  const [files, setFiles] = useState({ resume: null, jd: null })
  const [phase, setPhase] = useState('idle')
  const [results, setResults] = useState(null)
  const [loadingMsg, setLoadingMsg] = useState(LOADING_MESSAGES[0])
  const [error, setError] = useState('')
  const resultsRef = useRef(null)

  // Scroll progress bar
  useEffect(() => {
    const bar = document.getElementById('scroll-bar')
    const onScroll = () => {
      const pct = (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100
      if (bar) bar.style.width = pct + '%'
    }
    window.addEventListener('scroll', onScroll)
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  // Custom cursor
  useEffect(() => {
    const dot = document.getElementById('cursor-dot')
    const ring = document.getElementById('cursor-ring')
    if (!dot || !ring) return
    let mx = 0, my = 0, rx = 0, ry = 0
    const onMove = (e) => { mx = e.clientX; my = e.clientY }
    window.addEventListener('mousemove', onMove)
    let raf
    const animate = () => {
      dot.style.left = mx + 'px'
      dot.style.top = my + 'px'
      rx += (mx - rx) * 0.12
      ry += (my - ry) * 0.12
      ring.style.left = rx + 'px'
      ring.style.top = ry + 'px'
      raf = requestAnimationFrame(animate)
    }
    animate()
    return () => {
      window.removeEventListener('mousemove', onMove)
      cancelAnimationFrame(raf)
    }
  }, [])

  // Cursor hover effect — re-runs when phase changes so new elements get picked up
  useEffect(() => {
    const ring = document.getElementById('cursor-ring')
    if (!ring) return
    const add = () => ring.classList.add('hovering')
    const remove = () => ring.classList.remove('hovering')
    const els = document.querySelectorAll('button, a, .upload-zone, .path-step, .metric-card')
    els.forEach(el => { el.addEventListener('mouseenter', add); el.addEventListener('mouseleave', remove) })
    return () => els.forEach(el => { el.removeEventListener('mouseenter', add); el.removeEventListener('mouseleave', remove) })
  }, [phase])

  // Scroll reveal
  useEffect(() => {
    const observer = new IntersectionObserver(
      entries => entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible') }),
      { threshold: 0.1 }
    )
    document.querySelectorAll('.reveal').forEach(el => observer.observe(el))
    return () => observer.disconnect()
  }, [phase])

  const handleFile = (type, file) => setFiles(prev => ({ ...prev, [type]: file }))

  const runAnalysis = async () => {
    if (!files.resume || !files.jd) {
      setError('Please upload both a Resume and a Job Description first.')
      setTimeout(() => setError(''), 4000)
      return
    }
    setPhase('loading')
    let idx = 0
    setLoadingMsg(LOADING_MESSAGES[0])
    const interval = setInterval(() => {
      idx = (idx + 1) % LOADING_MESSAGES.length
      setLoadingMsg(LOADING_MESSAGES[idx])
    }, 900)

    try {
      // ── REAL INTEGRATION POINT ──────────────────────────────
      // When backend is ready, replace the two lines below with:
      //
      // const formData = new FormData()
      // formData.append('resume', files.resume)
      // formData.append('jd', files.jd)
      // const resp = await fetch('http://localhost:5000/analyze', {
      //   method: 'POST', body: formData
      // })
      // if (!resp.ok) throw new Error('Backend error')
      // const data = await resp.json()
      // ────────────────────────────────────────────────────────
      await new Promise(r => setTimeout(r, 3200))
      const data = MOCK_RESPONSE

      clearInterval(interval)
      setResults(data)
      setPhase('results')
      setTimeout(() => resultsRef.current?.scrollIntoView({ behavior: 'smooth' }), 200)
    } catch (err) {
      clearInterval(interval)
      setError('Analysis failed. Please check your files and try again.')
      setTimeout(() => setError(''), 4000)
      setPhase('idle')
    }
  }

  return (
    <>
      <div className="noise" />
      <div id="scroll-bar" />
      <div id="cursor-dot" />
      <div id="cursor-ring" />

      <Navbar />
      <Hero />

      <div style={{ maxWidth: 1100, margin: '0 auto', padding: '60px 24px 120px', position: 'relative', zIndex: 2 }}>
        <UploadSection
          files={files}
          onFile={handleFile}
          onAnalyze={runAnalysis}
          disabled={phase === 'loading'}
        />
        {phase === 'loading' && <LoadingState message={loadingMsg} />}
        {phase === 'results' && results && (
          <div ref={resultsRef}>
            <ResultsSection data={results} />
          </div>
        )}
      </div>

      {error && (
        <div style={{
          position: 'fixed', bottom: 32, right: 32,
          background: 'rgba(255,107,107,0.15)',
          border: '1px solid rgba(255,107,107,0.4)',
          color: '#ff6b6b', padding: '14px 20px',
          borderRadius: 12, fontSize: '0.85rem',
          zIndex: 200, animation: 'fadeUp 0.3s ease'
        }}>
          {error}
        </div>
      )}
    </>
  )
}