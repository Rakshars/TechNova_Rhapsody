import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

export default function Chatbot() {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState([
    { role: 'ai', text: 'Hi! I am the TechNova assistant. Let me know if you need help navigating your skillset.' }
  ])
  const [input, setInput] = useState('')
  const msgsEndRef = useRef(null)

  useEffect(() => {
    if (isOpen) {
      msgsEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages, isOpen])

  const handleSend = (e) => {
    e.preventDefault()
    if (!input.trim()) return

    const userMsg = { role: 'user', text: input }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    
    // Simulate AI response for the demo
    setTimeout(() => {
      setMessages(prev => [...prev, { 
        role: 'ai', 
        text: "I am currently set to demo mode, but I can be wired up to an actual LLM backend to answer specific questions about your uploaded documents!" 
      }])
    }, 1200)
  }

  return (
    <>
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 50, scale: 0.8, originX: 1, originY: 1 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 50, scale: 0.8, transition: { duration: 0.2 } }}
            transition={{ type: 'spring', stiffness: 300, damping: 25 }}
            style={{
              position: 'fixed', bottom: 96, right: 30, zIndex: 100,
              width: 340, height: 480,
              background: 'rgba(12, 21, 37, 0.85)',
              backdropFilter: 'blur(20px)',
              border: '1px solid rgba(74, 240, 196, 0.2)',
              borderRadius: 20,
              boxShadow: '0 10px 40px rgba(0,0,0,0.5), inset 0 2px 20px rgba(255,255,255,0.02)',
              display: 'flex', flexDirection: 'column', overflow: 'hidden'
            }}
          >
            {/* Header */}
            <div style={{
              padding: '16px 20px', borderBottom: '1px solid rgba(255,255,255,0.05)',
              display: 'flex', justifyContent: 'space-between', alignItems: 'center',
              background: 'rgba(255,255,255,0.02)'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <div style={{ 
                  width: 8, height: 8, borderRadius: '50%', 
                  background: 'var(--accent)', boxShadow: '0 0 10px var(--accent)' 
                }} />
                <span style={{ fontWeight: 600, fontSize: '0.95rem', letterSpacing: '0.02em' }}>TechNova AI</span>
              </div>
              <button 
                onClick={() => setIsOpen(false)}
                style={{ 
                  background: 'none', border: 'none', color: 'var(--muted)', cursor: 'pointer',
                  fontSize: '1.4rem', padding: 4, display: 'flex', alignItems: 'center', justifyContent: 'center',
                  lineHeight: 1
                }}
              >
                &times;
              </button>
            </div>

            {/* Messages Area */}
            <div className="chatbot-scroll" style={{
              flex: 1, overflowY: 'auto', padding: '20px 16px',
              display: 'flex', flexDirection: 'column', gap: 12,
              scrollbarWidth: 'thin', scrollbarColor: 'rgba(255,255,255,0.1) transparent'
            }}>
              {messages.map((m, i) => (
                <div key={i} style={{
                  alignSelf: m.role === 'user' ? 'flex-end' : 'flex-start',
                  maxWidth: '85%', padding: '12px 16px',
                  borderRadius: 16, fontSize: '0.9rem', lineHeight: 1.5,
                  background: m.role === 'user' ? 'rgba(74, 240, 196, 0.15)' : 'rgba(255, 255, 255, 0.04)',
                  color: m.role === 'user' ? '#fff' : 'var(--text)',
                  border: m.role === 'user' ? '1px solid rgba(74, 240, 196, 0.3)' : '1px solid rgba(255,255,255,0.08)',
                  borderBottomRightRadius: m.role === 'user' ? 4 : 16,
                  borderBottomLeftRadius: m.role === 'ai' ? 4 : 16,
                  boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
                }}>
                  {m.text}
                </div>
              ))}
              <div ref={msgsEndRef} />
            </div>

            {/* Input Form */}
            <form onSubmit={handleSend} style={{
              padding: 14, borderTop: '1px solid rgba(255,255,255,0.05)',
              display: 'flex', gap: 8, background: 'rgba(0,0,0,0.2)'
            }}>
              <input 
                type="text" 
                value={input}
                onChange={e => setInput(e.target.value)}
                placeholder="Ask me anything..."
                style={{
                  flex: 1, background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.1)',
                  padding: '10px 16px', borderRadius: 24, color: '#fff', outline: 'none',
                  fontSize: '0.9rem', transition: 'border 0.2s',
                }}
                onFocus={e => e.target.style.borderColor = 'rgba(74, 240, 196, 0.4)'}
                onBlur={e => e.target.style.borderColor = 'rgba(255,255,255,0.1)'}
              />
              <button type="submit" style={{
                background: 'rgba(74, 240, 196, 0.15)', border: '1px solid rgba(74, 240, 196, 0.3)',
                color: 'var(--accent)', borderRadius: '50%', width: 42, height: 42,
                display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer',
                transition: 'all 0.2s'
              }}
              onMouseEnter={e => e.currentTarget.style.background = 'rgba(74, 240, 196, 0.25)'}
              onMouseLeave={e => e.currentTarget.style.background = 'rgba(74, 240, 196, 0.15)'}
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="22" y1="2" x2="11" y2="13"></line>
                  <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                </svg>
              </button>
            </form>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Floating Action Button */}
      <motion.button
        onClick={() => setIsOpen(!isOpen)}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        style={{
          position: 'fixed', bottom: 24, right: 30, zIndex: 100,
          width: 58, height: 58, borderRadius: '50%',
          background: 'linear-gradient(135deg, var(--accent), #1f7d63)',
          border: 'none', color: '#03060a', cursor: 'pointer',
          boxShadow: '0 8px 24px rgba(74, 240, 196, 0.4), inset 0 2px 6px rgba(255,255,255,0.4)',
          display: 'flex', alignItems: 'center', justifyContent: 'center'
        }}
      >
        <AnimatePresence mode="wait">
          {isOpen ? (
            <motion.svg 
              key="close" initial={{ opacity: 0, rotate: -90 }} animate={{ opacity: 1, rotate: 0 }} exit={{ opacity: 0, rotate: 90 }}
              width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"
            >
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </motion.svg>
          ) : (
            <motion.svg 
              key="message" initial={{ opacity: 0, scale: 0.5 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.5 }}
              width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
            >
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            </motion.svg>
          )}
        </AnimatePresence>
      </motion.button>
    </>
  )
}
