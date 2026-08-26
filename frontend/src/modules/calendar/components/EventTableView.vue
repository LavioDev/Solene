<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  Calendar as CalendarIcon,
  Heart,
  Search,
  Sparkles,
  Edit2,
  Trash2,
  CalendarHeart,
  Repeat,
} from 'lucide-vue-next'
import { apiClient } from '@/services/apiClient'
import AppButton from '@/components/ui/AppButton.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppSelect from '@/components/ui/AppSelect.vue'
import type { SpecialEvent } from '../types'

const emit = defineEmits<{
  (e: 'add-event'): void
  (e: 'edit-event', event: SpecialEvent): void
  (e: 'delete-event', event: SpecialEvent): void
}>()

const { t, locale } = useI18n()

const events = ref<SpecialEvent[]>([])
const loading = ref(false)
const searchQuery = ref('')
const selectedRecurrence = ref<string>('ALL')

const recurrenceFilterOptions = computed(() => [
  { label: t('calendar.list.filterAll'), value: 'ALL' },
  { label: t('calendar.recurrenceOptions.everyNDays'), value: 'EVERY_N_DAYS' },
  { label: t('calendar.recurrenceOptions.monthly'), value: 'MONTHLY' },
  { label: t('calendar.recurrenceOptions.yearly'), value: 'YEARLY' },
])

async function fetchEvents() {
  loading.value = true
  try {
    const res = await apiClient.get<SpecialEvent[]>('/events')
    events.value = res.data
  } catch (err) {
    console.error('Failed to fetch special events list:', err)
  } finally {
    loading.value = false
  }
}

const filteredEvents = computed(() => {
  let result = [...events.value]

  if (selectedRecurrence.value !== 'ALL') {
    result = result.filter((e) => e.recurrence_type === selectedRecurrence.value)
  }

  if (searchQuery.value.trim()) {
    const query = searchQuery.value.trim().toLowerCase()
    result = result.filter(
      (e) =>
        e.title.toLowerCase().includes(query) ||
        (e.description && e.description.toLowerCase().includes(query))
    )
  }

  return result
})

function formatDate(dateStr?: string | null): string {
  if (!dateStr) return '-'
  try {
    const d = new Date(dateStr)
    const loc =
      locale.value === 'vi'
        ? 'vi-VN'
        : locale.value === 'fr'
        ? 'fr-FR'
        : locale.value === 'zh'
        ? 'zh-CN'
        : 'en-US'
    return d.toLocaleDateString(loc, { year: 'numeric', month: 'short', day: 'numeric' })
  } catch {
    return dateStr
  }
}

function formatMonthDay(dateStr?: string | null): string {
  if (!dateStr) return '-'
  try {
    const parts = dateStr.split('-')
    if (parts.length >= 3) {
      const month = Number(parts[1])
      const day = Number(parts[2])
      if (locale.value === 'vi') return `${day}/${month}`
      return `${month}/${day}`
    }
    return dateStr
  } catch {
    return dateStr || '-'
  }
}

function getDayFromDate(dateStr?: string | null): number | string {
  if (!dateStr) return '-'
  try {
    const parts = dateStr.split('-')
    return parts.length >= 3 ? Number(parts[2]) : '-'
  } catch {
    return '-'
  }
}

function getRecurrenceBadgeVariant(type: string): 'violet' | 'rose' | 'ok' | 'neutral' {
  switch (type) {
    case 'EVERY_N_DAYS':
      return 'violet'
    case 'YEARLY':
      return 'rose'
    case 'MONTHLY':
      return 'ok'
    default:
      return 'neutral'
  }
}

function getRecurrenceLabel(type: string): string {
  switch (type) {
    case 'EVERY_N_DAYS':
      return t('calendar.recurrenceOptions.everyNDays')
    case 'MONTHLY':
      return t('calendar.recurrenceOptions.monthly')
    case 'YEARLY':
      return t('calendar.recurrenceOptions.yearly')
    default:
      return type
  }
}

function getIntervalDetail(evt: SpecialEvent): string {
  if (evt.recurrence_type === 'EVERY_N_DAYS') {
    return t('calendar.list.everyNDaysText', { n: evt.interval_value || 100 })
  } else if (evt.recurrence_type === 'MONTHLY') {
    return t('calendar.list.monthlyText', { day: getDayFromDate(evt.anchor_date) })
  } else if (evt.recurrence_type === 'YEARLY') {
    return t('calendar.list.yearlyText', { date: formatMonthDay(evt.anchor_date) })
  }
  return t('calendar.list.singleText')
}

onMounted(() => {
  fetchEvents()
})

defineExpose({
  fetchEvents,
  events,
})
</script>

<template>
  <div class="space-y-4 select-none">
    <!-- Action Bar (Search & Filter) - Standalone Card 1:1 with Couples & Users view -->
    <div class="bg-white border border-border rounded-2xl p-3.5 shadow-card flex flex-col sm:flex-row sm:items-center justify-between gap-3">
      <!-- Search Input -->
      <div class="relative flex-1 max-w-md">
        <Search class="w-3.5 h-3.5 text-ink-faint absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
        <input
          v-model="searchQuery"
          type="text"
          :placeholder="t('calendar.list.searchPlaceholder')"
          class="w-full h-[42px] pl-9 pr-3.5 py-2.5 text-xs bg-surface-subtle/80 hover:bg-surface-raised focus:bg-white border border-border rounded-xl text-ink placeholder:text-ink-faint focus:outline-none focus:ring-2 focus:ring-violet-400/20 focus:border-violet-500 transition-all shadow-2xs"
        />
      </div>

      <!-- Filters & Add Event Button -->
      <div class="flex flex-wrap items-center gap-2.5 shrink-0">
        <div class="w-40 sm:w-48">
          <AppSelect
            v-model="selectedRecurrence"
            :options="recurrenceFilterOptions"
            size="sm"
          />
        </div>
        <AppButton
          size="md"
          @click="emit('add-event')"
          class="h-[42px] py-2.5 px-4 shrink-0 shadow-2xs rounded-xl text-xs font-semibold inline-flex items-center justify-center cursor-pointer"
        >
          <Sparkles class="w-3.5 h-3.5 mr-1 text-white" />
          {{ t('calendar.list.addEvent') }}
        </AppButton>
      </div>
    </div>

    <!-- Events Table Card - Standalone Card 1:1 with Couples & Users view -->
    <div class="bg-white border border-border rounded-2xl shadow-card overflow-hidden">
      <!-- Loading State -->
      <div v-if="loading" class="py-20 text-center text-sm text-ink-faint">
        <div class="animate-spin w-6 h-6 border-2 border-violet-600 border-t-transparent rounded-full mx-auto mb-2"></div>
        {{ t('calendar.loading') }}
      </div>

      <!-- Empty State -->
      <div v-else-if="filteredEvents.length === 0" class="py-16 text-center space-y-3">
        <div class="w-12 h-12 rounded-full bg-violet-50 border border-violet-100 flex items-center justify-center text-violet-400 mx-auto">
          <CalendarHeart class="w-6 h-6" />
        </div>
        <p class="text-sm font-semibold text-ink">{{ t('calendar.list.emptyTitle') }}</p>
        <p class="text-xs text-ink-muted max-w-sm mx-auto">{{ t('calendar.list.emptySubtitle') }}</p>
        <AppButton size="sm" @click="emit('add-event')" class="mx-auto mt-2 cursor-pointer">
          <Sparkles class="w-3.5 h-3.5 mr-1 text-white" />
          {{ t('calendar.list.addEvent') }}
        </AppButton>
      </div>

      <!-- Table -->
      <div v-else class="overflow-x-auto">
        <table class="w-full min-w-[800px] text-left border-collapse">
          <thead>
            <tr class="border-b border-border/80 bg-surface-subtle/60 text-[11px] font-bold text-ink-faint uppercase tracking-wider">
              <th class="py-3.5 px-5 whitespace-nowrap select-none">{{ t('calendar.list.colTitle') }}</th>
              <th class="py-3.5 px-4 whitespace-nowrap select-none">{{ t('calendar.list.colRecurrence') }}</th>
              <th class="py-3.5 px-4 whitespace-nowrap select-none">{{ t('calendar.list.colAnchorDate') }}</th>
              <th class="py-3.5 px-4 whitespace-nowrap select-none">{{ t('calendar.list.colInterval') }}</th>
              <th class="py-3.5 px-4 whitespace-nowrap select-none">{{ t('calendar.list.colCreatedAt') }}</th>
              <th class="py-3.5 px-5 text-right whitespace-nowrap select-none sticky right-0 z-20 bg-surface-subtle shadow-[-6px_0_10px_-4px_rgba(0,0,0,0.06)] border-l border-border/50">{{ t('calendar.list.colActions') }}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border/60 text-xs sm:text-sm bg-white">
            <tr
              v-for="evt in filteredEvents"
              :key="evt.id"
              class="hover:bg-surface-raised/60 transition-colors group cursor-default"
            >
              <!-- Title & Category -->
              <td class="py-3.5 px-5">
                <div class="flex items-center gap-3">
                  <div class="w-8 h-8 rounded-xl bg-rose-50 border border-rose-100 flex items-center justify-center text-rose-500 shrink-0 shadow-2xs">
                    <Heart class="w-4 h-4 fill-current" />
                  </div>
                  <div class="min-w-0">
                    <div class="flex items-center gap-1.5">
                      <p class="font-semibold text-ink truncate">{{ evt.title }}</p>
                      <AppBadge v-if="evt.is_shared" variant="violet" size="sm">
                        <Heart class="w-2.5 h-2.5 fill-current text-violet-500" />
                        <span>{{ t('common.shared') }}</span>
                      </AppBadge>
                    </div>
                    <p v-if="evt.description" class="text-xs text-ink-faint truncate mt-0.5">{{ evt.description }}</p>
                  </div>
                </div>
              </td>

              <!-- Recurrence Badge -->
              <td class="py-3.5 px-4 whitespace-nowrap">
                <AppBadge :variant="getRecurrenceBadgeVariant(evt.recurrence_type)" size="sm">
                  <Repeat class="w-3 h-3 mr-1" />
                  {{ getRecurrenceLabel(evt.recurrence_type) }}
                </AppBadge>
              </td>

              <!-- Anchor Date -->
              <td class="py-3.5 px-4 text-ink-muted font-mono text-xs whitespace-nowrap">
                <div class="flex items-center gap-1.5">
                  <CalendarIcon class="w-3.5 h-3.5 text-ink-faint shrink-0" />
                  <span>{{ formatDate(evt.anchor_date) }}</span>
                </div>
              </td>

              <!-- Interval Detail -->
              <td class="py-3.5 px-4 text-ink text-xs font-medium whitespace-nowrap">
                {{ getIntervalDetail(evt) }}
              </td>

              <!-- Created Date -->
              <td class="py-3.5 px-4 text-ink-faint font-mono text-xs whitespace-nowrap">
                {{ formatDate(evt.created_at) }}
              </td>

              <!-- Actions -->
              <td class="py-3.5 px-5 text-right whitespace-nowrap sticky right-0 z-10 bg-white group-hover:bg-surface-raised/80 transition-colors shadow-[-6px_0_10px_-4px_rgba(0,0,0,0.06)] border-l border-border/50" @click.stop>
                <div class="flex items-center justify-end gap-1">
                  <button
                    type="button"
                    @click="emit('edit-event', evt)"
                    class="p-1.5 rounded-lg text-ink-faint hover:text-violet-600 hover:bg-violet-50 transition-colors cursor-pointer"
                    :title="t('calendar.list.editEvent')"
                  >
                    <Edit2 class="w-3.5 h-3.5" />
                  </button>
                  <button
                    type="button"
                    @click="emit('delete-event', evt)"
                    class="p-1.5 rounded-lg text-ink-faint hover:text-err-text hover:bg-err-bg transition-colors cursor-pointer"
                    :title="t('common.delete')"
                  >
                    <Trash2 class="w-3.5 h-3.5" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
