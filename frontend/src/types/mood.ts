export interface MoodItem {
  id: string
  user_id: string
  entry_date: string
  mood_score: number
  mood_tag: string
  note?: string | null
  activities?: string | null
  is_shared: boolean
  is_locked: boolean
  created_at: string
  updated_at: string
  user_full_name?: string | null
  user_avatar_url?: string | null
}

export interface MoodCreatePayload {
  mood_score: number
  mood_tag: string
  note?: string | null
  activities?: string | null
  is_shared?: boolean
  entry_date?: string
  timezone?: string
}

export interface MoodUpdatePayload {
  mood_score?: number
  mood_tag?: string
  note?: string | null
  activities?: string | null
  is_shared?: boolean
  timezone?: string
}

export interface TodayMoodResponse {
  my_mood: MoodItem | null
  partner_mood: MoodItem | null
}

export interface HeatmapDayItem {
  date: string
  mood_id?: string | null
  score?: number | null  // 1 to 10
  tag?: string | null
  note?: string | null
  is_locked: boolean
  is_today: boolean

  partner_mood_id?: string | null
  partner_score?: number | null
  partner_tag?: string | null
  partner_note?: string | null
}

export interface HeatmapResponse {
  year: number
  total_logged_days: number
  current_streak: number
  longest_streak: number
  average_score: number
  days: HeatmapDayItem[]
}

export interface MoodStats {
  total_entries: number
  average_score: number
  mood_counts: Record<string, number>
  score_distribution: Record<number, number>
}

export interface MoodDefinition {
  score: number
  emoji: string
  tag: string
  nameKey: string
  color: string
  badgeColor: string
  heatmapClass: string
}
