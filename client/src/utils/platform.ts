// client/src/utils/platform.ts
export const isTauri = () => '__TAURI__' in window
export const isMobile = () => /Android|iPhone|iPad/i.test(navigator.userAgent)

export type Platform = 'tauri' | 'browser' | 'mobile'

export function getPlatform(): Platform {
  if (isTauri()) return 'tauri'
  if (isMobile()) return 'mobile'
  return 'browser'
}

export function canOpenLocalFolder(): boolean {
  return isTauri()
}

export function canAccessLocalProject(): boolean {
  return isTauri()
}
