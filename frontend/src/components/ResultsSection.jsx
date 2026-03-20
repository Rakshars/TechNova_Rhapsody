import MetricCard from './MetricCard'
import SkillChip from './SkillChip'
import PathStep from './PathStep'
import ReasoningBox from './ReasoningBox'

export default function ResultsSection({ data }) {
  return (
    <>
      <div className="reveal section-label" style={{ marginTop: 0 }}>Analysis Summary</div>
      <div className="reveal" style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 16 }}>
        <MetricCard value={data.skills_matched.length} label="Skills Matched" color="var(--accent)" />
        <MetricCard value={data.skills_missing.length} label="Gaps Found" color="var(--accent3)" />
        <MetricCard value={data.learning_path.length} label="Learning Steps" color="var(--accent2)" />
      </div>

      <div className="divider reveal" />

      <div className="reveal">
        <div className="section-label">Step 02 — Skill Analysis</div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
          <div style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 16, padding: 24 }}>
            <div style={{ fontFamily: 'Syne, sans-serif', fontWeight: 700, fontSize: '0.9rem', marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ display: 'inline-block', width: 8, height: 8, background: 'var(--accent)', borderRadius: '50%' }} />
              Skills You Have
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10 }}>
              {data.skills_matched.map((s, i) => <SkillChip key={s} label={s} type="has" delay={i * 0.05} />)}
            </div>
          </div>
          <div style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 16, padding: 24 }}>
            <div style={{ fontFamily: 'Syne, sans-serif', fontWeight: 700, fontSize: '0.9rem', marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ display: 'inline-block', width: 8, height: 8, background: 'var(--accent3)', borderRadius: '50%' }} />
              Skills to Acquire
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10 }}>
              {data.skills_missing.map((s, i) => <SkillChip key={s} label={s} type="missing" delay={i * 0.05} />)}
            </div>
          </div>
        </div>
      </div>

      <div className="divider reveal" />

      <div className="reveal">
        <div className="section-label">Step 03 — Learning Pathway</div>
        <div style={{ position: 'relative' }}>
          <div style={{
            position: 'absolute', left: 21, top: 0, bottom: 0, width: 1,
            background: 'linear-gradient(180deg, var(--accent), var(--accent2), var(--accent3))'
          }} />
          {data.learning_path.map(step => <PathStep key={step.step} step={step} />)}
        </div>
      </div>

      <div className="divider reveal" />

      <div className="reveal">
        <div className="section-label">Step 04 — Reasoning Trace</div>
        <ReasoningBox text={data.reasoning} />
      </div>
    </>
  )
}