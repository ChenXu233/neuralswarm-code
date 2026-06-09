// client/src/utils/platform.ts
/**
 * 检测当前运行环境
 */

// 检测是否在 Tauri 环境中
export function isTauri(): boolean {
  return typeof window !== 'undefined' && '__TAURI__' in window
}

// 检测是否在桌面环境中（Tauri 或 Electron）
export function isDesktop(): boolean {
  return isTauri() || (typeof window !== 'undefined' && '__ELECTRON__' in window)
}

// 检测是否在浏览器中
export function isBrowser(): boolean {
  return !isDesktop()
}

// 获取平台信息
export function getPlatform(): 'tauri' | 'browser' {
  return isTauri() ? 'tauri' : 'browser'
}

// 检测是否可以打开本地文件夹（仅 Tauri）
export function canOpenLocalFolder(): boolean {
  return isTauri()
}

// 检测是否可以访问本地项目（仅 Tauri）
export function canAccessLocalProject(): boolean {
  return isTauri()
}
