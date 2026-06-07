<script setup lang="ts">
import { ref, computed } from 'vue'
import { ArrowLeft } from 'lucide-vue-next'
import ActivityBar from '../components/layout/ActivityBar.vue'
import Sidebar from '../components/layout/Sidebar.vue'
import MainContent from '../components/layout/MainContent.vue'
import ChatPanel from '../components/sidebar/ChatPanel.vue'
import FilesPanel from '../components/sidebar/FilesPanel.vue'
import PluginsPanel from '../components/sidebar/PluginsPanel.vue'
import SettingsPanel from '../components/sidebar/SettingsPanel.vue'
import ChatMessage from '../components/ChatMessage.vue'
import ToolCall from '../components/ToolCall.vue'
import ChatInput from '../components/chat/ChatInput.vue'
import StatusDot from '../components/ui/StatusDot.vue'
import { useWebSocket } from '../composables/useWebSocket'
import { useTask } from '../composables/useTask'
import type { Project } from '../api/client'

const props = defineProps<{ project: Project }>()
const emit = defineEmits<{ back: [] }>()

const activePanel = ref<'chat' | 'files' | 'plugins' | 'settings'>('chat')
const { tasks, currentTask, loading, submit, loadTasks } = useTask()

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
    <ActivityBar v-model:active-panel="activePanel" />

    <Sidebar v-if="activePanel !== 'settings'" :title="activePanel === 'chat' ? '对话' : activePanel === 'files' ? '文件' : '插件'">
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
        <span class="ws-status">{{ connected ? '已连接' : '未连接' }}</span>
      </div>

      <div class="messages-area">
        <template v-for="(msg, i) in messages" :key="i">
          <ChatMessage
            v-if="msg.type === 'message'"
            role="assistant"
            :content="msg.data.content"
          />
          <ToolCall
            v-if="msg.type === 'tool_call'"
            :tool="msg.data.tool"
            :args="msg.data.args"
            :output="msg.data.output"
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
  height: 100vh;
  background: var(--color-bg);
}

.chat-header {
  padding: 10px 16px;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface);
  display: flex;
  align-items: center;
  gap: 10px;
}

.back-btn {
  padding: 4px;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--color-text-secondary);
  display: flex;
  align-items: center;
}

.back-btn:hover {
  color: var(--color-text);
}

.task-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text);
}

.ws-status {
  font-size: 11px;
  color: var(--color-text-tertiary);
  margin-left: auto;
}

.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}
</style>
