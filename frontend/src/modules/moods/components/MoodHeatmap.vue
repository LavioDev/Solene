<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { HeatmapDayItem } from '@/types/mood'
import { getMoodByScore } from '@/constants/moods'
import { Calendar } from 'lucide-vue-next'

const props = defineProps<{
  days: HeatmapDayItem[]
  year: number
  viewMode?: 'my' | 'partner' | 'combined'
}>()

const emit = defineEmits<{
  (e: 'select-day', day: HeatmapDayItem): void
}>()

const { t, te } = useI18n()

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

const monthKeys = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']

const weeksGrid = computed<WeekColumn[]>(() => {
  if (!props.days || props.days.length === 0) return []

  const weeks: WeekColumn[] = []
  let currentWeek: (HeatmapDayItem | null)[] = new Array(7).fill(null)
  let lastMonth = -1
  let currentWeekMonthLabel: string | undefined = undefined
  let weekIdx = 0

  props.days.forEach((dayItem) => {
    // Parse date (YYYY-MM-DD)
    const [y, m, d] = dayItem.date.split('-').map(Number)
    const dateObj = new Date(y, m - 1, d)
    const dayOfWeek = dateObj.getDay() // 0=Sun, 1=Mon, ..., 6=Sat
    const month = dateObj.getMonth()

    if (month !== lastMonth) {
      const key = monthKeys[month]
      const transKey = `mood.heatmap.months.${key}`
      currentWeekMonthLabel = te(transKey)
        ? t(transKey)
        : ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][month]
      lastMonth = month
    }

    currentWeek[dayOfWeek] = dayItem

    // If Saturday (6) or last day of the year, push week and start new
    if (dayOfWeek === 6) {
      weeks.push({
        weekIndex: weekIdx++,
        monthLabel: currentWeekMonthLabel,
        days: [...currentWeek],
      })
      currentWeek = new Array(7).fill(null)
      currentWeekMonthLabel = undefined
    } else if (month === 11 && d === 31) {
      // Last day of year
      weeks.push({
        weekIndex: weekIdx++,
        monthLabel: currentWeekMonthLabel,
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

function getMoodTagLabel(day: HeatmapDayItem): string {
  const tag = (props.viewMode === 'partner' ? day.partner_tag : day.tag) || (day.score ? getMoodByScore(day.score)?.tag : '')
  if (!tag) return ''
  const key = `mood.tags.${tag.toLowerCase()}`
  if (te(key)) return t(key)
  return tag.replace(/_/g, ' ')
}
</script>

<template>
  <div class="bg-white text-ink rounded-2xl p-5 sm:p-6 border border-border/80 shadow-card overflow-hidden">
    <!-- Header info bar inside heatmap -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-5 pb-3.5 border-b border-border/60">
      <div class="flex items-center gap-2.5">
        <div class="w-8 h-8 rounded-xl bg-violet-100/70 text-violet-600 flex items-center justify-center shrink-0">
          <Calendar class="w-4 h-4" />
        </div>
        <h3 class="text-sm font-bold text-ink tracking-tight font-sans">
          {{ t('mood.heatmap.title') }} — {{ year }}
        </h3>
      </div>
      <p class="text-xs text-ink-muted">
        {{ t('mood.heatmap.subtitle') }}
      </p>
    </div>

    <!-- Heatmap Matrix Scroll Area (Always Centered) -->
    <div class="w-full overflow-x-auto pb-2 scrollbar-thin scrollbar-thumb-violet-200">
      <div class="w-fit mx-auto min-w-max py-1">
        <!-- Month Headers (Exact week-aligned) -->
        <div class="flex items-center gap-1 sm:gap-1.5 ml-7 sm:ml-8 mb-2 h-4 select-none">
          <div
            v-for="col in weeksGrid"
            :key="`m-${col.weekIndex}`"
            class="w-3.5 h-3.5 sm:w-4 sm:h-4 shrink-0 relative flex items-center"
          >
            <span
              v-if="col.monthLabel"
              class="absolute left-0 top-0 text-[10px] sm:text-[11px] font-semibold text-ink-muted whitespace-nowrap leading-none"
            >
              {{ col.monthLabel }}
            </span>
          </div>
        </div>

        <!-- Heatmap Grid (7 rows Sun..Sat) -->
        <div class="flex items-start">
          <!-- Weekday Row Labels (Mon=1, Wed=3, Fri=5 with matching heights) -->
          <div class="w-7 sm:w-8 flex flex-col gap-1 sm:gap-1.5 pr-2 text-[10px] font-medium text-ink-faint select-none shrink-0">
            <span class="h-3.5 sm:h-4 flex items-center justify-end leading-none"></span>
            <span class="h-3.5 sm:h-4 flex items-center justify-end leading-none text-ink-muted">{{ t('mood.heatmap.mon') }}</span>
            <span class="h-3.5 sm:h-4 flex items-center justify-end leading-none"></span>
            <span class="h-3.5 sm:h-4 flex items-center justify-end leading-none text-ink-muted">{{ t('mood.heatmap.wed') }}</span>
            <span class="h-3.5 sm:h-4 flex items-center justify-end leading-none"></span>
            <span class="h-3.5 sm:h-4 flex items-center justify-end leading-none text-ink-muted">{{ t('mood.heatmap.fri') }}</span>
            <span class="h-3.5 sm:h-4 flex items-center justify-end leading-none"></span>
          </div>

          <!-- 53 Week Columns -->
          <div class="flex gap-1 sm:gap-1.5 shrink-0">
            <div
              v-for="col in weeksGrid"
              :key="`col-${col.weekIndex}`"
              class="flex flex-col gap-1 sm:gap-1.5 shrink-0"
            >
              <!-- 7 Day Cells in each column (0=Sun, 1=Mon, ..., 6=Sat) -->
              <div
                v-for="(day, dayIdx) in col.days"
                :key="`d-${col.weekIndex}-${dayIdx}`"
                :class="[
                  'w-3.5 h-3.5 sm:w-4 sm:h-4 rounded-[3.5px] sm:rounded-[4px] transition-all duration-150',
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
    <div class="flex flex-wrap items-center justify-between text-xs text-ink-muted mt-5 pt-3.5 border-t border-border/60 gap-2 select-none">
      <div class="flex items-center gap-3">
        <span class="inline-flex items-center gap-1.5">
          <span class="w-3.5 h-3.5 rounded-[3.5px] bg-slate-100 border border-slate-200"></span>
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
          <span class="w-3.5 h-3.5 rounded-[3.5px] bg-slate-100 border border-slate-200" title="0"></span>
          <span class="w-3.5 h-3.5 rounded-[3.5px] bg-violet-100 border border-violet-200" title="1-2"></span>
          <span class="w-3.5 h-3.5 rounded-[3.5px] bg-violet-200 border border-violet-300" title="3-4"></span>
          <span class="w-3.5 h-3.5 rounded-[3.5px] bg-violet-400 border border-violet-400" title="5-6"></span>
          <span class="w-3.5 h-3.5 rounded-[3.5px] bg-violet-600 border border-violet-600" title="7-8"></span>
          <span class="w-3.5 h-3.5 rounded-[3.5px] bg-purple-600 border border-purple-600" title="9-10"></span>
        </div>
        <span>{{ t('mood.heatmap.more') }}</span>
      </div>
    </div>

    <!-- Floating Minimalist Tooltip -->
    <Teleport to="body">
      <Transition name="tooltip-fade">
        <div
          v-if="showTooltip && hoveredDay"
          class="fixed z-50 pointer-events-none -translate-x-1/2 -translate-y-full px-3 py-2 bg-white text-xs rounded-xl shadow-lg shadow-violet-950/5 border border-border/80 max-w-[240px] space-y-1 select-none"
          :style="{ left: `${tooltipX}px`, top: `${tooltipY}px` }"
        >
          <!-- Top Row: Date & Today indicator -->
          <div class="flex items-center justify-between gap-2 text-[11px]">
            <span class="font-medium text-ink-muted">{{ formatDateDisplay(hoveredDay.date) }}</span>
            <span v-if="hoveredDay.is_today" class="px-1.5 py-0.2 rounded-md text-[10px] font-semibold bg-violet-50 text-violet-700">
              {{ t('calendar.today') }}
            </span>
            <span v-else-if="hoveredDay.is_locked" class="text-[10px] text-ink-faint">🔒</span>
          </div>

          <!-- Score & Tag -->
          <div v-if="getEffectiveScore(hoveredDay)" class="flex items-center gap-1.5 pt-0.5">
            <span class="text-sm leading-none">{{ getMoodByScore(getEffectiveScore(hoveredDay))?.emoji }}</span>
            <span class="font-bold text-ink">{{ getEffectiveScore(hoveredDay) }}/10</span>
            <span v-if="getMoodTagLabel(hoveredDay)" class="text-ink-faint text-[11px] truncate">
              · {{ getMoodTagLabel(hoveredDay) }}
            </span>
          </div>
          <div v-else class="text-ink-faint italic text-[11px] pt-0.5">
            {{ t('mood.heatmap.unlogged') }}
          </div>

          <!-- Note (Clean, borderless text) -->
          <p v-if="getEffectiveNote(hoveredDay)" class="text-ink-muted text-[11px] leading-relaxed line-clamp-2 italic pt-0.5">
            “{{ getEffectiveNote(hoveredDay) }}”
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
