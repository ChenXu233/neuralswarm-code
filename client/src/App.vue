import { ref, computed, provide } from 'vue'
import { useTheme } from './composables/useTheme'
import { useWorkspace } from './composables/useWorkspace'
import { useSession } from './composables/useSession'
import ActivityBar from './components/layout/ActivityBar.vue'
import Sidebar from './components/layout/Sidebar.vue'
import ChatPanel from './plugins/chat-panel/ChatPanel.vue'
import HomePage from './components/HomePage.vue'
import SessionView from './views/SessionView.vue'
import SettingsPanel from './components/sidebar/SettingsPanel.vue'
import PluginSlot from './core/plugin-slot.vue'
import ServerSetupDialog from './components/ServerSetupDialog.vue'
import { useServerConnection } from './composables/useServerConnection'
import { useI18n } from 'vue-i18n'

useI18n()
useTheme()

const { workspaces, currentWorkspace, loadWorkspaces, selectWorkspace, clearWorkspace } = useWorkspace()
const session = useSession()

const activePanel = ref<'chat' | 'files' | 'plugins' | 'memory' | null>('chat')
const showSettings = ref(false)
const showServerSetup = ref(false)

const { hasConfiguredServers } = useServerConnection()

const sidebarTitle = computed(() => {
  const titles: Record<string, string> = {
    chat: '对话',
    files: '文件',
    plugins: '插件',
    memory: '记忆',
    settings: '设置',
  }
  return activePanel.value ? titles[activePanel.value] || activePanel.value : ''
})

provide('workspace', { currentWorkspace, workspaces })
provide('session', session)

loadWorkspaces()

// 检查是否需要显示服务器设置对话框
if (!hasConfiguredServers.value) {
  showServerSetup.value = true
}

function handleSelectWorkspace(path: string) {
  selectWorkspace(path)
  session.loadSessions(path)
}

function handleBackToHome() {
  clearWorkspace()
}

function handleServerConnected() {
  showServerSetup.value = false
  loadWorkspaces()
}

function handleToggleSettings() {
  showSettings.value = !showSettings.value
}

function workspaceName(path: string) {
  return path.split(/[/\\]/).filter(Boolean).pop() || path
}
</script>

<template>
  <div id="app" class="app-layout">
    <!-- 服务器设置对话框 -->
    <ServerSetupDialog
      v-if="showServerSetup"
      @connected="handleServerConnected"
    />

    <HomePage
      v-if="!currentWorkspace"
      :workspaces="workspaces"
      @select="handleSelectWorkspace"
    />

    <template v-else>
      <div class="workspace-header">
        <button class="back-btn" @click="handleBackToHome">←</button>
        <span class="workspace-title">{{ workspaceName(currentWorkspace) }}</span>
      </div>

      <ActivityBar
        v-model:active-panel="activePanel"
        :show-settings="showSettings"
        @toggle-settings="handleToggleSettings"
      />

      <Sidebar
        v-if="activePanel && !showSettings"
        :title="sidebarTitle"
        :panel-id="activePanel"
      >
        <ChatPanel
          v-if="activePanel === 'chat'"
          :sessions="session.sessions.value"
          :active-session-id="session.currentSession.value?.id"
          @select="session.selectSession"
          @new-session="() => session.createNewSession(currentWorkspace!)"
        />
      </Sidebar>

      <div class="app-content">
        <SessionView
          v-if="session.currentSession.value"
          :session="session.currentSession.value"
          :messages="session.messages.value"
          :events="session.events.value"
          :loading="session.loading.value"
          @submit="session.send"
        />
        <div v-else class="empty-state">
          选择一个对话或创建新对话
        </div>
      </div>
    </template>

    <!-- Settings overlay -->
    <SettingsPanel v-if="showSettings" @close="showSettings = false" />
    <PluginSlot name="dialog" />
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  height: 100vh;
}

.app-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.workspace-header {
  display: none;
}

.empty-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-tertiary);
  font-size: var(--text-sm);
}
</style>