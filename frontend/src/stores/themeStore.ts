import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { THEME_PRESETS, DEFAULT_THEME_ID, applyThemeToCssVars, type ThemePreset } from '@/constants/themeColors'

export const useThemeStore = defineStore('theme', () => {
  const storedTheme = typeof window !== 'undefined' ? localStorage.getItem('solene_theme_color') : null
  const initialThemeId = storedTheme && THEME_PRESETS.some(p => p.id === storedTheme)
    ? storedTheme
    : DEFAULT_THEME_ID

  const activeThemeId = ref<string>(initialThemeId)

  const currentTheme = computed<ThemePreset>(() => {
    return THEME_PRESETS.find(p => p.id === activeThemeId.value) || THEME_PRESETS[0]
  })

  const availableThemes = computed<ThemePreset[]>(() => THEME_PRESETS)

  function setTheme(themeId: string) {
    const targetPreset = THEME_PRESETS.find(p => p.id === themeId)
    if (!targetPreset) return

    activeThemeId.value = themeId
    applyThemeToCssVars(targetPreset)
    if (typeof window !== 'undefined') {
      localStorage.setItem('solene_theme_color', themeId)
    }
  }

  function resetTheme() {
    setTheme(DEFAULT_THEME_ID)
  }

  function initTheme() {
    const saved = typeof window !== 'undefined' ? localStorage.getItem('solene_theme_color') : null
    const validPreset = THEME_PRESETS.find(p => p.id === saved)
    const presetToApply = validPreset || THEME_PRESETS.find(p => p.id === DEFAULT_THEME_ID) || THEME_PRESETS[0]

    activeThemeId.value = presetToApply.id
    applyThemeToCssVars(presetToApply)
  }

  return {
    activeThemeId,
    currentTheme,
    availableThemes,
    setTheme,
    resetTheme,
    initTheme,
  }
})
