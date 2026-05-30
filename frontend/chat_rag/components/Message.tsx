'use client'

import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism'
import type { Message as MessageType } from '@/hooks/useChat'

function CopyButton({ code }: { code: string }) {
  const [copied, setCopied] = useState(false)
  const copy = () => {
    navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }
  return (
    <button onClick={copy} style={styles.copyBtn}>
      {copied ? '✓ copiado' : 'copiar'}
    </button>
  )
}

function CodeBlock({ children, className }: { children: string; className?: string }) {
  const lang = (className ?? '').replace('language-', '') || 'python'
  const code = String(children).replace(/\n$/, '')
  return (
    <div style={styles.codeWrapper}>
      <div style={styles.codeHeader}>
        <span style={styles.codeLang}>{lang}</span>
        <CopyButton code={code} />
      </div>
      <SyntaxHighlighter
        language={lang}
        style={oneLight}
        customStyle={styles.highlighter as React.CSSProperties}
        showLineNumbers
      >
        {code}
      </SyntaxHighlighter>
    </div>
  )
}

export function Message({ role, content, sources }: MessageType) {
  const isUser = role === 'user'

  return (
    <div style={{ ...styles.wrapper, justifyContent: isUser ? 'flex-end' : 'flex-start' }}>
      {!isUser && <div style={styles.avatar}>M</div>}

      <div style={{ ...styles.bubble, ...(isUser ? styles.userBubble : styles.aiBubble) }}>
        {isUser ? (
          <p style={styles.userText}>{content}</p>
        ) : (
          <div style={styles.markdown}>
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                code(props) {
                  const { children, className, ...rest } = props
                  const isInline = !className
                  if (isInline) {
                    return <code style={styles.inlineCode} {...rest}>{children}</code>
                  }
                  return (
                    <CodeBlock className={className}>
                      {String(children)}
                    </CodeBlock>
                  )
                },
                p: ({ children }) => <p style={styles.p}>{children}</p>,
                ul: ({ children }) => <ul style={styles.ul}>{children}</ul>,
                ol: ({ children }) => <ol style={styles.ol}>{children}</ol>,
                li: ({ children }) => <li style={styles.li}>{children}</li>,
                strong: ({ children }) => <strong style={styles.strong}>{children}</strong>,
              }}
            >
              {content}
            </ReactMarkdown>

            {sources.length > 0 && (
              <div style={styles.sources}>
                <span style={styles.sourcesLabel}>fontes</span>
                {sources.map((s, i) => (
                  <span key={i} style={styles.source}>{s}</span>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {isUser && <div style={{ ...styles.avatar, ...styles.userAvatar }}>U</div>}
    </div>
  )
}

const styles: Record<string, React.CSSProperties> = {
  wrapper: {
    display: 'flex',
    alignItems: 'flex-end',
    gap: '10px',
    marginBottom: '20px',
    animation: 'fadeUp 0.25s ease',
  },
  avatar: {
    width: '30px',
    height: '30px',
    borderRadius: '50%',
    background: 'var(--accent)',
    color: '#fff',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '12px',
    fontFamily: 'var(--font-mono)',
    fontWeight: 500,
    flexShrink: 0,
  },
  userAvatar: {
    background: 'var(--user-bg)',
  },
  bubble: {
    maxWidth: '78%',
    borderRadius: 'var(--radius)',
    padding: '12px 16px',
    boxShadow: 'var(--shadow)',
  },
  aiBubble: {
    background: 'var(--surface)',
    border: '1px solid var(--border)',
    borderBottomLeftRadius: '3px',
  },
  userBubble: {
    background: 'var(--user-bg)',
    borderBottomRightRadius: '3px',
  },
  userText: {
    color: 'var(--user-text)',
    fontSize: '14px',
    lineHeight: '1.55',
  },
  markdown: {
    fontSize: '14px',
    lineHeight: '1.6',
    color: 'var(--text)',
  },
  p:      { marginBottom: '8px' },
  ul:     { paddingLeft: '18px', marginBottom: '8px' },
  ol:     { paddingLeft: '18px', marginBottom: '8px' },
  li:     { marginBottom: '4px' },
  strong: { fontWeight: 500 },
  inlineCode: {
    fontFamily: 'var(--font-mono)',
    fontSize: '12.5px',
    background: 'var(--code-bg)',
    padding: '1px 5px',
    borderRadius: '4px',
    border: '1px solid var(--border)',
  },
  codeWrapper: {
    borderRadius: '7px',
    overflow: 'hidden',
    border: '1px solid var(--border)',
    marginTop: '8px',
    marginBottom: '8px',
  },
  codeHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    background: 'var(--code-bg)',
    padding: '5px 12px',
    borderBottom: '1px solid var(--border)',
  },
  codeLang: {
    fontFamily: 'var(--font-mono)',
    fontSize: '11px',
    color: 'var(--text-muted)',
    textTransform: 'uppercase',
    letterSpacing: '0.06em',
  },
  copyBtn: {
    background: 'none',
    border: '1px solid var(--border)',
    borderRadius: '4px',
    fontFamily: 'var(--font-mono)',
    fontSize: '11px',
    color: 'var(--text-muted)',
    padding: '2px 8px',
    cursor: 'pointer',
  },
  highlighter: {
    margin: 0,
    borderRadius: 0,
    fontSize: '13px',
    background: '#faf9f6',
  },
  sources: {
    marginTop: '10px',
    paddingTop: '8px',
    borderTop: '1px solid var(--border-soft)',
    display: 'flex',
    flexWrap: 'wrap',
    gap: '6px',
    alignItems: 'center',
  },
  sourcesLabel: {
    fontFamily: 'var(--font-mono)',
    fontSize: '11px',
    color: 'var(--text-muted)',
    textTransform: 'uppercase',
    letterSpacing: '0.06em',
    marginRight: '4px',
  },
  source: {
    fontFamily: 'var(--font-mono)',
    fontSize: '11px',
    background: 'var(--accent-soft)',
    color: 'var(--accent)',
    padding: '2px 8px',
    borderRadius: '99px',
    border: '1px solid #c6e0d2',
  },
}