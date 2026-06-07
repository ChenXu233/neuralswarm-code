import { isTauri } from '../utils/platform'

export function useNotification() {
  async function notify(title: string, body: string) {
    if (isTauri()) {
      // Tauri: use native notification
      try {
        // @ts-ignore - only available in Tauri runtime
        const { sendNotification } = await import('@tauri-apps/plugin-notification')
        sendNotification({ title, body })
      } catch {
        // Fallback to browser notification
        browserNotify(title, body)
      }
    } else {
      browserNotify(title, body)
    }
  }

  function browserNotify(title: string, body: string) {
    if ('Notification' in window) {
      if (Notification.permission === 'granted') {
        new Notification(title, { body })
      } else if (Notification.permission !== 'denied') {
        Notification.requestPermission().then(permission => {
          if (permission === 'granted') {
            new Notification(title, { body })
          }
        })
      }
    }
  }

  return { notify }
}
