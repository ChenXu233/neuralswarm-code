import { registerPlugin } from '@/core/plugin-registry'
import FilesPanel from './FilesPanel.vue'
import FileTreeAction from './FileTreeAction.vue'

registerPlugin({
  id: 'builtin:file-tree',
  name: 'File Tree',
  slots: {
    'activity:action': {
      component: FileTreeAction,
      icon: FileTreeAction,
      priority: 20,
      panelId: 'files',
    },
    'sidebar:panel': {
      component: FilesPanel,
      priority: 20,
      panelId: 'files',
      panelLabel: 'sidebar.files',
    },
  },
})

export { default as FilesPanel } from './FilesPanel.vue'
