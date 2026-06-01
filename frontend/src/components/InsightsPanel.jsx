import { useState } from 'react'
import MarkdownText from './MarkdownText'

const SECTIONS = [
  { key: 'customer_insights',     label: '👥 Customer Feedback',      icon: '👥' },
  { key: 'sales_analysis',        label: '📈 Sales Performance',       icon: '📈' },
  { key: 'market_opportunities',  label: '🚀 Market Opportunities',    icon: '🚀' },
  { key: 'feature_priorities',    label: '⚡ Feature Prioritization',  icon: '⚡' },
]

export default function InsightsPanel({ result }) {
  const [active, setActive] = useState('customer_insights')

  if (!result) {
    return (
      <div style={{ textAlign: 'center', color: '#90A4AE', paddingTop: 80, fontSize: 15 }}>
        Run analysis to view agent insights.
      </div>
    )
  }

  const currentSection = SECTIONS.find(s => s.key === active)
  const data = result[active] || {}
  const text = data.analysis || 'No analysis available for this section.'

  const s = {
    container: { display: 'flex', gap: 20, height: 'calc(100vh - 130px)' },
    nav:  { width: 210, display: 'flex', flexDirection: 'column', gap: 6 },
    navBtn: (isActive) => ({
      background: isActive ? '#DDE3EA' : '#fff',
      color:      isActive ? '#1565C0' : '#546E7A',
      border:     'none',
      borderLeft: isActive ? '3px solid #1565C0' : '3px solid transparent',
      borderRadius: 8, padding: '11px 14px',
      textAlign: 'left', fontSize: 13,
      fontWeight: isActive ? 600 : 400,
      cursor: 'pointer',
      boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
      transition: 'all 0.15s',
    }),
    content: {
      flex: 1, background: '#fff', borderRadius: 10,
      padding: 24, overflow: 'auto',
      boxShadow: '0 1px 4px rgba(0,0,0,0.07)',
    },
    title: { fontSize: 17, fontWeight: 700, color: '#1565C0', marginBottom: 18, paddingBottom: 12, borderBottom: '2px solid #DDE3EA' },
    body:  { color: '#263238' },
  }

  return (
    <div style={s.container}>
      <div style={s.nav}>
        {SECTIONS.map(sec => (
          <button key={sec.key} style={s.navBtn(active === sec.key)} onClick={() => setActive(sec.key)}>
            {sec.label}
          </button>
        ))}
      </div>
      <div style={s.content}>
        <div style={s.title}>{currentSection?.label}</div>
        <div style={s.body}><MarkdownText text={text} /></div>
      </div>
    </div>
  )
}
