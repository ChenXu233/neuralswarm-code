import { registerPlugin } from '@/core/plugin-registry'
import MemoryPanel from './MemoryPanel.vue'
import MemoryAction from './MemoryAction.vue'

registerPlugin({
  id: 'builtin:memory',
  name: 'Memory',
  slots: {
    'activity:action': {
      component: MemoryAction,
      icon: MemoryAction,
      priority: 40,
      panelId: 'memory',
    },
    'sidebar:panel': {
      component: MemoryPanel,
      priority: 40,
      panelId: 'memory',
      panelLabel: 'sidebar.memory',
    },
  },
})

export { default as MemoryPanel } from './MemoryPanel.vue'
