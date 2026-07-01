import { ref, readonly } from 'vue'
import { listWorkspaces, type WorkspaceInfo } from '@/api/client'

export function useWorkspace() {
  const workspaces = ref<WorkspaceInfo[]>([])
  const currentWorkspace = ref<string | null>(null)
  const loading = ref(false)

  async function loadWorkspaces() {
    loading.value = true
    try {
      workspaces.value = await listWorkspaces()
    } catch (e) {
      console.error('Failed to load workspaces:', e)
    } finally {
      loading.value = false
    }
  }

  function selectWorkspace(path: string) {
    currentWorkspace.value = path
  }

  function clearWorkspace() {
    currentWorkspace.value = null
  }

  return {
    workspaces: readonly(workspaces),
    currentWorkspace: readonly(currentWorkspace),
    loading: readonly(loading),
    loadWorkspaces,
    selectWorkspace,
    clearWorkspace,
  }
}
