export interface User {
  id: string
  email: string
  full_name: string
  role: string
  is_active: boolean
  avatar_url?: string | null
  created_at?: string
  updated_at?: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

export interface LoginPayload {
  email: string
  password: string
}

export interface RegisterPayload {
  email: string
  password: string
  full_name?: string
}

export interface UserCreatePayload {
  email: string
  password: string
  full_name?: string
  role?: string
  avatar_url?: string | null
  is_active?: boolean
}

export interface UserUpdatePayload {
  email?: string
  password?: string
  full_name?: string
  role?: string
  avatar_url?: string | null
  is_active?: boolean
}

export interface UserFilterParams {
  skip?: number
  limit?: number
  role?: string
  is_active?: boolean
  search?: string
}


