<script setup lang="ts">
import { ref, computed } from 'vue'
import { useWebSocket } from '../composables/useWebSocket'
import { useTask } from '../composables/useTask'
import { type Project } from '../api/client'
import ChatMessage from '../components/ChatMessage.vue'
import ToolCall from '../components/ToolCall.vue'
import TaskStatus from '../components/TaskStatus.vue'

const props = defineProps<{ project: Project }>()
const emit = defineEmits<{ back: [] }>()

const prompt = ref('')
const { tasks, currentTask, loading, error, submit, loadTasks } = useTask()

const activeTaskId = computed(() => currentTask.value?.id || '')
const { events, connected } = useWebSocket(activeTaskId)

const messages = computed(() => {
  const result: Array<{ type: string; data: any }> = []
  for (const event of events.value) {
    if (event.type === 'message') {
      result.push({ type: 'message', data: event.data })
    } else if (event.type === 'tool_call') {
      result.push({ type: 'tool_call', data: event.data })
    } else if (event.type === 'tool_result') {
      const last = result[result.length - 1]
      if (last?.type === 'tool_call') {
        last.data.output = event.data.output
      }
    }
  }
  return result
})

const taskStatus = computed(() => {
  const statusEvent = [...events.value].reverse().find(e => e.type === 'status')
  return statusEvent?.data.status || currentTask.value?.status || 'pending'
})

async function handleSubmit() {
  if (!prompt.value.trim()) return
  await submit(props.project.id, prompt.value)
  prompt.value = ''
}

loadTasks(props.project.id)
</script>

<template>
  <div class="task-view">
    <div class="header">
      <button @click="emit('back')">&larr; Back</button>
      <h2>{{ project.name }}</h2>
      <TaskStatus :status="taskStatus" />
      <span class="ws-status">{{ connected ? 'Connected' : 'Disconnected' }}</span>
    </div>

    <div class="chat-area">
      <div class="task-list">
        <div v-for="t in tasks" :key="t.id" :class="['task-item', { active: t.id === currentTask?.id }]" @click="currentTask = t">
          <span class="task-input">{{ t.input.slice(0, 50) }}</span>
          <TaskStatus :status="t.status" />
        </div>
      </div>

      <div class="messages">
        <template v-for="(msg, i) in messages" :key="i">
          <ChatMessage v-if="msg.type === 'message'" role="assistant" :content="msg.data.content" />
          <ToolCall v-if="msg.type === 'tool_call'" :tool="msg.data.tool" :args="msg.data.args" :output="msg.data.output" />
        </template>
      </div>
    </div>

    <div class="input-area">
      <textarea v-model="prompt" placeholder="Enter your task... (Ctrl+Enter to send)" @keydown.ctrl.enter="handleSubmit"></textarea>
      <button @click="handleSubmit" :disabled="loading">{{ loading ? 'Sending...' : 'Send' }}</button>
    </div>

    <div v-if="error" class="error">{{ error }}</div>
  </div>
</template>

<style scoped>
.task-view { display: flex; flex-direction: column; height: 100vh; }
.header { display: flex; align-items: center; gap: 12px; padding: 12px; border-bottom: 1px solid #e8e8e8; }
.header button { padding: 4px 12px; background: none; border: 1px solid #d9d9d9; border-radius: 4px; cursor: pointer; }
.ws-status { font-size: 12px; color: #999; margin-left: auto; }
.chat-area { flex: 1; display: flex; overflow: hidden; }
.task-list { width: 240px; border-right: 1px solid #e8e8e8; overflow-y: auto; }
.task-item { padding: 12px; cursor: pointer; border-bottom: 1px solid #f0f0f0; }
.task-item.active { background: #e6f7ff; }
.task-input { font-size: 13px; display: block; margin-bottom: 4px; }
.messages { flex: 1; overflow-y: auto; padding: 16px; }
.input-area { display: flex; gap: 8px; padding: 12px; border-top: 1px solid #e8e8e8; }
textarea { flex: 1; padding: 8px; border: 1px solid #d9d9d9; border-radius: 4px; resize: none; min-height: 60px; font-family: inherit; }
.input-area button { padding: 8px 24px; background: #1890ff; color: white; border: none; border-radius: 4px; cursor: pointer; align-self: flex-end; }
.error { color: #ff4d4f; padding: 8px 12px; }
</style>
