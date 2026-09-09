<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import type { StickerItem, StickerPackManifest } from '@/types/sticker'
import AppModal from '@/components/ui/AppModal.vue'
import AppButton from '@/components/ui/AppButton.vue'
import { Sparkles, Trash2, Loader2, Check, X, UploadCloud } from 'lucide-vue-next'
import { apiClient } from '@/services/apiClient'

interface Props {
  show: boolean
  manifest: StickerPackManifest | null
  pinnedCount: number
}

const props = withDefaults(defineProps<Props>(), {
  show: false,
  manifest: null,
  pinnedCount: 0,
})

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'select-sticker', item: StickerItem): void
  (e: 'clear-all'): void
}>()

const { t, te } = useI18n()
const selectedCategory = ref<string>('all')

// Tip banner state: cho phép user tắt, nhưng khi mở lại modal thì vẫn hiện lại
const showTip = ref(true)

watch(
  () => props.show,
  (isOpen) => {
    if (isOpen) {
      showTip.value = true
    }
  }
)

// Modal loading & feedback state
const isPinning = ref(false)
const pinningItem = ref<StickerItem | null>(null)
const isSuccess = ref(false)

// Custom stickers & image/gif input upload state
const CUSTOM_STORAGE_KEY = 'solene_custom_stickers'
const fileInputRef = ref<HTMLInputElement | null>(null)
const customStickers = ref<StickerItem[]>([])

function loadCustomStickers() {
  try {
    const raw = localStorage.getItem(CUSTOM_STORAGE_KEY)
    if (raw) {
      customStickers.value = JSON.parse(raw)
    }
  } catch {
    customStickers.value = []
  }
}

function saveCustomStickers() {
  try {
    localStorage.setItem(CUSTOM_STORAGE_KEY, JSON.stringify(customStickers.value))
  } catch {
    // Ignore quota limits
  }
}

onMounted(() => {
  loadCustomStickers()
})

function triggerFileInput() {
  if (fileInputRef.value) {
    fileInputRef.value.value = ''
    fileInputRef.value.click()
  }
}

async function handleFileChange(e: Event) {
  const input = e.target as HTMLInputElement
  if (!input.files || input.files.length === 0) return
  const file = input.files[0]
  if (!file.type.startsWith('image/')) return

  const cleanName = file.name.replace(/\.[^/.]+$/, '').slice(0, 30) || 'Sticker'
  const localPreviewUrl = URL.createObjectURL(file)

  isPinning.value = true
  isSuccess.value = false
  pinningItem.value = {
    id: `temp_custom_${Date.now()}`,
    name: cleanName,
    filename: file.name,
    url: localPreviewUrl,
    category: file.type === 'image/gif' ? 'gif' : 'custom',
  }

  try {
    let finalUrl = localPreviewUrl

    // Try backend upload
    try {
      const formData = new FormData()
      formData.append('file', file, file.name)
      const res = await apiClient.post<{ url: string }>('/media/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      if (res.data?.url) {
        finalUrl = res.data.url
      }
    } catch (uploadErr) {
      console.warn('Backend upload unavailable, falling back to base64 Data URL:', uploadErr)
      finalUrl = await new Promise<string>((resolve) => {
        const reader = new FileReader()
        reader.onload = () => resolve(reader.result as string)
        reader.onerror = () => resolve(localPreviewUrl)
        reader.readAsDataURL(file)
      })
    }

    const newCustomItem: StickerItem = {
      id: `custom_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
      name: cleanName,
      filename: file.name,
      url: finalUrl,
      category: file.type === 'image/gif' ? 'gif' : 'custom',
    }

    customStickers.value.unshift(newCustomItem)
    saveCustomStickers()

    // Pin directly onto canvas
    emit('select-sticker', newCustomItem)

    await new Promise((resolve) => setTimeout(resolve, 400))
    isSuccess.value = true
    await new Promise((resolve) => setTimeout(resolve, 450))
  } catch (err) {
    console.error('Failed to process custom sticker:', err)
  } finally {
    isPinning.value = false
    pinningItem.value = null
    isSuccess.value = false
    if (fileInputRef.value) {
      fileInputRef.value.value = ''
    }
  }
}

function handleDeleteCustom(id: string) {
  customStickers.value = customStickers.value.filter((s) => s.id !== id)
  saveCustomStickers()
}

function getCategoryLabel(key: string, fallback: string) {
  const i18nKey = `stickers.categories.${key}`
  return te(i18nKey) ? t(i18nKey) : fallback
}

const categories = computed(() => {
  const customCount = customStickers.value.length
  const customLabel = customCount > 0
    ? `${getCategoryLabel('custom', 'Của bạn')} (${customCount})`
    : getCategoryLabel('custom', 'Của bạn')

  if (!props.manifest?.categories) {
    return [
      { key: 'all', name: t('stickers.categories.all') },
      { key: 'custom', name: customLabel },
      { key: 'gif', name: getCategoryLabel('gif', 'GIF') },
      { key: 'chiikawa', name: 'Chiikawa' },
      { key: 'hachiware', name: 'Hachiware' },
      { key: 'usagi', name: 'Usagi' },
    ]
  }

  const list = [...props.manifest.categories]
  if (!list.some((c) => c.key === 'custom')) {
    list.splice(1, 0, { key: 'custom', name: customLabel })
  }
  return list
})

const allStickers = computed(() => {
  const base = props.manifest?.stickers || []
  return [...customStickers.value, ...base]
})

const filteredStickers = computed(() => {
  if (selectedCategory.value === 'all') {
    return allStickers.value
  }
  if (selectedCategory.value === 'custom') {
    return customStickers.value
  }
  return allStickers.value.filter(
    (s) => s.category.toLowerCase() === selectedCategory.value.toLowerCase()
  )
})

async function handlePick(item: StickerItem) {
  if (isPinning.value) return
  isPinning.value = true
  pinningItem.value = item
  isSuccess.value = false

  emit('select-sticker', item)

  await new Promise((resolve) => setTimeout(resolve, 400))
  isSuccess.value = true

  await new Promise((resolve) => setTimeout(resolve, 450))
  isPinning.value = false
  pinningItem.value = null
  isSuccess.value = false
}

function handleClearAll() {
  if (confirm(t('stickers.confirmClear'))) {
    emit('clear-all')
  }
}
</script>

<template>
  <AppModal
    :show="show"
    width="md"
    :draggable="false"
    :maximizable="false"
    :bottom-sheet-on-mobile="false"
    @close="emit('close')"
  >
    <!-- Modal Header -->
    <template #header>
      <div class="flex items-center justify-between gap-3 w-full pr-2 select-none">
        <div class="flex items-center gap-2">
          <div class="w-8 h-8 rounded-xl bg-amber-100 flex items-center justify-center text-amber-600 shadow-2xs">
            <Sparkles class="w-4 h-4" />
          </div>
          <div>
            <h3 class="text-sm sm:text-base font-bold text-ink leading-tight">
              {{ t('stickers.title') }}
            </h3>
            <p class="text-[11px] text-ink-muted">
              {{ t('stickers.subtitle') }}
            </p>
          </div>
        </div>

        <!-- Pinned count badge -->
        <span
          v-if="pinnedCount > 0"
          class="px-2.5 py-1 rounded-full bg-primary-50 border border-primary-200 text-primary-700 text-xs font-semibold"
        >
          {{ t('stickers.pinnedCount', { count: pinnedCount }) }}
        </span>
      </div>
    </template>

    <!-- Modal Content Body -->
    <div class="space-y-3.5 py-1 select-none">
      <!-- Tip Banner: Pinning & Double-Tap to Unlock (Có nút tắt, mở lại modal vẫn hiện) -->
      <Transition name="fade">
        <div
          v-if="showTip"
          class="relative flex items-start gap-2.5 p-2.5 sm:p-3 rounded-2xl bg-amber-50/90 border border-amber-200/80 text-amber-950 text-xs shadow-2xs"
        >
          <span class="text-base leading-none shrink-0 mt-0.5">📌</span>
          <div class="space-y-0.5 leading-snug flex-1 pr-1">
            <p class="font-bold text-amber-900">
              {{ t('stickers.tipTitle') }}
            </p>
            <p class="text-[11px] text-amber-800/90">
              {{ t('stickers.tipDesc') }}
            </p>
          </div>
          <button
            type="button"
            class="p-1 -mr-1 -mt-1 rounded-lg text-amber-800/60 hover:text-amber-950 hover:bg-amber-200/60 transition-colors cursor-pointer shrink-0"
            :title="t('common.close')"
            @click="showTip = false"
          >
            <X class="w-3.5 h-3.5" />
          </button>
        </div>
      </Transition>

      <!-- Category Filter Tabs & Upload Button -->
      <div class="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-none">
        <button
          v-for="cat in categories"
          :key="cat.key"
          type="button"
          class="px-3 py-1.5 rounded-xl text-xs font-semibold transition-all cursor-pointer whitespace-nowrap"
          :class="[
            selectedCategory === cat.key
              ? 'bg-primary-600 text-white shadow-xs'
              : 'bg-surface-subtle text-ink-muted hover:text-ink hover:bg-surface-raised'
          ]"
          @click="selectedCategory = cat.key"
        >
          {{ getCategoryLabel(cat.key, cat.name) }}
        </button>

        <!-- Nút thêm ảnh / sticker / GIF tùy chỉnh -->
        <button
          type="button"
          class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-primary-50 hover:bg-primary-100 text-primary-700 border border-primary-200/80 transition-all cursor-pointer whitespace-nowrap ml-auto shrink-0 shadow-2xs"
          :title="t('stickers.uploadCustomTitle')"
          @click="triggerFileInput"
        >
          <UploadCloud class="w-3.5 h-3.5" />
          <span>{{ t('stickers.uploadCustom') }}</span>
        </button>
      </div>

      <!-- Hidden File Input for Custom Image/GIF Upload -->
      <input
        ref="fileInputRef"
        type="file"
        accept="image/png,image/jpeg,image/webp,image/gif,image/svg+xml"
        class="hidden"
        @change="handleFileChange"
      />

      <!-- Sticker Cards Grid -->
      <div class="grid grid-cols-3 sm:grid-cols-4 gap-2.5 max-h-[380px] overflow-y-auto pr-1 py-1">
        <!-- Ô tải lên ảnh/sticker trực tiếp trong lưới (Hiển thị ở tab Tất cả & tab Của bạn) -->
        <button
          v-if="selectedCategory === 'all' || selectedCategory === 'custom'"
          type="button"
          class="group relative flex flex-col items-center justify-center p-2.5 rounded-2xl border-2 border-dashed border-primary-200 hover:border-primary-400 bg-primary-50/40 hover:bg-primary-50/80 transition-all cursor-pointer min-h-[115px]"
          :title="t('stickers.uploadCustomTitle')"
          @click="triggerFileInput"
        >
          <div class="w-10 h-10 rounded-xl bg-white border border-primary-100 flex items-center justify-center text-primary-600 shadow-2xs group-hover:scale-110 group-hover:rotate-6 transition-transform mb-1.5">
            <UploadCloud class="w-5 h-5" />
          </div>
          <span class="text-xs font-bold text-primary-950 text-center leading-tight">
            {{ t('stickers.uploadCustom') }}
          </span>
          <span class="text-[9px] text-primary-600/80 font-mono mt-0.5">
            PNG, GIF, JPG
          </span>
        </button>

        <div
          v-for="item in filteredStickers"
          :key="item.id"
          class="group relative flex flex-col items-center justify-center p-2.5 rounded-2xl bg-white border border-neutral-100 hover:border-primary-300 shadow-2xs hover:shadow-md hover:-translate-y-0.5 active:scale-95 transition-all cursor-pointer select-none"
          :title="t('stickers.clickToPin', { name: item.name })"
          @click="handlePick(item)"
        >
          <!-- Nút xóa sticker tùy chỉnh do user tự thêm -->
          <button
            v-if="item.id.startsWith('custom_')"
            type="button"
            class="absolute top-1.5 right-1.5 p-1 rounded-lg bg-neutral-100 hover:bg-rose-500 hover:text-white text-neutral-500 transition-colors z-20 cursor-pointer shadow-2xs opacity-0 group-hover:opacity-100"
            :title="t('stickers.deleteCustom')"
            @click.stop="handleDeleteCustom(item.id)"
          >
            <X class="w-3 h-3" />
          </button>

          <!-- GIF Indicator Badge -->
          <span
            v-if="item.url.endsWith('.gif') || item.category === 'gif'"
            class="absolute top-2 left-2 px-1 py-0.2 rounded-md bg-amber-500 text-white text-[9px] font-bold font-mono tracking-wider shadow-2xs z-10 pointer-events-none"
          >
            GIF
          </span>

          <div class="w-16 h-16 sm:w-20 sm:h-20 flex items-center justify-center p-1">
            <img
              :src="item.url"
              :alt="item.name"
              class="w-full h-full object-contain group-hover:scale-110 transition-transform duration-200"
              loading="lazy"
            />
          </div>
          <span class="text-[11px] text-ink font-medium mt-1 truncate max-w-full text-center">
            {{ item.name }}
          </span>
        </div>
      </div>
    </div>

    <!-- Modal Footer Actions -->
    <template #footer>
      <div class="flex items-center justify-between w-full">
        <AppButton
          v-if="pinnedCount > 0"
          variant="secondary"
          size="sm"
          class="text-rose-600 hover:bg-rose-50 border-rose-200"
          @click="handleClearAll"
        >
          <Trash2 class="w-3.5 h-3.5 mr-1" />
          {{ t('stickers.clearAll') }}
        </AppButton>
        <div v-else></div>

        <AppButton
          variant="primary"
          size="sm"
          @click="emit('close')"
        >
          {{ t('common.close') }}
        </AppButton>
      </div>
    </template>

    <!-- Modal Full Loading & Notification Overlay -->
    <template #overlay>
      <Transition name="fade">
        <div
          v-if="isPinning"
          class="absolute inset-0 z-50 bg-white/85 backdrop-blur-xs flex flex-col items-center justify-center p-6 select-none"
        >
          <div class="relative w-20 h-20 mb-3 flex items-center justify-center animate-bounce">
            <img
              v-if="pinningItem"
              :src="pinningItem.url"
              :alt="pinningItem.name"
              class="w-full h-full object-contain"
            />
          </div>

          <div class="flex items-center gap-2 px-4 py-2.5 rounded-2xl bg-white/95 border border-primary-200/80 shadow-lg shadow-primary-500/10">
            <Loader2 v-if="!isSuccess" class="w-4 h-4 text-primary-600 animate-spin shrink-0" />
            <Check v-else class="w-4 h-4 text-emerald-600 stroke-[3] shrink-0" />
            <span class="text-xs sm:text-sm font-semibold text-primary-950">
              {{ isSuccess ? t('stickers.pinSuccess', { name: pinningItem?.name || '' }) : t('stickers.pinningNotice', { name: pinningItem?.name || '' }) }}
            </span>
          </div>
        </div>
      </Transition>
    </template>
  </AppModal>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
