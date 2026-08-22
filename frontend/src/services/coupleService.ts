import { apiClient } from '@/services/apiClient'
import type { Couple, CoupleCreatePayload, CoupleUpdatePayload } from '@/types/couple'

export const coupleService = {
  async getCouples(status?: string): Promise<Couple[]> {
    const response = await apiClient.get<Couple[]>('/couples', {
      params: status ? { status } : undefined,
    })
    return response.data
  },

  async getMyCouple(): Promise<Couple> {
    const response = await apiClient.get<Couple>('/couples/me')
    return response.data
  },

  async getCouple(coupleId: string): Promise<Couple> {
    const response = await apiClient.get<Couple>(`/couples/${coupleId}`)
    return response.data
  },

  async createCouple(payload: CoupleCreatePayload): Promise<Couple> {
    const response = await apiClient.post<Couple>('/couples', payload)
    return response.data
  },

  async updateCouple(coupleId: string, payload: CoupleUpdatePayload): Promise<Couple> {
    const response = await apiClient.patch<Couple>(`/couples/${coupleId}`, payload)
    return response.data
  },

  async deleteCouple(coupleId: string): Promise<void> {
    await apiClient.delete(`/couples/${coupleId}`)
  },
}
