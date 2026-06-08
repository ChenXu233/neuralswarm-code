const API_BASE = 'http://localhost:8000'

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

export async function createProject(name: string, path: string): Promise<Project> {
  const resp = await fetch(`${API_BASE}/api/projects`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, path }),
  })
  const data = await resp.json()
  if (!resp.ok) throw new Error(data.error?.message || 'Failed to create project')
  return data.data
}

export async function listProjects(): Promise<Project[]> {
  const resp = await fetch(`${API_BASE}/api/projects`)
  const data = await resp.json()
  return data.items
}

export async function createTask(projectId: string, prompt: string): Promise<Task> {
  const resp = await fetch(`${API_BASE}/api/tasks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ project_id: projectId, prompt }),
  })
  const data = await resp.json()
  if (!resp.ok) throw new Error(data.error?.message || 'Failed to create task')
  return data.data
}

export async function getTask(taskId: string): Promise<Task> {
  const resp = await fetch(`${API_BASE}/api/tasks/${taskId}`)
  const data = await resp.json()
  return data.data
}

export async function listTasks(projectId?: string): Promise<Task[]> {
  const url = projectId
    ? `${API_BASE}/api/tasks?project_id=${projectId}`
    : `${API_BASE}/api/tasks`
  const resp = await fetch(url)
  const data = await resp.json()
  return data.items
}

export async function cancelTask(taskId: string): Promise<Task> {
  const resp = await fetch(`${API_BASE}/api/tasks/${taskId}`, { method: 'DELETE' })
  const data = await resp.json()
  return data.data
}

// ── Agent API ─────────────────────────────────────────────────

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

export async function listAgents(params?: {
  project_id?: string
  status?: string
  agent_type?: string
}): Promise<{ items: Agent[]; total: number }> {
  const url = new URL(`${API_BASE}/api/agents`)
  if (params?.project_id) url.searchParams.set('project_id', params.project_id)
  if (params?.status) url.searchParams.set('status', params.status)
  if (params?.agent_type) url.searchParams.set('agent_type', params.agent_type)
  const resp = await fetch(url.toString())
  return resp.json()
}

export async function getAgent(agentId: string): Promise<Agent> {
  const resp = await fetch(`${API_BASE}/api/agents/${agentId}`)
  const data = await resp.json()
  return data.data
}

// ── Conflict API ──────────────────────────────────────────────

export interface Conflict {
  id: string
  task_id: string
  file_path: string
  agent_id: string
  other_agent_id: string
  old_hash: string
  current_hash: string
  current_content: string
  new_content: string
  status: 'pending' | 'resolved' | 'timeout'
  action: 're_read' | 'overwrite' | 'submit_to_scheduler' | null
  created_at: string
  resolved_at: string | null
}

export async function getConflict(conflictId: string): Promise<Conflict> {
  const resp = await fetch(`${API_BASE}/api/conflicts/${conflictId}`)
  const data = await resp.json()
  return data.data
}

export async function decideConflict(
  conflictId: string,
  action: 're_read' | 'overwrite' | 'submit_to_scheduler'
): Promise<Conflict> {
  const resp = await fetch(`${API_BASE}/api/conflicts/${conflictId}/decide`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action }),
  })
  const data = await resp.json()
  return data.data
}
