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
