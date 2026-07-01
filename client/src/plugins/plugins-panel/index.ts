import { registerPlugin } from '@/core/plugin-registry'
import PluginsPanel from './PluginsPanel.vue'
import PluginsAction from './PluginsAction.vue'

registerPlugin({
  id: 'builtin:plugins',
  name: 'Plugins',
  slots: {
    'activity:action': {
      component: PluginsAction,
      icon: PluginsAction,
      priority: 30,
      panelId: 'plugins',
    },
    'sidebar:panel': {
      component: PluginsPanel,
      priority: 30,
      panelId: 'plugins',
      panelLabel: 'sidebar.plugins',
    },
  },
})

export { default as PluginsPanel } from './PluginsPanel.vue'
