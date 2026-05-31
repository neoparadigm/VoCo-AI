'use client'

import { motion } from 'framer-motion'

type UIState = 'idle' | 'listening' | 'processing' | 'done' | 'error'

const color: Record<UIState, string> = {
  idle: '#1e293b', listening: '#3b82f6', processing: '#f59e0b', done: '#3b82f6', error: '#ef4444',
}

export default function WaveformViz({ state }: { state: UIState }) {
  const N = 36
  const active = state === 'listening' || state === 'processing'
  const c = color[state]

  return (
    <div className="flex items-center justify-center gap-[2px]" style={{ height: 36 }}>
      {Array.from({ length: N }).map((_, i) => {
        const pos  = i / N
        const bell = Math.sin(pos * Math.PI)           // bell curve — taller in centre
        const maxH = 6 + bell * 26
        return (
          <motion.div
            key={i}
            style={{ backgroundColor: c, width: 2, borderRadius: 2 }}
            animate={active
              ? { height: [`2px`, `${maxH * (0.5 + Math.random() * 0.5)}px`, `2px`] }
              : { height: '2px', opacity: 0.15 }
            }
            transition={{
              duration: state === 'listening' ? 0.3 + Math.random() * 0.25 : 0.55,
              delay: Math.abs(i - N / 2) * 0.015,
              repeat: active ? Infinity : 0,
              ease: 'easeInOut',
              repeatType: 'mirror',
            }}
          />
        )
      })}
    </div>
  )
}
