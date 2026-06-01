import { useEffect, useRef, useState } from 'react'
import { chat } from '../api/client'
import MarkdownText from './MarkdownText'

const SUGGESTIONS = [
  'Which product has the best marketing ROI?',
  'What are the top 3 growth opportunities?',
  'Which region should we expand to next?',
  'What are the biggest customer pain points?',
]

const ACCENT = '#2D3A4A'
const BORDER = '#DDE3EA'

export default function ChatPanel({ sessionId, result, messages, setMessages }) {
  const [input, setInput]     = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef()

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const ready = !!sessionId && !!result

  const s = {
    wrap: {
      display: 'flex', flexDirection: 'column',
      height: 'calc(100vh - 130px)',
      background: '#fff', borderRadius: 10,
      boxShadow: '0 1px 4px rgba(0,0,0,0.07)', overflow: 'hidden',
    },
    header: {
      padding: '13px 20px', borderBottom: `1px solid ${BORDER}`,
      fontWeight: 700, fontSize: 14, color: ACCENT, flexShrink: 0,
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
    },
    clearBtn: {
      background: 'none', border: `1px solid ${BORDER}`, borderRadius: 6,
      padding: '3px 10px', fontSize: 12, color: '#78909C', cursor: 'pointer',
    },
    messages: {
      flex: 1, overflow: 'auto', padding: '18px 20px',
      display: 'flex', flexDirection: 'column', gap: 14,
    },
    userRow: { display: 'flex', justifyContent: 'flex-end' },
    aiRow:   { display: 'flex', justifyContent: 'flex-start', gap: 10, alignItems: 'flex-start' },
    avatar:  {
      width: 30, height: 30, borderRadius: '50%', background: ACCENT,
      color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center',
      fontSize: 13, fontWeight: 700, flexShrink: 0, marginTop: 2,
    },
    userBubble: {
      maxWidth: '68%', background: '#1565C0', color: '#fff',
      borderRadius: '16px 16px 4px 16px',
      padding: '10px 16px', fontSize: 13.5, lineHeight: 1.6,
    },
    aiBubble: {
      maxWidth: '74%', background: '#F7F8FA', color: '#263238',
      borderRadius: '16px 16px 16px 4px',
      padding: '12px 16px', border: `1px solid ${BORDER}`,
    },
    thinkingBubble: {
      background: '#F7F8FA', borderRadius: '16px 16px 16px 4px',
      padding: '10px 16px', fontSize: 13, color: '#90A4AE',
      border: `1px solid ${BORDER}`, display: 'flex', gap: 6, alignItems: 'center',
    },
    suggestions: { display: 'flex', flexWrap: 'wrap', gap: 8, padding: '0 20px 14px' },
    chip: {
      background: '#F7F8FA', color: ACCENT,
      border: `1px solid ${BORDER}`,
      borderRadius: 20, padding: '5px 14px', fontSize: 12,
      cursor: 'pointer', fontWeight: 500, transition: 'all 0.15s',
    },
    inputArea: {
      padding: '12px 16px', borderTop: `1px solid ${BORDER}`,
      display: 'flex', gap: 10, flexShrink: 0,
    },
    input: {
      flex: 1, border: `1px solid ${BORDER}`, borderRadius: 8,
      padding: '10px 14px', fontSize: 14, outline: 'none',
      background: ready ? '#fff' : '#FAFAFA', color: '#263238',
    },
    sendBtn: (disabled) => ({
      background: disabled ? '#DDE3EA' : '#1565C0',
      color: disabled ? '#90A4AE' : '#fff',
      border: 'none', borderRadius: 8,
      padding: '10px 22px', fontSize: 14, fontWeight: 600,
      cursor: disabled ? 'not-allowed' : 'pointer',
      transition: 'background 0.15s',
    }),
    empty: {
      color: '#90A4AE', textAlign: 'center',
      paddingTop: 50, fontSize: 14, lineHeight: 2,
    },
  }

  async function send(text) {
    const q = (text || input).trim()
    if (!q || !ready || loading) return
    setInput('')
    setMessages(prev => [...prev, { role: 'user', text: q }])
    setLoading(true)
    try {
      const { answer } = await chat(sessionId, q)
      setMessages(prev => [...prev, { role: 'ai', text: answer }])
    } catch (e) {
      setMessages(prev => [...prev, { role: 'ai', text: 'Error: ' + e.message }])
    }
    setLoading(false)
  }

  const disabled = !ready || loading

  return (
    <div style={s.wrap}>
      <div style={s.header}>
        <span>💬 Product Strategy Q&A</span>
        {messages.length > 0 && (
          <button style={s.clearBtn} onClick={() => setMessages([])}>Clear chat</button>
        )}
      </div>

      <div style={s.messages}>
        {messages.length === 0 && (
          <div style={s.empty}>
            {!ready
              ? 'Complete the analysis first to enable Q&A.'
              : 'Ask anything about your products, sales, customers, or strategy.'}
          </div>
        )}

        {messages.map((m, i) => (
          m.role === 'user'
            ? (
              <div key={i} style={s.userRow}>
                <div style={s.userBubble}>{m.text}</div>
              </div>
            )
            : (
              <div key={i} style={s.aiRow}>
                <div style={s.avatar}>AI</div>
                <div style={s.aiBubble}>
                  <MarkdownText text={m.text} fontSize={13.5} />
                </div>
              </div>
            )
        ))}

        {loading && (
          <div style={s.aiRow}>
            <div style={s.avatar}>AI</div>
            <div style={s.thinkingBubble}>
              <span>●</span><span>●</span><span>●</span>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {messages.length === 0 && ready && (
        <div style={s.suggestions}>
          {SUGGESTIONS.map(q => (
            <button key={q} style={s.chip} onClick={() => send(q)}>{q}</button>
          ))}
        </div>
      )}

      <div style={s.inputArea}>
        <input
          style={s.input}
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && !e.shiftKey && send()}
          placeholder={ready ? 'Ask a question about your data…' : 'Run analysis first…'}
          disabled={!ready}
        />
        <button
          style={s.sendBtn(disabled || !input.trim())}
          onClick={() => send()}
          disabled={disabled || !input.trim()}
        >
          Send
        </button>
      </div>
    </div>
  )
}
