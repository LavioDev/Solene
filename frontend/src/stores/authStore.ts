import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiClient, configureAuthInterceptors } from '@/services/apiClient'
import type { User, AuthResponse, LoginPayload, RegisterPayload } from '@/types/auth'

export const useAuthStore = defineStore('auth', () => {
  // In-memory token storage only (Zero localStorage)
  const accessToken = ref<string | null>(null)
  const user = ref<User | null>(null)
  const isInitializing = ref<boolean>(true)

  const isAuthenticated = computed(() => Boolean(accessToken.value && user.value))
  const isAdmin = computed(() => user.value?.role === 'admin')
  const isManager = computed(() => user.value?.role === 'manager')

  function hasPermission(permissionCode: string): boolean {
    if (!user.value) return false
    if (user.value.role === 'admin') return true
    if (!user.value.permissions) return false
    return user.value.permissions.includes(permissionCode) || user.value.permissions.includes('*')
  }

  function setAccessToken(token: string | null) {
    accessToken.value = token
  }

  function setUser(newUser: User | null) {
    user.value = newUser
  }

  async function login(payload: LoginPayload): Promise<void> {
    const response = await apiClient.post<AuthResponse>('/auth/login', payload)
    accessToken.value = response.data.access_token
    user.value = response.data.user
  }

  async function register(payload: RegisterPayload): Promise<void> {
    const response = await apiClient.post<AuthResponse>('/auth/register', payload)
    accessToken.value = response.data.access_token
    user.value = response.data.user
  }

  async function logout(): Promise<void> {
    try {
      await apiClient.post('/auth/logout')
    } catch {
      // ignore network errors on logout
    } finally {
      accessToken.value = null
      user.value = null
      const { useMoodStore } = await import('./moodStore')
      useMoodStore().reset()
    }
  }

  async function checkAuth(): Promise<boolean> {
    isInitializing.value = true
    try {
      // Attempt silent refresh via HttpOnly cookie
      const refreshResponse = await apiClient.post<AuthResponse>('/auth/refresh')
      accessToken.value = refreshResponse.data.access_token
      user.value = refreshResponse.data.user
      return true
    } catch {
      accessToken.value = null
      user.value = null
      return false
    } finally {
      isInitializing.value = false
    }
  }

  // Setup interceptors linking with this Pinia store
  configureAuthInterceptors(
    () => accessToken.value,
    (token) => { accessToken.value = token },
    () => {
      accessToken.value = null
      user.value = null
    }
  )

  return {
    accessToken,
    user,
    isInitializing,
    isAuthenticated,
    isAdmin,
    isManager,
    hasPermission,
    setAccessToken,
    setUser,
    login,
    register,
    logout,
    checkAuth,
  }
})
