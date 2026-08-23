import { apiClient } from '@/services/apiClient'
import type {
  HeatmapResponse,
  MoodCreatePayload,
  MoodItem,
  MoodStats,
  MoodUpdatePayload,
  TodayMoodResponse,
} from '@/types/mood'

export const moodService = {
  async getTodayMood(timezone?: string): Promise<TodayMoodResponse> {
    const tz = timezone || Intl.DateTimeFormat().resolvedOptions().timeZone || 'Asia/Ho_Chi_Minh'
    const response = await apiClient.get<TodayMoodResponse>('/moods/today', {
      params: { timezone: tz },
    })
    return response.data
  },

  async logMood(payload: MoodCreatePayload): Promise<MoodItem> {
    const tz = payload.timezone || Intl.DateTimeFormat().resolvedOptions().timeZone || 'Asia/Ho_Chi_Minh'
    const response = await apiClient.post<MoodItem>('/moods', {
      ...payload,
      timezone: tz,
    })
    return response.data
  },

  async updateMood(moodId: string, payload: MoodUpdatePayload): Promise<MoodItem> {
    const tz = payload.timezone || Intl.DateTimeFormat().resolvedOptions().timeZone || 'Asia/Ho_Chi_Minh'
    const response = await apiClient.put<MoodItem>(`/moods/${moodId}`, {
      ...payload,
      timezone: tz,
    })
    return response.data
  },

  async deleteMood(moodId: string, timezone?: string): Promise<void> {
    const tz = timezone || Intl.DateTimeFormat().resolvedOptions().timeZone || 'Asia/Ho_Chi_Minh'
    await apiClient.delete(`/moods/${moodId}`, {
      params: { timezone: tz },
    })
  },

  async getMoods(params?: {
    from_date?: string
    to_date?: string
    include_partner?: boolean
    timezone?: string
    skip?: number
    limit?: number
  }): Promise<MoodItem[]> {
    const tz = params?.timezone || Intl.DateTimeFormat().resolvedOptions().timeZone || 'Asia/Ho_Chi_Minh'
    const response = await apiClient.get<MoodItem[]>('/moods', {
      params: { ...params, timezone: tz },
    })
    return response.data
  },

  async getHeatmap(params?: {
    year?: number
    timezone?: string
    include_partner?: boolean
  }): Promise<HeatmapResponse> {
    const tz = params?.timezone || Intl.DateTimeFormat().resolvedOptions().timeZone || 'Asia/Ho_Chi_Minh'
    const response = await apiClient.get<HeatmapResponse>('/moods/heatmap', {
      params: { ...params, timezone: tz },
    })
    return response.data
  },

  async getStats(params?: { from_date?: string; to_date?: string }): Promise<MoodStats> {
    const response = await apiClient.get<MoodStats>('/moods/stats', { params })
    return response.data
  },
}
