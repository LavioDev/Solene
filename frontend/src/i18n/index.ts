import { createI18n } from 'vue-i18n'
import en from './locales/en'
import vi from './locales/vi'
import fr from './locales/fr'
import zh from './locales/zh'

const savedLanguage = localStorage.getItem('solene_language') || 'en'

export const i18n = createI18n({
  legacy: false, // Use Composition API mode ($t, t(), locale)
  locale: savedLanguage,
  fallbackLocale: 'en',
  messages: {
    en,
    vi,
    fr,
    zh,
  },
})

export function setLanguage(lang: 'en' | 'vi' | 'fr' | 'zh') {
  i18n.global.locale.value = lang
  localStorage.setItem('solene_language', lang)
}
