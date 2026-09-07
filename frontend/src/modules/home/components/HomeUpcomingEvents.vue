<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { EventOccurrence } from '@/modules/calendar/types'
import { ArrowRight, Calendar as CalendarIcon } from 'lucide-vue-next'

interface Props {
  occurrences: EventOccurrence[]
  formatDisplayDate: (dateStr: string) => string
  calculateDaysRemaining: (dateStr: string) => number
}

defineProps<Props>()

const emit = defineEmits<{
  (e: 'view-calendar'): void
}>()

const { t } = useI18n()
</script>

<template>
  <div class="p-4 sm:p-5 rounded-2xl bg-white border border-border/60 shadow-2xs space-y-3">
    <!-- Header -->
    <div class="flex items-center justify-between border-b border-border/40 pb-3">
      <h2 class="text-xs font-bold uppercase tracking-wider text-ink font-mono flex items-center gap-1.5">
        <CalendarIcon class="w-3.5 h-3.5 text-violet-600" />
        <span>{{ t('home.upcomingEvents.title') }}</span>
      </h2>
      <button
        type="button"
        @click="emit('view-calendar')"
        class="text-[11px] font-semibold text-violet-600 hover:text-violet-700 cursor-pointer inline-flex items-center gap-0.5"
      >
        <span>{{ t('home.upcomingEvents.viewCalendar') }}</span>
        <ArrowRight class="w-3 h-3" />
      </button>
    </div>

    <!-- Upcoming List -->
    <div v-if="occurrences.length > 0" class="space-y-2 pt-1">
      <div
        v-for="occ in occurrences"
        :key="occ.event_id"
        class="p-2.5 rounded-xl hover:bg-surface-subtle transition-colors flex items-center justify-between gap-2"
      >
        <div class="min-w-0">
          <p class="text-xs font-semibold text-ink truncate">{{ occ.title }}</p>
          <p class="text-[11px] text-ink-muted font-mono mt-0.5">
            {{ formatDisplayDate(occ.date) }}
          </p>
        </div>
        <span class="text-[10px] font-bold text-violet-700 bg-violet-50 px-2 py-0.5 rounded-full font-mono shrink-0">
          {{ t('home.upcomingEvents.inDays', { n: calculateDaysRemaining(occ.date) }) }}
        </span>
      </div>
    </div>

    <p v-else class="text-xs text-ink-faint py-4 text-center">
      {{ t('home.upcomingEvents.empty') }}
    </p>
  </div>
</template>
