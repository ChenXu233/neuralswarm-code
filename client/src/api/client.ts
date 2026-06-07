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
