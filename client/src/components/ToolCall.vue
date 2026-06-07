<script setup lang="ts">
defineProps<{ tool: string; args: any; output?: string }>()
</script>

<template>
  <div class="tool-call">
    <div class="header">
      <span class="icon">&#x1f527;</span>
      <span class="name">{{ tool }}</span>
    </div>
    <pre class="args">{{ JSON.stringify(args, null, 2) }}</pre>
    <div v-if="output" class="output">
      <div class="label">Output:</div>
      <pre>{{ output }}</pre>
    </div>
  </div>
</template>

<style scoped>
.tool-call { margin: 8px 0; padding: 12px; background: #fafafa; border: 1px solid #e8e8e8; border-radius: 8px; }
.header { font-weight: 500; margin-bottom: 8px; }
.icon { margin-right: 4px; }
.args { background: #1e1e1e; color: #d4d4d4; padding: 8px; border-radius: 4px; font-size: 12px; overflow-x: auto; }
.output { margin-top: 8px; }
.label { font-size: 12px; color: #666; margin-bottom: 4px; }
.output pre { background: #f6f6f6; padding: 8px; border-radius: 4px; font-size: 12px; max-height: 200px; overflow-y: auto; }
</style>
