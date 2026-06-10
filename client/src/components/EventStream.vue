<template>
  <div class="event-stream">
    <div class="stream-header">
      <span class="stream-title">{{ $t('event.stream') }}</span>
      <span class="event-count">{{ $t('event.count', { n: events.length }) }}</span>
    </div>

    <div class="stream-content" ref="streamRef">
      <div v-for="(event, index) in events" :key="index" class="stream-event">
        <span class="event-time">{{ formatTime(event.timestamp) }}</span>
        <span class="event-type-badge" :class="event.type">{{ event.type }}</span>
        <span class="event-data">{{ event.data }}</span>
      </div>
      <div v-if="events.length === 0" class="empty">{{ $t('event.noEvents') }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'

interface StreamEvent {
  type: string
  data: string
  timestamp: string
}

const events = ref<StreamEvent[]>([])
const streamRef = ref<HTMLElement | null>(null)

function formatTime(timestamp: string): string {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleTimeString()
}

function scrollToBottom() {
  nextTick(() => {
    if (streamRef.value) {
      streamRef.value.scrollTop = streamRef.value.scrollHeight
    }
  })
}

// 模拟事件流（实际应该连接 WebSocket）
let interval: number | null = null

onMounted(() => {
  // 这里应该连接 WebSocket 接收事件
  // 示例：每 5 秒添加一个模拟事件
  interval = window.setInterval(() => {
    const types = ['task_start', 'tool_call', 'task_complete']
    const type = types[Math.floor(Math.random() * types.length)]
    events.value.push({
      type,
      data: `模拟 ${type} 事件`,
      timestamp: new Date().toISOString()
    })
    scrollToBottom()
  }, 5000)
})

onUnmounted(() => {
  if (interval) {
    clearInterval(interval)
  }
})
</script>

<style scoped>
.event-stream {
  display: flex;
  flex-direction: column;
  height: 200px;
  border-top: 1px solid var(--color-border);
}

.stream-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
}

.stream-title {
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  color: var(--color-text-tertiary);
  letter-spacing: 1.5px;
}

.event-count {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
}

.stream-content {
  flex: 1;
  overflow-y: auto;
  font-size: var(--text-xs);
  padding: 0 12px;
}

.stream-event {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;
  border-bottom: 1px solid var(--color-surface-hover);
}

.event-time {
  color: var(--color-text-tertiary);
  font-family: monospace;
  font-size: 11px;
}

.event-type-badge {
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 10px;
  font-weight: var(--font-semibold);
  text-transform: uppercase;
}

.event-type-badge.task_start {
  background: #e3f2fd;
  color: #1976d2;
}

.event-type-badge.tool_call {
  background: #fff3e0;
  color: #f57c00;
}

.event-type-badge.task_complete {
  background: #e8f5e9;
  color: #388e3c;
}

.event-data {
  flex: 1;
  color: var(--color-text);
}

.empty {
  text-align: center;
  padding: 20px;
  color: var(--color-text-tertiary);
}
</style>
