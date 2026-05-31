'use client'

import { motion } from 'framer-motion'
import { Mic, Square, Loader2 } from 'lucide-react'

type UIState = 'idle' | 'listening' | 'processing' | 'done' | 'error'

interface Props {
  state: UIState
  onClick: () => void
}

const config = {
  idle:       { bg: 'bg-blue-600 hover:bg-blue-500',  icon: Mic,     label: 'Click to speak',  pulse: false },
  listening:  { bg: 'bg-red-600 hover:bg-red-500',    icon: Square,  label: 'Click to stop',   pulse: true  },
  processing: { bg: 'bg-yellow-600',                  icon: Loader2, label: 'Processing...',   pulse: false },
  done:       { bg: 'bg-blue-600 hover:bg-blue-500',  icon: Mic,     label: 'Ask another',     pulse: false },
  error:      { bg: 'bg-red-700 hover:bg-red-600',    icon: Mic,     label: 'Try again',       pulse: false },
}

export default function VoiceButton({ state, onClick }: Props) {
  const { bg, icon: Icon, label, pulse } = config[state]
  const disabled = state === 'processing'

  return (
    <div className="flex flex-col items-center gap-4">
      <motion.button
        onClick={onClick}
        disabled={disabled}
        whileHover={disabled ? {} : { scale: 1.05 }}
        whileTap={disabled ? {} : { scale: 0.95 }}
        className={`
          relative w-20 h-20 rounded-full flex items-center justify-center
          text-white shadow-lg transition-colors duration-200 cursor-pointer
          disabled:cursor-not-allowed disabled:opacity-60 ${bg}
        `}
      >
        {pulse && (
          <motion.div
            className="absolute inset-0 rounded-full bg-red-500 opacity-30"
            animate={{ scale: [1, 1.4, 1], opacity: [0.3, 0, 0.3] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          />
        )}
        <Icon
          size={32}
          className={state === 'processing' ? 'animate-spin' : ''}
        />
      </motion.button>
      <p className="text-sm text-slate-400">{label}</p>
    </div>
  )
}
