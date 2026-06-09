<template>
  <div v-if="showBanner" class="platform-banner" :class="type">
    <div class="banner-icon">
      <svg v-if="type === 'warning'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
        <line x1="12" y1="9" x2="12" y2="13"/>
        <line x1="12" y1="17" x2="12.01" y2="17"/>
      </svg>
      <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"/>
        <line x1="12" y1="8" x2="12" y2="12"/>
        <line x1="12" y1="16" x2="12.01" y2="16"/>
      </svg>
    </div>
    <div class="banner-content">
      <div class="banner-title">{{ title }}</div>
      <div class="banner-message">{{ message }}</div>
    </div>
    <button v-if="dismissible" class="banner-close" @click="dismiss">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="18" y1="6" x2="6" y2="18"/>
        <line x1="6" y1="6" x2="18" y2="18"/>
      </svg>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineProps<{
  type: 'warning' | 'info'
  title: string
  message: string
  dismissible?: boolean
}>()

const showBanner = ref(true)

function dismiss() {
  showBanner.value = false
}
</script>

<style scoped>
.platform-banner {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 6px;
  margin-bottom: 12px;
  font-size: 13px;
}

.platform-banner.warning {
  background: #fff3e0;
  border: 1px solid #ffe0b2;
  color: #e65100;
}

.platform-banner.info {
  background: #e3f2fd;
  border: 1px solid #bbdefb;
  color: #1565c0;
}

.banner-icon {
  flex-shrink: 0;
  margin-top: 2px;
}

.banner-content {
  flex: 1;
}

.banner-title {
  font-weight: 600;
  margin-bottom: 2px;
}

.banner-message {
  opacity: 0.9;
  line-height: 1.4;
}

.banner-close {
  flex-shrink: 0;
  background: none;
  border: none;
  cursor: pointer;
  opacity: 0.6;
  padding: 2px;
}

.banner-close:hover {
  opacity: 1;
}
</style>
