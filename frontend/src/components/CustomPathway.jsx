import { useState } from 'react'
import { motion } from 'framer-motion'
import TerminalText from './TerminalText'

export default function CustomPathway({ skills }) {
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [schedule, setSchedule] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleGenerate = async () => {
    if (!startDate || !endDate) {
      setError('Please select both a start and end date.')
      return
    }
    const sDate = new Date(startDate)
    const eDate = new Date(endDate)
    const dtms = eDate - sDate
    const daysTotal = Math.ceil(dtms / (1000 * 60 * 60 * 24)) + 1

    if (daysTotal <= 0) {
      setError('End date must be after or equal to the start date.')
      return
    }

    if (daysTotal < skills.length) {
      setError(`Please select a wider date range. You need a minimum of ${skills.length} days to properly cover these ${skills.length} missing skills.`)
      return
    }

    setError('')
    setLoading(true)

    try {
      const resp = await fetch('/api/custom_pathway', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ skills, start_date: startDate, end_date: endDate })
      })

      if (!resp.ok) {
        const err = await resp.json().catch(() => ({}))
        throw new Error(err.detail || `Server error ${resp.status}`)
      }
      const raw = await resp.json()
      setSchedule(raw.schedule)
    } catch (err) {
      setError(`Failed to generate schedule: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ marginTop: 40 }}>
      <div className="section-label"><TerminalText text="Optional — Customized Day-by-Day Pathway" delay={0.2} /></div>
      
      <div style={{
        background: 'var(--card)', border: '1px solid var(--border)',
        borderRadius: 16, padding: '24px 32px', display: 'flex', flexDirection: 'column', gap: 20
      }}>
        <div style={{ display: 'flex', gap: 20, flexWrap: 'wrap', alignItems: 'flex-end', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', gap: 20, flexWrap: 'wrap', flex: 1 }}>
            <div style={{ minWidth: 200, flex: 1 }}>
              <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--muted)', marginBottom: 8, fontFamily: 'Syne, sans-serif' }}>
                Start Date
              </label>
              <input 
                type="date"
                value={startDate}
                onChange={e => setStartDate(e.target.value)}
                style={{
                  width: '100%', background: 'rgba(0,0,0,0.3)', border: '1px solid rgba(255,255,255,0.1)',
                  padding: '12px 16px', borderRadius: 12, color: '#fff', outline: 'none',
                  fontFamily: 'DM Sans, sans-serif', colorScheme: 'dark'
                }}
              />
            </div>
            <div style={{ minWidth: 200, flex: 1 }}>
              <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--muted)', marginBottom: 8, fontFamily: 'Syne, sans-serif' }}>
                End Date
              </label>
              <input 
                type="date"
                value={endDate}
                onChange={e => setEndDate(e.target.value)}
                style={{
                  width: '100%', background: 'rgba(0,0,0,0.3)', border: '1px solid rgba(255,255,255,0.1)',
                  padding: '12px 16px', borderRadius: 12, color: '#fff', outline: 'none',
                  fontFamily: 'DM Sans, sans-serif', colorScheme: 'dark'
                }}
              />
            </div>
          </div>
          <button 
            onClick={handleGenerate}
            disabled={loading}
            style={{
              background: 'var(--accent)', color: '#000', border: 'none',
              padding: '0 24px', borderRadius: 12, fontWeight: 600,
              cursor: loading ? 'not-allowed' : 'pointer', fontFamily: 'Syne, sans-serif',
              height: 46
            }}
          >
            {loading ? 'Generating...' : 'Build Custom Plan'}
          </button>
        </div>

        {error && <div style={{ color: 'var(--accent3)', fontSize: '0.9rem' }}>{error}</div>}

        {schedule && schedule.length > 0 && (
          <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} style={{ overflow: 'hidden' }}>
            <div style={{ position: 'relative', marginTop: 32, marginLeft: 6 }}>
              <div style={{ position: 'absolute', left: 21, top: 0, bottom: 0, width: 2, background: 'var(--card)' }} />
              
              {schedule.map((item, i) => (
                <div key={i} style={{ display: 'flex', gap: 24, marginBottom: i === schedule.length - 1 ? 0 : 24, position: 'relative' }}>
                  <div style={{ width: 44, display: 'flex', justifyContent: 'center', zIndex: 1, marginTop: 8 }}>
                    <div style={{ width: 14, height: 14, borderRadius: '50%', background: 'var(--accent)', border: '3px solid var(--bg)' }} />
                  </div>
                  
                  <div style={{
                    flex: 1, background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.05)',
                    borderRadius: 12, padding: 16
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <div style={{ paddingRight: 16 }}>
                        <h4 style={{ margin: 0, fontSize: '1.05rem', fontFamily: 'Syne, sans-serif', color: 'var(--text)' }}>
                          {item.skill}
                        </h4>
                        <p style={{ margin: '6px 0 0', color: '#aab8c8', fontSize: '0.9rem', lineHeight: 1.4 }}>
                          {item.topic}
                        </p>
                      </div>
                      <div style={{ 
                        background: 'rgba(74, 240, 196, 0.1)', color: 'var(--accent)', 
                        padding: '4px 10px', borderRadius: 20, fontSize: '0.75rem', 
                        fontWeight: 600, letterSpacing: '0.05em', whiteSpace: 'nowrap'
                      }}>
                        {item.day_name}, {item.date}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </div>
    </div>
  )
}
