<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useMoodStore } from '@/stores/moodStore'
import { getMoodByScore } from '@/constants/moods'
import type { HeatmapDayItem } from '@/types/mood'
import MoodHeatmap from '../components/MoodHeatmap.vue'
import MoodDetailModal from '../components/MoodDetailModal.vue'
import AppSelect from '@/components/ui/AppSelect.vue'
import {
  Sparkles,
  Heart,
  User,
  Layers,
} from 'lucide-vue-next'

const { t, te } = useI18n()
const moodStore = useMoodStore()

const currentYear = new Date().getFullYear()
const selectedYear = ref<number>(currentYear)
const viewMode = ref<'my' | 'partner' | 'combined'>('my')

// Modal state
const selectedDay = ref<HeatmapDayItem | null>(null)
const showDetailModal = ref(false)

const yearOptions = computed(() => {
  const years = []
  for (let y = currentYear; y >= currentYear - 3; y--) {
    years.push({ label: `${y}`, value: y })
  }
  return years
})

const heatmapData = computed(() => moodStore.heatmapData)

function getMoodTag(tag?: string): string {
  if (!tag) return ''
  const key = `mood.tags.${tag.toLowerCase()}`
  if (te(key)) return t(key)
  return tag.replace(/_/g, ' ')
}

function formatDate(dateStr?: string): string {
  if (!dateStr) return ''
  const [y, m, d] = dateStr.split('-')
  return `${d}/${m}/${y}`
}

async function loadData() {
  await moodStore.fetchHeatmap(selectedYear.value, true)
  await moodStore.fetchMoodHistory({ limit: 10 } as any)
}

function handleSelectDay(day: HeatmapDayItem) {
  selectedDay.value = day
  showDetailModal.value = true
}

function handleYearChange(newYear: number | string) {
  selectedYear.value = Number(newYear)
  moodStore.fetchHeatmap(selectedYear.value, true)
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="space-y-4 px-4 sm:px-6 lg:px-8 pt-1 sm:pt-2 pb-16 w-full select-none">
    <!-- Page Header & Controls -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <div class="flex items-center gap-2">
          <h1 class="text-xl sm:text-2xl font-bold text-ink font-sans tracking-tight">
            {{ t('nav.moods') }}
          </h1>
        </div>
        <p class="text-xs sm:text-sm text-ink-muted mt-0.5">
          {{ t('nav.moodsDesc') }}
        </p>
      </div>

      <!-- Controls: Year Selector & View Mode Switcher -->
      <div class="flex flex-wrap sm:flex-nowrap items-center gap-3 w-full sm:w-auto">
        <!-- View Mode Segmented Pill (Responsive scrollable tabs) -->
        <div class="w-full sm:w-auto overflow-x-auto pb-1 max-w-full">
          <div class="flex bg-surface-raised p-1 rounded-xl border border-border/80 text-xs font-medium shrink-0 w-max">
            <button
              type="button"
              class="px-3.5 py-1.5 rounded-lg transition-all flex items-center gap-1.5 cursor-pointer text-xs font-medium shrink-0 whitespace-nowrap"
              :class="viewMode === 'my' ? 'bg-white text-violet-700 font-semibold shadow-2xs' : 'text-ink-muted hover:text-ink'"
              @click="viewMode = 'my'"
            >
              <User class="w-4 h-4" />
              <span class="text-xs">{{ t('mood.heatmap.myMood') }}</span>
            </button>
            <button
              type="button"
              class="px-3.5 py-1.5 rounded-lg transition-all flex items-center gap-1.5 cursor-pointer text-xs font-medium shrink-0 whitespace-nowrap"
              :class="viewMode === 'partner' ? 'bg-white text-pink-600 font-semibold shadow-2xs' : 'text-ink-muted hover:text-ink'"
              @click="viewMode = 'partner'"
            >
              <Heart class="w-4 h-4" />
              <span class="text-xs">{{ t('mood.heatmap.partnerMood') }}</span>
            </button>
            <button
              type="button"
              class="px-3.5 py-1.5 rounded-lg transition-all flex items-center gap-1.5 cursor-pointer text-xs font-medium shrink-0 whitespace-nowrap"
              :class="viewMode === 'combined' ? 'bg-white text-emerald-700 font-semibold shadow-2xs' : 'text-ink-muted hover:text-ink'"
              @click="viewMode = 'combined'"
            >
              <Layers class="w-4 h-4" />
              <span class="text-xs">{{ t('mood.heatmap.combinedMood') }}</span>
            </button>
          </div>
        </div>

        <!-- Year Selector -->
        <div class="w-24 shrink-0">
          <AppSelect
            :model-value="selectedYear"
            :options="yearOptions"
            @update:model-value="handleYearChange"
          />
        </div>
      </div>
    </div>

    <!-- The GitHub-Style Contribution Heatmap Matrix -->
    <MoodHeatmap
      v-if="heatmapData"
      :days="heatmapData.days"
      :year="selectedYear"
      :view-mode="viewMode"
      @select-day="handleSelectDay"
    />
    <div v-else class="h-48 rounded-2xl bg-surface-raised animate-pulse flex items-center justify-center text-ink-muted text-sm">
      Loading...
    </div>

    <!-- Recent Notes (Đơn giản & Tinh tế) -->
    <div v-if="moodStore.moods.length > 0" class="p-5 rounded-2xl bg-white border border-border/80 shadow-card space-y-3">
      <div class="flex items-center justify-between pb-2.5 border-b border-border/50">
        <h3 class="text-xs font-bold uppercase tracking-wider text-ink-muted flex items-center gap-1.5">
          <Sparkles class="w-3.5 h-3.5 text-violet-600" />
          <span>{{ t('mood.noteLabel') }}</span>
        </h3>
      </div>

      <div class="divide-y divide-border/40">
        <div
          v-for="item in moodStore.moods"
          :key="item.id"
          class="py-2.5 px-2 -mx-2 rounded-xl hover:bg-surface-subtle/60 transition-colors flex items-start justify-between gap-4 text-xs"
        >
          <div class="flex items-start gap-3 min-w-0">
            <span class="text-lg leading-none shrink-0 mt-0.5 select-none">
              {{ getMoodByScore(item.mood_score)?.emoji || '😊' }}
            </span>
            <div class="min-w-0 space-y-0.5">
              <div class="flex flex-wrap items-center gap-1.5 leading-none">
                <span class="font-bold text-ink">{{ item.mood_score }}/10</span>
                <span v-if="item.mood_tag" class="text-ink-muted text-xs">
                  · {{ getMoodTag(item.mood_tag) }}
                </span>
                <span v-if="item.user_full_name" class="text-[11px] text-ink-faint">
                  ({{ item.user_full_name }})
                </span>
              </div>
              <p v-if="item.note" class="text-ink-muted text-xs leading-relaxed whitespace-pre-wrap font-sans italic pt-0.5">
                {{ item.note }}
              </p>
            </div>
          </div>
          <span class="text-[11px] text-ink-faint shrink-0 font-mono pt-0.5">
            {{ formatDate(item.entry_date) }}
          </span>
        </div>
      </div>
    </div>

    <!-- Day Detail Modal -->
    <MoodDetailModal
      :show="showDetailModal"
      :day="selectedDay"
      @close="showDetailModal = false"
    />
  </div>
</template>
