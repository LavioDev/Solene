import type { UserPartnerSummary } from './couple'

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

export interface PartnerActiveStatus {
  in_couple: boolean
  partner?: UserPartnerSummary | null
  is_busy: boolean
  active_task?: TaskItem | null
}

export interface TaskCreatePayload {
  title: string
  content?: string | null
  is_completed?: boolean
  start_time?: string | null
  end_time?: string | null
  priority?: string
}
