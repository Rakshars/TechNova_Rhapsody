import { useState, useEffect, useRef } from 'react'
import { motion, useMotionValue, useSpring } from 'framer-motion'
import Lenis from 'lenis'
import Navbar from './components/Navbar'
import Hero from './components/Hero'
import UploadSection from './components/UploadSection'
import LoadingState from './components/LoadingState'
import ResultsSection from './components/ResultsSection'

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

  // Framer Motion Cursor State
  const cursorX = useMotionValue(-100)
  const cursorY = useMotionValue(-100)
  const springConfig = { damping: 25, stiffness: 200, mass: 0.5 }
  const cursorXSpring = useSpring(cursorX, springConfig)
  const cursorYSpring = useSpring(cursorY, springConfig)
  const [isHovering, setIsHovering] = useState(false)

  // Smooth Scroll Initialization
  useEffect(() => {
    const lenis = new Lenis({
      duration: 1.2,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      smoothWheel: true,
    })
    function raf(time) {
      lenis.raf(time)
      requestAnimationFrame(raf)
    }
    requestAnimationFrame(raf)
    return () => lenis.destroy()
  }, [])

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

  // Framer Motion Cursor Tracker
  useEffect(() => {
    const onMove = (e) => {
      cursorX.set(e.clientX)
      cursorY.set(e.clientY)
    }
    window.addEventListener('mousemove', onMove)
    return () => window.removeEventListener('mousemove', onMove)
  }, [cursorX, cursorY])

  // Framer Motion Cursor Hover state across the app
  useEffect(() => {
    const add = () => setIsHovering(true)
    const remove = () => setIsHovering(false)
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
      const formData = new FormData()
      formData.append('resume', files.resume)
      formData.append('jd_file', files.jd)
      formData.append('mode', 'semantic')

      const resp = await fetch('/api/upload', { method: 'POST', body: formData })
      if (!resp.ok) {
        const err = await resp.json().catch(() => ({}))
        throw new Error(err.detail || `Server error ${resp.status}`)
      }
      const raw = await resp.json()

      // Map backend response shape → frontend component shape
      const data = {
        level:          raw.level ?? 'beginner',
        skills_matched: raw.user_skills ?? [],
        skills_missing: raw.missing_skills ?? [],
        match_score:    raw.match_score ?? 0,
        learning_path:  (raw.learning_path ?? []).map((step, i) => ({
          step:        i + 1,
          title:       step.skill,
          duration:    step.duration,
          type:        step.type,
          priority:    step.priority,
          tier:        step.tier ?? 0,
          resources:   step.resources ?? [],
          description: step.tier === 1
            ? 'Foundation skill — builds the base for everything above it.'
            : step.tier === 3
            ? 'Advanced topic — directly targeted by the job description.'
            : 'Core skill — bridges your current knowledge to the role.',
        })),
        reasoning: (raw.reasoning ?? []).map(r => r.reason ?? '').filter(Boolean).join(' '),
      }

      clearInterval(interval)
      setResults(data)
      setPhase('results')
      setTimeout(() => resultsRef.current?.scrollIntoView({ behavior: 'smooth' }), 200)
    } catch (err) {
      clearInterval(interval)
      setError(`Analysis failed: ${err.message}`)
      setTimeout(() => setError(''), 5000)
      setPhase('idle')
    }
  }

  return (
    <>
      <div className="noise" />
      <div id="scroll-bar" />
      <motion.div
        className="cursor-dot"
        style={{ left: cursorX, top: cursorY }}
      />
      <motion.div
        className={`cursor-ring ${isHovering ? 'hovering' : ''}`}
        style={{ left: cursorXSpring, top: cursorYSpring }}
      />

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