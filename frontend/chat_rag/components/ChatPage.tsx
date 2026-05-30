'use client'

import { useEffect, useRef, useState } from 'react'
import { useChat } from '@/hooks/useChat'
import { Message } from '@/components/Message'
import { ChatInput } from '@/components/ChatInput'
import { TypingIndicator } from '@/components/TypingIndicator'
import { checkHealth } from '@/lib/api'

const SUGGESTIONS = [
  'Crie dois agentes que se comunicam via mensagem',
  'Agente com plano reativo a um objetivo específico',
  'Sistema de negociação com contract-net protocol',
  'Agente que insere e consulta crenças',
]

const PIPELINE_STEPS = ['Retriever', 'Gerador', 'Revisor', 'Sanitizador']

export default function ChatPage() {
  const { messages, loading, error, submit, clear } = useChat()
  const [online, setOnline] = useState<boolean | null>(null)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    checkHealth().then(setOnline)
    const interval = setInterval(() => checkHealth().then(setOnline), 30_000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const isEmpty = messages.length === 0

  const statusColor =
    online === null ? '#aaa' : online ? '#22c55e' : '#ef4444'
  const statusText =
    online === null ? 'verificando...' : online ? 'API conectada' : 'API offline'

  return (
    <div style={styles.layout}>
      {/* ── Sidebar ── */}
      <aside style={styles.sidebar}>
        <div style={styles.brand}>
          <span style={styles.brandIcon}>{'{ }'}</span>
          <div>
            <div style={styles.brandName}>MASPy</div>
            <div style={styles.brandSub}>Code Generator</div>
          </div>
        </div>

        <div style={styles.sideSection}>
          <div style={styles.sideLabel}>status</div>
          <div style={styles.statusRow}>
            <span style={{ ...styles.statusDot, background: statusColor }} />
            <span style={styles.statusText}>{statusText}</span>
          </div>
        </div>

        <div style={styles.sideSection}>
          <div style={styles.sideLabel}>modelos</div>
          {['qwen2.5-coder:7b', 'llama3 (revisor)', 'bge-m3 (embed)'].map(m => (
            <div key={m} style={styles.modelTag}>{m}</div>
          ))}
        </div>

        <div style={styles.sideSection}>
          <div style={styles.sideLabel}>pipeline</div>
          <div style={styles.pipeline}>
            {PIPELINE_STEPS.map((step, i) => (
              <div key={step}>
                <div style={styles.pipelineStep}>{step}</div>
                {i < PIPELINE_STEPS.length - 1 && (
                  <div style={styles.pipelineArrow}>↓</div>
                )}
              </div>
            ))}
          </div>
        </div>

        <div style={{ flex: 1 }} />

        {messages.length > 0 && (
          <button onClick={clear} style={styles.clearBtn}>
            limpar conversa
          </button>
        )}
      </aside>

      {/* ── Chat ── */}
      <main style={styles.main}>
        <div style={styles.messages}>
          {isEmpty ? (
            <div style={styles.empty}>
              <div style={styles.emptyIcon}>{'<MASPy />'}</div>
              <h2 style={styles.emptyTitle}>O que você quer criar?</h2>
              <p style={styles.emptySubtitle}>
                Descreva em português o sistema multiagente e o código será gerado automaticamente.
              </p>
              <div style={styles.suggestions}>
                {SUGGESTIONS.map(s => (
                  <button key={s} onClick={() => submit(s)} style={styles.suggestion}>
                    {s}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <>
              {messages.map(msg => (
                <Message key={msg.id} {...msg} />
              ))}
              {loading && <TypingIndicator />}
              {error && (
                <div style={styles.errorBox}>
                  <strong>Erro:</strong> {error}
                </div>
              )}
            </>
          )}
          <div ref={bottomRef} />
        </div>

        <ChatInput onSubmit={submit} loading={loading} />
      </main>
    </div>
  )
}

const styles: Record<string, React.CSSProperties> = {
  layout: {
    display: 'flex',
    height: '100vh',
    overflow: 'hidden',
  },
  sidebar: {
    width: '220px',
    flexShrink: 0,
    background: 'var(--surface)',
    borderRight: '1px solid var(--border)',
    display: 'flex',
    flexDirection: 'column',
    padding: '20px 16px',
    gap: '6px',
  },
  brand: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    marginBottom: '20px',
  },
  brandIcon: {
    fontFamily: 'var(--font-mono)',
    fontSize: '20px',
    color: 'var(--accent)',
    fontWeight: 500,
  },
  brandName: {
    fontFamily: 'var(--font-mono)',
    fontSize: '14px',
    fontWeight: 500,
    color: 'var(--text)',
    lineHeight: 1.2,
  },
  brandSub: {
    fontSize: '11px',
    color: 'var(--text-muted)',
    lineHeight: 1.2,
  },
  sideSection: { marginBottom: '18px' },
  sideLabel: {
    fontFamily: 'var(--font-mono)',
    fontSize: '10px',
    textTransform: 'uppercase',
    letterSpacing: '0.1em',
    color: 'var(--text-muted)',
    marginBottom: '7px',
  },
  statusRow: { display: 'flex', alignItems: 'center', gap: '7px' },
  statusDot: { width: '7px', height: '7px', borderRadius: '50%', flexShrink: 0 },
  statusText: { fontSize: '12px', fontFamily: 'var(--font-mono)', color: 'var(--text)' },
  modelTag: {
    fontFamily: 'var(--font-mono)',
    fontSize: '11px',
    color: 'var(--accent)',
    background: 'var(--accent-soft)',
    border: '1px solid #c6e0d2',
    borderRadius: '4px',
    padding: '3px 8px',
    marginBottom: '4px',
    display: 'inline-block',
  },
  pipeline: { display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: '1px' },
  pipelineStep: {
    fontFamily: 'var(--font-mono)',
    fontSize: '12px',
    color: 'var(--text)',
    background: 'var(--bg)',
    border: '1px solid var(--border)',
    borderRadius: '4px',
    padding: '3px 10px',
  },
  pipelineArrow: {
    fontFamily: 'var(--font-mono)',
    fontSize: '11px',
    color: 'var(--text-muted)',
    paddingLeft: '12px',
  },
  clearBtn: {
    background: 'none',
    border: '1px solid var(--border)',
    borderRadius: '6px',
    fontFamily: 'var(--font-mono)',
    fontSize: '11px',
    color: 'var(--text-muted)',
    padding: '7px 10px',
    cursor: 'pointer',
    width: '100%',
    textAlign: 'center',
  },
  main: { flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', background: 'var(--bg)' },
  messages: { flex: 1, overflowY: 'auto', padding: '28px 32px' },
  empty: {
    height: '100%',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    textAlign: 'center',
    gap: '10px',
    paddingBottom: '40px',
  },
  emptyIcon: {
    fontFamily: 'var(--font-mono)',
    fontSize: '28px',
    color: 'var(--accent)',
    marginBottom: '6px',
    letterSpacing: '-0.02em',
  },
  emptyTitle: { fontSize: '22px', fontWeight: 400, color: 'var(--text)' },
  emptySubtitle: { fontSize: '14px', color: 'var(--text-muted)', maxWidth: '400px', lineHeight: 1.6, marginBottom: '10px' },
  suggestions: { display: 'flex', flexWrap: 'wrap', gap: '8px', justifyContent: 'center', maxWidth: '520px', marginTop: '4px' },
  suggestion: {
    background: 'var(--surface)',
    border: '1px solid var(--border)',
    borderRadius: '8px',
    padding: '8px 14px',
    fontSize: '13px',
    color: 'var(--text)',
    cursor: 'pointer',
    textAlign: 'left',
    lineHeight: 1.4,
  },
  errorBox: {
    background: '#fef2f2',
    border: '1px solid #fecaca',
    color: '#b91c1c',
    borderRadius: '8px',
    padding: '10px 14px',
    fontSize: '13px',
    marginBottom: '16px',
  },
}