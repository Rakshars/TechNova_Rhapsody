import { motion } from 'framer-motion'

const TIER_STYLE = {
  1: { color: '#fac850', bg: 'rgba(250,200,80,0.10)',  border: 'rgba(250,200,80,0.25)',  label: 'Foundation' },
  2: { color: 'var(--accent)',  bg: 'rgba(74,240,196,0.08)', border: 'rgba(74,240,196,0.2)',  label: 'Core Skill' },
  3: { color: 'var(--accent2)', bg: 'rgba(123,97,255,0.10)', border: 'rgba(123,97,255,0.25)', label: 'Advanced' },
}

const PLATFORM_STYLE = {
  youtube:      { icon: '▶️', color: '#ff4444',       bg: 'rgba(255,68,68,0.10)',    border: 'rgba(255,68,68,0.25)' },
  coursera:     { icon: '🎓', color: '#0056d2',       bg: 'rgba(0,86,210,0.10)',     border: 'rgba(0,86,210,0.25)' },
  udemy:        { icon: '📘', color: '#a435f0',       bg: 'rgba(164,53,240,0.10)',   border: 'rgba(164,53,240,0.25)' },
  docs:         { icon: '📄', color: 'var(--muted)',  bg: 'rgba(255,255,255,0.05)', border: 'rgba(255,255,255,0.12)' },
  kaggle:       { icon: '🏆', color: '#20beff',       bg: 'rgba(32,190,255,0.10)',   border: 'rgba(32,190,255,0.25)' },
  freecodecamp: { icon: '🔥', color: '#0a0a23',       bg: 'rgba(10,10,35,0.30)',     border: 'rgba(255,255,255,0.15)' },
  roadmap:      { icon: '🗺️', color: '#4af0c4',  bg: 'rgba(74,240,196,0.08)',  border: 'rgba(74,240,196,0.2)' },
}

export default function PathStep({ step }) {
  const tier   = step.tier ?? 0
  const ts     = TIER_STYLE[tier] ?? TIER_STYLE[2]
  const resources = step.resources ?? []
  const priorityStyle = step.priority === 'High'
    ? { background: 'rgba(255,107,107,0.12)', color: 'var(--accent3)' }
    : { background: 'rgba(250,200,80,0.12)',  color: '#fac850' }

  return (
    <motion.div
      className="path-step"
      initial={{ x: -25, opacity: 0 }}
      whileInView={{ x: 0, opacity: 1 }}
      viewport={{ once: true, margin: "-40px" }}
      transition={{ type: "spring", stiffness: 200, damping: 20 }}
      style={{ display: 'flex', gap: 20, marginBottom: 20 }}
    >
      <motion.div
        whileHover={{ scale: 1.15, borderColor: ts.color }}
        transition={{ type: "spring" }}
        style={{
          width: 42, height: 42, minWidth: 42, borderRadius: '50%',
          background: ts.bg, border: `1.5px solid ${ts.border}`,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontFamily: 'Syne, sans-serif', fontWeight: 800, fontSize: '0.85rem',
          color: ts.color, position: 'relative', zIndex: 1,
          transition: 'border-color 0.25s, background-color 0.25s'
        }}
      >
        {step.step}
      </motion.div>

      <motion.div
        whileHover={{ x: 6, borderColor: ts.border }}
        style={{
          flex: 1, background: 'var(--card)', border: `1px solid var(--border)`,
          borderRadius: 14, padding: '18px 20px',
          transition: 'border-color 0.25s'
        }}
      >
        {/* Title + tier badge */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
          <div style={{ fontFamily: 'Syne, sans-serif', fontWeight: 700, fontSize: '0.95rem' }}>{step.title}</div>
          {tier > 0 && (
            <span style={{ fontSize: '0.65rem', fontWeight: 700, padding: '2px 8px', borderRadius: 100,
              background: ts.bg, color: ts.color, border: `1px solid ${ts.border}`,
              letterSpacing: '0.06em', textTransform: 'uppercase' }}>
              {ts.label}
            </span>
          )}
        </div>

        {/* Description */}
        <div style={{ fontSize: '0.82rem', color: 'var(--muted)', lineHeight: 1.6, marginBottom: 10 }}>
          {step.description}
        </div>

        {/* Meta tags */}
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: resources.length ? 14 : 0 }}>
          <span style={{ fontSize: '0.72rem', padding: '3px 10px', borderRadius: 100, background: 'rgba(123,97,255,0.12)', color: 'var(--accent2)' }}>⏱ {step.duration}</span>
          <span style={{ fontSize: '0.72rem', padding: '3px 10px', borderRadius: 100, background: ts.bg, color: ts.color }}>{step.type}</span>
          <span style={{ fontSize: '0.72rem', padding: '3px 10px', borderRadius: 100, ...priorityStyle }}>{step.priority} Priority</span>
        </div>

        {/* Learning resources */}
        {resources.length > 0 && (
          <div>
            <div style={{ fontSize: '0.7rem', color: 'var(--muted)', textTransform: 'uppercase',
              letterSpacing: '0.08em', marginBottom: 8, fontWeight: 600 }}>
              Learn this skill
            </div>
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              {resources.map((r, i) => {
                const ps = PLATFORM_STYLE[r.platform] ?? PLATFORM_STYLE.docs
                return (
                  <motion.a
                    key={i}
                    href={r.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    whileHover={{ scale: 1.05, y: -2 }}
                    whileTap={{ scale: 0.97 }}
                    style={{
                      display: 'inline-flex', alignItems: 'center', gap: 5,
                      fontSize: '0.72rem', fontWeight: 600,
                      padding: '5px 12px', borderRadius: 100,
                      background: ps.bg, color: ps.color,
                      border: `1px solid ${ps.border}`,
                      textDecoration: 'none', cursor: 'pointer',
                      transition: 'box-shadow 0.2s',
                      whiteSpace: 'nowrap',
                    }}
                  >
                    <span>{ps.icon}</span>
                    <span>{r.title}</span>
                    <span style={{ opacity: 0.5, fontSize: '0.65rem' }}>↗</span>
                  </motion.a>
                )
              })}
            </div>
          </div>
        )}
      </motion.div>
    </motion.div>
  )
}