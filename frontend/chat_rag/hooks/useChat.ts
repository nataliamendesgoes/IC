'use client'

import { useState, useCallback } from 'react'
import { sendMessage } from '@/lib/api'

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources: string[]
  ts: Date
}

const SESSION_ID = `session_${Date.now()}`

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading]   = useState(false)
  const [error, setError]       = useState<string | null>(null)

  const addMessage = useCallback(
    (role: Message['role'], content: string, sources: string[] = []) => {
      setMessages(prev => [
        ...prev,
        {
          id: `${Date.now()}_${Math.random()}`,
          role,
          content,
          sources,
          ts: new Date(),
        },
      ])
    },
    []
  )

  const submit = useCallback(
    async (text: string) => {
      if (!text.trim() || loading) return

      setError(null)
      addMessage('user', text)
      setLoading(true)

      try {
        const data = await sendMessage(text, SESSION_ID)
        addMessage('assistant', data.answer, data.sources ?? [])
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Erro desconhecido')
      } finally {
        setLoading(false)
      }
    },
    [loading, addMessage]
  )

  const clear = useCallback(() => {
    setMessages([])
    setError(null)
  }, [])

  return { messages, loading, error, submit, clear }
}