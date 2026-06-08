import { ref } from 'vue'

export type Theme = 'warm-stone' | 'dark-slate' | 'pure-minimal' | 'amber-glow'
export type FontSize = 'small' | 'medium' | 'large' | 'xl'

const FONT_SIZE_MAP: Record<FontSize, number> = {
  small: 14,
  medium: 16,
  large: 18,
  xl: 20,
}

const theme = ref<Theme>((localStorage.getItem('theme') as Theme) || 'warm-stone')
const fontSize = ref<FontSize>((localStorage.getItem('fontSize') as FontSize) || 'medium')

function applyFontSize(size: FontSize) {
  document.documentElement.style.fontSize = `${FONT_SIZE_MAP[size]}px`
}

export function useTheme() {
  function setTheme(newTheme: Theme) {
    theme.value = newTheme
    localStorage.setItem('theme', newTheme)
    document.documentElement.dataset.theme = newTheme
  }

  function setFontSize(size: FontSize) {
    fontSize.value = size
    localStorage.setItem('fontSize', size)
    applyFontSize(size)
  }

  // Initialize
  document.documentElement.dataset.theme = theme.value
  applyFontSize(fontSize.value)

  return { theme, setTheme, fontSize, setFontSize }
}
