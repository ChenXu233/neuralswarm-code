import { isTauri } from './platform'

const SUPPORTED_LOCALES = ['en', 'zh', 'jp', 'ru']

export async function detectLocale(): Promise<string> {
  // 1. 优先使用用户手动设置
  const saved = localStorage.getItem('locale')
  if (saved && SUPPORTED_LOCALES.includes(saved)) return saved

  // 2. Tauri 桌面端检测系统语言
  if (isTauri()) {
    try {
      const tauriOsPlugin = '@tauri-apps/plugin-os'
      const { locale } = await import(tauriOsPlugin)
      const systemLocale = await locale()
      const lang = systemLocale?.split('-')[0]
      if (lang && SUPPORTED_LOCALES.includes(lang)) return lang
    } catch {
      // ignore errors
    }
  }

  // 3. 浏览器语言检测
  const browserLang = navigator.language.split('-')[0]
  if (SUPPORTED_LOCALES.includes(browserLang)) return browserLang

  return 'en'
}
