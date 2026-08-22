export interface UserPartnerSummary {
  id: string
  email: string
  full_name: string
  avatar_url?: string | null
}

export interface Couple {
  id: string
  user1_id: string
  user2_id: string
  start_date: string
  nickname?: string | null
  status: string
  cover_url?: string | null
  created_at: string
  updated_at: string
  user1?: UserPartnerSummary | null
  user2?: UserPartnerSummary | null
  days_together?: number
}

export interface CoupleCreatePayload {
  user1_id: string
  user2_id: string
  start_date: string
  nickname?: string | null
  status?: string
  cover_url?: string | null
}

export interface CoupleUpdatePayload {
  user1_id?: string
  user2_id?: string
  start_date?: string
  nickname?: string | null
  status?: string
  cover_url?: string | null
}
