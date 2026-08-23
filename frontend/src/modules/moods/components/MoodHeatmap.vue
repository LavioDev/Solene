<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { HeatmapDayItem } from '@/types/mood'
import { getMoodByScore } from '@/constants/moods'

const props = defineProps<{
  days: HeatmapDayItem[]
  year: number
  viewMode?: 'my' | 'partner' | 'combined'
}>()

const emit = defineEmits<{
  (e: 'select-day', day: HeatmapDayItem): void
}>()

const { t } = useI18n()

// Tooltip state
const hoveredDay = ref<HeatmapDayItem | null>(null)
const tooltipX = ref(0)
const tooltipY = ref(0)
const showTooltip = ref(false)

// Organize 365 days into 53 weeks x 7 days (Sunday = 0 to Saturday = 6)
interface WeekColumn {
  weekIndex: number
  monthLabel?: string
  days: (HeatmapDayItem | null)[] // 7 rows (0=Sun, 1=Mon, ..., 6=Sat)
}

const weeksGrid = computed<WeekColumn[]>(() => {
  if (!props.days || props.days.length === 0) return []

  const weeks: WeekColumn[] = []
  let currentWeek: (HeatmapDayItem | null)[] = new Array(7).fill(null)
  let lastMonth = -1
  let weekIdx = 0

  props.days.forEach((dayItem) => {
    // Parse date (YYYY-MM-DD)
    const [y, m, d] = dayItem.date.split('-').map(Number)
    const dateObj = new Date(y, m - 1, d)
    const dayOfWeek = dateObj.getDay() // 0=Sun, 1=Mon, ..., 6=Sat
    const month = dateObj.getMonth()

    let monthLabel: string | undefined = undefined
    if (month !== lastMonth) {
      // New month label on this week
      const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
      monthLabel = monthNames[month]
      lastMonth = month
    }

    currentWeek[dayOfWeek] = dayItem

    // If Saturday (6) or last day of the year, push week and start new
    if (dayOfWeek === 6) {
      weeks.push({
        weekIndex: weekIdx++,
        monthLabel,
        days: [...currentWeek],
      })
      currentWeek = new Array(7).fill(null)
    } else if (month === 11 && d === 31) {
      // Last day of year
      weeks.push({
        weekIndex: weekIdx++,
        monthLabel,
        days: [...currentWeek],
      })
    }
  })

  return weeks
})

function getEffectiveScore(day: HeatmapDayItem): number | null {
  if (props.viewMode === 'partner') {
    return day.partner_score ?? null
  }
  if (props.viewMode === 'combined') {
    if (day.score && day.partner_score) {
      return Math.round((day.score + day.partner_score) / 2)
    }
    return day.score || day.partner_score || null
  }
  return day.score ?? null
}

function getEffectiveNote(day: HeatmapDayItem): string | null {
  if (props.viewMode === 'partner') return day.partner_note ?? null
  return day.note ?? null
}

function getCellColorClass(day: HeatmapDayItem | null): string {
  if (!day) return 'opacity-0 pointer-events-none'

  const score = getEffectiveScore(day)
  if (!score || score < 1) {
    // Empty cell in clean pastel Solene theme
    return 'bg-slate-100/80 border border-slate-200/70 hover:border-violet-400'
  }

  // Solène Violet/Purple palette representing emotion intensity
  if (score <= 2) return 'bg-violet-100 border border-violet-200'
  if (score <= 4) return 'bg-violet-200 border border-violet-300'
  if (score <= 6) return 'bg-violet-400 border border-violet-400'
  if (score <= 8) return 'bg-violet-600 border border-violet-600'
  return 'bg-purple-600 border border-purple-600 shadow-2xs' // 9-10 Awesome
}

function handleMouseEnter(event: MouseEvent, day: HeatmapDayItem | null) {
  if (!day) return
  hoveredDay.value = day
  const rect = (event.target as HTMLElement).getBoundingClientRect()
  tooltipX.value = rect.left + rect.width / 2
  tooltipY.value = rect.top - 8
  showTooltip.value = true
}

function handleMouseLeave() {
  showTooltip.value = false
  hoveredDay.value = null
}

function formatDateDisplay(dateStr: string): string {
  const [y, m, d] = dateStr.split('-')
  return `${d}/${m}/${y}`
}
</script>

<template>
  <div class="bg-white text-ink rounded-2xl p-5 sm:p-6 border border-border/80 shadow-card overflow-hidden">
    <!-- Header info bar inside heatmap -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4 pb-3 border-b border-border/60">
      <div class="flex items-center gap-2">
        <h3 class="text-sm font-bold text-ink tracking-tight font-sans">
          {{ t('mood.heatmap.title') }} — {{ year }}
        </h3>
      </div>
      <p class="text-xs text-ink-muted">
        {{ t('mood.heatmap.subtitle') }}
      </p>
    </div>

    <!-- Heatmap Matrix Scroll Area -->
    <div class="overflow-x-auto pb-2 scrollbar-thin scrollbar-thumb-violet-200">
      <div class="inline-block min-w-full">
        <!-- Month Headers -->
        <div class="flex ml-8 mb-1.5 text-[10px] sm:text-[11px] font-semibold text-ink-muted select-none">
          <div
            v-for="col in weeksGrid"
            :key="`m-${col.weekIndex}`"
            class="w-3 sm:w-3.5 mr-1 text-left shrink-0"
          >
          </div>
        </div>

        <!-- Heatmap Grid (7 rows Mon..Sun) -->
        <div class="flex items-start">
          <!-- Weekday Row Labels (Mon=1, Wed=3, Fri=5) -->
          <div class="w-8 flex flex-col justify-between pr-2 text-[10px] font-medium text-ink-faint select-none shrink-0 py-0.5">
            <span class="h-3 sm:h-3.5 leading-3"></span>
            <span class="h-3 sm:h-3.5 leading-3">{{ t('mood.heatmap.mon') }}</span>
            <span class="h-3 sm:h-3.5 leading-3"></span>
            <span class="h-3 sm:h-3.5 leading-3">{{ t('mood.heatmap.wed') }}</span>
            <span class="h-3 sm:h-3.5 leading-3"></span>
            <span class="h-3 sm:h-3.5 leading-3">{{ t('mood.heatmap.fri') }}</span>
            <span class="h-3 sm:h-3.5 leading-3"></span>
          </div>

          <!-- 53 Week Columns -->
          <div class="flex gap-1 shrink-0">
            <div
              v-for="col in weeksGrid"
              :key="`col-${col.weekIndex}`"
              class="flex flex-col gap-1 shrink-0"
            >
              <!-- 7 Day Cells in each column (0=Sun, 1=Mon, ..., 6=Sat) -->
              <div
                v-for="(day, dayIdx) in col.days"
                :key="`d-${col.weekIndex}-${dayIdx}`"
                :class="[
                  'w-3 h-3 sm:w-3.5 sm:h-3.5 rounded-[3px] transition-transform duration-100',
                  getCellColorClass(day),
                  day && day.is_today ? 'ring-2 ring-violet-600 ring-offset-1 ring-offset-white' : '',
                  day ? 'cursor-pointer hover:scale-125 hover:z-20 shadow-2xs' : ''
                ]"
                @mouseenter="handleMouseEnter($event, day)"
                @mouseleave="handleMouseLeave"
                @click="day && emit('select-day', day)"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer Legend Bar -->
    <div class="flex flex-wrap items-center justify-between text-xs text-ink-muted mt-4 pt-3 border-t border-border/60 gap-2 select-none">
      <div class="flex items-center gap-3">
        <span class="inline-flex items-center gap-1.5">
          <span class="w-3 h-3 rounded-[3px] bg-slate-100 border border-slate-200"></span>
          <span>{{ t('mood.heatmap.unlogged') }}</span>
        </span>
        <span class="text-border">•</span>
        <span class="text-ink-muted">
          {{ t('mood.scoreRank', { score: '1-10' }) }}
        </span>
      </div>

      <!-- Color Ramp: Less -> More -->
      <div class="flex items-center gap-1.5 font-medium">
        <span>{{ t('mood.heatmap.less') }}</span>
        <div class="flex gap-1 items-center px-1">
          <span class="w-3 h-3 rounded-[3px] bg-slate-100 border border-slate-200" title="0"></span>
          <span class="w-3 h-3 rounded-[3px] bg-violet-100 border border-violet-200" title="1-2"></span>
          <span class="w-3 h-3 rounded-[3px] bg-violet-200 border border-violet-300" title="3-4"></span>
          <span class="w-3 h-3 rounded-[3px] bg-violet-400 border border-violet-400" title="5-6"></span>
          <span class="w-3 h-3 rounded-[3px] bg-violet-600 border border-violet-600" title="7-8"></span>
          <span class="w-3 h-3 rounded-[3px] bg-purple-600 border border-purple-600" title="9-10"></span>
        </div>
        <span>{{ t('mood.heatmap.more') }}</span>
      </div>
    </div>

    <!-- Floating Tooltip -->
    <Teleport to="body">
      <Transition name="tooltip-fade">
        <div
          v-if="showTooltip && hoveredDay"
          class="fixed z-50 pointer-events-none -translate-x-1/2 -translate-y-full px-3.5 py-2.5 bg-white text-ink text-xs rounded-2xl shadow-xl border border-violet-200/90 max-w-xs space-y-1.5 backdrop-blur-md"
          :style="{ left: `${tooltipX}px`, top: `${tooltipY}px` }"
        >
          <div class="flex items-center justify-between gap-3 font-semibold text-ink border-b border-border/50 pb-1">
            <span>{{ formatDateDisplay(hoveredDay.date) }}</span>
            <span v-if="hoveredDay.is_today" class="px-1.5 py-0.5 rounded-full text-[10px] bg-violet-100 text-violet-700 border border-violet-200 font-bold">
              Hôm nay
            </span>
            <span v-else-if="hoveredDay.is_locked" class="text-[10px] text-ink-muted">🔒</span>
          </div>

          <div v-if="getEffectiveScore(hoveredDay)" class="flex items-center gap-2 pt-0.5">
            <span class="text-base leading-none">{{ getMoodByScore(getEffectiveScore(hoveredDay))?.emoji }}</span>
            <div>
              <span class="font-bold text-violet-700">{{ getEffectiveScore(hoveredDay) }}/10</span>
              <span class="text-ink-muted capitalize ml-1">({{ hoveredDay.tag || 'Mood' }})</span>
            </div>
          </div>
          <div v-else class="text-ink-muted italic pt-0.5 text-[11px]">
            {{ t('mood.heatmap.unlogged') }}
          </div>

          <!-- Note preview -->
          <p v-if="getEffectiveNote(hoveredDay)" class="text-ink text-[11px] line-clamp-2 italic bg-violet-50/60 p-1.5 rounded-xl border border-violet-100">
            "{{ getEffectiveNote(hoveredDay) }}"
          </p>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<style scoped>
.tooltip-fade-enter-active,
.tooltip-fade-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.tooltip-fade-enter-from,
.tooltip-fade-leave-to {
  opacity: 0;
  transform: translate(-50%, -90%) scale(0.95);
}
</style>
