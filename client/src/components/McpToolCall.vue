<script setup lang="ts">
import { ref, computed } from 'vue'
import { ChevronRight, ChevronDown } from 'lucide-vue-next'
import { isTauri } from '@/utils/platform'
import PlatformBanner from '@/components/ui/PlatformBanner.vue'

const props = defineProps<{
  toolName: string
  params: Record<string, any>
  result?: string
  error?: string
  status: 'pending' | 'running' | 'completed' | 'failed'
}>()

const isExpanded = ref(false)

function toggle() {
  isExpanded.value = !isExpanded.value
}

function formatJson(obj: any): string {
  try {
    return JSON.stringify(obj, null, 2)
  } catch {
    return String(obj)
  }
}

const statusText = computed(() => {
  switch (props.status) {
    case 'pending': return '等待中'
    case 'running': return '执行中'
    case 'completed': return '完成'
    case 'failed': return '失败'
    default: return props.status
  }
})

const toolDisplayName = computed(() => {
  const names: Record<string, string> = {
    'mcp_file_read': '读取文件',
    'mcp_file_write': '写入文件',
    'mcp_shell_execute': '执行命令',
    'mcp_git_log': 'Git 日志',
    'mcp_git_diff': 'Git diff'
  }
  return names[props.toolName] || props.toolName
})

const needsTauri = computed(() => {
  const tauriTools = ['mcp_file_read', 'mcp_file_write', 'mcp_shell_execute', 'mcp_git_log', 'mcp_git_diff']
  return tauriTools.includes(props.toolName)
})
</script>

<template>
  <div :class="['mcp-tool-call', { expanded: isExpanded }]">
    <!-- Platform warning banner -->
    <PlatformBanner
      v-if="!isTauri() && needsTauri"
      type="warning"
      title="本地操作不可用"
      message="此工具需要桌面应用支持。请在 Tauri 应用中使用。"
      :dismissible="true"
    />

    <!-- Collapsed header -->
    <div class="tool-header" @click="toggle">
      <ChevronRight v-if="!isExpanded" class="chevron" />
      <ChevronDown v-else class="chevron" />
      <div class="tool-icon">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 2L2 7l10 5 10-5-10-5z"/>
          <path d="M2 17l10 5 10-5"/>
          <path d="M2 12l10 5 10-5"/>
        </svg>
      </div>
      <span class="tool-name">{{ toolDisplayName }}</span>
      <span :class="['tool-status', status]">{{ statusText }}</span>
    </div>

    <!-- Expanded body -->
    <Transition name="expand">
      <div v-if="isExpanded" class="tool-body">
        <!-- Parameters -->
        <div class="tool-section">
          <div class="tool-section-label">参数</div>
          <pre class="tool-code">{{ formatJson(params) }}</pre>
        </div>

        <!-- Result -->
        <div v-if="result" class="tool-section result-section">
          <div class="tool-section-label">结果</div>
          <pre class="tool-code">{{ result }}</pre>
        </div>

        <!-- Error -->
        <div v-if="error" class="tool-section error-section">
          <div class="tool-section-label">错误</div>
          <pre class="tool-code error-code">{{ error }}</pre>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.mcp-tool-call {
  margin-bottom: 12px;
  border-left: 2px solid var(--color-border);
  border-radius: 0 var(--radius-md) var(--radius-md) 0;
  transition: border-color var(--transition-fast);
  animation: message-in var(--transition-normal) var(--ease-out);
  background: var(--color-surface);
}

.mcp-tool-call.expanded {
  border-left-color: #1976d2;
}

/* Header */
.tool-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
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

.tool-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 4px;
  background: #e3f2fd;
  color: #1976d2;
  flex-shrink: 0;
}

.tool-name {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: #1976d2;
  flex: 1;
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

.tool-section.error-section {
  background: color-mix(in srgb, var(--color-error) 5%, transparent);
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

.tool-code.error-code {
  color: var(--color-error);
}

/* Transition */
.expand-enter-active,
.expand-leave-active {
  transition: all var(--transition-normal);
  max-height: 500px;
}

.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  max-height: 0;
}
</style>
