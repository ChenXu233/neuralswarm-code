<script setup lang="ts">
import { computed } from 'vue'
import MarkdownIt from 'markdown-it'

const props = defineProps<{ role: string; content: string }>()
const md = new MarkdownIt()
const html = computed(() => md.render(props.content))
</script>

<template>
  <div :class="['message', role]">
    <div class="role">{{ role === 'user' ? 'You' : 'Agent' }}</div>
    <div class="content" v-html="html"></div>
  </div>
</template>

<style scoped>
.message { margin: 8px 0; padding: 12px; border-radius: 8px; }
.message.user { background: #f0f0f0; }
.message.assistant { background: #e6f7ff; }
.role { font-weight: bold; margin-bottom: 4px; font-size: 12px; color: #666; }
.content { line-height: 1.6; }
.content :deep(pre) { background: #1e1e1e; color: #d4d4d4; padding: 12px; border-radius: 4px; overflow-x: auto; }
.content :deep(code) { font-family: monospace; }
</style>
