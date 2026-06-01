import MarkdownText from './MarkdownText'

function Section({ title, content }) {
  if (!content) return null
  return (
    <div style={{ background: '#fff', borderRadius: 10, padding: 24, boxShadow: '0 1px 4px rgba(0,0,0,0.07)', marginBottom: 16 }}>
      <div style={{ fontSize: 15, fontWeight: 700, color: '#1565C0', marginBottom: 14, paddingBottom: 10, borderBottom: '2px solid #DDE3EA' }}>
        {title}
      </div>
      <MarkdownText text={content} />
    </div>
  )
}

function extract(raw, ...headings) {
  for (const heading of headings) {
    const regex = new RegExp(`##\\s*${heading}[\\s\\S]*?(?=\\n##|$)`, 'i')
    const match = raw.match(regex)
    if (match) {
      return match[0].replace(new RegExp(`##\\s*${heading}`, 'i'), '').trim()
    }
  }
  return ''
}

export default function StrategyPanel({ result }) {
  if (!result?.strategy?.analysis) {
    return (
      <div style={{ textAlign: 'center', color: '#90A4AE', paddingTop: 80, fontSize: 15 }}>
        Run analysis to view strategic recommendations.
      </div>
    )
  }

  const raw  = result.strategy.analysis
  const swot = extract(raw, 'SWOT Analysis')
  const recs = extract(raw, 'Top 5 Strategic Recommendations', 'Strategic Recommendations')
  const plan = extract(raw, '90-Day Action Plan')
  const kpis = extract(raw, '5 KPIs to Track', 'KPIs to Track')

  return (
    <div>
      <Section title="SWOT Analysis"                      content={swot || raw.slice(0, 1500)} />
      <Section title="Top 5 Strategic Recommendations"    content={recs} />
      <Section title="90-Day Action Plan"                  content={plan} />
      <Section title="KPIs to Track"                       content={kpis} />
    </div>
  )
}
