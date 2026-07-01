import { registerPlugin } from '@/core/plugin-registry'
import ChatPanel from './ChatPanel.vue'
import ChatAction from './ChatAction.vue'

registerPlugin({
  id: 'builtin:chat',
  name: 'Chat Panel',
  slots: {
    'activity:action': {
      component: ChatAction,
      icon: ChatAction,
      priority: 10,
      panelId: 'chat',
    },
    'sidebar:panel': {
      component: ChatPanel,
      priority: 10,
      panelId: 'chat',
      panelLabel: 'sidebar.chat',
    },
  },
})

// 保持向后兼容——其他文件仍可 import
export { default as ChatPanel } from './ChatPanel.vue'
export { default as ChatAction } from './ChatAction.vue'
