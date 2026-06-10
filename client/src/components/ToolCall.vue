<script setup lang="ts">
import { ref, computed } from 'vue'
import { ChevronRight, ChevronDown } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const MCP_TOOLS = [
  'mcp_file_read',
  'mcp_file_write',
  'mcp_shell_execute',
  'mcp_git_log',
  'mcp_git_diff'
]

const props = defineProps<{
  tool: string
  args: any
  output?: string
  status?: 'pending' | 'running' | 'completed' | 'failed'
}>()

const expanded = ref(false)
const isMcpTool = computed(() => MCP_TOOLS.includes(props.tool))

function toggle() {
  expanded.value = !expanded.value
}

function formatJson(obj: any): string {
  try {
    return JSON.stringify(obj, null, 2)
  } catch {
    return String(obj)
  }
}

const toolDisplayName = computed(() => {
  const names: Record<string, string> = {
    'mcp_file_read': t('tool.reading'),
    'mcp_file_write': t('tool.writing'),
    'mcp_shell_execute': t('tool.executing'),
    'mcp_git_log': t('tool.gitLog'),
    'mcp_git_diff': t('tool.gitDiff')
  }
  return names[props.tool] || props.tool
})

const statusText = computed(() => {
  switch (props.status) {
    case 'pending': return t('tool.status.pending')
    case 'running': return t('tool.status.running')
    case 'completed': return t('tool.status.completed')
    case 'failed': return t('tool.status.failed')
    default: return props.output ? t('common.done') : '...'
  }
})
</script>

<template>
  <div :class="['tool-call', { expanded, 'mcp-tool': isMcpTool }]">
    <!-- Collapsed header -->
    <div class="tool-header" @click="toggle">
      <ChevronRight v-if="!expanded" class="chevron" />
      <ChevronDown v-else class="chevron" />
      <span class="tool-bullet" :class="{ 'mcp-bullet': isMcpTool }">
        <template v-if="isMcpTool">
          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2L2 7l10 5 10-5-10-5z"/>
            <path d="M2 17l10 5 10-5"/>
            <path d="M2 12l10 5 10-5"/>
          </svg>
        </template>
        <template v-else>◆</template>
      </span>
      <span class="tool-name" :class="{ 'mcp-name': isMcpTool }">{{ isMcpTool ? toolDisplayName : tool }}</span>
      <span v-if="status" :class="['tool-status', status]">{{ statusText }}</span>
      <span v-else-if="output" class="tool-stat done">{{ $t('common.done') }}</span>
      <span v-else class="tool-stat pending">...</span>
    </div>

    <!-- Expanded body -->
    <Transition name="expand">
      <div v-if="expanded" class="tool-body">
        <!-- Parameters -->
        <div class="tool-section">
          <div class="tool-section-label">{{ $t('tool.parameters') }}</div>
          <pre class="tool-code">{{ formatJson(args) }}</pre>
        </div>

        <!-- Result -->
        <div v-if="output" class="tool-section result-section">
          <div class="tool-section-label">{{ $t('tool.result') }}</div>
          <pre class="tool-code">{{ output }}</pre>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.tool-call {
  margin-bottom: 12px;
  border-left: 2px solid var(--color-border);
  border-radius: 0 var(--radius-md) var(--radius-md) 0;
  transition: border-color var(--transition-fast);
  animation: message-in var(--transition-normal) var(--ease-out);
}

.tool-call.expanded {
  border-left-color: var(--color-accent);
}

.tool-call.mcp-tool {
  border-left-color: #1976d2;
}

.tool-call.mcp-tool.expanded {
  border-left-color: #1976d2;
}

/* Header */
.tool-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  cursor: pointer;
  user-select: none;
  transition: background-color var(--transition-fast);
}

.tool-header:hover {
  background: var(--color-surface-hover);
}

.chevron {
  flex-shrink: 0;
  color: var(--color-text-tertiary);
}

.tool-bullet {
  color: var(--color-accent);
  font-size: 8px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tool-bullet.mcp-bullet {
  color: #1976d2;
  width: 16px;
  height: 16px;
  background: #e3f2fd;
  border-radius: 3px;
}

.tool-name {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--color-accent);
  flex: 1;
}

.tool-name.mcp-name {
  color: #1976d2;
}

.tool-stat {
  font-size: var(--text-xs);
  padding: 1px 6px;
  border-radius: var(--radius-sm);
}

.tool-stat.done {
  color: var(--color-success);
  background: color-mix(in srgb, var(--color-success) 10%, transparent);
}

.tool-stat.pending {
  color: var(--color-text-tertiary);
}

.tool-status {
  font-size: var(--text-xs);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  flex-shrink: 0;
}

.tool-status.pending {
  color: var(--color-text-tertiary);
  background: var(--color-surface-hover);
}

.tool-status.running {
  color: #f57c00;
  background: #fff3e0;
}

.tool-status.completed {
  color: var(--color-success);
  background: color-mix(in srgb, var(--color-success) 10%, transparent);
}

.tool-status.failed {
  color: var(--color-error);
  background: color-mix(in srgb, var(--color-error) 10%, transparent);
}

/* Body */
.tool-body {
  overflow: hidden;
}

.tool-section {
  padding: 8px 14px;
  border-top: 1px solid var(--color-border);
}

.tool-section.result-section {
  background: var(--color-surface-hover);
}

.tool-section-label {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}

.tool-code {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
  margin: 0;
  white-space: pre-wrap;
  word-break: break-all;
  line-height: 1.6;
}
</style>
