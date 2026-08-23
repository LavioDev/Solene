export interface EventOccurrence {
  event_id: string
  title: string
  date: string // YYYY-MM-DD
  category: string
  milestone_info?: string
  image_url?: string
  is_shared?: boolean
}

export interface CalendarDay {
  date: Date
  dateStr: string
  dayNumber: number
  isCurrentMonth: boolean
  isToday: boolean
  events: EventOccurrence[]
}

export interface TaskItem {
  id: string
  user_id: string
  title: string
  content?: string | null
  is_completed: boolean
  is_shared?: boolean
  start_time?: string | null
  end_time?: string | null
  priority: string
  created_at: string
  updated_at: string
}

export interface SpecialEvent {
  id: string
  user_id: string
  title: string
  anchor_date: string
  recurrence_type: 'EVERY_N_DAYS' | 'MONTHLY' | 'YEARLY' | 'SINGLE'
  interval_value: number
  category: string
  description?: string | null
  is_shared?: boolean
  created_at: string
}



