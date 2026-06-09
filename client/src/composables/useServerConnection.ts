import { ref, computed } from 'vue'

interface ServerConfig {
  id: string
  name: string
  url: string
  token?: string
  status: 'connected' | 'disconnected' | 'connecting'
}

const servers = ref<ServerConfig[]>([])
const activeServerId = ref<string | null>(null)

export function useServerConnection() {
  const activeServer = computed(() =>
    servers.value.find(s => s.id === activeServerId.value)
  )

  async function addServer(config: Omit<ServerConfig, 'id' | 'status'>) {
    const id = `server-${Date.now()}`
    const server: ServerConfig = {
      ...config,
      id,
      status: 'disconnected'
    }
    servers.value.push(server)

    // 保存到 localStorage
    saveServers()

    return server
  }

  async function connectServer(serverId: string) {
    const server = servers.value.find(s => s.id === serverId)
    if (!server) return false

    server.status = 'connecting'

    try {
      // 测试连接
      const response = await fetch(`${server.url}/health`)
      if (response.ok) {
        server.status = 'connected'
        activeServerId.value = serverId
        saveServers()
        return true
      }
    } catch (error) {
      console.error('Connection failed:', error)
    }

    server.status = 'disconnected'
    return false
  }

  async function disconnectServer(serverId: string) {
    const server = servers.value.find(s => s.id === serverId)
    if (server) {
      server.status = 'disconnected'
      if (activeServerId.value === serverId) {
        activeServerId.value = null
      }
      saveServers()
    }
  }

  function removeServer(serverId: string) {
    servers.value = servers.value.filter(s => s.id !== serverId)
    if (activeServerId.value === serverId) {
      activeServerId.value = null
    }
    saveServers()
  }

  function saveServers() {
    localStorage.setItem('neuralswarm-servers', JSON.stringify(servers.value))
    localStorage.setItem('neuralswarm-active-server', activeServerId.value || '')
  }

  function loadServers() {
    try {
      const saved = localStorage.getItem('neuralswarm-servers')
      if (saved) {
        servers.value = JSON.parse(saved)
      }
      activeServerId.value = localStorage.getItem('neuralswarm-active-server')
    } catch (e) {
      console.error('Failed to load servers:', e)
    }
  }

  // 初始化时加载
  loadServers()

  return {
    servers,
    activeServer,
    activeServerId,
    addServer,
    connectServer,
    disconnectServer,
    removeServer
  }
}
