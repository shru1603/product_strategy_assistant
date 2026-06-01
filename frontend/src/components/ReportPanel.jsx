import { reportUrl } from '../api/client'

const SECTIONS = [
  'Executive Summary',
  'Customer Insights',
  'Sales Performance',
  'Market Opportunities',
  'Feature Prioritization (RICE)',
  'Strategic Recommendations & SWOT',
]

export default function ReportPanel({ sessionId, result }) {
  const ready = result?.report_status?.status === 'generated'

  const s = {
    outer: { display: 'flex', alignItems: 'center', justifyContent: 'center', height: 'calc(100vh - 130px)' },
    card: {
      background: '#fff', borderRadius: 14, padding: '48px 52px',
      boxShadow: '0 2px 16px rgba(0,0,0,0.09)', textAlign: 'center', maxWidth: 440,
    },
    icon:  { fontSize: 64, marginBottom: 20 },
    title: { fontSize: 22, fontWeight: 700, color: '#1565C0', marginBottom: 10 },
    desc:  { fontSize: 14, color: '#78909C', lineHeight: 1.7, marginBottom: 28 },
    btn: {
      display: 'inline-block', background: '#1565C0', color: '#fff',
      borderRadius: 8, padding: '13px 36px', fontSize: 15, fontWeight: 600,
      textDecoration: 'none', transition: 'background 0.2s',
    },
    sectionList: {
      marginTop: 24, textAlign: 'left',
      background: '#F5F7FA', borderRadius: 8, padding: '14px 18px',
    },
    sectionItem: { fontSize: 12, color: '#546E7A', lineHeight: 2 },
  }

  return (
    <div style={s.outer}>
      <div style={s.card}>
        <div style={s.icon}>{ready ? '📄' : '⏳'}</div>
        <div style={s.title}>{ready ? 'Report Ready' : 'Report Not Generated'}</div>
        <div style={s.desc}>
          {ready
            ? 'Your executive PDF strategy report has been generated and is ready for download.'
            : 'Upload data and run the full analysis pipeline. The report is generated automatically at the end.'}
        </div>

        {ready && sessionId && (
          <a href={reportUrl(sessionId)} target="_blank" rel="noreferrer" style={s.btn}>
            ⬇ Download PDF Report
          </a>
        )}

        {ready && (
          <div style={s.sectionList}>
            <div style={{ fontSize: 11, fontWeight: 700, color: '#90A4AE', textTransform: 'uppercase', letterSpacing: 0.8, marginBottom: 6 }}>
              Report Contents
            </div>
            {SECTIONS.map(sec => (
              <div key={sec} style={s.sectionItem}>• {sec}</div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
