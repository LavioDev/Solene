import { apiClient } from '@/services/apiClient'
import type {
  Couple,
  CoupleCreatePayload,
  CoupleInvitation,
  CoupleInvitationAcceptPayload,
  CoupleInvitationInfo,
  CoupleUpdatePayload,
} from '@/types/couple'
import type { PaginatedResponse } from '@/types/pagination'

export const coupleService = {
  async getCouples(params?: {
    status?: string
    page?: number
    per_page?: number
    search?: string
  } | string): Promise<PaginatedResponse<Couple>> {
    const queryParams = typeof params === 'string' ? { status: params } : params
    const response = await apiClient.get<PaginatedResponse<Couple>>('/couples', {
      params: queryParams,
    })
    return response.data
  },

  async getMyCouple(): Promise<Couple | null> {
    const response = await apiClient.get<Couple | null>('/couples/me')
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

  // --- Couple Invitations & Pairing ---

  async createInvitation(): Promise<CoupleInvitation> {
    const response = await apiClient.post<CoupleInvitation>('/couples/invitations')
    return response.data
  },

  async getCurrentInvitation(): Promise<CoupleInvitation | null> {
    const response = await apiClient.get<CoupleInvitation | null>('/couples/invitations/current')
    return response.data
  },

  async revokeCurrentInvitation(): Promise<void> {
    await apiClient.delete('/couples/invitations/current')
  },

  async getInvitationInfo(code: string): Promise<CoupleInvitationInfo> {
    const response = await apiClient.get<CoupleInvitationInfo>('/couples/invitations/info', {
      params: { code },
    })
    return response.data
  },

  async acceptInvitation(payload: CoupleInvitationAcceptPayload): Promise<Couple> {
    const response = await apiClient.post<Couple>('/couples/invitations/accept', payload)
    return response.data
  },
}

