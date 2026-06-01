const BASE = 'http://localhost:8000'

export async function listExistingFiles() {
  const res = await fetch(`${BASE}/api/load-existing`)
  if (!res.ok) throw new Error('Failed to list files')
  return res.json()
}

export async function loadExistingFiles(filenames) {
  const res = await fetch(`${BASE}/api/load-existing`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(filenames),
  })
  if (!res.ok) throw new Error('Failed to load existing files')
  return res.json()
}

export async function uploadFiles(files) {
  const form = new FormData()
  files.forEach(f => form.append('files', f))
  const res = await fetch(`${BASE}/api/upload`, { method: 'POST', body: form })
  if (!res.ok) throw new Error('Upload failed: ' + res.statusText)
  return res.json()
}

export function streamAnalysis(sessionId, onNode, onDone, onError) {
  const es = new EventSource(`${BASE}/api/analyze/${sessionId}`)
  es.onmessage = (e) => {
    try {
      const data = JSON.parse(e.data)
      if (data.status === 'done') {
        es.close()
        onDone(data.result)
      } else {
        onNode(data)
      }
    } catch (err) {
      console.error('Parse error', err)
    }
  }
  es.onerror = (err) => {
    es.close()
    if (onError) onError(err)
  }
  return es
}

export async function chat(sessionId, question) {
  const res = await fetch(`${BASE}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, question }),
  })
  if (!res.ok) throw new Error('Chat failed: ' + res.statusText)
  return res.json()
}

export function reportUrl(sessionId) {
  return `${BASE}/api/report/${sessionId}`
}
