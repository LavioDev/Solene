export interface Permission {
  id: string
  code: string
  name: string
  module: string
  description?: string | null
}

export interface User {
  id: string
  email: string
  full_name: string
  role: string
  is_active: boolean
  avatar_url?: string | null
  permissions?: string[]
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
  permission_ids?: string[]
}

export interface UserUpdatePayload {
  email?: string
  password?: string
  full_name?: string
  role?: string
  avatar_url?: string | null
  is_active?: boolean
  permission_ids?: string[]
}

export interface AssignPermissionsPayload {
  permission_ids: string[]
}

export interface UserFilterParams {
  page?: number
  per_page?: number
  skip?: number
  limit?: number
  role?: string
  is_active?: boolean
  search?: string
}
