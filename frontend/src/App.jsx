import { useState } from 'react'
import Sidebar from './components/Sidebar'
import Dashboard from './components/Dashboard'
import InsightsPanel from './components/InsightsPanel'
import StrategyPanel from './components/StrategyPanel'
import ChatPanel from './components/ChatPanel'
import ReportPanel from './components/ReportPanel'

const TABS = ['Dashboard', 'Insights', 'Strategy', 'Chat', 'Report']

export default function App() {
  const [tab, setTab]             = useState('Dashboard')
  const [sessionId, setSessionId] = useState(null)
  const [result, setResult]       = useState(null)
  const [nodes, setNodes]         = useState([])
  const [running, setRunning]     = useState(false)
  const [messages, setMessages]   = useState([])

  const s = {
    app:    { display: 'flex', minHeight: '100vh' },
    main:   { flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 },
    header: {
      background: '#2D3A4A', color: '#fff', padding: '0 24px',
      display: 'flex', alignItems: 'center', gap: 32, height: 56, flexShrink: 0,
    },
    brand:  { fontSize: 17, fontWeight: 700, letterSpacing: 0.3, whiteSpace: 'nowrap' },
    nav:    { display: 'flex', gap: 2 },
    navBtn: (active) => ({
      background: active ? 'rgba(255,255,255,0.18)' : 'transparent',
      color: '#fff', border: 'none', padding: '6px 18px',
      borderRadius: 6, fontWeight: active ? 600 : 400,
      fontSize: 14, transition: 'background 0.15s', cursor: 'pointer',
    }),
    content: { flex: 1, padding: 24, overflow: 'auto' },
  }

  const panelProps = { sessionId, result, nodes, running, messages, setMessages }

  return (
    <div style={s.app}>
      <Sidebar
        sessionId={sessionId}
        setSessionId={setSessionId}
        setResult={setResult}
        setNodes={setNodes}
        setRunning={setRunning}
        nodes={nodes}
        running={running}
      />
      <div style={s.main}>
        <div style={s.header}>
          <span style={s.brand}>Product Strategy AI</span>
          <nav style={s.nav}>
            {TABS.map(t => (
              <button key={t} style={s.navBtn(tab === t)} onClick={() => setTab(t)}>{t}</button>
            ))}
          </nav>
        </div>
        <div style={s.content}>
          {tab === 'Dashboard' && <Dashboard  {...panelProps} />}
          {tab === 'Insights'  && <InsightsPanel {...panelProps} />}
          {tab === 'Strategy'  && <StrategyPanel {...panelProps} />}
          {tab === 'Chat'      && <ChatPanel    {...panelProps} />}
          {tab === 'Report'    && <ReportPanel  {...panelProps} />}
        </div>
      </div>
    </div>
  )
}
