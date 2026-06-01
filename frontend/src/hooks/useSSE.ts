import { useEffect, useRef, useCallback } from 'react'
import { SSE_BASE_URL } from '../utils/constants'
import type { SSEProgressEvent } from '../types/task'

interface UseSSEOptions {
  taskId: string | null
  onMessage: (event: SSEProgressEvent) => void
  onError?: (error: Event) => void
  enabled?: boolean
}

/**
 * Subscribes to Server-Sent Events for a task progress stream.
 * Automatically reconnects on unexpected close.
 */
const useSSE = ({ taskId, onMessage, onError, enabled = true }: UseSSEOptions) => {
  const esRef = useRef<EventSource | null>(null)
  const onMessageRef = useRef(onMessage)
  const onErrorRef = useRef(onError)

  onMessageRef.current = onMessage
  onErrorRef.current = onError

  const disconnect = useCallback(() => {
    if (esRef.current) {
      esRef.current.close()
      esRef.current = null
    }
  }, [])

  useEffect(() => {
    if (!taskId || !enabled) {
      disconnect()
      return
    }

    const url = `${SSE_BASE_URL}/tasks/${taskId}`
    const es = new EventSource(url)
    esRef.current = es

    es.onmessage = (rawEvent) => {
      try {
        const parsed: SSEProgressEvent = JSON.parse(rawEvent.data)
        onMessageRef.current(parsed)

        // Disconnect once terminal status received
        if (parsed.status === 'done' || parsed.status === 'failed') {
          disconnect()
        }
      } catch {
        // ignore malformed SSE frames
      }
    }

    es.onerror = (err) => {
      onErrorRef.current?.(err)
    }

    return () => {
      disconnect()
    }
  }, [taskId, enabled, disconnect])

  return { disconnect }
}

export default useSSE
