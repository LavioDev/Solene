import { ref, onMounted } from 'vue'
import { stickerService } from '@/services/stickerService'
import type {
  PinnedSticker,
  StickerItem,
  StickerPackManifest,
} from '@/types/sticker'

const STORAGE_KEY = 'solene_board_stickers'

// Module-level shared reactive state
const pinnedStickers = ref<PinnedSticker[]>([])
const loading = ref(false)
const isSyncing = ref(false)
const isPickerOpen = ref(false)
const packManifest = ref<StickerPackManifest | null>(null)
let isInitialized = false

export function useStickerBoard() {
  // Debounce timer for saving moved stickers to backend
  let debounceSyncTimer: ReturnType<typeof setTimeout> | null = null

  function saveToLocalStorage() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(pinnedStickers.value))
    } catch {
      // Ignore quota errors
    }
  }

  function loadFromLocalStorage(): PinnedSticker[] {
    try {
      const raw = localStorage.getItem(STORAGE_KEY)
      return raw ? JSON.parse(raw) : []
    } catch {
      return []
    }
  }

  async function fetchBoardStickers() {
    loading.value = true
    try {
      const serverStickers = await stickerService.getBoardStickers()
      pinnedStickers.value = serverStickers
      saveToLocalStorage()
    } catch (err) {
      console.warn('Could not fetch stickers from backend, using local storage fallback:', err)
      pinnedStickers.value = loadFromLocalStorage()
    } finally {
      loading.value = false
    }
  }

  async function loadManifest() {
    try {
      packManifest.value = await stickerService.getPackManifest()
    } catch (err) {
      console.error('Failed to load Chiikawa sticker pack manifest:', err)
    }
  }

  function getHighestZIndex(): number {
    if (pinnedStickers.value.length === 0) return 10
    return Math.max(...pinnedStickers.value.map((s) => s.z_index || 10)) + 1
  }

  async function pinSticker(
    item: StickerItem,
    customPos?: { x_percent: number; y_percent: number }
  ) {
    // Random gentle tilt between -10 and +10 degrees for cute playful sticker feel
    const randomTilt = Math.round((Math.random() * 20 - 10) * 10) / 10
    // Default position: slightly scattered near center
    const x = customPos ? customPos.x_percent : Math.round(40 + Math.random() * 20)
    const y = customPos ? customPos.y_percent : Math.round(40 + Math.random() * 20)
    const nextZ = getHighestZIndex()

    const tempId = `temp_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`
    const newSticker: PinnedSticker = {
      id: tempId,
      sticker_url: item.url,
      name: item.name,
      x_percent: x,
      y_percent: y,
      scale: 1.0,
      rotation: randomTilt,
      z_index: nextZ,
    }

    // Optimistic UI update
    pinnedStickers.value.push(newSticker)
    saveToLocalStorage()

    try {
      const created = await stickerService.pinSticker({
        sticker_url: item.url,
        name: item.name,
        x_percent: x,
        y_percent: y,
        scale: 1.0,
        rotation: randomTilt,
        z_index: nextZ,
      })
      // Replace tempId with real UUID from server
      const idx = pinnedStickers.value.findIndex((s) => s.id === tempId)
      if (idx !== -1) {
        pinnedStickers.value[idx] = created
      }
      saveToLocalStorage()
    } catch (err) {
      console.warn('Sticker saved locally only (backend pairing not active or failed):', err)
    }
  }

  function updateStickerLocal(id: string, updates: Partial<PinnedSticker>) {
    const sticker = pinnedStickers.value.find((s) => s.id === id)
    if (!sticker) return

    Object.assign(sticker, updates)
    saveToLocalStorage()

    // Debounced sync to backend
    if (debounceSyncTimer) clearTimeout(debounceSyncTimer)
    debounceSyncTimer = setTimeout(async () => {
      if (sticker.id.startsWith('temp_')) return
      try {
        isSyncing.value = true
        await stickerService.updatePinnedSticker(sticker.id, {
          x_percent: sticker.x_percent,
          y_percent: sticker.y_percent,
          scale: sticker.scale,
          rotation: sticker.rotation,
          z_index: sticker.z_index,
          is_locked: sticker.is_locked,
        })
      } catch (err) {
        console.warn('Failed to sync sticker position to backend:', err)
      } finally {
        isSyncing.value = false
      }
    }, 400)
  }

  function toggleLock(id: string) {
    const sticker = pinnedStickers.value.find((s) => s.id === id)
    if (!sticker) return
    const nextLocked = !sticker.is_locked
    updateStickerLocal(id, { is_locked: nextLocked })
  }

  function bringToFront(id: string) {
    const sticker = pinnedStickers.value.find((s) => s.id === id)
    if (!sticker) return
    const highest = getHighestZIndex()
    if (sticker.z_index !== highest) {
      updateStickerLocal(id, { z_index: highest })
    }
  }

  async function removeSticker(id: string) {
    const idx = pinnedStickers.value.findIndex((s) => s.id === id)
    if (idx === -1) return

    const target = pinnedStickers.value[idx]
    pinnedStickers.value.splice(idx, 1)
    saveToLocalStorage()

    if (!target.id.startsWith('temp_')) {
      try {
        await stickerService.deletePinnedSticker(target.id)
      } catch (err) {
        console.warn('Failed to delete sticker on backend:', err)
      }
    }
  }

  async function clearAll() {
    pinnedStickers.value = []
    saveToLocalStorage()
    try {
      await stickerService.clearBoard()
    } catch (err) {
      console.warn('Failed to clear board on backend:', err)
    }
  }

  onMounted(() => {
    if (!isInitialized) {
      isInitialized = true
      fetchBoardStickers()
      loadManifest()
    }
  })

  return {
    pinnedStickers,
    loading,
    isSyncing,
    isPickerOpen,
    packManifest,
    pinSticker,
    updateStickerLocal,
    toggleLock,
    bringToFront,
    removeSticker,
    clearAll,
    fetchBoardStickers,
  }
}
