import { apiClient } from '@/services/apiClient'
import type { MemoryItem } from '@/types/memory'
import type { PaginatedResponse } from '@/types/pagination'

export const memoryService = {
  async getMemories(params?: {
    page?: number
    per_page?: number
    display_type?: string
    search?: string
  }): Promise<PaginatedResponse<MemoryItem>> {
    const response = await apiClient.get<PaginatedResponse<MemoryItem>>('/memories', { params })
    return response.data
  },

  async createMemory(payload: {
    title: string
    content: string
    image_url?: string | null
    image_urls?: string[]
    category?: string
    display_type?: 'DATE' | 'RANDOM'
    target_date?: string | null
    is_shared?: boolean
  }): Promise<MemoryItem> {
    const response = await apiClient.post<MemoryItem>('/memories', payload)
    return response.data
  },

  async updateMemory(
    memoryId: string,
    payload: {
      title?: string
      content?: string
      image_url?: string | null
      image_urls?: string[]
      category?: string
      display_type?: string
      target_date?: string | null
      is_shared?: boolean
    },
  ): Promise<MemoryItem> {
    const response = await apiClient.put<MemoryItem>(`/memories/${memoryId}`, payload)
    return response.data
  },

  async deleteMemory(memoryId: string): Promise<void> {
    await apiClient.delete(`/memories/${memoryId}`)
  },
}
