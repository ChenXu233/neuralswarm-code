import { ref, watch, onUnmounted } from 'vue'

export interface WsEvent {
  type: string
  data: Record<string, any>
  history?: boolean
  event_id?: string
}

export function useWebSocket(sessionId: () => string) {
  const events = ref<WsEvent[]>([])
  const connected = ref(false)

  let ws: WebSocket | null = null
  let reconnectTimer: number | null = null
  let reconnectDelay = 1000

  function getWsBase(): string {
    const servers = JSON.parse(localStorage.getItem('neuralswarm-servers') || '[]')
    const base = servers[0]?.url || 'http://localhost:8080'
    return base.replace(/^http/, 'ws')
  }

  function connect() {
    const id = sessionId()
    if (!id || ws?.readyState === WebSocket.OPEN) return

    const wsUrl = `${getWsBase()}/ws/sessions/${id}`
    ws = new WebSocket(wsUrl)

    ws.onopen = () => {
      connected.value = true
      reconnectDelay = 1000
    }

    ws.onmessage = (msg) => {
      try {
        const event: WsEvent = JSON.parse(msg.data)
        events.value.push(event)
      } catch (e) {
        console.error('WS parse error:', e)
      }
    }

    ws.onclose = () => {
      connected.value = false
      reconnectTimer = window.setTimeout(() => {
        reconnectDelay = Math.min(reconnectDelay * 2, 30000)
        connect()
      }, reconnectDelay)
    }

    ws.onerror = () => ws?.close()
  }

  function disconnect() {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
    ws?.close()
    ws = null
    connected.value = false
  }

  watch(
    () => sessionId(),
    (newId, oldId) => {
      if (newId !== oldId) {
        disconnect()
        events.value = []
        if (newId) connect()
      }
    }
  )

  onUnmounted(disconnect)

  return { events, connected, disconnect }
}
