'use client'

export function TypingIndicator() {
  return (
    <div style={styles.wrapper}>
      <div style={styles.avatar}>M</div>
      <div style={styles.bubble}>
        {[0, 180, 360].map(delay => (
          <span
            key={delay}
            style={{
              ...styles.dot,
              animationDelay: `${delay}ms`,
            }}
          />
        ))}
      </div>
    </div>
  )
}

const styles: Record<string, React.CSSProperties> = {
  wrapper: {
    display: 'flex',
    alignItems: 'flex-end',
    gap: '10px',
    marginBottom: '20px',
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
  bubble: {
    background: 'var(--surface)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius)',
    borderBottomLeftRadius: '3px',
    padding: '14px 18px',
    display: 'flex',
    gap: '5px',
    alignItems: 'center',
  },
  dot: {
    display: 'inline-block',
    width: '7px',
    height: '7px',
    borderRadius: '50%',
    background: 'var(--text-muted)',
    animation: 'bounce 1.1s ease-in-out infinite',
  },
}