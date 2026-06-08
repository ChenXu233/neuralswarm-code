export interface Agent {
  id: string
  name: string
  agent_type: 'scheduler' | 'worker'
  status: 'idle' | 'planning' | 'running' | 'waiting' | 'completed' | 'failed'
  task_id: string | null
  parent_id: string | null
  created_at: string
}

export interface Conflict {
  id: string
  file_path: string
  agent_id: string
  other_agent_id: string
  current_content: string
  new_content: string
  status: 'pending' | 'resolved' | 'timeout'
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
