const BACKEND = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8001'

export interface ReasonResponse {
  summary: string
  root_cause: string
  contributing_factors: string[]
  reasoning_chain: { step: string; detail: string }[]
  actions: { action: string }[]
  confidence_score: number
  business_impact: string
  raw_output: string
}

export async function transcribeAudio(audioBase64: string): Promise<{ transcript: string; confidence: number }> {
  const res = await fetch(`${BACKEND}/transcribe`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ audio_base64: audioBase64 })
  })
  if (!res.ok) throw new Error(`Transcribe failed: ${res.status}`)
  return res.json()
}

export async function reasonAboutQuestion(question: string, model?: string): Promise<ReasonResponse> {
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), 5 * 60 * 1000)
  try {
    const res = await fetch(`${BACKEND}/reason`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, model }),
      signal: controller.signal
    })
    if (!res.ok) throw new Error(`Reason failed: ${res.status}`)
    return res.json()
  } catch (err: unknown) {
    if (err instanceof Error && err.name === 'AbortError') throw new Error('Analysis timed out. Try a faster model.')
    throw err
  } finally {
    clearTimeout(timeout)
  }
}

export async function speakText(text: string): Promise<{ audio_base64: string }> {
  const res = await fetch(`${BACKEND}/speak`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text })
  })
  if (!res.ok) throw new Error(`Speak failed: ${res.status}`)
  return res.json()
}
