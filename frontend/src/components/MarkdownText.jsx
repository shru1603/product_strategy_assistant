function renderInline(text) {
  const parts = text.split(/(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)/g)
  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**'))
      return <strong key={i} style={{ fontWeight: 700 }}>{part.slice(2, -2)}</strong>
    if (part.startsWith('*') && part.endsWith('*'))
      return <em key={i}>{part.slice(1, -1)}</em>
    if (part.startsWith('`') && part.endsWith('`'))
      return <code key={i} style={{ background: '#F0F2F5', padding: '1px 5px', borderRadius: 4, fontSize: '0.92em', fontFamily: 'monospace' }}>{part.slice(1, -1)}</code>
    return part
  })
}

export default function MarkdownText({ text, fontSize = 14 }) {
  if (!text) return null

  const lines = text.split('\n')
  const elements = []
  let i = 0

  while (i < lines.length) {
    const raw = lines[i]
    const line = raw.trimEnd()
    const trimmed = line.trim()

    // blank
    if (!trimmed) {
      elements.push(<div key={i} style={{ height: 8 }} />)
      i++; continue
    }

    // h1 — # or ===
    if (/^#\s/.test(line) && !/^##/.test(line)) {
      elements.push(
        <div key={i} style={{
          fontSize: fontSize + 4, fontWeight: 800, color: '#1a2533',
          marginTop: 20, marginBottom: 8,
          paddingBottom: 6, borderBottom: '2px solid #DDE3EA',
        }}>
          {renderInline(line.replace(/^#\s*/, ''))}
        </div>
      )
      i++; continue
    }

    // h2 — ##
    if (/^##\s/.test(line) && !/^###/.test(line)) {
      elements.push(
        <div key={i} style={{
          fontSize: fontSize + 2, fontWeight: 700, color: '#1a2533',
          marginTop: 18, marginBottom: 6,
          paddingBottom: 4, borderBottom: '1.5px solid #DDE3EA',
        }}>
          {renderInline(line.replace(/^##\s*/, ''))}
        </div>
      )
      i++; continue
    }

    // h3 — ###
    if (/^###/.test(line)) {
      elements.push(
        <div key={i} style={{
          fontSize: fontSize + 1, fontWeight: 700, color: '#2D3A4A',
          marginTop: 14, marginBottom: 4,
        }}>
          {renderInline(line.replace(/^###\s*/, ''))}
        </div>
      )
      i++; continue
    }

    // bold-only line acting as label: **Label:** or **Label**
    if (/^\*\*[^*]+\*\*:?\s*$/.test(trimmed)) {
      elements.push(
        <div key={i} style={{
          fontWeight: 700, color: '#1565C0', fontSize: fontSize,
          marginTop: 12, marginBottom: 4,
        }}>
          {trimmed.replace(/\*\*/g, '').replace(/:$/, '')}:
        </div>
      )
      i++; continue
    }

    // horizontal rule
    if (/^(-{3,}|_{3,}|\*{3,})$/.test(trimmed)) {
      elements.push(<hr key={i} style={{ border: 'none', borderTop: '1px solid #DDE3EA', margin: '10px 0' }} />)
      i++; continue
    }

    // bullet
    if (/^[-*+]\s/.test(line)) {
      elements.push(
        <div key={i} style={{ display: 'flex', gap: 10, marginBottom: 4, alignItems: 'flex-start' }}>
          <span style={{ color: '#1565C0', fontWeight: 700, flexShrink: 0, lineHeight: '1.65', marginTop: 1 }}>•</span>
          <span style={{ lineHeight: 1.65 }}>{renderInline(line.replace(/^[-*+]\s/, ''))}</span>
        </div>
      )
      i++; continue
    }

    // numbered list
    if (/^\d+[\).]\s/.test(line)) {
      const num = line.match(/^(\d+)/)[1]
      elements.push(
        <div key={i} style={{ display: 'flex', gap: 10, marginBottom: 4, alignItems: 'flex-start' }}>
          <span style={{ color: '#1565C0', fontWeight: 700, flexShrink: 0, minWidth: 22, lineHeight: '1.65' }}>{num}.</span>
          <span style={{ lineHeight: 1.65 }}>{renderInline(line.replace(/^\d+[\).]\s/, ''))}</span>
        </div>
      )
      i++; continue
    }

    // plain paragraph
    elements.push(
      <div key={i} style={{ lineHeight: 1.7, marginBottom: 2 }}>
        {renderInline(line)}
      </div>
    )
    i++
  }

  return <div style={{ fontSize }}>{elements}</div>
}
