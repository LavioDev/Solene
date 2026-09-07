<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { HeatmapDayItem } from '@/types/mood'
import { getMoodByScore } from '@/constants/moods'
import AppModal from '@/components/ui/AppModal.vue'
import AppButton from '@/components/ui/AppButton.vue'
import { Calendar, Lock, Heart, User } from 'lucide-vue-next'

defineProps<{
  show: boolean
  day: HeatmapDayItem | null
  partnerName?: string
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

const { t } = useI18n()

function formatDateDisplay(dateStr?: string): string {
  if (!dateStr) return ''
  const [y, m, d] = dateStr.split('-')
  return `${d}/${m}/${y}`
}
</script>

<template>
  <AppModal
    :show="show"
    :title="t('mood.heatmap.dayDetails')"
    @close="emit('close')"
  >
    <div v-if="day" class="space-y-4 text-sm text-ink">
      <!-- Date and Lock status banner -->
      <div class="flex items-center justify-between p-3 rounded-xl bg-surface-raised border border-border/70">
        <div class="flex items-center gap-2">
          <Calendar class="w-4 h-4 text-primary-600" />
          <span class="font-semibold text-ink">{{ formatDateDisplay(day.date) }}</span>
        </div>
        <div class="flex items-center gap-2">
          <span
            v-if="day.is_today"
            class="px-2 py-0.5 rounded-full text-xs font-semibold bg-primary-100 text-primary-700 border border-primary-200"
          >
            Today
          </span>
          <span
            v-else-if="day.is_locked"
            class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-zinc-100 text-zinc-600 border border-zinc-200"
          >
            <Lock class="w-3 h-3 text-zinc-500" />
            {{ t('mood.lockedBadge') }}
          </span>
        </div>
      </div>

      <!-- My Mood Section -->
      <div class="p-4 rounded-2xl border border-primary-100 bg-primary-50/40 space-y-2">
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold text-primary-900 uppercase tracking-wider flex items-center gap-1.5">
            <User class="w-3.5 h-3.5 text-primary-600" />
            {{ t('mood.heatmap.myMood') }}
          </span>
          <div v-if="day.score" class="flex items-center gap-1.5 font-bold text-primary-700">
            <span class="text-xl">{{ getMoodByScore(day.score)?.emoji }}</span>
            <span>{{ day.score }}/10</span>
          </div>
        </div>

        <div v-if="day.score">
          <p class="text-xs text-ink-muted capitalize mb-1">
            {{ day.tag }}
          </p>
          <div v-if="day.note" class="p-3 rounded-xl bg-white border border-primary-100 shadow-2xs">
            <p class="text-ink leading-relaxed whitespace-pre-wrap text-xs sm:text-sm font-sans">{{ day.note }}</p>
          </div>
          <p v-else class="text-xs text-ink-faint italic">
            (No personal note recorded for this day)
          </p>
        </div>
        <div v-else class="text-xs text-ink-muted italic py-1">
          {{ t('mood.heatmap.unlogged') }}
        </div>
      </div>

      <!-- Partner Mood Section (if present) -->
      <div v-if="day.partner_score" class="p-4 rounded-2xl border border-pink-100 bg-pink-50/40 space-y-2">
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold text-pink-900 uppercase tracking-wider flex items-center gap-1.5">
            <Heart class="w-3.5 h-3.5 text-pink-500" />
            {{ partnerName ? t('mood.partnerMood', { name: partnerName }) : t('mood.heatmap.partnerMood') }}
          </span>
          <div class="flex items-center gap-1.5 font-bold text-pink-700">
            <span class="text-xl">{{ getMoodByScore(day.partner_score)?.emoji }}</span>
            <span>{{ day.partner_score }}/10</span>
          </div>
        </div>

        <div>
          <p class="text-xs text-pink-600 capitalize mb-1">
            {{ day.partner_tag }}
          </p>
          <div v-if="day.partner_note" class="p-3 rounded-xl bg-white border border-pink-100 shadow-2xs">
            <p class="text-ink leading-relaxed whitespace-pre-wrap text-xs sm:text-sm font-sans">{{ day.partner_note }}</p>
          </div>
          <p v-else class="text-xs text-ink-faint italic">
            (No partner note recorded)
          </p>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex justify-end pt-2">
        <AppButton variant="secondary" size="sm" @click="emit('close')">
          {{ t('common.close') }}
        </AppButton>
      </div>
    </div>
  </AppModal>
</template>
