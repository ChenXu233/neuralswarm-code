import { registerPlugin } from '@/core/plugin-registry'
import SettingsAction from './SettingsAction.vue'

registerPlugin({
  id: 'builtin:settings',
  name: 'Settings',
  slots: {
    'activity:settings': {
      component: SettingsAction,
      icon: SettingsAction,
      priority: 10,
    },
  },
})

export { default as SettingsPanel } from './SettingsPanel.vue'
export { default as SettingsAction } from './SettingsAction.vue'
