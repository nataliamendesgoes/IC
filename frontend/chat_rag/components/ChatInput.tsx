'use client'

import { useRef, useEffect, useState } from 'react'

interface Props {
  onSubmit: (text: string) => void
  loading: boolean
}

export function ChatInput({ onSubmit, loading }: Props) {
  const [value, setValue] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = Math.min(el.scrollHeight, 180) + 'px'
  }, [value])

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      send()
    }
  }

  const send = () => {
    const trimmed = value.trim()
    if (!trimmed || loading) return
    onSubmit(trimmed)
    setValue('')
    if (textareaRef.current) textareaRef.current.style.height = 'auto'
  }

  const disabled = !value.trim() || loading

  return (
    <div style={styles.wrapper}>
      <div style={styles.inputRow}>
        <textarea
          ref={textareaRef}
          rows={1}
          value={value}
          onChange={e => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Descreva o agente MASPy que você quer criar..."
          style={styles.textarea}
          disabled={loading}
        />
        <button
          onClick={send}
          disabled={disabled}
          style={{ ...styles.btn, ...(disabled ? styles.btnDisabled : {}) }}
        >
          {loading ? <Spinner /> : <SendIcon />}
        </button>
      </div>
      <p style={styles.hint}>Enter para enviar · Shift+Enter para nova linha</p>
    </div>
  )
}

function SendIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2.2"
      strokeLinecap="round" strokeLinejoin="round">
      <line x1="22" y1="2" x2="11" y2="13" />
      <polygon points="22 2 15 22 11 13 2 9 22 2" />
    </svg>
  )
}

function Spinner() {
  return (
    <div style={{
      width: '15px', height: '15px',
      border: '2px solid rgba(255,255,255,0.3)',
      borderTopColor: '#fff',
      borderRadius: '50%',
      animation: 'spin 0.7s linear infinite',
    }} />
  )
}

const styles: Record<string, React.CSSProperties> = {
  wrapper: {
    padding: '12px 16px 10px',
    borderTop: '1px solid var(--border)',
    background: 'var(--surface)',
  },
  inputRow: {
    display: 'flex',
    gap: '10px',
    alignItems: 'flex-end',
  },
  textarea: {
    flex: 1,
    resize: 'none',
    border: '1px solid var(--border)',
    borderRadius: '8px',
    padding: '10px 14px',
    fontFamily: 'var(--font-sans)',
    fontSize: '14px',
    color: 'var(--text)',
    background: 'var(--bg)',
    lineHeight: '1.5',
    transition: 'border-color 0.15s',
    overflowY: 'hidden',
  },
  btn: {
    width: '38px',
    height: '38px',
    borderRadius: '8px',
    border: 'none',
    background: 'var(--accent)',
    color: '#fff',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    flexShrink: 0,
    transition: 'opacity 0.15s',
  },
  btnDisabled: {
    opacity: 0.4,
    cursor: 'not-allowed',
  },
  hint: {
    marginTop: '6px',
    fontSize: '11px',
    fontFamily: 'var(--font-mono)',
    color: 'var(--text-muted)',
    letterSpacing: '0.02em',
  },
}