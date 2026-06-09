import { invoke } from '@tauri-apps/api/core'

export async function readFile(path: string): Promise<string> {
  return await invoke('read_file', { path })
}

export async function writeFile(path: string, content: string): Promise<void> {
  return await invoke('write_file', { path, content })
}

export async function executeCommand(command: string, cwd?: string): Promise<string> {
  return await invoke('execute_command', { command, cwd })
}

export async function gitLog(path: string, limit?: number): Promise<string> {
  return await invoke('git_log', { path, limit })
}

export async function gitDiff(path: string): Promise<string> {
  return await invoke('git_diff', { path })
}

// 检查是否在 Tauri 环境中
export function isTauri(): boolean {
  return typeof window !== 'undefined' && (window as any).__TAURI__ !== undefined
}
