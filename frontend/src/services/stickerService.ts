import { apiClient } from '@/services/apiClient'
import type {
  PinnedSticker,
  PinnedStickerCreatePayload,
  PinnedStickerUpdatePayload,
  StickerPackManifest,
} from '@/types/sticker'

export const stickerService = {
  async getPackManifest(packPath: string = '/stickers/chiikawa/manifest.json'): Promise<StickerPackManifest> {
    const res = await fetch(packPath)
    if (!res.ok) {
      throw new Error(`Failed to load sticker manifest: ${res.statusText}`)
    }
    return await res.json()
  },

  async getBoardStickers(): Promise<PinnedSticker[]> {
    const response = await apiClient.get<PinnedSticker[]>('/stickers/board')
    return response.data
  },

  async pinSticker(payload: PinnedStickerCreatePayload): Promise<PinnedSticker> {
    const response = await apiClient.post<PinnedSticker>('/stickers/board', payload)
    return response.data
  },

  async updatePinnedSticker(
    stickerId: string,
    payload: PinnedStickerUpdatePayload
  ): Promise<PinnedSticker> {
    const response = await apiClient.put<PinnedSticker>(`/stickers/board/${stickerId}`, payload)
    return response.data
  },

  async batchSyncStickers(stickers: PinnedSticker[]): Promise<PinnedSticker[]> {
    const response = await apiClient.put<PinnedSticker[]>('/stickers/board/batch', {
      stickers: stickers.map((s) => ({
        id: s.id,
        x_percent: s.x_percent,
        y_percent: s.y_percent,
        scale: s.scale,
        rotation: s.rotation,
        z_index: s.z_index,
      })),
    })
    return response.data
  },

  async deletePinnedSticker(stickerId: string): Promise<void> {
    await apiClient.delete(`/stickers/board/${stickerId}`)
  },

  async clearBoard(): Promise<{ message: string; deleted_count: number }> {
    const response = await apiClient.delete<{ message: string; deleted_count: number }>('/stickers/board')
    return response.data
  },
}
