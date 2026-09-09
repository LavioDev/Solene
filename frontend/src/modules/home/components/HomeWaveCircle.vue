<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { Heart, RotateCcw, GripHorizontal } from 'lucide-vue-next'
import type { MoodItem } from '@/types/mood'

interface Props {
  days: number
  hours: number
  minutes: number
  seconds: number
  formattedStartDate: string
  partnerMood?: MoodItem | null
  partnerName?: string
}

withDefaults(defineProps<Props>(), {
  partnerMood: null,
  partnerName: '',
})

const emit = defineEmits<{
  (e: 'open-random-memory'): void
  (e: 'open-particle-heart'): void
}>()

const { t, te } = useI18n()

// Dragging state for partner note (desktop)
const noteRef = ref<HTMLElement | null>(null)
const position = ref({ x: 0, y: 0 })
const isDragging = ref(false)
const isMobile = ref(false)

function checkMobile() {
  if (typeof window !== 'undefined') {
    const wasMobile = isMobile.value
    isMobile.value = window.innerWidth < 768
    if (wasMobile !== isMobile.value) {
      position.value = { x: 0, y: 0 }
      isDragging.value = false
    }
  }
}

const isMoved = computed(() => Math.abs(position.value.x) > 1 || Math.abs(position.value.y) > 1)

const noteTransformStyle = computed(() => {
  return {
    transform: `translate3d(${position.value.x}px, calc(-50% + ${position.value.y}px), 0)${
      isDragging.value ? ' scale(1.02) rotate(1.5deg)' : ''
    }`,
  }
})

let startPointer = { x: 0, y: 0 }
let startPosition = { x: 0, y: 0 }
let startNoteRect = { left: 0, top: 0, width: 0, height: 0 }
let containerBounds = { left: 0, top: 0, right: 0, bottom: 0 }

const MARGIN = 12 // Safe margin to avoid overflowing layout sidebar, header, and screen edges

function getContainerBounds() {
  const mainEl = noteRef.value?.closest('main') || document.querySelector('main')
  if (mainEl) {
    const rect = mainEl.getBoundingClientRect()
    return {
      left: rect.left,
      top: rect.top,
      right: rect.right,
      bottom: rect.bottom,
    }
  }
  return {
    left: 0,
    top: 0,
    right: window.innerWidth,
    bottom: window.innerHeight,
  }
}

function handlePointerDown(event: PointerEvent) {
  if (event.button !== 0 && event.pointerType === 'mouse') return
  if (!noteRef.value) return

  event.preventDefault()

  const noteEl = noteRef.value
  const noteRect = noteEl.getBoundingClientRect()
  const bounds = getContainerBounds()

  startPointer = { x: event.clientX, y: event.clientY }
  startPosition = { x: position.value.x, y: position.value.y }
  startNoteRect = {
    left: noteRect.left,
    top: noteRect.top,
    width: noteRect.width,
    height: noteRect.height,
  }
  containerBounds = bounds

  isDragging.value = true

  window.addEventListener('pointermove', handlePointerMove, { passive: false })
  window.addEventListener('pointerup', handlePointerUp)
  window.addEventListener('pointercancel', handlePointerUp)
}

function handlePointerMove(event: PointerEvent) {
  if (!isDragging.value || !noteRef.value) return

  const deltaX = event.clientX - startPointer.x
  const deltaY = event.clientY - startPointer.y

  const targetClientLeft = startNoteRect.left + deltaX
  const targetClientTop = startNoteRect.top + deltaY

  const minLeft = containerBounds.left + MARGIN
  const maxLeft = containerBounds.right - startNoteRect.width - MARGIN
  const minTop = containerBounds.top + MARGIN
  const maxTop = containerBounds.bottom - startNoteRect.height - MARGIN

  const clampedLeft = Math.max(minLeft, Math.min(maxLeft, targetClientLeft))
  const clampedTop = Math.max(minTop, Math.min(maxTop, targetClientTop))

  position.value = {
    x: startPosition.x + (clampedLeft - startNoteRect.left),
    y: startPosition.y + (clampedTop - startNoteRect.top),
  }
}

function handlePointerUp() {
  if (!isDragging.value) return
  isDragging.value = false
  window.removeEventListener('pointermove', handlePointerMove)
  window.removeEventListener('pointerup', handlePointerUp)
  window.removeEventListener('pointercancel', handlePointerUp)
}

function resetPosition() {
  position.value = { x: 0, y: 0 }
}

function handleWindowResize() {
  checkMobile()
  if (!noteRef.value || (!position.value.x && !position.value.y)) return
  const noteRect = noteRef.value.getBoundingClientRect()
  const bounds = getContainerBounds()

  const minLeft = bounds.left + MARGIN
  const maxLeft = bounds.right - noteRect.width - MARGIN
  const minTop = bounds.top + MARGIN
  const maxTop = bounds.bottom - noteRect.height - MARGIN

  let adjustX = 0
  let adjustY = 0

  if (noteRect.left < minLeft) {
    adjustX = minLeft - noteRect.left
  } else if (noteRect.left > maxLeft && maxLeft >= minLeft) {
    adjustX = maxLeft - noteRect.left
  }

  if (noteRect.top < minTop) {
    adjustY = minTop - noteRect.top
  } else if (noteRect.top > maxTop && maxTop >= minTop) {
    adjustY = maxTop - noteRect.top
  }

  if (adjustX !== 0 || adjustY !== 0) {
    position.value = {
      x: position.value.x + adjustX,
      y: position.value.y + adjustY,
    }
  }
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', handleWindowResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleWindowResize)
  window.removeEventListener('pointermove', handlePointerMove)
  window.removeEventListener('pointerup', handlePointerUp)
  window.removeEventListener('pointercancel', handlePointerUp)
})
</script>

<template>
  <div class="relative py-7 sm:py-8 md:py-10 flex flex-col items-center justify-center select-none" style="margin-top:0 !important;">
    <!-- Hub: Waves and Circle share the exact same physical center -->
    <div class="relative flex items-center justify-center">
      <!-- Ambient Radiating Ripple Waves (centered strictly around the circle) -->
      <div class="absolute inset-0 m-auto w-44 h-44 sm:w-56 sm:h-56 md:w-60 md:h-60 rounded-full border border-primary-400/35 animate-gentle-wave-1 pointer-events-none"></div>
      <div class="absolute inset-0 m-auto w-44 h-44 sm:w-56 sm:h-56 md:w-60 md:h-60 rounded-full border border-primary-300/25 animate-gentle-wave-2 pointer-events-none"></div>
      <div class="absolute inset-0 m-auto w-44 h-44 sm:w-56 sm:h-56 md:w-60 md:h-60 rounded-full border border-rose-400/20 animate-gentle-wave-3 pointer-events-none"></div>

      <!-- Main Pure White Circular Love Core (Clickable to reveal random memory) -->
      <div
        @click="emit('open-random-memory')"
        class="relative w-44 h-44 sm:w-56 sm:h-56 md:w-60 md:h-60 rounded-full bg-white border border-border/60 shadow-xl shadow-primary-500/10 flex flex-col items-center justify-center p-4 sm:p-6 text-center text-ink transition-all duration-300 hover:scale-[1.03] active:scale-[0.98] cursor-pointer group z-10 shrink-0"
        :title="t('home.heartHint')"
      >
        <!-- Beating Heart Button (Click to open Glowing Particle Heart on Black BG) -->
        <button
          type="button"
          @click.stop="emit('open-particle-heart')"
          class="w-6 h-6 sm:w-7 sm:h-7 rounded-full bg-rose-50 hover:bg-rose-100 flex items-center justify-center transition-transform active:scale-90 cursor-pointer group/heart mb-0.5 sm:mb-1"
          :title="t('home.particleHeartHint')"
        >
          <Heart class="w-3 h-3 sm:w-3.5 sm:h-3.5 text-rose-500 fill-rose-500 animate-heartbeat group-hover/heart:scale-125 transition-transform" />
        </button>

        <!-- Label -->
        <p class="text-[9px] sm:text-[10px] uppercase font-mono tracking-[0.24em] text-primary-700 font-bold">
          {{ t('home.together') }}
        </p>

        <!-- Big Days Number -->
        <div class="flex items-baseline justify-center gap-1 my-0.5 sm:my-1">
          <span class="text-3xl sm:text-4xl md:text-5xl font-extrabold text-ink tracking-tight font-sans">
            {{ days }}
          </span>
          <span class="text-[11px] sm:text-xs font-bold uppercase tracking-wider text-primary-700 font-mono">
            {{ t('home.days') }}
          </span>
        </div>

        <!-- Real-Time Digital Clock Pill (HH : MM : SS) -->
        <div class="text-[11px] sm:text-xs font-mono font-bold text-ink px-2.5 sm:px-3 py-0.5 sm:py-1 tracking-wider my-0.5">
          {{ String(hours).padStart(2, '0') }}:{{ String(minutes).padStart(2, '0') }}:{{ String(seconds).padStart(2, '0') }}
        </div>

        <!-- Since Date -->
        <p v-if="formattedStartDate" class="text-[9px] sm:text-[10px] text-ink-muted font-mono mt-0.5 sm:mt-1">
          {{ t('home.since', { date: formattedStartDate }) }}
        </p>
      </div>
    </div>

    <!-- Desktop: Miếng dán sticky note có thể kéo thả bên cạnh div tròn (chỉ hiện trên màn hình md trở lên - giữ nền vàng note chân thực) -->
    <Transition name="partner-note">
      <div
        ref="noteRef"
        v-if="partnerMood"
        :style="noteTransformStyle"
        class="hidden md:flex flex-col select-none text-left bg-[#fffef5] border border-amber-200/90 rounded-xl p-4 pt-4.5 transition-shadow group
               absolute right-0 top-1/2 w-64 lg:w-72 shadow-md shadow-amber-900/5 z-20"
        :class="[
          isDragging
            ? 'cursor-grabbing shadow-2xl shadow-primary-500/20 z-40 ring-2 ring-primary-400/50 border-primary-500 touch-none transition-none'
            : isMoved
              ? 'cursor-grab shadow-lg shadow-amber-900/10 hover:shadow-xl hover:border-amber-300/80 z-30 touch-none duration-300'
              : 'cursor-grab hover:border-amber-300/80 hover:shadow-xl z-20 duration-300 touch-none'
        ]"
        :title="isMoved ? t('home.doubleClickReset') : t('home.dragNoteHint')"
        @pointerdown="handlePointerDown"
        @dblclick="resetPosition"
      >
        <!-- Băng dính Washi Tape dán đầu tờ note (chân thực, bán trong suốt) -->
        <div class="absolute -top-3 left-1/2 -translate-x-1/2 w-20 h-5 bg-amber-100/85 backdrop-blur-[2px] border-y border-amber-300/60 border-x border-dashed border-amber-300/40 rounded-2xs shadow-2xs rotate-[-1.2deg] pointer-events-none z-20 flex items-center justify-center">
          <span class="w-full h-px bg-amber-200/50"></span>
        </div>

        <!-- Header Note: Tiêu đề ghi chú & Huy hiệu cảm xúc & Nút Reset / Drag grip -->
        <div class="flex items-center justify-between gap-2 pb-1.5 mb-1.5 border-b border-amber-200/50">
          <div class="flex items-center gap-1.5 min-w-0">
            <Heart class="w-3.5 h-3.5 text-rose-400 fill-rose-400 shrink-0" />
            <span class="text-xs font-bold text-amber-950 truncate font-sans">
              {{ partnerName ? t('mood.partnerMessage', { name: partnerName }) : t('mood.partnerMessage', { name: t('mood.partnerDefault') }) }}
            </span>
          </div>

          <!-- Drag controls (Chỉ hiện trên desktop để kéo / reset vị trí) -->
          <div class="flex items-center gap-1 shrink-0">
            <button
              v-if="isMoved"
              type="button"
              class="p-1 rounded text-amber-600 hover:text-amber-900 hover:bg-amber-100/80 active:scale-95 transition-all cursor-pointer"
              :title="t('home.resetPosition')"
              @pointerdown.stop
              @click.stop="resetPosition"
            >
              <RotateCcw class="w-3.5 h-3.5" />
            </button>
            <GripHorizontal class="w-3.5 h-3.5 text-amber-400/80 group-hover:text-amber-600 transition-colors cursor-grab" />
          </div>
        </div>

        <!-- Nội dung Ghi chú hôm nay của đối phương -->
        <div class="relative">
          <p v-if="partnerMood.note" class="text-xs text-amber-950/90 leading-relaxed font-sans whitespace-pre-wrap italic">
            {{ partnerMood.note }}
          </p>
          <p v-else class="text-xs text-amber-800/60 italic font-sans">
            ({{ t('mood.feelingStatus', { tag: partnerMood.mood_tag ? (te('mood.tags.' + partnerMood.mood_tag) ? t('mood.tags.' + partnerMood.mood_tag) : partnerMood.mood_tag) : t('mood.tags.calm') }) }})
          </p>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
@keyframes gentleWave1 {
  0% {
    transform: scale(0.96);
    opacity: 0.75;
  }
  50% {
    transform: scale(1.22);
    opacity: 0.35;
  }
  100% {
    transform: scale(1.48);
    opacity: 0;
  }
}

@keyframes gentleWave2 {
  0% {
    transform: scale(0.96);
    opacity: 0.6;
  }
  50% {
    transform: scale(1.36);
    opacity: 0.25;
  }
  100% {
    transform: scale(1.75);
    opacity: 0;
  }
}

@keyframes gentleWave3 {
  0% {
    transform: scale(0.96);
    opacity: 0.45;
  }
  50% {
    transform: scale(1.48);
    opacity: 0.15;
  }
  100% {
    transform: scale(2.02);
    opacity: 0;
  }
}

.animate-gentle-wave-1,
.animate-gentle-wave-2,
.animate-gentle-wave-3 {
  will-change: transform, opacity;
  transform-origin: center;
}

.animate-gentle-wave-1 {
  animation: gentleWave1 3.2s cubic-bezier(0, 0, 0.2, 1) infinite;
}

.animate-gentle-wave-2 {
  animation: gentleWave2 3.2s cubic-bezier(0, 0, 0.2, 1) infinite 1.05s;
}

.animate-gentle-wave-3 {
  animation: gentleWave3 3.2s cubic-bezier(0, 0, 0.2, 1) infinite 2.1s;
}

@keyframes heartbeat {
  0% {
    transform: scale(1);
  }
  14% {
    transform: scale(1.24);
  }
  28% {
    transform: scale(1);
  }
  42% {
    transform: scale(1.18);
  }
  70% {
    transform: scale(1);
  }
}

.animate-heartbeat {
  animation: heartbeat 1.8s ease-in-out infinite;
  will-change: transform;
}

.partner-note-enter-active,
.partner-note-leave-active {
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.partner-note-enter-from,
.partner-note-leave-to {
  opacity: 0;
  transform: translateY(-50%) translateX(12px) scale(0.95);
}
</style>
