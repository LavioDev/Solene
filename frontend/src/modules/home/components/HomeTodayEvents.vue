<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { EventOccurrence } from '@/modules/calendar/types'
import { Sparkles } from 'lucide-vue-next'

interface Props {
  occurrences: EventOccurrence[]
  todayDateStr: string
  formatDisplayDate: (dateStr: string) => string
  loading?: boolean
}

withDefaults(defineProps<Props>(), {
  loading: false,
})

const { t } = useI18n()
</script>

<template>
  <div class="p-4 sm:p-5 rounded-2xl bg-white border border-border/60 shadow-2xs space-y-3">
    <!-- Header -->
    <div class="flex items-center justify-between border-b border-border/40 pb-3">
      <h2 class="text-xs font-bold uppercase tracking-wider text-ink font-mono flex items-center gap-1.5">
        <Sparkles class="w-3.5 h-3.5 text-amber-500" />
        <span>{{ t('home.todayEvents.title') }}</span>
      </h2>
      <span class="hidden sm:inline text-[11px] text-ink-faint font-mono">{{ formatDisplayDate(todayDateStr) }}</span>
    </div>

    <!-- Skeleton Loading -->
    <div v-if="loading" class="space-y-2 pt-1">
      <div v-for="i in 2" :key="i" class="p-2.5 rounded-xl flex items-start gap-2.5 animate-pulse">
        <div class="w-2 h-2 rounded-full bg-border mt-1.5 shrink-0"></div>
        <div class="min-w-0 flex-1 space-y-1.5">
          <div class="h-3 w-3/4 bg-surface-raised rounded"></div>
          <div class="h-2.5 w-1/2 bg-surface-raised/70 rounded"></div>
        </div>
      </div>
    </div>

    <!-- Today's List -->
    <div v-else-if="occurrences.length > 0" class="space-y-2 pt-1">
      <div
        v-for="occ in occurrences"
        :key="occ.event_id"
        class="p-2.5 rounded-xl hover:bg-surface-subtle transition-colors flex items-start gap-2.5"
      >
        <div class="w-2 h-2 rounded-full bg-primary-600 mt-1 shrink-0"></div>
        <div class="min-w-0 flex-1">
          <p class="text-xs font-bold text-ink truncate">{{ occ.title }}</p>
          <p v-if="occ.milestone_info" class="text-[11px] text-ink-muted mt-0.5 line-clamp-1">
            {{ occ.milestone_info }}
          </p>
        </div>
      </div>
    </div>

    <p v-else class="text-xs text-ink-faint py-4 text-center">
      {{ t('home.todayEvents.empty') }}
    </p>
  </div>
</template>
