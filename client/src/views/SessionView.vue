<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import MainContent from '@/components/layout/MainContent.vue'
import ChatMessage from '@/components/ChatMessage.vue'
import ChatInput from '@/components/chat/ChatInput.vue'
import ToolCall from '@/components/ToolCall.vue'
import type { SessionMessage } from '@/api/client'
import type { WsEvent } from '@/composables/useWebSocket'

const props = defineProps<{
  session: { id: string }
  messages: SessionMessage[]
  events: WsEvent[]
  loading: boolean
}>()

const emit = defineEmits<{
  submit: [content: string]
}>()

const messagesArea = ref<HTMLDivElement | null>(null)

interface DisplayItem {
  type: 'user' | 'message' | 'tool_result' | 'tool_call' | 'error'
  data: Record<string, any>
}

const displayMessages = computed<DisplayItem[]>(() => {
  const result: DisplayItem[] = []

  for (const msg of props.messages) {
    if (msg.role === 'user') {
      result.push({ type: 'user', data: { content: msg.content } })
    } else if (msg.role === 'assistant') {
      result.push({ type: 'message', data: { content: msg.content } })
    } else if (msg.role === 'tool') {
      result.push({ type: 'tool_result', data: { content: msg.content, tool_call_id: msg.tool_call_id } })
    }
  }

  for (const event of props.events) {
    if (event.history) continue
    if (event.type === 'message') {
      result.push({ type: 'message', data: event.data })
    } else if (event.type === 'tool_call') {
      result.push({ type: 'tool_call', data: event.data })
    } else if (event.type === 'tool_result') {
      const last = result[result.length - 1]
      if (last?.type === 'tool_call') {
        last.data.output = event.data.output
      }
    } else if (event.type === 'stream') {
      const last = result[result.length - 1]
      if (last?.type === 'message') {
        last.data.content = (last.data.content || '') + event.data.content
      } else {
        result.push({ type: 'message', data: { content: event.data.content } })
      }
    } else if (event.type === 'error') {
      result.push({ type: 'error', data: event.data })
    }
  }

  return result
})

watch(displayMessages, () => {
  nextTick(() => {
    if (messagesArea.value) {
      messagesArea.value.scrollTop = messagesArea.value.scrollHeight
    }
  })
}, { deep: true })
</script>

<template>
  <MainContent>
    <div class="messages-area" ref="messagesArea">
      <template v-for="(msg, i) in displayMessages" :key="i">
        <ChatMessage
          v-if="msg.type === 'user' || msg.type === 'message'"
          :role="msg.type === 'user' ? 'user' : 'assistant'"
          :content="msg.data.content || ''"
        />
        <ToolCall
          v-else-if="msg.type === 'tool_call'"
          :tool="msg.data.tool || ''"
          :args="msg.data.args || {}"
          :output="msg.data.output"
        />
      </template>
    </div>
    <ChatInput :loading="loading" @submit="(text: string) => emit('submit', text)" />
  </MainContent>
</template>

<style scoped>
.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
}
</style>