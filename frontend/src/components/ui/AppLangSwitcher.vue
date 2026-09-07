<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { setLanguage } from '@/i18n'
import { Globe, Check, ChevronDown } from 'lucide-vue-next'

interface Props {
  collapsed?: boolean
  direction?: 'up' | 'down'
  align?: 'left' | 'right'
}

withDefaults(defineProps<Props>(), {
  collapsed: false,
  direction: 'down',
  align: 'right',
})

const { locale, t } = useI18n()

const isOpen = ref(false)
const dropdownRef = ref<HTMLElement | null>(null)

const languages = [
  { code: 'vi', label: 'Tiếng Việt', short: 'VI' },
  { code: 'en', label: 'English',    short: 'EN' },
  { code: 'fr', label: 'Français',   short: 'FR' },
  { code: 'zh', label: '中文',        short: 'ZH' },
]

const currentLanguage = computed(() => {
  return languages.find(l => l.code === locale.value) || languages[0]
})

function selectLang(code: 'en' | 'vi' | 'fr' | 'zh') {
  setLanguage(code)
  isOpen.value = false
}

function handleClickOutside(e: MouseEvent) {
  if (dropdownRef.value && !dropdownRef.value.contains(e.target as Node)) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<template>
  <div
    ref="dropdownRef"
    class="relative select-none"
    :class="collapsed ? 'inline-block' : 'w-full'"
  >

    <!-- Collapsed Mode Trigger: Icon-only Button -->
    <button
      v-if="collapsed"
      type="button"
      @click.stop="isOpen = !isOpen"
      :title="t('common.language')"
      class="p-2 rounded-xl text-ink-muted hover:text-primary-600 hover:bg-surface-raised transition-colors cursor-pointer border border-transparent hover:border-border/60 flex items-center justify-center"
      :class="isOpen ? 'bg-primary-50 text-primary-700 !border-primary-200' : ''"
    >
      <Globe class="w-4 h-4 text-primary-500 shrink-0" />
    </button>

    <!-- Expanded Mode Trigger: Full width row with clear spacing and badge -->
    <button
      v-else
      type="button"
      @click.stop="isOpen = !isOpen"
      class="w-full flex items-center justify-between px-3 py-2 rounded-xl text-ink-muted hover:bg-surface-raised hover:text-ink transition-colors cursor-pointer group"
      :class="isOpen ? 'bg-surface-raised text-ink' : ''"
    >
      <!-- Left icon & Label -->
      <div class="flex items-center gap-2.5 text-ink-faint group-hover:text-primary-600 shrink-0">
        <Globe class="w-4 h-4 text-primary-500 shrink-0" />
        <span class="text-xs font-medium text-ink-muted group-hover:text-ink">
          {{ t('common.language') }}
        </span>
      </div>

      <!-- Right Short Code Badge & Chevron -->
      <div class="flex items-center gap-1.5 shrink-0 ml-2">
        <span class="text-[11px] font-bold text-primary-700 bg-primary-100/90 px-1.5 py-0.5 rounded font-mono">
          {{ currentLanguage.short }}
        </span>
        <ChevronDown
          class="w-3.5 h-3.5 text-ink-faint transition-transform duration-200"
          :class="isOpen ? 'rotate-180 text-primary-600' : ''"
        />
      </div>
    </button>

    <!-- Native UI Popover Dropdown Menu -->
    <transition
      enter-active-class="transition duration-150 ease-out"
      :enter-from-class="direction === 'up' ? 'transform scale-95 opacity-0 translate-y-1' : 'transform scale-95 opacity-0 -translate-y-1'"
      enter-to-class="transform scale-100 opacity-100 translate-y-0"
      leave-active-class="transition duration-100 ease-in"
      leave-from-class="transform scale-100 opacity-100 translate-y-0"
      :leave-to-class="direction === 'up' ? 'transform scale-95 opacity-0 translate-y-1' : 'transform scale-95 opacity-0 -translate-y-1'"
    >
      <div
        v-if="isOpen"
        class="absolute w-44 bg-white/95 backdrop-blur-md border border-border rounded-2xl shadow-xl p-1.5 space-y-0.5 z-50"
        :class="[
          direction === 'up' ? 'bottom-full mb-2' : 'top-full mt-2',
          align === 'right' ? 'right-0' : 'left-0'
        ]"
      >
        <div class="px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider text-ink-faint border-b border-border/50 mb-1">
          {{ t('common.language') }}
        </div>

        <button
          v-for="lang in languages"
          :key="lang.code"
          type="button"
          @click="selectLang(lang.code as any)"
          class="w-full flex items-center justify-between px-2.5 py-1.5 rounded-xl text-xs transition-colors cursor-pointer"
          :class="locale === lang.code
            ? 'bg-primary-50 text-primary-700 font-semibold shadow-2xs'
            : 'text-ink-muted hover:bg-surface-raised hover:text-ink font-medium'"
        >
          <div class="flex items-center gap-2">
            <span class="w-5 text-[10px] font-mono font-bold text-primary-600 bg-primary-100/80 px-1 py-0.5 rounded text-center">
              {{ lang.short }}
            </span>
            <span>{{ lang.label }}</span>
          </div>

          <Check v-if="locale === lang.code" class="w-3.5 h-3.5 text-primary-600 shrink-0" />
        </button>
      </div>
    </transition>

  </div>
</template>
