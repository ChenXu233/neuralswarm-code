<script setup lang="ts">
import { ref } from 'vue'
import { X, Server, Palette, Globe, Monitor } from 'lucide-vue-next'
import StatusDot from '../ui/StatusDot.vue'
import { useTheme } from '../../composables/useTheme'
import { useServerConnection } from '../../composables/useServerConnection'
import { useLocale } from '../../composables/useLocale'
import type { Theme } from '../../composables/useTheme'

const emit = defineEmits<{ close: [] }>()

const { theme, setTheme, fontSize, setFontSize } = useTheme()
const { servers, activeServerId, addServer, connectServer, disconnectServer, removeServer } = useServerConnection()
const { currentLocale, supportedLocales, setLocale } = useLocale()

type Section = 'servers' | 'appearance' | 'language'
const activeSection = ref<Section>('servers')

const showAddForm = ref(false)
const newName = ref('')
const newUrl = ref('')
const newToken = ref('')

const themes: { value: Theme; label: string; descKey: string }[] = [
  { value: 'warm-stone', label: 'Warm Stone', descKey: 'settings.themeWarmStoneDesc' },
  { value: 'dark-slate', label: 'Dark Slate', descKey: 'settings.themeDarkSlateDesc' },
  { value: 'pure-minimal', label: 'Pure Minimal', descKey: 'settings.themePureMinimalDesc' },
  { value: 'amber-glow', label: 'Amber Glow', descKey: 'settings.themeAmberGlowDesc' },
]

const fontSizes = [
  { value: 'small' as const, label: 'S', px: '10px' },
  { value: 'medium' as const, label: 'M', px: '12px' },
  { value: 'large' as const, label: 'L', px: '14px' },
  { value: 'xl' as const, label: 'XL', px: '16px' },
]

const navItems: { id: Section; icon: typeof Server; labelKey: string }[] = [
  { id: 'servers', icon: Server, labelKey: 'settings.servers' },
  { id: 'appearance', icon: Palette, labelKey: 'settings.appearance' },
  { id: 'language', icon: Globe, labelKey: 'settings.language' },
]

async function handleAddServer() {
  if (!newName.value || !newUrl.value) return
  await addServer({
    name: newName.value,
    url: newUrl.value,
    token: newToken.value || undefined
  })
  newName.value = ''
  newUrl.value = ''
  newToken.value = ''
  showAddForm.value = false
}
</script>

<template>
  <div class="settings-overlay" @click.self="emit('close')">
    <div class="settings-page">
      <!-- Header -->
      <header class="settings-header">
        <div class="header-title">
          <Monitor :size="18" />
          <span>{{ $t('settings.title') }}</span>
        </div>
        <button class="close-btn" @click="emit('close')">
          <X :size="18" />
        </button>
      </header>

      <div class="settings-body">
        <!-- Left nav -->
        <nav class="settings-nav">
          <button
            v-for="item in navItems"
            :key="item.id"
            :class="['nav-item', { active: activeSection === item.id }]"
            @click="activeSection = item.id"
          >
            <component :is="item.icon" :size="16" />
            <span>{{ $t(item.labelKey) }}</span>
          </button>
        </nav>

        <!-- Right content -->
        <div class="settings-main">
          <!-- Servers -->
          <section v-if="activeSection === 'servers'" class="content-section">
            <h2 class="section-title">{{ $t('settings.servers') }}</h2>
            <p class="section-desc">{{ $t('settings.serversDesc') }}</p>

            <div class="server-list">
              <div
                v-for="server in servers"
                :key="server.id"
                :class="['server-card', { active: server.id === activeServerId }]"
              >
                <div class="server-info">
                  <StatusDot :status="server.status === 'connected' ? 'connected' : 'disconnected'" />
                  <div class="server-detail">
                    <span class="server-name" @click="activeServerId = server.id">{{ server.name }}</span>
                    <span class="server-status">{{ server.status }}</span>
                  </div>
                </div>
                <div class="server-actions">
                  <button
                    v-if="server.status === 'disconnected'"
                    class="btn btn-accent"
                    @click="connectServer(server.id)"
                  >{{ $t('settings.connect') }}</button>
                  <button
                    v-else-if="server.status === 'connected'"
                    class="btn btn-ghost"
                    @click="disconnectServer(server.id)"
                  >{{ $t('settings.disconnect') }}</button>
                  <button
                    v-else
                    class="btn btn-ghost"
                    disabled
                  >{{ $t('settings.connecting') }}</button>
                  <button class="btn btn-danger-ghost" @click="removeServer(server.id)">
                    {{ $t('common.remove') }}
                  </button>
                </div>
              </div>
            </div>

            <!-- Add form -->
            <div v-if="showAddForm" class="add-form">
              <div class="form-row">
                <input v-model="newName" :placeholder="$t('settings.serverName')" class="form-input" />
                <input v-model="newUrl" placeholder="http://localhost:8000" class="form-input" />
                <input v-model="newToken" :placeholder="$t('settings.tokenOptional')" type="password" class="form-input" />
              </div>
              <div class="form-actions">
                <button class="btn btn-accent" @click="handleAddServer">{{ $t('common.add') }}</button>
                <button class="btn btn-ghost" @click="showAddForm = false">{{ $t('common.cancel') }}</button>
              </div>
            </div>
            <button v-else class="add-btn" @click="showAddForm = true">
              + {{ $t('settings.addServer') }}
            </button>
          </section>

          <!-- Appearance -->
          <section v-if="activeSection === 'appearance'" class="content-section">
            <h2 class="section-title">{{ $t('settings.theme') }}</h2>
            <p class="section-desc">{{ $t('settings.themeDesc') }}</p>

            <div class="theme-grid">
              <div
                v-for="t in themes"
                :key="t.value"
                :class="['theme-card', { active: theme === t.value }]"
                @click="setTheme(t.value)"
              >
                <div class="theme-preview" :data-theme-preview="t.value"></div>
                <div class="theme-info">
                  <span class="theme-name">{{ t.label }}</span>
                  <span class="theme-desc">{{ $t(t.descKey) }}</span>
                </div>
              </div>
            </div>

            <h2 class="section-title" style="margin-top: 2rem">{{ $t('settings.fontSize') }}</h2>
            <p class="section-desc">{{ $t('settings.fontSizeDesc') }}</p>

            <div class="font-size-row">
              <button
                v-for="opt in fontSizes"
                :key="opt.value"
                :class="['font-btn', { active: fontSize === opt.value }]"
                @click="setFontSize(opt.value)"
              >
                <span class="font-label">{{ opt.label }}</span>
                <span class="font-px">{{ opt.px }}</span>
              </button>
            </div>

            <h2 class="section-title" style="margin-top: 2rem">{{ $t('settings.fontFamily') }}</h2>
            <p class="section-desc">{{ $t('settings.fontFamilyDesc') }}</p>
            <input :placeholder="$t('settings.fontFamilyPlaceholder')" class="form-input wide" spellcheck="false" />
          </section>

          <!-- Language -->
          <section v-if="activeSection === 'language'" class="content-section">
            <h2 class="section-title">{{ $t('settings.language') }}</h2>
            <p class="section-desc">{{ $t('settings.languageDesc') }}</p>

            <div class="lang-list">
              <div
                v-for="loc in supportedLocales"
                :key="loc.code"
                :class="['lang-item', { active: currentLocale === loc.code }]"
                @click="setLocale(loc.code)"
              >
                <span class="lang-name">{{ loc.name }}</span>
                <span v-if="currentLocale === loc.code" class="lang-check">✓</span>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.settings-overlay {
  position: fixed;
  inset: 0;
  left: var(--activity-bar-width);
  z-index: var(--z-overlay);
  background: var(--color-overlay);
  display: flex;
  align-items: center;
  justify-content: center;
  animation: fadeIn var(--transition-normal) var(--ease-out);
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.settings-page {
  width: calc(100vw - var(--activity-bar-width) - 4rem);
  max-width: 56rem;
  height: calc(100vh - 4rem);
  background: var(--color-surface);
  border-radius: var(--radius-xl);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-xl);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: slideUp var(--transition-slow) var(--ease-out);
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(12px) scale(0.98); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

/* Header */
.settings-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1.25rem;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-surface);
  flex-shrink: 0;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--color-text);
}

.close-btn {
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
  border: none;
  background: transparent;
  color: var(--color-text-tertiary);
  cursor: pointer;
  transition: background var(--transition-fast), color var(--transition-fast);
}

.close-btn:hover {
  background: var(--color-surface-hover);
  color: var(--color-text);
}

/* Body */
.settings-body {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* Left nav */
.settings-nav {
  width: 10rem;
  border-right: 1px solid var(--color-border);
  padding: 0.75rem 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex-shrink: 0;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  border-radius: var(--radius-md);
  border: none;
  background: transparent;
  color: var(--color-text-secondary);
  font-size: var(--text-sm);
  cursor: pointer;
  transition: background var(--transition-fast), color var(--transition-fast);
  text-align: left;
}

.nav-item:hover {
  background: var(--color-surface-hover);
  color: var(--color-text);
}

.nav-item.active {
  background: var(--color-accent-soft);
  color: var(--color-accent);
  font-weight: var(--font-medium);
}

/* Right content */
.settings-main {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem 2rem;
}

.content-section {
  max-width: 36rem;
}

.section-title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--color-text);
  margin: 0 0 0.25rem;
}

.section-desc {
  font-size: var(--text-sm);
  color: var(--color-text-tertiary);
  margin: 0 0 1.25rem;
}

/* Server cards */
.server-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.server-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  transition: border-color var(--transition-fast), background var(--transition-fast);
}

.server-card:hover {
  border-color: var(--color-border-strong);
}

.server-card.active {
  border-color: var(--color-accent);
  background: var(--color-accent-soft);
}

.server-info {
  display: flex;
  align-items: center;
  gap: 0.625rem;
}

.server-detail {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.server-name {
  font-size: var(--text-base);
  font-weight: var(--font-medium);
  color: var(--color-text);
  cursor: pointer;
}

.server-status {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
}

.server-actions {
  display: flex;
  gap: 0.375rem;
}

/* Buttons */
.btn {
  padding: 0.375rem 0.75rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  background: transparent;
  font-size: var(--text-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
  white-space: nowrap;
}

.btn-accent {
  background: var(--color-accent);
  border-color: var(--color-accent);
  color: var(--color-surface);
}

.btn-accent:hover {
  opacity: 0.9;
}

.btn-ghost {
  color: var(--color-text-secondary);
}

.btn-ghost:hover {
  background: var(--color-surface-hover);
}

.btn-danger-ghost {
  color: var(--color-error);
  border-color: transparent;
}

.btn-danger-ghost:hover {
  background: var(--color-error-soft);
}

/* Add form */
.add-form {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 1rem;
}

.form-row {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.form-input {
  flex: 1;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  font-size: var(--text-sm);
  color: var(--color-text);
  outline: none;
  font-family: var(--font-mono);
  transition: border-color var(--transition-fast);
}

.form-input:focus {
  border-color: var(--color-accent);
}

.form-input.wide {
  width: 100%;
  max-width: 24rem;
}

.form-actions {
  display: flex;
  gap: 0.5rem;
}

.add-btn {
  padding: 0.5rem 1rem;
  border: 1px dashed var(--color-border);
  border-radius: var(--radius-md);
  background: transparent;
  color: var(--color-text-tertiary);
  font-size: var(--text-sm);
  cursor: pointer;
  transition: border-color var(--transition-fast), color var(--transition-fast);
}

.add-btn:hover {
  border-color: var(--color-text-tertiary);
  color: var(--color-text-secondary);
}

/* Theme grid */
.theme-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}

.theme-card {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  cursor: pointer;
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.theme-card:hover {
  border-color: var(--color-border-strong);
}

.theme-card.active {
  border-color: var(--color-accent);
  box-shadow: 0 0 0 1px var(--color-accent);
}

.theme-preview {
  height: 3.5rem;
  background: var(--color-bg);
  border-bottom: 1px solid var(--color-border);
}

.theme-preview[data-theme-preview="warm-stone"] {
  background: linear-gradient(135deg, #faf8f5 50%, #f5f3f0 50%);
}

.theme-preview[data-theme-preview="dark-slate"] {
  background: linear-gradient(135deg, #1a1d23 50%, #25282e 50%);
}

.theme-preview[data-theme-preview="pure-minimal"] {
  background: linear-gradient(135deg, #ffffff 50%, #fafafa 50%);
}

.theme-preview[data-theme-preview="amber-glow"] {
  background: linear-gradient(135deg, #0d0d0d 50%, #141414 50%);
}

.theme-info {
  padding: 0.625rem 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.theme-name {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--color-text);
}

.theme-desc {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
}

/* Font size */
.font-size-row {
  display: flex;
  gap: 0.5rem;
}

.font-btn {
  flex: 1;
  padding: 0.625rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: transparent;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
  transition: border-color var(--transition-fast), background var(--transition-fast);
}

.font-btn:hover {
  border-color: var(--color-border-strong);
}

.font-btn.active {
  border-color: var(--color-accent);
  background: var(--color-accent-soft);
}

.font-label {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--color-text);
}

.font-px {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
}

/* Language */
.lang-list {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.lang-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.625rem 1rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: border-color var(--transition-fast), background var(--transition-fast);
}

.lang-item:hover {
  border-color: var(--color-border-strong);
}

.lang-item.active {
  border-color: var(--color-accent);
  background: var(--color-accent-soft);
}

.lang-name {
  font-size: var(--text-base);
  color: var(--color-text);
}

.lang-check {
  color: var(--color-accent);
  font-weight: var(--font-semibold);
}
</style>
