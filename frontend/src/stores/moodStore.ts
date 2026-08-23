import { defineStore } from 'pinia'
import { ref } from 'vue'
import { moodService } from '@/services/moodService'
import type {
  HeatmapResponse,
  MoodCreatePayload,
  MoodItem,
  MoodUpdatePayload,
} from '@/types/mood'

export const useMoodStore = defineStore('mood', () => {
  const myTodayMood = ref<MoodItem | null>(null)
  const partnerTodayMood = ref<MoodItem | null>(null)
  const moods = ref<MoodItem[]>([])
  const heatmapData = ref<HeatmapResponse | null>(null)
  const isLoading = ref<boolean>(false)
  const isHeatmapLoading = ref<boolean>(false)

  async function fetchTodayMood() {
    isLoading.value = true
    try {
      const data = await moodService.getTodayMood()
      myTodayMood.value = data.my_mood
      partnerTodayMood.value = data.partner_mood
    } finally {
      isLoading.value = false
    }
  }

  async function logTodayMood(payload: MoodCreatePayload) {
    isLoading.value = true
    try {
      const created = await moodService.logMood(payload)
      myTodayMood.value = created
      // Also refresh heatmap in background if present
      if (heatmapData.value) {
        fetchHeatmap(heatmapData.value.year)
      }
      return created
    } finally {
      isLoading.value = false
    }
  }

  async function updateTodayMood(moodId: string, payload: MoodUpdatePayload) {
    isLoading.value = true
    try {
      const updated = await moodService.updateMood(moodId, payload)
      myTodayMood.value = updated
      if (heatmapData.value) {
        fetchHeatmap(heatmapData.value.year)
      }
      return updated
    } finally {
      isLoading.value = false
    }
  }

  async function deleteTodayMood(moodId: string) {
    isLoading.value = true
    try {
      await moodService.deleteMood(moodId)
      myTodayMood.value = null
      if (heatmapData.value) {
        fetchHeatmap(heatmapData.value.year)
      }
    } finally {
      isLoading.value = false
    }
  }

  async function fetchMoodHistory(params?: { from_date?: string; to_date?: string }) {
    isLoading.value = true
    try {
      const data = await moodService.getMoods(params)
      moods.value = data
      return data
    } finally {
      isLoading.value = false
    }
  }

  async function fetchHeatmap(year?: number, include_partner: boolean = true) {
    isHeatmapLoading.value = true
    try {
      const data = await moodService.getHeatmap({ year, include_partner })
      heatmapData.value = data
      return data
    } finally {
      isHeatmapLoading.value = false
    }
  }

  return {
    myTodayMood,
    partnerTodayMood,
    moods,
    heatmapData,
    isLoading,
    isHeatmapLoading,
    fetchTodayMood,
    logTodayMood,
    updateTodayMood,
    deleteTodayMood,
    fetchMoodHistory,
    fetchHeatmap,
    reset() {
      myTodayMood.value = null
      partnerTodayMood.value = null
      moods.value = []
      heatmapData.value = null
    },
  }
})
