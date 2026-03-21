import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

export default function Chatbot() {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState([
    { role: 'ai', text: 'Hi! I am the TechNova assistant. Let me know if you need help navigating your skillset.' }
  ])
  const [input, setInput] = useState('')
  const messagesEndRef = useRef(null)

  useEffect(() => {
    if (isOpen) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }) // Updated ref name
    }
  }, [messages, isOpen])

  const sendMessage = async (text) => {
    if (!text.trim()) return

    const userMsg = { role: 'user', text }
    // Use a functional update for setMessages to ensure we're working with the latest state
    setMessages(prevMessages => {
      const newMessages = [...prevMessages, userMsg];
      
      // Immediately send the message to the API
      fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: newMessages }) // Send the updated list of messages
      })
      .then(resp => {
        if (!resp.ok) {
          throw new Error(`Server error ${resp.status}`);
        }
        return resp.json();
      })
      .then(data => {
        setMessages(prev => [...prev, { role: 'ai', text: data.reply }]);
      })
      .catch(err => {
        console.error("Error sending message:", err);
        setMessages(prev => [...prev, { role: 'ai', text: "Error connecting to the backend right now." }]);
      });

      return newMessages; // Return the new state for the user message
    });
  };

  const handleSend = async (e) => {
    e.preventDefault()
    if (!input.trim()) return
    sendMessage(input)
    setInput('')
  }

  return (
    <div style={{ position: 'fixed', bottom: 32, right: 32, zIndex: 9990, display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            transition={{ duration: 0.2, ease: 'easeOut' }}
            style={{
              width: 360, height: 500, background: '#090e17', borderRadius: 16,
              border: '1px solid rgba(255,255,255,0.1)', boxShadow: '0 20px 40px rgba(0,0,0,0.5)',
              marginBottom: 20, display: 'flex', flexDirection: 'column', overflow: 'hidden'
            }}
          >
            {/* Header */}
            <div style={{
              padding: '16px 20px', borderBottom: '1px solid rgba(255,255,255,0.05)',
              display: 'flex', alignItems: 'center', justifyContent: 'space-between',
              background: 'rgba(255,255,255,0.02)'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <div style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--accent)', boxShadow: '0 0 10px var(--accent)' }} />
                <h3 style={{ margin: 0, fontSize: '1rem', fontFamily: 'Syne, sans-serif', fontWeight: 600 }}>TechNova AI</h3>
              </div>
              <button 
                onClick={() => setIsOpen(false)}
                style={{ background: 'transparent', border: 'none', color: '#aab8c8', cursor: 'pointer', fontSize: '1.2rem' }}
              >
                &times;
              </button>
            </div>

            {/* Chat Messages */}
            <div className="chatbot-scroll" style={{ flex: 1, padding: 16, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 16 }}>
              {messages.map((msg, idx) => (
                <div key={idx} style={{
                  alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                  background: msg.role === 'user' ? 'rgba(74, 240, 196, 0.1)' : 'rgba(255,255,255,0.03)',
                  border: msg.role === 'user' ? '1px solid rgba(74, 240, 196, 0.2)' : '1px solid rgba(255,255,255,0.05)',
                  padding: '12px 16px', borderRadius: 16, maxWidth: '85%',
                  borderBottomRightRadius: msg.role === 'user' ? 4 : 16,
                  borderBottomLeftRadius: msg.role === 'user' ? 16 : 4,
                  color: msg.role === 'user' ? '#fff' : '#aab8c8',
                  fontSize: '0.9rem', lineHeight: 1.5, fontFamily: 'DM Sans, sans-serif'
                }}>
                  {msg.text}
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>

            {/* Predefined Chips */}
            {messages.length <= 2 && (
              <div className="chatbot-scroll" style={{
                display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 8, padding: '0 16px 12px'
              }}>
                {[
                  "What is a skill gap?",
                  "How do I use this app?",
                  "What's a custom pathway?"
                ].map((q, i) => (
                  <button
                    key={i}
                    type="button"
                    onClick={() => sendMessage(q)}
                    style={{
                      flexShrink: 0, background: 'rgba(74, 240, 196, 0.05)',
                      border: '1px solid rgba(74, 240, 196, 0.2)',
                      color: 'var(--accent)', padding: '6px 14px',
                      borderRadius: 16, fontSize: '0.8rem', cursor: 'pointer',
                      fontFamily: 'DM Sans, sans-serif', transition: 'all 0.2s'
                    }}
                    onMouseOver={(e) => { e.target.style.background = 'rgba(74, 240, 196, 0.15)' }}
                    onMouseOut={(e) => { e.target.style.background = 'rgba(74, 240, 196, 0.05)' }}
                  >
                    {q}
                  </button>
                ))}
              </div>
            )}

            {/* Input Area */}
            <div style={{ padding: 16, borderTop: '1px solid rgba(255,255,255,0.05)', background: 'rgba(0,0,0,0.2)' }}>
              <form style={{ display: 'flex', gap: 12 }} onSubmit={handleSend}>
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
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Floating Action Button */}
      <motion.button
        onClick={() => setIsOpen(!isOpen)}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        style={{
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
    </div>
  )
}
