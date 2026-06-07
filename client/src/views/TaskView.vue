<script setup lang="ts">
import { ref, computed } from 'vue'
import { ArrowLeft } from 'lucide-vue-next'
import Sidebar from '../components/layout/Sidebar.vue'
import MainContent from '../components/layout/MainContent.vue'
import ChatPanel from '../components/sidebar/ChatPanel.vue'
import FilesPanel from '../components/sidebar/FilesPanel.vue'
import PluginsPanel from '../components/sidebar/PluginsPanel.vue'
import SettingsPanel from '../components/sidebar/SettingsPanel.vue'
import ChatMessage from '../components/ChatMessage.vue'
import ToolCall from '../components/ToolCall.vue'
import DiffView from '../components/chat/DiffView.vue'
import ChatInput from '../components/chat/ChatInput.vue'
import StatusDot from '../components/ui/StatusDot.vue'
import { useWebSocket } from '../composables/useWebSocket'
import { useTask } from '../composables/useTask'
import type { Project } from '../api/client'

const props = defineProps<{
  project: Project
  activePanel: 'chat' | 'files' | 'plugins' | 'settings'
}>()

const emit = defineEmits<{
  back: []
  'update:activePanel': [panel: 'chat' | 'files' | 'plugins' | 'settings']
}>()

const { tasks, currentTask, loading, submit, loadTasks } = useTask()

const activeTaskId = computed(() => currentTask.value?.id || '')
const { events, connected } = useWebSocket(activeTaskId)

interface MessageEvent {
  type: string
  data: any
}

const messages = computed(() => {
  const result: MessageEvent[] = []
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
    } else if (event.type === 'diff') {
      result.push({ type: 'diff', data: event.data })
    }
  }
  return result
})

const taskStatus = computed(() => {
  const statusEvent = [...events.value].reverse().find(e => e.type === 'status')
  return statusEvent?.data.status || currentTask.value?.status || 'pending'
})

const servers = ref([
  { url: 'localhost:8000', status: 'connected' as const },
])

async function handleSubmit(text: string) {
  await submit(props.project.id, text)
}

loadTasks(props.project.id)
</script>

<template>
  <div class="task-view">
    <Sidebar
      v-if="activePanel !== 'settings'"
      :title="activePanel === 'chat' ? 'Chat' : activePanel === 'files' ? 'Files' : 'Plugins'"
    >
      <ChatPanel
        v-if="activePanel === 'chat'"
        :tasks="tasks"
        :active-task-id="activeTaskId"
        @select="currentTask = $event"
      />
      <FilesPanel v-else-if="activePanel === 'files'" />
      <PluginsPanel v-else />
    </Sidebar>

    <SettingsPanel
      v-else
      :servers="servers"
      active-server="localhost:8000"
    />

    <MainContent>
      <div class="chat-header">
        <button class="back-btn" @click="emit('back')">
          <ArrowLeft :size="16" />
        </button>
        <span class="task-title">{{ project.name }}</span>
        <StatusDot :status="taskStatus" />
        <span class="ws-status">{{ connected ? 'connected' : 'disconnected' }}</span>
      </div>

      <div class="messages-area">
        <template v-for="(msg, i) in messages" :key="i">
          <ChatMessage
            v-if="msg.type === 'message'"
            role="assistant"
            :content="msg.data.content"
          />
          <ToolCall
            v-else-if="msg.type === 'tool_call'"
            :tool="msg.data.tool"
            :args="msg.data.args"
            :output="msg.data.output"
          />
          <DiffView
            v-else-if="msg.type === 'diff'"
            :tool="msg.data.tool"
            :file-path="msg.data.filePath"
            :lines="msg.data.lines"
            :added-count="msg.data.addedCount"
            :removed-count="msg.data.removedCount"
          />
        </template>
      </div>

      <ChatInput :loading="loading" @submit="handleSubmit" />
    </MainContent>
  </div>
</template>

<style scoped>
.task-view {
  display: flex;
  flex: 1;
  background: var(--color-bg);
}

.chat-header {
  padding: 10px 16px;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface);
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.back-btn {
  padding: 4px;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--color-text-secondary);
  display: flex;
  align-items: center;
  border-radius: var(--radius-sm);
  transition: color var(--transition-fast), background-color var(--transition-fast);
}

.back-btn:hover {
  color: var(--color-text);
  background: var(--color-surface-hover);
}

.task-title {
  font-size: var(--text-base);
  font-weight: var(--font-medium);
  color: var(--color-text);
}

.ws-status {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
  margin-left: auto;
}

.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
}
</style>
