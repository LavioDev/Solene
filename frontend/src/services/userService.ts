import { apiClient } from '@/services/apiClient'
import type { Permission, User, UserCreatePayload, UserFilterParams, UserUpdatePayload } from '@/types/auth'
import type { PaginatedResponse } from '@/types/pagination'

export const userService = {
  async getUsers(params?: UserFilterParams): Promise<PaginatedResponse<User>> {
    const response = await apiClient.get<PaginatedResponse<User>>('/users', { params })
    return response.data
  },

  async getUser(userId: string): Promise<User> {
    const response = await apiClient.get<User>(`/users/${userId}`)
    return response.data
  },

  async createUser(payload: UserCreatePayload): Promise<User> {
    const response = await apiClient.post<User>('/users', payload)
    return response.data
  },

  async updateUser(userId: string, payload: UserUpdatePayload): Promise<User> {
    const response = await apiClient.patch<User>(`/users/${userId}`, payload)
    return response.data
  },

  async deleteUser(userId: string): Promise<void> {
    await apiClient.delete(`/users/${userId}`)
  },

  async getAllPermissions(): Promise<Permission[]> {
    const response = await apiClient.get<Permission[]>('/permissions')
    return response.data
  },

  async getUserPermissions(userId: string): Promise<Permission[]> {
    const response = await apiClient.get<Permission[]>(`/permissions/users/${userId}`)
    return response.data
  },

  async assignUserPermissions(userId: string, permissionIds: string[]): Promise<Permission[]> {
    const response = await apiClient.put<Permission[]>(`/permissions/users/${userId}`, {
      permission_ids: permissionIds,
    })
    return response.data
  },
}
