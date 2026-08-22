export interface EventOccurrence {
  event_id: string
  title: string
  date: string // YYYY-MM-DD
  category: string
  milestone_info?: string
  image_url?: string
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
  start_time?: string | null
  end_time?: string | null
  priority: string
  created_at: string
  updated_at: string
}

