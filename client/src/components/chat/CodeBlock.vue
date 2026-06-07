<script setup lang="ts">
defineProps<{
  code: string
  language?: string
}>()
</script>

<template>
  <div class="code-block">
    <div class="code-header">
      <span class="language">{{ language || 'plaintext' }}</span>
    </div>
    <pre><code>{{ code }}</code></pre>
  </div>
</template>

<style scoped>
.code-block {
  background: #1e1e1e;
  border-radius: var(--radius-md);
  overflow: hidden;
  margin: 8px 0;
}

.code-header {
  padding: 6px 12px;
  background: #2d2d2d;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.language {
  font-size: 10px;
  color: #999;
  font-family: var(--font-mono);
}

pre {
  padding: 12px;
  margin: 0;
  overflow-x: auto;
}

code {
  font-family: var(--font-mono);
  font-size: 12px;
  line-height: 1.6;
  color: #d4d4d4;
}
</style>
