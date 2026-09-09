export interface StickerItem {
  id: string
  filename: string
  url: string
  name: string
  category: string
}

export interface StickerCategory {
  key: string
  name: string
}

export interface StickerPackManifest {
  pack_id: string
  pack_name: string
  version: string
  author?: string
  categories: StickerCategory[]
  stickers: StickerItem[]
}

export interface PinnedSticker {
  id: string
  couple_id?: string
  user_id?: string
  user_name?: string | null
  sticker_url: string
  name?: string | null
  x_percent: number // 0 to 100
  y_percent: number // 0 to 100
  scale: number // e.g. 1.0
  rotation: number // e.g. 0 to 360 or -15 to +15
  z_index: number
  is_locked?: boolean
  created_at?: string
  updated_at?: string
}

export interface PinnedStickerCreatePayload {
  sticker_url: string
  name?: string | null
  x_percent: number
  y_percent: number
  scale?: number
  rotation?: number
  z_index?: number
  is_locked?: boolean
}

export interface PinnedStickerUpdatePayload {
  x_percent?: number
  y_percent?: number
  scale?: number
  rotation?: number
  z_index?: number
  is_locked?: boolean
}
