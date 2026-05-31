'use client'

import { useState, useRef, useEffect, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import VoiceOrb from './components/VoiceOrb'
import WaveformViz from './components/WaveformViz'
import OutputPanel from './components/OutputPanel'
import { transcribeAudio, reasonAboutQuestion, speakText, type ReasonResponse } from '@/lib/api'
import { Send, Sun, Moon, Zap } from 'lucide-react'

type UIState = 'idle' | 'listening' | 'processing' | 'done' | 'error'

function getTimeGreeting() {
  const h = new Date().getHours()
  if (h < 12) return 'Good morning'
  if (h < 17) return 'Good afternoon'
  return 'Good evening'
}

const HERO_PROMPTS = [
  { line1: 'What do you want', line2: 'to know today?' },
  { line1: 'Which systems need', line2: 'your attention?' },
  { line1: "What's happening in", line2: 'your enterprise?' },
  { line1: 'Surface an insight,', line2: 'ask anything.' },
]

const MODELS = [
  { id: 'mistral:latest', label: 'Mistral', tag: 'Fast'    },
  { id: 'gemma4:latest',  label: 'Gemma 4', tag: 'Deep'    },
  { id: 'glm4:9b',        label: 'GLM-4',   tag: 'Balanced'},
]

export default function Home() {
  const [state,         setState]         = useState<UIState>('idle')
  const [transcript,    setTranscript]    = useState('')
  const [textInput,     setTextInput]     = useState('')
  const [output,        setOutput]        = useState<ReasonResponse | null>(null)
  const [error,         setError]         = useState('')
  const [isSpeaking,    setIsSpeaking]    = useState(false)
  const [model,         setModel]         = useState(MODELS[0].id)
  const [light,         setLight]         = useState(false)
  const [hoveredModel,  setHoveredModel]  = useState<string | null>(null)

  const [heroIdx,       setHeroIdx]       = useState(0)
  const greeting = useMemo(() => getTimeGreeting(), [])

  const recorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef   = useRef<Blob[]>([])
  const inputRef    = useRef<HTMLInputElement | null>(null)

  useEffect(() => {
    document.documentElement.classList.toggle('light', light)
  }, [light])

  useEffect(() => {
    const t = setInterval(() => setHeroIdx(i => (i + 1) % HERO_PROMPTS.length), 8000)
    return () => clearInterval(t)
  }, [])

  const ask = async (question: string) => {
    setTranscript(question)
    setOutput(null)
    setError('')
    setState('processing')
    try {
      setOutput(await reasonAboutQuestion(question, model))
      setState('done')
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Something went wrong')
      setState('error')
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const q = textInput.trim()
    if (!q || state === 'processing') return
    setTextInput('')
    await ask(q)
  }

  const handleOrb = async () => {
    if (state === 'listening')       stopRec()
    else if (state !== 'processing') await startRec()
  }

  const startRec = async () => {
    try {
      setError(''); setOutput(null); setTranscript(''); setState('listening')
      chunksRef.current = []
      const stream   = await navigator.mediaDevices.getUserMedia({ audio: true })
      const recorder = new MediaRecorder(stream, { mimeType: 'audio/webm' })
      recorderRef.current = recorder
      recorder.ondataavailable = (e) => chunksRef.current.push(e.data)
      recorder.onstop = async () => {
        stream.getTracks().forEach(t => t.stop())
        setState('processing')
        try {
          const blob = new Blob(chunksRef.current, { type: 'audio/webm' })
          const b64  = await new Promise<string>(r => {
            const fr = new FileReader()
            fr.onload = () => r((fr.result as string).split(',')[1])
            fr.readAsDataURL(blob)
          })
          const { transcript: text } = await transcribeAudio(b64)
          if (!text) {
            setError("Couldn't hear that. Try speaking clearly or type your question.")
            setState('error')
            return
          }
          await ask(text)
        } catch (e) {
          setError(e instanceof Error ? e.message : 'Something went wrong')
          setState('error')
        }
      }
      recorder.start()
    } catch {
      setError('Microphone access denied.'); setState('error')
    }
  }

  const stopRec = () => recorderRef.current?.stop()

  const handleSpeak = async () => {
    if (!output?.summary || isSpeaking) return
    setIsSpeaking(true)
    try {
      const { audio_base64 } = await speakText(output.summary)
      const a = new Audio(`data:audio/wav;base64,${audio_base64}`)
      a.onended = () => setIsSpeaking(false)
      await a.play()
    } catch { setIsSpeaking(false) }
  }

  const hasResult = state === 'done' && output

  return (
    <div
      className="min-h-screen flex flex-col"
      style={{
        background: light
          ? 'radial-gradient(ellipse 140% 60% at 50% -5%, #dbeafe 0%, #f0f4fa 55%)'
          : 'radial-gradient(ellipse 140% 60% at 50% -5%, #0f1f3d 0%, #07090f 55%)',
      }}
    >
      {/* ── Top nav ──────────────────────────────────────────────────────── */}
      <nav className="flex items-center justify-between px-6 md:px-10 py-4 shrink-0">
        <motion.div initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }}
                    className="flex items-baseline gap-1.5">
          <span
            className="font-semibold tracking-tight"
            style={{
              fontSize: 22,
              background: light
                ? 'linear-gradient(135deg, #0f172a 30%, #3b82f6)'
                : 'linear-gradient(135deg, #f1f5f9 30%, #93c5fd)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            VoCo
          </span>
          <span
            className="font-semibold text-xs px-1.5 py-0.5 rounded-md"
            style={{ background: 'var(--accent-dim)', color: 'var(--accent)', border: '1px solid var(--accent)33' }}
          >
            AI
          </span>
        </motion.div>

        <div className="flex items-center gap-3">
          {/* Model toggle */}
          <div
            className="inline-flex rounded-full p-[3px] gap-[2px]"
            style={{ background: 'var(--bg-surface)', border: '1px solid var(--border)' }}
            onMouseLeave={() => setHoveredModel(null)}
          >
            {MODELS.map(m => {
              const active = model === m.id
              const pill   = hoveredModel ? hoveredModel === m.id : active
              return (
                <button
                  key={m.id}
                  onClick={() => setModel(m.id)}
                  onMouseEnter={() => setHoveredModel(m.id)}
                  className="relative flex items-center gap-1.5 rounded-full px-3 py-1.5"
                  style={{
                    fontSize: 11,
                    color: pill ? 'var(--accent)' : 'var(--text-muted)',
                    fontWeight: pill ? 600 : 400,
                    background: 'transparent',
                    border: '1px solid transparent',
                    transition: 'color 0.15s',
                    zIndex: 1,
                  }}
                >
                  {pill && (
                    <motion.div
                      layoutId="model-pill"
                      className="absolute inset-0 rounded-full"
                      style={{ background: 'var(--accent-dim)', border: '1px solid var(--accent)33' }}
                      transition={{ type: 'spring', stiffness: 400, damping: 32 }}
                    />
                  )}
                  <span className="relative flex items-center gap-1">
                    {pill && <Zap size={9} />}
                    {m.label}
                    <span style={{ opacity: 0.4, fontSize: 9 }}>{m.tag}</span>
                  </span>
                </button>
              )
            })}
          </div>

          {/* Theme toggle */}
          <button
            onClick={() => setLight(!light)}
            className="rounded-full p-2 transition-all"
            style={{ background: 'var(--bg-surface)', border: '1px solid var(--border)', color: 'var(--text-muted)' }}
          >
            {light ? <Moon size={13} /> : <Sun size={13} />}
          </button>
        </div>
      </nav>

      {/* ── Main content ─────────────────────────────────────────────────── */}
      <main className="flex-1 flex flex-col items-center px-4 md:px-8 pb-12 w-full">

        {/* Hero — shown before first result, collapses after */}
        <AnimatePresence>
          {!hasResult && (
            <motion.div
              key="hero"
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20, height: 0 }}
              transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
              className="text-center mt-[8vh] mb-8"
            >
              {/* Time-based greeting */}
              <p className="text-sm tracking-[0.15em] uppercase mb-4" style={{ color: 'var(--text-muted)' }}>
                {greeting}
              </p>

              {/* Rotating headline */}
              <div style={{ height: 'clamp(80px, 12vw, 130px)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <AnimatePresence mode="wait">
                  <motion.h1
                    key={heroIdx}
                    initial={{ opacity: 0, y: 12, filter: 'blur(4px)' }}
                    animate={{ opacity: 1, y: 0,  filter: 'blur(0px)' }}
                    exit={{    opacity: 0, y: -10, filter: 'blur(4px)' }}
                    transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
                    className="font-semibold tracking-tight text-center"
                    style={{
                      fontSize: 'clamp(34px, 4.5vw, 54px)',
                      background: light
                        ? 'linear-gradient(135deg, #0f172a 30%, #3b82f6)'
                        : 'linear-gradient(135deg, #f1f5f9 30%, #93c5fd)',
                      WebkitBackgroundClip: 'text',
                      WebkitTextFillColor: 'transparent',
                      lineHeight: 1.15,
                    }}
                  >
                    {HERO_PROMPTS[heroIdx].line1}<br />{HERO_PROMPTS[heroIdx].line2}
                  </motion.h1>
                </AnimatePresence>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Transcript / query echo — shown after submit */}
        <AnimatePresence>
          {transcript && hasResult && (
            <motion.p
              initial={{ opacity: 0, y: 4 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-sm mb-6 text-center"
              style={{ color: 'var(--text-muted)', maxWidth: 700, marginTop: hasResult ? '4vh' : 0 }}
            >
              "{transcript}"
            </motion.p>
          )}
        </AnimatePresence>

        {/* ── Input bar ────────────────────────────────────────────────── */}
        <motion.div
          layout
          className="w-full"
          style={{ maxWidth: 780 }}
          transition={{ type: 'spring', stiffness: 300, damping: 30 }}
        >
          <motion.div
            initial={{ opacity: 0, y: 16, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
            className="rounded-2xl p-5"
            style={{
              background: 'var(--bg-surface)',
              backdropFilter: 'blur(24px)',
              border: '1px solid var(--border)',
              boxShadow: light ? '0 8px 32px rgba(0,0,0,0.08)' : '0 20px 60px rgba(0,0,0,0.5)',
            }}
          >
            {/* Waveform */}
            <AnimatePresence>
              {(state === 'listening' || state === 'processing') && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  style={{ overflow: 'hidden', marginBottom: 16 }}
                >
                  <WaveformViz state={state} />
                </motion.div>
              )}
            </AnimatePresence>

            {/* Row: orb + input + send */}
            <div className="flex items-center gap-4">
              <VoiceOrb state={state} onClick={handleOrb} compact />

              <form onSubmit={handleSubmit} className="relative flex-1">
                <input
                  ref={inputRef}
                  type="text"
                  value={textInput}
                  onChange={e => setTextInput(e.target.value)}
                  placeholder="Ask anything about your enterprise data…"
                  disabled={state === 'processing'}
                  className="w-full rounded-xl px-4 py-3 pr-11 text-sm outline-none disabled:opacity-40 transition-all"
                  style={{
                    background: 'var(--bg-input)',
                    border: '1px solid var(--border)',
                    color: 'var(--text-primary)',
                    caretColor: 'var(--accent)',
                  }}
                  onFocus={e => e.target.style.borderColor = 'var(--accent)'}
                  onBlur={e => e.target.style.borderColor = 'var(--border)'}
                />
                <button
                  type="submit"
                  disabled={!textInput.trim() || state === 'processing'}
                  className="absolute right-2.5 top-1/2 -translate-y-1/2 p-1 rounded-lg transition-opacity disabled:opacity-25"
                  style={{ color: 'var(--accent)' }}
                >
                  <Send size={14} />
                </button>
              </form>
            </div>

            {/* Transcript (pre-result) / error */}
            <AnimatePresence>
              {transcript && !hasResult && (
                <motion.p
                  initial={{ opacity: 0, y: 3 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="text-xs text-center mt-3"
                  style={{ color: 'var(--text-muted)' }}
                >
                  "{transcript}"
                </motion.p>
              )}
              {error && (
                <motion.p
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="text-xs text-center mt-3"
                  style={{ color: '#ef4444' }}
                >
                  {error}
                </motion.p>
              )}
            </AnimatePresence>
          </motion.div>
        </motion.div>

        {/* ── Results ──────────────────────────────────────────────────── */}
        <AnimatePresence>
          {hasResult && (
            <motion.div
              key="result"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.45, ease: [0.16, 1, 0.3, 1] }}
              className="w-full mt-6"
              style={{ maxWidth: 780 }}
            >
              <div
                className="rounded-2xl overflow-hidden"
                style={{
                  background: 'var(--bg-surface)',
                  backdropFilter: 'blur(24px)',
                  border: '1px solid var(--border)',
                  boxShadow: light ? '0 8px 32px rgba(0,0,0,0.07)' : '0 20px 48px rgba(0,0,0,0.45)',
                }}
              >
                <div className="px-7 py-6">
                  <OutputPanel output={output!} onSpeak={handleSpeak} isSpeaking={isSpeaking} lightMode={light} />
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Footer */}
        {!hasResult && (
          <p className="mt-auto pt-12 text-center" style={{ fontSize: 10, color: 'var(--text-muted)', opacity: 0.3, letterSpacing: '0.1em' }}>
            LOCAL &nbsp;·&nbsp; ZERO-COST &nbsp;·&nbsp; FULLY PRIVATE
          </p>
        )}
      </main>
    </div>
  )
}
