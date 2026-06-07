import { ref } from 'vue'

type Theme = 'light' | 'dark'

const theme = ref<Theme>((localStorage.getItem('theme') as Theme) || 'light')

export function useTheme() {
  function setTheme(newTheme: Theme) {
    theme.value = newTheme
    document.documentElement.dataset.theme = newTheme
    localStorage.setItem('theme', newTheme)
  }

  function toggleTheme() {
    setTheme(theme.value === 'light' ? 'dark' : 'light')
  }

  // 初始化
  document.documentElement.dataset.theme = theme.value

  return {
    theme,
    setTheme,
    toggleTheme
  }
}
