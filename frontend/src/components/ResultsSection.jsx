import { useRef } from 'react'
import { motion, useScroll, useSpring } from 'framer-motion'
import MetricCard from './MetricCard'
import SkillChip from './SkillChip'
import PathStep from './PathStep'
import ReasoningBox from './ReasoningBox'
import AvatarScanner from './AvatarScanner'
import TerminalText from './TerminalText'

export default function ResultsSection({ data }) {
  const pathRef = useRef(null)
  
  const { scrollYProgress } = useScroll({
    target: pathRef,
    offset: ["start 70%", "end 70%"]
  })
  
  const scaleY = useSpring(scrollYProgress, { stiffness: 100, damping: 25 })

  const slideUp = {
    hidden: { opacity: 0, y: 30 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.6 } }
  }

  return (
    <>
      <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={slideUp} className="section-label" style={{ marginTop: 0, display: 'flex', alignItems: 'center', gap: 14 }}>
        <TerminalText text="Analysis Summary" delay={0.1} />
      </motion.div>
      
      <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={slideUp}>
        <AvatarScanner matchedSkills={data.skills_matched} missingSkills={data.skills_missing} level={data.level} />
      </motion.div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 16 }}>
        <MetricCard value={data.skills_matched.length} label="Skills Matched" color="var(--accent)" />
        <MetricCard value={data.skills_missing.length} label="Gaps Found" color="var(--accent3)" />
        <MetricCard value={`${data.match_score ?? 0}%`} label="Match Score" color="var(--accent2)" />
      </div>

      <motion.div className="divider" initial="hidden" whileInView="visible" viewport={{ once: true }} variants={slideUp} />

      <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={slideUp}>
        <div className="section-label"><TerminalText text="Step 02 — Skill Analysis" delay={0.2} /></div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
          <div style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 16, padding: 24, transition: 'border-color 0.3s' }} className="metric-card">
            <div style={{ fontFamily: 'Syne, sans-serif', fontWeight: 700, fontSize: '0.9rem', marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ display: 'inline-block', width: 8, height: 8, background: 'var(--accent)', borderRadius: '50%' }} />
              Skills You Have
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10 }}>
              {data.skills_matched.map((s, i) => <SkillChip key={s} label={s} type="has" delay={i * 0.04} />)}
            </div>
          </div>
          <div style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 16, padding: 24, transition: 'border-color 0.3s' }} className="metric-card">
            <div style={{ fontFamily: 'Syne, sans-serif', fontWeight: 700, fontSize: '0.9rem', marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ display: 'inline-block', width: 8, height: 8, background: 'var(--accent3)', borderRadius: '50%' }} />
              Skills to Acquire
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10 }}>
              {data.skills_missing.map((s, i) => <SkillChip key={s} label={s} type="missing" delay={i * 0.04} />)}
            </div>
          </div>
        </div>
      </motion.div>

      <motion.div className="divider" initial="hidden" whileInView="visible" viewport={{ once: true }} variants={slideUp} />

      <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={slideUp}>
        <div className="section-label"><TerminalText text="Step 03 — Learning Pathway" delay={0.2} /></div>
        <div ref={pathRef} style={{ position: 'relative' }}>
          <div style={{
            position: 'absolute', left: 21, top: 0, bottom: 0, width: 2,
            background: 'var(--card)', borderRadius: 2
          }} />
          <motion.div style={{
            position: 'absolute', left: 21, top: 0, bottom: 0, width: 2,
            background: 'linear-gradient(180deg, var(--accent), var(--accent2), var(--accent3))',
            originY: 0, scaleY: scaleY, borderRadius: 2,
            zIndex: 0
          }} />
          <div style={{ position: 'relative', zIndex: 1 }}>
            {data.learning_path.map(step => <PathStep key={step.step} step={step} />)}
          </div>
        </div>
      </motion.div>

      <motion.div className="divider" initial="hidden" whileInView="visible" viewport={{ once: true }} variants={slideUp} />

      <motion.div initial="hidden" whileInView="visible" viewport={{ once: true }} variants={slideUp}>
        <div className="section-label"><TerminalText text="Step 04 — Reasoning Trace" delay={0.2} /></div>
        <ReasoningBox text={data.reasoning} />
      </motion.div>
    </>
  )
}