<script setup lang="ts">
import { ref, computed } from 'vue'
import { ChevronRight, ChevronDown, Copy, Undo2 } from 'lucide-vue-next'

export interface DiffLine {
  type: 'add' | 'remove' | 'context'
  oldLineNum?: number
  newLineNum?: number
  content: string
}

const props = defineProps<{
  tool: string
  filePath: string
  lines: DiffLine[]
  addedCount?: number
  removedCount?: number
  duration?: string
}>()

const emit = defineEmits<{
  undo: []
}>()

const expanded = ref(false)
const copied = ref(false)
const fullyExpanded = ref(false)

const truncated = computed(() => props.lines.length > 50)
const displayLines = computed(() =>
  truncated.value && !fullyExpanded.value ? props.lines.slice(0, 50) : props.lines
)

function toggle() {
  expanded.value = !expanded.value
}

function toggleFull() {
  fullyExpanded.value = !fullyExpanded.value
}

async function handleCopy() {
  const text = props.lines
    .map(l => `${l.type === 'add' ? '+' : l.type === 'remove' ? '-' : ' '} ${l.content}`)
    .join('\n')
  await navigator.clipboard.writeText(text)
  copied.value = true
  setTimeout(() => (copied.value = false), 1500)
}
</script>

<template>
  <div :class="['diff-view', { expanded }]">
    <!-- Header -->
    <div class="diff-header" @click="toggle">
      <ChevronRight v-if="!expanded" :size="12" class="chevron" />
      <ChevronDown v-else :size="12" class="chevron" />
      <span class="diff-name">{{ tool }}</span>
      <span class="diff-path">{{ filePath }}</span>
      <span v-if="addedCount" class="diff-count add">+{{ addedCount }}</span>
      <span v-if="removedCount" class="diff-count remove">−{{ removedCount }}</span>
      <span v-if="duration" class="diff-duration">{{ duration }}</span>
    </div>

    <!-- Body -->
    <Transition name="expand">
      <div v-if="expanded" class="diff-body">
        <!-- Column headers -->
        <div class="diff-columns-header">
          <div class="diff-col old-col">− OLD</div>
          <div class="diff-col new-col">+ NEW</div>
        </div>

        <!-- Side-by-side diff -->
        <div class="diff-content">
          <div v-for="(line, i) in displayLines" :key="i" class="diff-row">
            <!-- Left: OLD -->
            <div :class="['diff-col', 'old-col', line.type === 'remove' ? 'removed' : line.type === 'add' ? 'empty' : '']">
              <span v-if="line.type !== 'add'" class="line-num">{{ line.oldLineNum }}</span>
              <span v-else class="line-num empty-num"></span>
              <template v-if="line.type === 'add'">
                <span class="line-placeholder"></span>
              </template>
              <template v-else>
                <span class="line-text">{{ line.content }}</span>
              </template>
            </div>
            <!-- Right: NEW -->
            <div :class="['diff-col', 'new-col', line.type === 'add' ? 'added' : line.type === 'remove' ? 'empty' : '']">
              <span v-if="line.type !== 'remove'" class="line-num">{{ line.newLineNum }}</span>
              <span v-else class="line-num empty-num"></span>
              <template v-if="line.type === 'remove'">
                <span class="line-placeholder"></span>
              </template>
              <template v-else>
                <span class="line-text">{{ line.content }}</span>
              </template>
            </div>
          </div>
        </div>

        <!-- Truncation hint -->
        <div v-if="truncated" class="diff-truncation" @click="toggleFull">
          <span v-if="fullyExpanded">Show less</span>
          <span v-else>Show all {{ lines.length }} lines</span>
        </div>

        <!-- Actions -->
        <div class="diff-actions">
          <button class="diff-action-btn" @click="handleCopy">
            <Copy :size="12" />
            <span>{{ copied ? 'Copied' : 'Copy' }}</span>
          </button>
          <button class="diff-action-btn" @click="emit('undo')">
            <Undo2 :size="12" />
            Undo
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.diff-view {
  margin-bottom: 12px;
  border-left: 2px solid var(--color-border);
  border-radius: 0 var(--radius-lg) var(--radius-lg) 0;
  overflow: hidden;
  animation: message-in var(--transition-normal) var(--ease-out);
}

.diff-view.expanded {
  border-left-color: var(--color-accent);
}

/* Header */
.diff-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  cursor: pointer;
  user-select: none;
  transition: background-color var(--transition-fast);
}

.diff-header:hover {
  background: var(--color-surface-hover);
}

.chevron {
  flex-shrink: 0;
  color: var(--color-text-tertiary);
}

.diff-name {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--color-accent);
}

.diff-path {
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.diff-count {
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  padding: 1px 4px;
  border-radius: var(--radius-sm);
}

.diff-count.add {
  color: var(--color-success);
  background: color-mix(in srgb, var(--color-success) 10%, transparent);
}

.diff-count.remove {
  color: var(--color-error);
  background: color-mix(in srgb, var(--color-error) 10%, transparent);
}

.diff-duration {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
}

/* Body */
.diff-body {
  overflow: hidden;
}

.diff-columns-header {
  display: flex;
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
  letter-spacing: 0.5px;
  border-bottom: 1px solid var(--color-border);
}

.diff-col {
  flex: 1;
  padding: 3px 12px;
}

.old-col {
  background: color-mix(in srgb, var(--color-error) 3%, transparent);
}

.new-col {
  background: color-mix(in srgb, var(--color-success) 3%, transparent);
  border-left: 1px solid var(--color-border);
}

/* Rows */
.diff-content {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  line-height: 1.9;
}

.diff-row {
  display: flex;
}

.diff-row .diff-col {
  display: flex;
  align-items: baseline;
  min-height: 1.8em;
}

.diff-col.removed {
  background: color-mix(in srgb, var(--color-error) 8%, transparent);
  color: var(--color-error);
}

.diff-col.added {
  background: color-mix(in srgb, var(--color-success) 8%, transparent);
  color: var(--color-success);
}

.diff-col.empty .line-placeholder {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--color-border), transparent);
  margin: auto 8px;
}

.line-num {
  width: 28px;
  text-align: right;
  flex-shrink: 0;
  margin-right: 8px;
  color: var(--color-text-tertiary);
}

.removed .line-num { color: var(--color-error); }
.added .line-num { color: var(--color-success); }

.empty-num {
  visibility: hidden;
}

.line-text {
  flex: 1;
  white-space: pre;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Truncation */
.diff-truncation {
  padding: 6px;
  text-align: center;
  font-size: var(--text-xs);
  color: var(--color-accent);
  cursor: pointer;
  border-top: 1px solid var(--color-border);
}

.diff-truncation:hover {
  text-decoration: underline;
}

/* Actions */
.diff-actions {
  display: flex;
  gap: 4px;
  padding: 6px 12px;
  border-top: 1px solid var(--color-border);
}

.diff-action-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 8px;
  border: none;
  background: transparent;
  color: var(--color-text-tertiary);
  font-size: var(--text-xs);
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: background-color var(--transition-fast), color var(--transition-fast);
}

.diff-action-btn:hover {
  background: var(--color-surface-hover);
  color: var(--color-text);
}
</style>
