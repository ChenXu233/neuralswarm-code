import { isTauri } from './platform'

export async function setTitle(title: string) {
  if (isTauri()) {
    try {
      // @ts-ignore - only available in Tauri runtime
      const { getCurrentWindow } = await import('@tauri-apps/api/window')
      await getCurrentWindow().setTitle(title)
    } catch {
      document.title = title
    }
  } else {
    document.title = title
  }
}

export async function minimize() {
  if (isTauri()) {
    // @ts-ignore - only available in Tauri runtime
    const { getCurrentWindow } = await import('@tauri-apps/api/window')
    await getCurrentWindow().minimize()
  }
}

export async function toggleMaximize() {
  if (isTauri()) {
    // @ts-ignore - only available in Tauri runtime
    const { getCurrentWindow } = await import('@tauri-apps/api/window')
    await getCurrentWindow().toggleMaximize()
  }
}
