import { createI18n } from 'vue-i18n'
import en from './en.json'
import zh from './zh.json'
import jp from './jp.json'
import ru from './ru.json'

const SUPPORTED_LOCALES = ['en', 'zh', 'jp', 'ru']

function getInitialLocale(): string {
  // 1. 优先使用用户手动设置
  const saved = localStorage.getItem('locale')
  if (saved && SUPPORTED_LOCALES.includes(saved)) return saved

  // 2. 浏览器语言检测（Tauri 检测在异步函数中处理）
  const browserLang = navigator.language.split('-')[0]
  if (SUPPORTED_LOCALES.includes(browserLang)) return browserLang

  return 'en'
}

const i18n = createI18n({
  legacy: false,
  locale: getInitialLocale(),
  fallbackLocale: 'en',
  messages: {
    en,
    zh,
    jp,
    ru
  }
})

// 异步检测 Tauri 系统语言（仅在 Tauri 环境中）
if (typeof window !== 'undefined' && '__TAURI__' in window) {
  const tauriOsPlugin = '@tauri-apps/plugin-os'
  import(tauriOsPlugin).then(({ locale }) => {
    return locale()
  }).then((systemLocale) => {
    const lang = systemLocale?.split('-')[0]
    if (lang && SUPPORTED_LOCALES.includes(lang)) {
      const saved = localStorage.getItem('locale')
      if (!saved) {
        i18n.global.locale.value = lang as 'en' | 'zh' | 'jp' | 'ru'
      }
    }
  }).catch(() => {
    // ignore errors - 非 Tauri 环境会失败，这是正常的
  })
}

export default i18n
