function getApiBase(): string {
  // 注意：这里不能直接调用 composable，因为 composable 只能在 setup 中调用
  // 改为在每次调用时从 localStorage 读取
  const servers = JSON.parse(localStorage.getItem('neuralswarm-servers') || '[]')
  return servers[0]?.url || 'http://localhost:8080'
}

// ── Types ──────────────────────────────────────────────

export interface WorkspaceInfo {
  path: string
  last_active: string
  session_count: number
}

export interface Session {
  id: string
  workspace: string
  created_at: string
  message_count: number
}

export interface SessionMessage {
  role: string
  content: string
  tool_calls?: any[]
  tool_call_id?: string
}

// ── Workspaces ─────────────────────────────────────────

export async function listWorkspaces(): Promise<WorkspaceInfo[]> {
  const resp = await fetch(`${getApiBase()}/api/workspaces`)
  const data = await resp.json()
  return data.workspaces || []
}

// ── Sessions ───────────────────────────────────────────

export async function createSession(workspace: string): Promise<{ session_id: string; workspace: string; created_at: string }> {
  const resp = await fetch(`${getApiBase()}/api/sessions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ workspace }),
  })
  return await resp.json()
}

export async function listSessions(workspace?: string): Promise<Session[]> {
  const url = workspace
    ? `${getApiBase()}/api/sessions?workspace=${encodeURIComponent(workspace)}`
    : `${getApiBase()}/api/sessions`
  const resp = await fetch(url)
  const data = await resp.json()
  return data.sessions || []
}

export async function getSessionMessages(sessionId: string): Promise<SessionMessage[]> {
  const resp = await fetch(`${getApiBase()}/api/sessions/${sessionId}/messages`)
  const data = await resp.json()
  return data.messages || []
}

export async function sendMessage(sessionId: string, content: string): Promise<{ message_count: number }> {
  const resp = await fetch(`${getApiBase()}/api/sessions/${sessionId}/messages`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content }),
  })
  return await resp.json()
}

export async function deleteSession(sessionId: string): Promise<void> {
  await fetch(`${getApiBase()}/api/sessions/${sessionId}`, { method: 'DELETE' })
}

// ── 旧 API 兼容导出（逐步迁移中，新代码请使用上面的 workspace/session API）──

export interface Project {
  id: string
  name: string
  path: string
  created_at: string
  updated_at: string
}

export interface Task {
  id: string
  project_id: string
  agent_id: string
  llm_id: string
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
  input: string
  output: string | null
  error: string | null
  created_at: string
  completed_at: string | null
}

export interface Agent {
  id: string
  project_id: string
  name: string
  agent_type: 'scheduler' | 'worker'
  status: 'idle' | 'planning' | 'running' | 'waiting' | 'completed' | 'failed'
  task_id: string | null
  parent_id: string | null
  llm_config: Record<string, any>
  worktree_path: string | null
  created_at: string
  updated_at: string
}

export const API_BASE = ''

export async function createProject(name: string, path: string): Promise<Project> {
  const resp = await fetch(`${getApiBase()}/api/projects`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, path }),
  })
  const data = await resp.json()
  if (!resp.ok) throw new Error(data.error?.message || 'Failed to create project')
  return data.data
}

export async function listProjects(): Promise<Project[]> {
  const resp = await fetch(`${getApiBase()}/api/projects`)
  const data = await resp.json()
  return data.items
}

export async function createTask(projectId: string, prompt: string): Promise<Task> {
  const resp = await fetch(`${getApiBase()}/api/tasks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ project_id: projectId, prompt }),
  })
  const data = await resp.json()
  if (!resp.ok) throw new Error(data.error?.message || 'Failed to create task')
  return data.data
}

export async function getTask(taskId: string): Promise<Task> {
  const resp = await fetch(`${getApiBase()}/api/tasks/${taskId}`)
  const data = await resp.json()
  return data.data
}

export async function listTasks(projectId?: string): Promise<Task[]> {
  const url = projectId
    ? `${getApiBase()}/api/tasks?project_id=${projectId}`
    : `${getApiBase()}/api/tasks`
  const resp = await fetch(url)
  const data = await resp.json()
  return data.items
}

export async function cancelTask(taskId: string): Promise<Task> {
  const resp = await fetch(`${getApiBase()}/api/tasks/${taskId}`, { method: 'DELETE' })
  const data = await resp.json()
  return data.data
}

export async function listAgents(params?: {
  project_id?: string
  status?: string
  agent_type?: string
}): Promise<{ items: Agent[]; total: number }> {
  const url = new URL(`${getApiBase()}/api/agents`)
  if (params?.project_id) url.searchParams.set('project_id', params.project_id)
  if (params?.status) url.searchParams.set('status', params.status)
  if (params?.agent_type) url.searchParams.set('agent_type', params.agent_type)
  const resp = await fetch(url.toString())
  return resp.json()
}

export async function getAgent(agentId: string): Promise<Agent> {
  const resp = await fetch(`${getApiBase()}/api/agents/${agentId}`)
  const data = await resp.json()
  return data.data
}

export async function getMemory(projectId: string, level: string, limit: number = 100): Promise<any> {
  const response = await fetch(`${getApiBase()}/api/memory/${projectId}?level=${level}&limit=${limit}`)
  return response.json()
}

export async function writeMemory(projectId: string, level: string, content: string): Promise<any> {
  const response = await fetch(`${getApiBase()}/api/memory/${projectId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ level, content })
  })
  return response.json()
}