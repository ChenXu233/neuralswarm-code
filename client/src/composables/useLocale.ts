import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

const SUPPORTED_LOCALES = [
  { code: 'en', name: 'English' },
  { code: 'zh', name: '中文' },
  { code: 'jp', name: '日本語' },
  { code: 'ru', name: 'Русский' }
]

export function useLocale() {
  const { locale } = useI18n()
  const currentLocale = ref(locale.value)

  function setLocale(newLocale: string) {
    locale.value = newLocale
    currentLocale.value = newLocale
    localStorage.setItem('locale', newLocale)
  }

  watch(locale, (newVal) => {
    currentLocale.value = newVal
  })

  return {
    currentLocale,
    supportedLocales: SUPPORTED_LOCALES,
    setLocale
  }
}
