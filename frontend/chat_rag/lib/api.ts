const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

export interface ChatRequest {
  message: string
  session_id?: string
}

export interface ChatResponse {
  answer: string
  session_id: string
  sources: string[]
}

export async function sendMessage(
  message: string,
  sessionId = 'default'
): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, session_id: sessionId } satisfies ChatRequest),
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error((err as { detail?: string }).detail ?? `Erro ${res.status}`)
  }

  return res.json() as Promise<ChatResponse>
}

export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/health`, { cache: 'no-store' })
    return res.ok
  } catch {
    return false
  }
}
