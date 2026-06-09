<script setup lang="ts">
import { computed, ref } from 'vue'
import { ArrowLeft } from 'lucide-vue-next'
import MainContent from '../components/layout/MainContent.vue'
import ChatMessage from '../components/ChatMessage.vue'
import ToolCall from '../components/ToolCall.vue'
import McpToolCall from '../components/McpToolCall.vue'
import DiffView from '../components/chat/DiffView.vue'
import ChatInput from '../components/chat/ChatInput.vue'
import StatusDot from '../components/ui/StatusDot.vue'
import AgentPanel from '../components/AgentPanel.vue'
import EventStream from '../components/EventStream.vue'
import { useWebSocket } from '../composables/useWebSocket'
import { useTask } from '../composables/useTask'
import { listAgents, type Agent, type Project } from '../api/client'

const props = defineProps<{
  project: Project
}>()

const emit = defineEmits<{
  back: []
}>()

const { currentTask, loading, submit } = useTask()

const activeTaskId = computed(() => currentTask.value?.id || '')
const { events, connected } = useWebSocket(activeTaskId)

// Agent 状态
const agents = ref<Agent[]>([])
const showAgents = ref(false)

async function refreshAgents() {
  try {
    const result = await listAgents({ project_id: props.project.id })
    agents.value = result.items
  } catch (e) {
    console.error('Failed to load agents:', e)
  }
}

interface MessageEvent {
  type: string
  data: any
}

const MCP_TOOLS = [
  'mcp_file_read',
  'mcp_file_write',
  'mcp_shell_execute',
  'mcp_git_log',
  'mcp_git_diff'
]

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
    } else if (event.type === 'plan_start') {
      result.push({ type: 'plan_start', data: event.data })
    } else if (event.type === 'plan_generated') {
      result.push({ type: 'plan_generated', data: event.data })
    } else if (event.type === 'plan_completed') {
      result.push({ type: 'plan_completed', data: event.data })
    }
  }
  return result
})

function isMcpTool(toolName: string): boolean {
  return MCP_TOOLS.includes(toolName)
}

const taskStatus = computed(() => {
  const statusEvent = [...events.value].reverse().find(e => e.type === 'status')
  return statusEvent?.data.status || currentTask.value?.status || 'pending'
})

// 监听事件刷新 Agent 列表
const lastEventId = computed(() => {
  const last = events.value[events.value.length - 1]
  return last?.event_id
})

import { watch } from 'vue'
watch(lastEventId, () => {
  if (showAgents.value) refreshAgents()
})

async function handleSubmit(text: string) {
  await submit(props.project.id, text)
  // 提交后刷新 Agent 列表
  setTimeout(refreshAgents, 1000)
}

function toggleAgents() {
  showAgents.value = !showAgents.value
  if (showAgents.value) refreshAgents()
}
</script>

<template>
  <MainContent>
    <div class="chat-header">
      <button class="back-btn" @click="emit('back')">
        <ArrowLeft />
      </button>
      <span class="task-title">{{ project.name }}</span>
      <StatusDot :status="taskStatus" />
      <button class="agents-btn" @click="toggleAgents" :class="{ active: showAgents }">
        Agents ({{ agents.length }})
      </button>
      <span class="ws-status">{{ connected ? 'connected' : 'disconnected' }}</span>
    </div>

    <div class="content-area">
      <div class="messages-area">
        <template v-for="(msg, i) in messages" :key="i">
          <ChatMessage
            v-if="msg.type === 'message'"
            role="assistant"
            :content="msg.data.content"
          />
          <McpToolCall
            v-else-if="msg.type === 'tool_call' && isMcpTool(msg.data.tool)"
            :tool-name="msg.data.tool"
            :params="msg.data.args"
            :result="msg.data.output"
            :error="msg.data.error"
            :status="msg.data.status || (msg.data.output ? 'completed' : 'running')"
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
          <div v-else-if="msg.type === 'plan_start'" class="plan-event">
            <span class="plan-icon">📋</span>
            <span>分析任务中...</span>
          </div>
          <div v-else-if="msg.type === 'plan_generated'" class="plan-event">
            <span class="plan-icon">✅</span>
            <span>计划生成：{{ msg.data.steps }} 个步骤</span>
            <div v-if="msg.data.plan" class="plan-steps">
              <div v-for="(step, j) in msg.data.plan" :key="j" class="plan-step">
                <span class="step-type">{{ step.type }}</span>
                <span class="step-desc">{{ step.description || step.command || step.path }}</span>
              </div>
            </div>
          </div>
          <div v-else-if="msg.type === 'plan_completed'" class="plan-event">
            <span class="plan-icon">{{ msg.data.success ? '✅' : '❌' }}</span>
            <span>执行{{ msg.data.success ? '成功' : '失败' }}：{{ msg.data.results?.length || 0 }} 个结果</span>
          </div>
        </template>
      </div>

      <AgentPanel v-if="showAgents" :agents="agents" />
    </div>

    <EventStream />
    <ChatInput :loading="loading" @submit="handleSubmit" />
  </MainContent>
</template>

<style scoped>
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

.agents-btn {
  padding: 4px 10px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-surface);
  color: var(--color-text-secondary);
  font-size: var(--text-xs);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.agents-btn:hover,
.agents-btn.active {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

.ws-status {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
  margin-left: auto;
}

.content-area {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
}

.plan-event {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 8px 12px;
  margin: 4px 0;
  background: var(--color-surface);
  border-radius: var(--radius-sm);
  border-left: 3px solid var(--color-primary);
  font-size: var(--text-sm);
  color: var(--color-text);
}

.plan-icon {
  flex-shrink: 0;
}

.plan-steps {
  margin-top: 8px;
  padding-left: 24px;
}

.plan-step {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 2px 0;
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
}

.step-type {
  padding: 1px 6px;
  background: var(--color-surface-hover);
  border-radius: 3px;
  font-family: monospace;
  font-size: 10px;
}

.step-desc {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
