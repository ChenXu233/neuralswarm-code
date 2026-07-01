import { registerPlugin } from '@/core/plugin-registry'
import ConflictDialog from './ConflictDialog.vue'

registerPlugin({
  id: 'builtin:conflict-dialog',
  name: 'Conflict Dialog',
  slots: {
    'dialog': {
      component: ConflictDialog,
      priority: 10,
    },
  },
})

export { default as ConflictDialog } from './ConflictDialog.vue'
