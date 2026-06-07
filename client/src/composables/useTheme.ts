import { ref } from 'vue'

export type Theme = 'warm-stone' | 'dark-slate' | 'pure-minimal' | 'amber-glow'

const theme = ref<Theme>((localStorage.getItem('theme') as Theme) || 'warm-stone')

export function useTheme() {
  function setTheme(newTheme: Theme) {
    theme.value = newTheme
    localStorage.setItem('theme', newTheme)
    document.documentElement.dataset.theme = newTheme
  }

  // Initialize on first call
  document.documentElement.dataset.theme = theme.value

  return { theme, setTheme }
}
