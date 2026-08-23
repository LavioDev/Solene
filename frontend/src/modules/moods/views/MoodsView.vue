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

const { t } = useI18n()
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
    <!-- Page Header & Stats Row -->
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
      <div class="flex items-center gap-3">
        <!-- View Mode Segmented Pill -->
        <div class="flex bg-surface-raised p-1 rounded-xl border border-border/80 text-xs font-medium">
          <button
            type="button"
            class="px-3.5 py-1.5 rounded-lg transition-all flex items-center gap-1.5 cursor-pointer text-xs font-medium"
            :class="viewMode === 'my' ? 'bg-white text-violet-700 font-semibold shadow-2xs' : 'text-ink-muted hover:text-ink'"
            @click="viewMode = 'my'"
          >
            <User class="w-4 h-4" />
            <span class="text-xs">{{ t('mood.heatmap.myMood') }}</span>
          </button>
          <button
            type="button"
            class="px-3.5 py-1.5 rounded-lg transition-all flex items-center gap-1.5 cursor-pointer text-xs font-medium"
            :class="viewMode === 'partner' ? 'bg-white text-pink-600 font-semibold shadow-2xs' : 'text-ink-muted hover:text-ink'"
            @click="viewMode = 'partner'"
          >
            <Heart class="w-4 h-4" />
            <span class="text-xs">{{ t('mood.heatmap.partnerMood') }}</span>
          </button>
          <button
            type="button"
            class="px-3.5 py-1.5 rounded-lg transition-all flex items-center gap-1.5 cursor-pointer text-xs font-medium"
            :class="viewMode === 'combined' ? 'bg-white text-emerald-700 font-semibold shadow-2xs' : 'text-ink-muted hover:text-ink'"
            @click="viewMode = 'combined'"
          >
            <Layers class="w-4 h-4" />
            <span class="text-xs">{{ t('mood.heatmap.combinedMood') }}</span>
          </button>
        </div>

        <!-- Year Selector -->
        <div class="w-24">
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

    <!-- Recent Notes (Đơn giản & gọn gàng) -->
    <div v-if="moodStore.moods.length > 0" class="p-5 rounded-2xl bg-white border border-border/80 shadow-card space-y-3">
      <h3 class="text-xs font-bold uppercase tracking-wider text-ink-muted flex items-center gap-1.5 pb-2 border-b border-border/60">
        <Sparkles class="w-3.5 h-3.5 text-violet-600" />
        <span>{{ t('mood.noteLabel') }}</span>
      </h3>

      <div class="divide-y divide-border/40">
        <div
          v-for="item in moodStore.moods"
          :key="item.id"
          class="py-2.5 flex items-start justify-between gap-3 text-xs"
        >
          <div class="flex items-start gap-2.5 min-w-0">
            <span class="text-base leading-none shrink-0 mt-0.5">
              {{ getMoodByScore(item.mood_score)?.emoji || '😊' }}
            </span>
            <div class="min-w-0">
              <div class="flex items-center gap-2">
                <span class="font-semibold text-ink capitalize">{{ item.mood_tag }}</span>
                <span class="font-bold text-violet-700">({{ item.mood_score }}/10)</span>
                <span v-if="item.user_full_name" class="text-[11px] text-ink-muted">· {{ item.user_full_name }}</span>
              </div>
              <p v-if="item.note" class="text-ink-muted mt-0.5 whitespace-pre-wrap font-sans text-xs">
                {{ item.note }}
              </p>
            </div>
          </div>
          <span class="text-[11px] text-ink-faint shrink-0 font-mono">{{ item.entry_date }}</span>
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
