<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { Calendar as CalendarIcon, StickyNote, Users } from 'lucide-vue-next'
import AppButton from '@/components/ui/AppButton.vue'

const emit = defineEmits<{
  (e: 'navigate', path: string): void
}>()

const { t } = useI18n()
</script>

<template>
  <div class="pt-2 flex flex-wrap items-center justify-center gap-2 sm:gap-3">
    <AppButton
      variant="secondary"
      size="sm"
      @click="emit('navigate', '/calendar')"
      class="bg-white hover:bg-surface-subtle shadow-2xs border border-border/60 text-xs text-ink"
    >
      <CalendarIcon class="w-3.5 h-3.5 mr-1.5 text-primary-600" />
      {{ t('home.quickActions.viewCalendar') }}
    </AppButton>

    <AppButton
      variant="secondary"
      size="sm"
      @click="emit('navigate', '/memories')"
      class="bg-white hover:bg-surface-subtle shadow-2xs border border-border/60 text-xs text-ink"
    >
      <StickyNote class="w-3.5 h-3.5 mr-1.5 text-amber-500" />
      kỷ niệm
    </AppButton>

    <AppButton
      variant="secondary"
      size="sm"
      @click="emit('navigate', '/couples')"
      class="bg-white hover:bg-surface-subtle shadow-2xs border border-border/60 text-xs text-ink"
    >
      <Users class="w-3.5 h-3.5 mr-1.5 text-primary-600" />
      {{ t('home.quickActions.viewCouples') }}
    </AppButton>
  </div>
</template>
