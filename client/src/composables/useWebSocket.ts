import { ref, computed, watch, onUnmounted, type Ref } from 'vue'

export interface TaskEvent {
  type: 'status' | 'tool_call' | 'tool_result' | 'message' | 'error'
  data: Record<string, any>
  timestamp: string
  event_id?: string
}

export function useWebSocket(taskId: string | Ref<string>) {
  const events = ref<TaskEvent[]>([])
  const connected = ref(false)
  let ws: WebSocket | null = null
  let reconnectTimer: number | null = null
  let reconnectDelay = 1000
  let lastEventId: string | null = null

  const taskIdValue = computed(() => typeof taskId === 'string' ? taskId : taskId.value)

  function connect() {
    const id = taskIdValue.value
    if (!id || ws?.readyState === WebSocket.OPEN) return

    ws = new WebSocket(`ws://localhost:8000/ws/tasks/${id}`)

    ws.onopen = () => {
      connected.value = true
      reconnectDelay = 1000
      if (lastEventId) {
        ws!.send(JSON.stringify({ last_event_id: lastEventId }))
      }
    }

    ws.onmessage = (msg) => {
      const event: TaskEvent = JSON.parse(msg.data)
      events.value.push(event)
      if (event.event_id) {
        lastEventId = event.event_id
      }
    }

    ws.onclose = () => {
      connected.value = false
      reconnectTimer = window.setTimeout(() => {
        reconnectDelay = Math.min(reconnectDelay * 2, 30000)
        connect()
      }, reconnectDelay)
    }

    ws.onerror = () => {
      ws?.close()
    }
  }

  function disconnect() {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
    ws?.close()
    ws = null
  }

  connect()

  watch(taskIdValue, (newId, oldId) => {
    if (newId !== oldId) {
      disconnect()
      events.value = []
      lastEventId = null
      if (newId) connect()
    }
  })

  onUnmounted(disconnect)

  return { events, connected, disconnect }
}
