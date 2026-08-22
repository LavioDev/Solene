import { apiClient } from '@/services/apiClient'
import type { PartnerActiveStatus, TaskCreatePayload, TaskItem } from '@/types/task'

export const taskService = {
  async getPartnerActiveStatus(): Promise<PartnerActiveStatus> {
    const response = await apiClient.get<PartnerActiveStatus>('/tasks/partner-active')
    return response.data
  },

  async getTasks(params?: {
    is_completed?: boolean
    start_from?: string
    end_to?: string
    skip?: number
    limit?: number
  }): Promise<TaskItem[]> {
    const response = await apiClient.get<TaskItem[]>('/tasks', { params })
    return response.data
  },

  async createTask(payload: TaskCreatePayload): Promise<TaskItem> {
    const response = await apiClient.post<TaskItem>('/tasks', payload)
    return response.data
  },

  async updateTask(taskId: string, payload: Partial<TaskCreatePayload>): Promise<TaskItem> {
    const response = await apiClient.put<TaskItem>(`/tasks/${taskId}`, payload)
    return response.data
  },

  async toggleTask(taskId: string, is_completed?: boolean): Promise<TaskItem> {
    const response = await apiClient.patch<TaskItem>(`/tasks/${taskId}/toggle`, {
      is_completed,
    })
    return response.data
  },

  async deleteTask(taskId: string): Promise<void> {
    await apiClient.delete(`/tasks/${taskId}`)
  },
}
