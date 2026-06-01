import { useEffect, useRef, useState } from 'react'
import { uploadFiles, streamAnalysis, listExistingFiles, loadExistingFiles } from '../api/client'

const PIPELINE = [
  { key: 'ingest',             label: 'Ingest Data' },
  { key: 'customer_feedback',  label: 'Customer Feedback' },
  { key: 'sales_performance',  label: 'Sales Performance' },
  { key: 'market_opportunity', label: 'Market Opportunity' },
  { key: 'feature_priority',   label: 'Feature Priority' },
  { key: 'strategy',           label: 'Strategy & SWOT' },
  { key: 'report',             label: 'PDF Report' },
]

export default function Sidebar({ sessionId, setSessionId, setResult, setNodes, setRunning, nodes, running }) {
  const [files, setFiles]         = useState([])
  const [uploading, setUploading] = useState(false)
  const [error, setError]         = useState('')
  const [existingFiles, setExistingFiles] = useState([])
  const [selectedExisting, setSelectedExisting] = useState([])
  const inputRef = useRef()

  useEffect(() => {
    listExistingFiles()
      .then(d => setExistingFiles(d.files || []))
      .catch(() => {})
  }, [])

  const completedKeys = new Set(nodes.map(n => n.key))
  const currentIdx    = nodes.length
  const canRun        = (files.length > 0 || selectedExisting.length > 0) && !running && !uploading

  function toggleExisting(name) {
    setSelectedExisting(prev =>
      prev.includes(name) ? prev.filter(f => f !== name) : [...prev, name]
    )
  }

  const s = {
    sidebar: {
      width: 256, background: '#0D1B2A', color: '#CFD8DC',
      padding: '20px 16px', display: 'flex', flexDirection: 'column',
      gap: 18, flexShrink: 0, minHeight: '100vh',
    },
    sectionLabel: { fontSize: 11, fontWeight: 700, color: '#546E7A', textTransform: 'uppercase', letterSpacing: 1.2, marginBottom: 8 },
    dropzone: {
      border: '1.5px dashed #37474F', borderRadius: 8, padding: '14px 10px',
      textAlign: 'center', cursor: 'pointer', fontSize: 12, color: '#78909C',
      background: 'rgba(255,255,255,0.03)', lineHeight: 1.6,
    },
    fileItem: { fontSize: 12, color: '#66BB6A', display: 'flex', alignItems: 'center', gap: 6, marginTop: 6 },
    btn: (disabled) => ({
      background: disabled ? '#263238' : '#1565C0',
      color: disabled ? '#546E7A' : '#fff',
      border: 'none', borderRadius: 8, padding: '10px 0',
      width: '100%', fontSize: 14, fontWeight: 600,
      cursor: disabled ? 'not-allowed' : 'pointer',
      transition: 'background 0.2s',
    }),
    divider: { border: 'none', borderTop: '1px solid #1C2D3A', margin: '2px 0' },
    nodeRow: (done, active) => ({
      display: 'flex', alignItems: 'center', gap: 9,
      fontSize: 12, padding: '5px 0',
      color: done ? '#66BB6A' : active ? '#90CAF9' : '#546E7A',
      fontWeight: active ? 600 : 400,
    }),
    dot: (done, active) => ({
      width: 7, height: 7, borderRadius: '50%', flexShrink: 0,
      background: done ? '#66BB6A' : active ? '#90CAF9' : '#263238',
      boxShadow: active ? '0 0 6px #90CAF9' : 'none',
    }),
    error: { fontSize: 12, color: '#EF9A9A', marginTop: 6 },
    sessionLabel: { fontSize: 11, color: '#37474F', marginTop: 'auto', wordBreak: 'break-all' },
  }

  async function startStream(session_id) {
    setRunning(true)
    streamAnalysis(
      session_id,
      (nodeData) => setNodes(prev => [...prev, { key: nodeData.node, label: nodeData.label }]),
      (finalResult) => { setResult(finalResult); setRunning(false) },
      () => { setError('Stream error'); setRunning(false) }
    )
  }

  async function handleRun() {
    const hasNew      = files.length > 0
    const hasExisting = selectedExisting.length > 0
    if (!hasNew && !hasExisting) return
    setError('')
    setNodes([])
    setResult(null)
    setUploading(true)
    try {
      let session_id
      if (hasNew) {
        const res = await uploadFiles(files)
        session_id = res.session_id
      } else {
        const res = await loadExistingFiles(selectedExisting)
        session_id = res.session_id
      }
      setSessionId(session_id)
      setUploading(false)
      startStream(session_id)
    } catch (e) {
      setError(e.message)
      setUploading(false)
      setRunning(false)
    }
  }

  return (
    <div style={s.sidebar}>
      <div>
        <div style={s.sectionLabel}>Upload Data</div>
        <div style={s.dropzone} onClick={() => inputRef.current.click()}>
          Drop CSV / PDF / TXT<br />or click to browse
        </div>
        <input
          ref={inputRef} type="file" multiple accept=".csv,.pdf,.txt"
          style={{ display: 'none' }}
          onChange={e => setFiles(Array.from(e.target.files))}
        />
        {files.map(f => (
          <div key={f.name} style={s.fileItem}>✓ {f.name}</div>
        ))}
        {error && <div style={s.error}>{error}</div>}
      </div>

      {existingFiles.length > 0 && (
        <div>
          <div style={s.sectionLabel}>Data Folder Files</div>
          {existingFiles.map(f => (
            <div key={f} style={{ ...s.fileItem, cursor: 'pointer' }} onClick={() => toggleExisting(f)}>
              <span style={{ color: selectedExisting.includes(f) ? '#66BB6A' : '#546E7A' }}>
                {selectedExisting.includes(f) ? '✓' : '○'}
              </span>
              {f}
            </div>
          ))}
        </div>
      )}

      <button
        style={s.btn(!canRun)}
        onClick={handleRun}
        disabled={!canRun}
      >
        {uploading ? 'Uploading…' : running ? 'Analyzing…' : '▶  Run Analysis'}
      </button>

      <hr style={s.divider} />

      <div>
        <div style={s.sectionLabel}>Agent Pipeline</div>
        {PIPELINE.map((node, idx) => {
          const done   = completedKeys.has(node.key)
          const active = running && idx === currentIdx
          return (
            <div key={node.key} style={s.nodeRow(done, active)}>
              <div style={s.dot(done, active)} />
              {node.label}
              {active && <span style={{ marginLeft: 'auto', fontSize: 10 }}>⏳</span>}
              {done   && <span style={{ marginLeft: 'auto', fontSize: 10 }}>✓</span>}
            </div>
          )
        })}
      </div>

      {sessionId && (
        <div style={s.sessionLabel}>Session: {sessionId}</div>
      )}
    </div>
  )
}
