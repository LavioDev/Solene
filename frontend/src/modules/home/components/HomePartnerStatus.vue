<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { UserPartnerSummary } from '@/types/couple'
import type { PartnerActiveStatus } from '@/types/task'
import { RotateCw } from 'lucide-vue-next'
import AppBadge from '@/components/ui/AppBadge.vue'

interface Props {
  partner: UserPartnerSummary | null
  partnerStatus: PartnerActiveStatus | null
  isRefreshing?: boolean
  formatTaskTime: (isoString?: string | null) => string
}

const props = withDefaults(defineProps<Props>(), {
  isRefreshing: false,
})

const emit = defineEmits<{
  (e: 'refresh'): void
}>()

const { t } = useI18n()

// Active Task Priority Badge Variant
const priorityBadgeVariant = computed<'err' | 'warn' | 'ok' | 'primary' | 'violet' | 'neutral'>(() => {
  const p = props.partnerStatus?.active_task?.priority?.toLowerCase()
  if (p === 'urgent' || p === 'high') return 'err'
  if (p === 'medium') return 'warn'
  if (p === 'low') return 'ok'
  return 'primary'
})

const priorityLabel = computed(() => {
  const p = props.partnerStatus?.active_task?.priority?.toLowerCase()
  if (p === 'urgent') return t('home.partnerStatus.priorityUrgent')
  if (p === 'high') return t('home.partnerStatus.priorityHigh')
  if (p === 'medium') return t('home.partnerStatus.priorityMedium')
  if (p === 'low') return t('home.partnerStatus.priorityLow')
  return t('home.partnerStatus.priorityMedium')
})
</script>

<template>
  <div
    v-if="partner"
    class="py-3 px-4 rounded-2xl bg-white border border-border/60 shadow-2xs flex flex-wrap items-center justify-between gap-3 text-xs"
  >
    <!-- Left: Status Indicator & Details -->
    <div class="flex items-center gap-2.5 min-w-0">
      <!-- Dot Indicator (Red pulsing if busy, Green if free) -->
      <span class="relative flex h-2.5 w-2.5 shrink-0">
        <span
          v-if="partnerStatus?.is_busy"
          class="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"
        ></span>
      </span>

      <!-- Status text -->
      <div class="flex flex-wrap items-center gap-2 min-w-0">
        <span class="font-bold text-ink">
          {{ partnerStatus?.is_busy ? t('home.partnerStatus.busy', { name: partner.full_name }) : t('home.partnerStatus.available', { name: partner.full_name }) }}
        </span>

        <!-- If Busy: Task title & Priority tag & Time range -->
        <template v-if="partnerStatus?.is_busy && partnerStatus.active_task">
          <span class="text-ink-faint">·</span>
          <span class="font-medium text-ink truncate max-w-[200px] sm:max-w-xs">
            {{ partnerStatus.active_task.title }}
          </span>
          <AppBadge :variant="priorityBadgeVariant" size="sm">
            {{ priorityLabel }}
          </AppBadge>
          <span class="text-ink-faint font-mono">
            ({{ formatTaskTime(partnerStatus.active_task.start_time) }} - {{ formatTaskTime(partnerStatus.active_task.end_time) }})
          </span>
        </template>

        <template v-else>
          <span class="text-ink-faint">·</span>
          <span class="text-ink-muted">{{ t('home.partnerStatus.noTasks') }}</span>
        </template>
      </div>
    </div>

    <!-- Right: Refresh icon -->
    <button
      type="button"
      @click="emit('refresh')"
      class="text-ink-faint hover:text-ink transition-colors cursor-pointer p-1 rounded-md hover:bg-surface-subtle"
      :class="{ 'animate-spin text-primary-600': isRefreshing }"
      :title="t('tabs.refresh')"
    >
      <RotateCw class="w-3.5 h-3.5" />
    </button>
  </div>
</template>
