'use client'

import { motion } from 'framer-motion'
import { Mic, Square, Loader2 } from 'lucide-react'

type UIState = 'idle' | 'listening' | 'processing' | 'done' | 'error'

interface Props { state: UIState; onClick: () => void; compact?: boolean }

const cfg = {
  idle:       { label: 'Tap to speak',    ring: '#3b82f6', core: ['#1d4ed8','#3b82f6'] },
  listening:  { label: 'Tap to stop',     ring: '#ef4444', core: ['#b91c1c','#ef4444'] },
  processing: { label: 'Analysing...',    ring: '#f59e0b', core: ['#b45309','#f59e0b'] },
  done:       { label: 'Ask again',       ring: '#3b82f6', core: ['#1d4ed8','#3b82f6'] },
  error:      { label: 'Try again',       ring: '#ef4444', core: ['#b91c1c','#ef4444'] },
}

export default function VoiceOrb({ state, onClick, compact }: Props) {
  const { label, ring, core } = cfg[state]
  const active  = state === 'listening'
  const loading = state === 'processing'

  const orbSize  = compact ? 44 : 72
  const wrapSize = compact ? 52 : 96

  if (compact) {
    return (
      <div className="relative flex items-center justify-center select-none shrink-0" style={{ width: wrapSize, height: wrapSize }}>
        {active && (
          <motion.div
            className="absolute rounded-full pointer-events-none"
            style={{ inset: -4, border: `1.5px solid ${ring}55` }}
            animate={{ scale: [1, 1.5], opacity: [0.5, 0] }}
            transition={{ duration: 1.2, repeat: Infinity, ease: 'easeOut' }}
          />
        )}
        <motion.button
          onClick={onClick}
          disabled={loading}
          whileHover={loading ? {} : { scale: 1.06 }}
          whileTap={loading ? {} : { scale: 0.92 }}
          className="relative z-10 flex items-center justify-center rounded-full disabled:cursor-not-allowed"
          style={{
            width: orbSize, height: orbSize,
            background: `radial-gradient(circle at 38% 32%, ${core[1]}, ${core[0]})`,
            boxShadow: `0 0 16px ${ring}44, 0 4px 16px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.18)`,
            border: `1px solid ${ring}33`,
          }}
        >
          <motion.div
            animate={loading ? { rotate: 360 } : { rotate: 0 }}
            transition={loading ? { duration: 1.4, repeat: Infinity, ease: 'linear' } : {}}
          >
            {active   ? <Square  size={16} fill="white" stroke="white" />  :
             loading  ? <Loader2 size={16} color="white" />                 :
                        <Mic     size={16} color="white" />}
          </motion.div>
        </motion.button>
      </div>
    )
  }

  return (
    <div className="flex flex-col items-center gap-4 select-none">
      <div className="relative flex items-center justify-center" style={{ width: 96, height: 96 }}>

        {/* Outer diffuse glow */}
        <motion.div
          className="absolute rounded-full pointer-events-none"
          style={{ inset: -20, background: `radial-gradient(circle, ${ring}22 0%, transparent 70%)` }}
          animate={active || loading ? { opacity: [0.5, 1, 0.5], scale: [1, 1.15, 1] } : { opacity: 0.3 }}
          transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
        />

        {/* Ripple ring — listening only */}
        {active && (
          <motion.div
            className="absolute rounded-full pointer-events-none"
            style={{ inset: -4, border: `1.5px solid ${ring}55` }}
            animate={{ scale: [1, 1.5], opacity: [0.5, 0] }}
            transition={{ duration: 1.2, repeat: Infinity, ease: 'easeOut' }}
          />
        )}

        {/* Orb */}
        <motion.button
          onClick={onClick}
          disabled={loading}
          whileHover={loading ? {} : { scale: 1.05 }}
          whileTap={loading ? {} : { scale: 0.93 }}
          className="relative z-10 flex items-center justify-center rounded-full disabled:cursor-not-allowed"
          style={{
            width: 72, height: 72,
            background: `radial-gradient(circle at 38% 32%, ${core[1]}, ${core[0]})`,
            boxShadow: `0 0 24px ${ring}55, 0 8px 32px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.18)`,
            border: `1px solid ${ring}33`,
          }}
        >
          <motion.div
            animate={loading ? { rotate: 360 } : { rotate: 0 }}
            transition={loading ? { duration: 1.4, repeat: Infinity, ease: 'linear' } : {}}
          >
            {active   ? <Square  size={24} fill="white" stroke="white" />  :
             loading  ? <Loader2 size={24} color="white" />                 :
                        <Mic     size={24} color="white" />}
          </motion.div>
        </motion.button>
      </div>

      <motion.p
        key={label}
        initial={{ opacity: 0, y: 3 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-xs tracking-wide"
        style={{ color: 'var(--text-muted)' }}
      >
        {label}
      </motion.p>
    </div>
  )
}
