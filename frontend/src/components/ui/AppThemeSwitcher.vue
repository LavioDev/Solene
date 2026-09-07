<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { Palette, Check, RotateCcw } from 'lucide-vue-next'
import { useThemeStore } from '@/stores/themeStore'

const { t } = useI18n()
const themeStore = useThemeStore()

const isOpen = ref(false)
const containerRef = ref<HTMLElement | null>(null)

function toggleDropdown() {
  isOpen.value = !isOpen.value
}

function selectTheme(themeId: string) {
  themeStore.setTheme(themeId)
}

function handleReset() {
  themeStore.resetTheme()
}

function handleClickOutside(event: MouseEvent) {
  if (containerRef.value && !containerRef.value.contains(event.target as Node)) {
    isOpen.value = false
  }
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape' && isOpen.value) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<template>
  <div ref="containerRef" class="relative">
    <!-- Header Trigger Button -->
    <button
      type="button"
      @click.stop="toggleDropdown"
      :title="t('theme.title')"
      class="p-2 rounded-xl text-ink-muted hover:text-primary-600 hover:bg-surface-raised transition-colors cursor-pointer border border-transparent hover:border-border/60 relative group"
    >
      <Palette class="w-4 h-4 transition-transform group-hover:scale-110" />
      <!-- Current theme active color dot -->
      <span
        class="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full ring-1 ring-white"
        :style="{ backgroundColor: themeStore.currentTheme.previewColor }"
      />
    </button>

    <!-- Theme Settings Popover -->
    <transition
      enter-active-class="transition duration-150 ease-out"
      enter-from-class="transform scale-95 opacity-0 -translate-y-1"
      enter-to-class="transform scale-100 opacity-100 translate-y-0"
      leave-active-class="transition duration-100 ease-in"
      leave-from-class="transform scale-100 opacity-100 translate-y-0"
      leave-to-class="transform scale-95 opacity-0 -translate-y-1"
    >
      <div
        v-if="isOpen"
        class="absolute right-0 top-full mt-2 w-72 p-3 bg-white/95 backdrop-blur-md border border-border rounded-2xl shadow-xl space-y-3 z-[100] select-none"
      >
        <!-- Popover Header -->
        <div class="flex items-center justify-between pb-2 border-b border-border/60">
          <div>
            <h4 class="text-xs font-bold text-ink leading-tight">{{ t('theme.title') }}</h4>
            <p class="text-[10px] text-ink-muted mt-0.5">{{ t('theme.subtitle') }}</p>
          </div>
          <button
            type="button"
            @click="handleReset"
            :title="t('theme.reset')"
            class="p-1 rounded-lg text-ink-faint hover:text-primary-600 hover:bg-surface-raised transition-colors cursor-pointer"
          >
            <RotateCcw class="w-3.5 h-3.5" />
          </button>
        </div>

        <!-- Presets Grid -->
        <div class="space-y-1.5">
          <div class="text-[10px] font-bold uppercase tracking-wider text-ink-faint">
            {{ t('theme.primaryColor') }}
          </div>
          <div class="grid grid-cols-3 gap-1.5">
            <button
              v-for="preset in themeStore.availableThemes"
              :key="preset.id"
              type="button"
              @click="selectTheme(preset.id)"
              class="flex flex-col items-center gap-1.5 p-2 rounded-xl transition-all border cursor-pointer group"
              :class="[
                themeStore.activeThemeId === preset.id
                  ? 'bg-primary-50/80 border-primary-400 shadow-2xs ring-1 ring-primary-400/40'
                  : 'bg-surface-subtle hover:bg-surface-raised border-border/60 hover:border-border'
              ]"
            >
              <!-- Color Swatch Circle with Check indicator -->
              <div
                class="w-6 h-6 rounded-full flex items-center justify-center shadow-xs transition-transform group-hover:scale-105"
                :class="[
                  themeStore.activeThemeId === preset.id
                    ? 'ring-2 ring-offset-1.5 ring-primary-500'
                    : ''
                ]"
                :style="{ backgroundColor: preset.previewColor }"
              >
                <Check
                  v-if="themeStore.activeThemeId === preset.id"
                  class="w-3.5 h-3.5 drop-shadow-xs"
                  :class="preset.id === 'yellow' ? 'text-amber-950 stroke-[3]' : 'text-white stroke-[2.5]'"
                />
              </div>
              <!-- Swatch Label -->
              <span
                class="text-[10px] truncate max-w-full transition-colors"
                :class="[
                  themeStore.activeThemeId === preset.id
                    ? 'text-primary-700 font-bold'
                    : 'text-ink-muted group-hover:text-ink font-medium'
                ]"
              >
                {{ t(preset.nameKey) }}
              </span>
            </button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>
