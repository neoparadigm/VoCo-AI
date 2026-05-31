'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Copy, Volume2, CheckCircle, AlertTriangle, ChevronRight } from 'lucide-react'
import type { ReasonResponse } from '@/lib/api'

interface Props {
  output: ReasonResponse
  onSpeak: () => void
  isSpeaking: boolean
  lightMode?: boolean
}

function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <p className="text-xs font-semibold uppercase tracking-[0.12em] mb-2"
       style={{ color: 'var(--text-muted)', fontSize: 10 }}>
      {children}
    </p>
  )
}

function Divider() {
  return <div style={{ height: 1, background: 'var(--bg-divider)', margin: '20px 0' }} />
}

export default function OutputPanel({ output, onSpeak, isSpeaking }: Props) {
  const [showReasoning, setShowReasoning] = useState(false)
  const [copied, setCopied] = useState(false)

  const copy = () => {
    navigator.clipboard.writeText(`${output.summary}\n\nRoot Cause: ${output.root_cause}`)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const pct  = Math.round(output.confidence_score * 100)
  const confColor = pct >= 85 ? '#22c55e' : pct >= 60 ? '#f59e0b' : '#ef4444'

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
    >
        {/* Header bar */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <span className="text-xs font-medium" style={{ color: 'var(--text-muted)' }}>Analysis complete</span>
            <span className="text-xs px-2 py-0.5 rounded-full font-mono"
                  style={{ background: `${confColor}15`, color: confColor, border: `1px solid ${confColor}30` }}>
              {pct}% confidence
            </span>
          </div>
          <div className="flex items-center gap-3">
            <button onClick={copy} style={{ color: 'var(--text-muted)' }}
                    className="hover:opacity-100 opacity-50 transition-opacity">
              {copied ? <CheckCircle size={14} color="#22c55e" /> : <Copy size={14} />}
            </button>
            <button onClick={onSpeak} style={{ color: isSpeaking ? 'var(--accent)' : 'var(--text-muted)' }}
                    className="hover:opacity-100 opacity-50 transition-opacity">
              <Volume2 size={14} />
            </button>
          </div>
        </div>

        {/* Body */}
        <div>

          {/* Summary */}
          {output.summary && (
            <>
              <SectionLabel>Summary</SectionLabel>
              <p className="leading-relaxed text-sm" style={{ color: 'var(--text-primary)', lineHeight: 1.7 }}>
                {output.summary}
              </p>
            </>
          )}

          {/* Root cause */}
          {output.root_cause && (
            <>
              <Divider />
              <SectionLabel>Root Cause</SectionLabel>
              <p className="text-sm font-medium leading-relaxed"
                 style={{ color: 'var(--accent)', lineHeight: 1.65 }}>
                {output.root_cause}
              </p>
            </>
          )}

          {/* Contributing factors */}
          {output.contributing_factors?.length > 0 && (
            <>
              <Divider />
              <SectionLabel>Contributing Factors</SectionLabel>
              <ul className="space-y-2.5">
                {output.contributing_factors.map((f, i) => (
                  <li key={i} className="flex items-start gap-2.5 text-sm"
                      style={{ color: 'var(--text-body)' }}>
                    <span style={{ color: '#f59e0b', marginTop: 4, flexShrink: 0, fontSize: 8 }}>◆</span>
                    {f}
                  </li>
                ))}
              </ul>
            </>
          )}

          {/* Actions */}
          {output.actions?.length > 0 && (
            <>
              <Divider />
              <SectionLabel>Recommended Actions</SectionLabel>
              <ol className="space-y-2.5">
                {output.actions.map((a, i) => (
                  <li key={i} className="flex items-start gap-3 text-sm"
                      style={{ color: 'var(--text-body)' }}>
                    <span className="shrink-0 rounded-full flex items-center justify-center text-xs font-semibold mt-0.5"
                          style={{ width: 18, height: 18, background: 'var(--accent-dim)',
                                   color: 'var(--accent)', border: '1px solid var(--accent)33' }}>
                      {i + 1}
                    </span>
                    {a.action}
                  </li>
                ))}
              </ol>
            </>
          )}

          {/* Business impact */}
          {output.business_impact && (
            <>
              <Divider />
              <div className="flex items-start gap-2.5 rounded-xl px-3.5 py-3"
                   style={{ background: 'rgba(239,68,68,0.06)', border: '1px solid rgba(239,68,68,0.12)' }}>
                <AlertTriangle size={13} color="#ef4444" style={{ marginTop: 2, flexShrink: 0 }} />
                <p className="text-xs leading-relaxed" style={{ color: 'var(--text-body)' }}>
                  <span style={{ color: '#ef4444', fontWeight: 600 }}>Risk: </span>
                  {output.business_impact}
                </p>
              </div>
            </>
          )}

          {/* Reasoning chain — collapsible */}
          {output.reasoning_chain?.length > 0 && (
            <>
              <Divider />
              <button
                onClick={() => setShowReasoning(!showReasoning)}
                className="flex items-center gap-2 w-full text-left transition-opacity opacity-50 hover:opacity-80"
              >
                <ChevronRight
                  size={13}
                  style={{ color: 'var(--text-muted)',
                           transform: showReasoning ? 'rotate(90deg)' : 'none',
                           transition: 'transform 0.2s' }}
                />
                <span className="text-xs" style={{ color: 'var(--text-muted)' }}>
                  {showReasoning ? 'Hide' : 'Show'} reasoning chain
                </span>
              </button>

              <AnimatePresence>
                {showReasoning && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.25 }}
                    style={{ overflow: 'hidden' }}
                  >
                    <div className="mt-4 space-y-3">
                      {output.reasoning_chain.map((s, i) => (
                        <div key={i} className="flex gap-3 text-xs">
                          <span className="font-bold shrink-0 w-20 pt-0.5"
                                style={{ color: 'var(--accent)', opacity: 0.8 }}>
                            {s.step}
                          </span>
                          <span style={{ color: 'var(--text-muted)', lineHeight: 1.6 }}>{s.detail}</span>
                        </div>
                      ))}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </>
          )}

        </div>
    </motion.div>
  )
}
