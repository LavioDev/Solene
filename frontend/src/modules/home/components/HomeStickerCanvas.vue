<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { PinnedSticker } from '@/types/sticker'
import { X, RotateCw, Check } from 'lucide-vue-next'

interface Props {
  stickers: PinnedSticker[]
}

defineProps<Props>()

const emit = defineEmits<{
  (e: 'update-sticker', id: string, updates: Partial<PinnedSticker>): void
  (e: 'remove-sticker', id: string): void
  (e: 'bring-to-front', id: string): void
}>()

const { t } = useI18n()
const containerRef = ref<HTMLElement | null>(null)
const draggingId = ref<string | null>(null)

let startPointer = { x: 0, y: 0 }
let startPercent = { x: 0, y: 0 }
let containerSize = { width: 1, height: 1 }
let lastTapTime = 0

function handlePointerDown(e: PointerEvent, sticker: PinnedSticker) {
  // If sticker is locked, dragging is strictly disabled
  if (sticker.is_locked) return
  if (!containerRef.value) return
  // Only handle primary button (left mouse button)
  if (e.button !== 0) return
  // If clicking on control buttons, do not initiate drag
  if ((e.target as HTMLElement).closest('.sticker-action-btn')) return

  emit('bring-to-front', sticker.id)

  const rect = containerRef.value.getBoundingClientRect()
  containerSize = {
    width: Math.max(rect.width, 100),
    height: Math.max(rect.height, 100),
  }

  startPointer = { x: e.clientX, y: e.clientY }
  startPercent = { x: sticker.x_percent, y: sticker.y_percent }
  draggingId.value = sticker.id

  const onPointerMove = (moveEvent: PointerEvent) => {
    if (draggingId.value !== sticker.id) return
    const deltaX = moveEvent.clientX - startPointer.x
    const deltaY = moveEvent.clientY - startPointer.y

    const deltaPercentX = (deltaX / containerSize.width) * 100
    const deltaPercentY = (deltaY / containerSize.height) * 100

    // Clamp between 2% and 92% to keep sticker within canvas
    const newX = Math.max(2, Math.min(92, startPercent.x + deltaPercentX))
    const newY = Math.max(2, Math.min(94, startPercent.y + deltaPercentY))

    emit('update-sticker', sticker.id, {
      x_percent: Math.round(newX * 10) / 10,
      y_percent: Math.round(newY * 10) / 10,
    })
  }

  const onPointerUp = () => {
    draggingId.value = null
    window.removeEventListener('pointermove', onPointerMove)
    window.removeEventListener('pointerup', onPointerUp)
    window.removeEventListener('pointercancel', onPointerUp)
  }

  window.addEventListener('pointermove', onPointerMove, { passive: true })
  window.addEventListener('pointerup', onPointerUp)
  window.addEventListener('pointercancel', onPointerUp)
}

function handleRotate(e: Event, sticker: PinnedSticker) {
  e.stopPropagation()
  const cur = Number(sticker.rotation) || 0
  const nextRotation = (cur + 30) % 360
  emit('update-sticker', sticker.id, { rotation: nextRotation })
}

function handleToggleLock(e: Event, sticker: PinnedSticker) {
  e.stopPropagation()
  emit('update-sticker', sticker.id, { is_locked: true })
}

function handleDoubleClick(sticker: PinnedSticker) {
  // Double-click to unlock sticker
  if (sticker.is_locked) {
    emit('update-sticker', sticker.id, { is_locked: false })
  }
}

function handleTap(sticker: PinnedSticker) {
  const now = Date.now()
  if (now - lastTapTime < 350) {
    handleDoubleClick(sticker)
    lastTapTime = 0
  } else {
    lastTapTime = now
  }
}

function handleWheel(e: WheelEvent, sticker: PinnedSticker) {
  if (sticker.is_locked) return
  e.preventDefault()
  const delta = e.deltaY < 0 ? 0.1 : -0.1
  const newScale = Math.max(0.6, Math.min(2.2, Math.round((sticker.scale + delta) * 10) / 10))
  emit('update-sticker', sticker.id, { scale: newScale })
}
</script>

<template>
  <div
    ref="containerRef"
    class="absolute inset-0 pointer-events-none select-none overflow-visible z-20"
  >
    <TransitionGroup name="sticker-pop">
      <div
        v-for="sticker in stickers"
        :key="sticker.id"
        class="absolute pointer-events-auto group touch-none select-none"
        :class="[
          sticker.is_locked
            ? 'cursor-pointer'
            : draggingId === sticker.id
              ? 'cursor-grabbing opacity-90'
              : 'cursor-grab'
        ]"
        :style="{
          left: `${sticker.x_percent}%`,
          top: `${sticker.y_percent}%`,
          transform: `translate(-50%, -50%) rotate(${sticker.rotation}deg) scale(${sticker.scale})`,
          zIndex: sticker.z_index,
          transition: draggingId === sticker.id ? 'none' : 'transform 0.15s ease-out',
        }"
        :title="sticker.is_locked ? t('stickers.lockedBadge') : (sticker.user_name ? `${sticker.name || 'Chiikawa'} (${t('stickers.pinnedBy', { name: sticker.user_name })})` : (sticker.name || 'Chiikawa'))"
        @pointerdown="(e) => handlePointerDown(e, sticker)"
        @dblclick="() => handleDoubleClick(sticker)"
        @click="() => handleTap(sticker)"
        @wheel="(e) => handleWheel(e, sticker)"
      >
        <!-- Sticker Image Container -->
        <div class="relative w-24 h-24 sm:w-28 sm:h-28 flex items-center justify-center">
          <img
            :src="sticker.sticker_url"
            :alt="sticker.name || 'Sticker'"
            class="w-full h-full object-contain pointer-events-none select-none"
            draggable="false"
          />

          <!-- Action Hover Controls (Only shown when UNLOCKED) -->
          <div
            v-if="!sticker.is_locked"
            class="absolute -top-3 -right-3 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity z-30 pointer-events-auto"
          >
            <!-- Pin / Lock button (Icon 'v' - Check) -->
            <button
              type="button"
              class="sticker-action-btn w-6.5 h-6.5 rounded-full bg-emerald-500 text-white hover:bg-emerald-600 border border-white shadow-md flex items-center justify-center cursor-pointer active:scale-90 transition-transform"
              :title="t('stickers.pinLock')"
              @pointerdown.stop
              @mousedown.stop
              @click="(e) => handleToggleLock(e, sticker)"
            >
              <Check class="w-3.5 h-3.5 stroke-[3]" />
            </button>

            <!-- Rotate button -->
            <button
              type="button"
              class="sticker-action-btn w-6.5 h-6.5 rounded-full bg-white/95 text-ink hover:text-primary-600 border border-neutral-200/90 shadow-md flex items-center justify-center cursor-pointer active:scale-90 transition-transform"
              :title="t('stickers.rotate')"
              @pointerdown.stop
              @mousedown.stop
              @click="(e) => handleRotate(e, sticker)"
            >
              <RotateCw class="w-3.5 h-3.5" />
            </button>

            <!-- Delete sticker button -->
            <button
              type="button"
              class="sticker-action-btn w-6.5 h-6.5 rounded-full bg-rose-500 text-white hover:bg-rose-600 border border-white shadow-md flex items-center justify-center cursor-pointer active:scale-90 transition-transform"
              :title="t('stickers.delete')"
              @pointerdown.stop
              @mousedown.stop
              @click.stop="emit('remove-sticker', sticker.id)"
            >
              <X class="w-3.5 h-3.5 stroke-[3]" />
            </button>
          </div>

          <!-- Pinned by badge (Tiny pill shown on hover when not locked) -->
          <div
            v-if="sticker.user_name && !sticker.is_locked"
            class="absolute -bottom-2 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity px-2 py-0.5 rounded-full bg-black/75 backdrop-blur-xs text-[10px] text-white whitespace-nowrap shadow-xs pointer-events-none font-medium"
          >
            {{ sticker.user_name }}
          </div>
        </div>
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
.sticker-pop-enter-active {
  animation: stickerBounceIn 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.sticker-pop-leave-active {
  transition: all 0.2s ease-in;
}
.sticker-pop-leave-to {
  opacity: 0;
  transform: translate(-50%, -50%) scale(0.4) rotate(15deg);
}

@keyframes stickerBounceIn {
  0% {
    opacity: 0;
    transform: translate(-50%, -50%) scale(0.2) rotate(-15deg);
  }
  70% {
    transform: translate(-50%, -50%) scale(1.15) rotate(4deg);
  }
  100% {
    opacity: 1;
    transform: translate(-50%, -50%) scale(1) rotate(0deg);
  }
}
</style>
