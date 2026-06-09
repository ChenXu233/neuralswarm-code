// client/src/api/tauri.ts
import { isTauri } from '@/utils/platform'

// Tauri API 类型定义
interface TauriAPI {
  invoke: (cmd: string, args?: Record<string, any>) => Promise<any>
}

// 获取 Tauri API（如果可用）
async function getTauriAPI(): Promise<TauriAPI | null> {
  if (!isTauri()) {
    return null
  }

  try {
    // 动态导入 Tauri API
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore -- @tauri-apps/api 仅在 Tauri 构建中可用
    const { invoke } = await import('@tauri-apps/api/core')
    return { invoke }
  } catch {
    return null
  }
}

// 本地操作结果类型
interface LocalOperationResult {
  success: boolean
  data?: string
  error?: string
  supported: boolean
}

/**
 * 读取本地文件
 */
export async function readLocalFile(path: string): Promise<LocalOperationResult> {
  const api = await getTauriAPI()

  if (!api) {
    return {
      success: false,
      error: '本地文件操作仅在桌面应用中可用',
      supported: false
    }
  }

  try {
    const data = await api.invoke('read_file', { path })
    return { success: true, data, supported: true }
  } catch (error) {
    return {
      success: false,
      error: String(error),
      supported: true
    }
  }
}

/**
 * 写入本地文件
 */
export async function writeLocalFile(path: string, content: string): Promise<LocalOperationResult> {
  const api = await getTauriAPI()

  if (!api) {
    return {
      success: false,
      error: '本地文件操作仅在桌面应用中可用',
      supported: false
    }
  }

  try {
    await api.invoke('write_file', { path, content })
    return { success: true, supported: true }
  } catch (error) {
    return {
      success: false,
      error: String(error),
      supported: true
    }
  }
}

/**
 * 执行本地命令
 */
export async function executeLocalCommand(command: string, cwd?: string): Promise<LocalOperationResult> {
  const api = await getTauriAPI()

  if (!api) {
    return {
      success: false,
      error: '本地命令执行仅在桌面应用中可用',
      supported: false
    }
  }

  try {
    const data = await api.invoke('execute_command', { command, cwd })
    return { success: true, data, supported: true }
  } catch (error) {
    return {
      success: false,
      error: String(error),
      supported: true
    }
  }
}

/**
 * 获取 Git 日志
 */
export async function getGitLog(path: string, limit?: number): Promise<LocalOperationResult> {
  const api = await getTauriAPI()

  if (!api) {
    return {
      success: false,
      error: 'Git 操作仅在桌面应用中可用',
      supported: false
    }
  }

  try {
    const data = await api.invoke('git_log', { path, limit })
    return { success: true, data, supported: true }
  } catch (error) {
    return {
      success: false,
      error: String(error),
      supported: true
    }
  }
}

/**
 * 获取 Git Diff
 */
export async function getGitDiff(path: string): Promise<LocalOperationResult> {
  const api = await getTauriAPI()

  if (!api) {
    return {
      success: false,
      error: 'Git 操作仅在桌面应用中可用',
      supported: false
    }
  }

  try {
    const data = await api.invoke('git_diff', { path })
    return { success: true, data, supported: true }
  } catch (error) {
    return {
      success: false,
      error: String(error),
      supported: true
    }
  }
}
