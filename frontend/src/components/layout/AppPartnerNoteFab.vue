<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { StickyNote, Heart, X } from 'lucide-vue-next'
import { useMoodStore } from '@/stores/moodStore'
import { useAuthStore } from '@/stores/authStore'
import { coupleService } from '@/services/coupleService'
import { useStickerBoard } from '@/modules/home/composables/useStickerBoard'
import type { Couple } from '@/types/couple'

const router = useRouter()
const route = useRoute()
const { t, te } = useI18n()
const moodStore = useMoodStore()
const authStore = useAuthStore()
const { isPickerOpen } = useStickerBoard()

const couple = ref<Couple | null>(null)
const showModal = ref(false)
const isMobile = ref(false)

// Partner mood from Pinia store
const partnerMood = computed(() => moodStore.partnerTodayMood)

// Partner full name calculation
const partnerName = computed(() => {
  if (partnerMood.value?.user_full_name) {
    return partnerMood.value.user_full_name
  }
  if (couple.value) {
    const currentUserId = authStore.user?.id
    const partnerObj = couple.value.user1_id === currentUserId ? couple.value.user2 : couple.value.user1
    if (partnerObj?.full_name) return partnerObj.full_name
  }
  return ''
})

// Draggable FAB state
const FAB_SIZE = 44
const MARGIN = 12
const TOP_MARGIN = 64 // Below navbar
const BOTTOM_SAFE_MARGIN = 84 // Safe margin above mobile browser bar/home gesture bar

const isHome = computed(() => route.path === '/')

const fabTotalHeight = computed(() => {
  let count = 0
  if (partnerMood.value) count++
  if (isHome.value) count++
  return count > 1 ? 96 : 44
})

const fabX = ref(0)
const fabY = ref(0)
const isPositioned = ref(false)
const isDragging = ref(false)

let startPointer = { x: 0, y: 0 }
let startFab = { x: 0, y: 0 }
let hasMoved = false
let modalOpenedAt = 0

function checkMobile() {
  if (typeof window !== 'undefined') {
    isMobile.value = window.innerWidth < 1024
    clampPosition()
  }
}

function initDefaultPosition() {
  if (typeof window === 'undefined') return
  fabX.value = Math.max(MARGIN, window.innerWidth - FAB_SIZE - 16)
  fabY.value = Math.max(TOP_MARGIN, window.innerHeight - fabTotalHeight.value - BOTTOM_SAFE_MARGIN)
  isPositioned.value = true
}

function clampPosition() {
  if (typeof window === 'undefined' || !isPositioned.value) return
  const maxX = Math.max(MARGIN, window.innerWidth - FAB_SIZE - MARGIN)
  const maxY = Math.max(TOP_MARGIN, window.innerHeight - fabTotalHeight.value - 32)

  fabX.value = Math.max(MARGIN, Math.min(maxX, fabX.value))
  fabY.value = Math.max(TOP_MARGIN, Math.min(maxY, fabY.value))
}

function openModal() {
  modalOpenedAt = Date.now()
  showModal.value = true
  // Nút FAB sau khi được mở sẽ về lại vị trí mặc định
  initDefaultPosition()
}

function closeModal() {
  showModal.value = false
  initDefaultPosition()
}

function handleBackdropClick() {
  // Prevent synthetic click from the tap that opened the modal from closing it immediately
  if (Date.now() - modalOpenedAt < 400) return
  closeModal()
}

function handlePointerDown(event: PointerEvent) {
  if (event.button !== 0 && event.pointerType === 'mouse') return

  startPointer = { x: event.clientX, y: event.clientY }
  startFab = { x: fabX.value, y: fabY.value }
  hasMoved = false
  isDragging.value = false

  const handlePointerMove = (e: PointerEvent) => {
    const dx = e.clientX - startPointer.x
    const dy = e.clientY - startPointer.y

    if (!hasMoved && Math.hypot(dx, dy) > 8) {
      hasMoved = true
      isDragging.value = true
    }

    if (hasMoved) {
      if (e.cancelable) e.preventDefault()
      const maxX = Math.max(MARGIN, window.innerWidth - FAB_SIZE - MARGIN)
      const maxY = Math.max(TOP_MARGIN, window.innerHeight - FAB_SIZE - 32)

      fabX.value = Math.max(MARGIN, Math.min(maxX, startFab.x + dx))
      fabY.value = Math.max(TOP_MARGIN, Math.min(maxY, startFab.y + dy))
    }
  }

  const handlePointerUp = () => {
    window.removeEventListener('pointermove', handlePointerMove)
    window.removeEventListener('pointerup', handlePointerUp)
    window.removeEventListener('pointercancel', handlePointerUp)

    if (hasMoved) {
      setTimeout(() => {
        isDragging.value = false
        hasMoved = false
      }, 100)
    } else {
      isDragging.value = false
      hasMoved = false
    }
  }

  window.addEventListener('pointermove', handlePointerMove, { passive: false })
  window.addEventListener('pointerup', handlePointerUp)
  window.addEventListener('pointercancel', handlePointerUp)
}

function handleClick(e: MouseEvent) {
  if (hasMoved || isDragging.value) {
    e.preventDefault()
    e.stopPropagation()
    return
  }
  if (!showModal.value) {
    openModal()
  }
}

async function handleStickerClick(e: MouseEvent) {
  if (hasMoved || isDragging.value) {
    e.preventDefault()
    e.stopPropagation()
    return
  }
  if (route.path !== '/') {
    await router.push('/')
  }
  isPickerOpen.value = true
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape' && showModal.value) {
    closeModal()
  }
}

// Lock body scrolling when modal is open
watch(showModal, (isOpen) => {
  if (typeof document !== 'undefined') {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
  }
})

onMounted(async () => {
  checkMobile()
  initDefaultPosition()
  window.addEventListener('resize', checkMobile)
  window.addEventListener('keydown', handleKeydown)

  // Ensure mood and couple data are loaded if not yet present
  if (authStore.isAuthenticated) {
    if (!moodStore.partnerTodayMood && !moodStore.isLoading) {
      moodStore.fetchTodayMood().catch(() => {})
    }
    try {
      couple.value = await coupleService.getMyCouple()
    } catch {
      // Ignore network errors on couple fetch
    }
  }
})

onUnmounted(() => {
  if (typeof document !== 'undefined') {
    document.body.style.overflow = ''
  }
  window.removeEventListener('resize', checkMobile)
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<template>
  <!-- Teleport directly to body so it sits at the absolute highest root layer -->
  <Teleport to="body">
    <!-- Only renders on mobile/responsive viewports (< 1024px) when on Home with couple or partner note exists -->
    <div v-if="isMobile && isPositioned && (partnerMood || (isHome && Boolean(couple)))" class="lg:hidden">
      <!-- Draggable Floating Action Button (FAB) Container -->
      <div
        :style="{
          transform: `translate3d(${fabX}px, ${fabY}px, 0)`,
          zIndex: 99999,
        }"
        class="partner-fab-container fixed top-0 left-0 select-none touch-none pointer-events-auto transition-opacity duration-200 flex flex-col items-center gap-2"
        :class="isDragging ? '' : 'transition-transform duration-300 ease-out'"
      >
        <!-- 1. Partner Note FAB (shown if partnerMood exists) -->
        <button
          v-if="partnerMood"
          type="button"
          @pointerdown="handlePointerDown"
          @click="handleClick"
          class="relative w-[44px] h-[44px] rounded-xl bg-[#fffef7] border border-amber-300/90 shadow-lg shadow-amber-950/20 flex items-center justify-center transition-shadow cursor-pointer"
          :class="[
            isDragging
              ? 'cursor-grabbing scale-110 shadow-2xl shadow-amber-950/35 ring-2 ring-amber-400/80 border-amber-400'
              : 'hover:shadow-xl hover:scale-105 active:scale-95'
          ]"
          :title="partnerName ? t('mood.partnerMessage', { name: partnerName }) : t('mood.partnerMessage', { name: t('mood.partnerDefault') })"
        >
          <!-- Realistic Translucent Washi Tape at top of the FAB note -->
          <div
            class="absolute -top-1.5 left-1/2 -translate-x-1/2 w-6 h-2.5 bg-amber-100/85 backdrop-blur-[2px] border-y border-amber-300/60 border-x border-dashed border-amber-300/40 rounded-2xs shadow-2xs rotate-[-3deg] pointer-events-none z-10"
          ></div>

          <!-- Sticky Note icon with animated pulsing heart -->
          <div class="relative flex items-center justify-center">
            <StickyNote class="w-5 h-5 text-amber-600" />
            <Heart class="w-2 h-2 text-rose-500 fill-rose-500 absolute -top-0.5 -right-0.5 animate-pulse" />
          </div>
        </button>

        <!-- 2. Sticker Board FAB (Chỉ hiện ở màn Home khi đã có relation couple) -->
        <button
          v-if="isHome && Boolean(couple)"
          type="button"
          @pointerdown="handlePointerDown"
          @click="handleStickerClick"
          class="relative w-[44px] h-[44px] rounded-xl bg-white/95 border border-primary-200/90 shadow-lg shadow-primary-950/15 flex items-center justify-center transition-all backdrop-blur-md cursor-pointer p-1"
          :class="[
            isDragging
              ? 'cursor-grabbing scale-110 shadow-2xl ring-2 ring-primary-400/80 border-primary-400'
              : 'hover:shadow-xl hover:scale-105 active:scale-95'
          ]"
          :title="t('stickers.openPicker')"
        >
          <img
            src="/stickers/chiikawa/gifs/chiikawa_anim_01.gif"
            alt="Sticker"
            class="w-8 h-8 object-contain select-none pointer-events-none"
            draggable="false"
          />
        </button>
      </div>

      <!-- Mobile Partner Note Modal with maximum z-index (2147483647) - giữ nền vàng note chân thực -->
      <Transition name="note-backdrop">
        <div
          v-if="showModal && partnerMood"
          :style="{ zIndex: 2147483647 }"
          class="fixed inset-0 bg-black/45 backdrop-blur-xs flex items-center justify-center p-4 select-none overscroll-none"
          @click.self="handleBackdropClick"
        >
          <div
            class="relative w-full max-w-sm bg-[#fffef7] border border-amber-200/90 rounded-2xl p-5 pt-6 shadow-2xl shadow-amber-950/25 animate-pop-note"
            @click.stop
          >
            <!-- Realistic Translucent Washi Tape at the top of the note -->
            <div
              class="absolute -top-3 left-1/2 -translate-x-1/2 w-20 h-5 bg-amber-100/85 backdrop-blur-[2px] border-y border-amber-300/60 border-x border-dashed border-amber-300/40 rounded-2xs shadow-2xs rotate-[-1.5deg] pointer-events-none z-20 flex items-center justify-center"
            >
              <span class="w-full h-px bg-amber-200/50"></span>
            </div>

            <!-- Header Note: Partner Message & Close Button -->
            <div class="flex items-center justify-between gap-2 pb-2 mb-3 border-b border-amber-200/60">
              <div class="flex items-center gap-1.5 min-w-0">
                <Heart class="w-4 h-4 text-rose-400 fill-rose-400 shrink-0 animate-pulse" />
                <span class="text-sm font-bold text-amber-950 truncate font-sans">
                  {{ partnerName ? t('mood.partnerMessage', { name: partnerName }) : t('mood.partnerMessage', { name: t('mood.partnerDefault') }) }}
                </span>
              </div>

              <button
                type="button"
                @click="closeModal"
                class="p-1 rounded-lg text-amber-700 hover:text-amber-950 hover:bg-amber-100/80 active:scale-90 transition-all cursor-pointer"
                title="Close"
              >
                <X class="w-4 h-4" />
              </button>
            </div>

            <!-- Note Body -->
            <div class="relative py-1">
              <p v-if="partnerMood.note" class="text-sm text-amber-950/90 leading-relaxed font-sans whitespace-pre-wrap italic">
                {{ partnerMood.note }}
              </p>
              <p v-else class="text-sm text-amber-800/60 italic font-sans">
                ({{ t('mood.feelingStatus', { tag: partnerMood.mood_tag ? (te('mood.tags.' + partnerMood.mood_tag) ? t('mood.tags.' + partnerMood.mood_tag) : partnerMood.mood_tag) : t('mood.tags.calm') }) }})
              </p>
            </div>

            <!-- Footer: Mood tag badge & watermark -->
            <div v-if="partnerMood.mood_tag" class="mt-4 pt-2.5 border-t border-amber-200/50 flex items-center justify-between">
              <span class="text-[11px] font-mono font-medium text-amber-800/80 bg-amber-100/70 px-2 py-0.5 rounded-full border border-amber-200/60">
                {{ te('mood.tags.' + partnerMood.mood_tag) ? t('mood.tags.' + partnerMood.mood_tag) : partnerMood.mood_tag }}
              </span>
              <span class="text-[10px] text-amber-600/60 font-mono">
                Solène
              </span>
            </div>
          </div>
        </div>
      </Transition>
    </div>
  </Teleport>
</template>

<style scoped>
.note-backdrop-enter-active,
.note-backdrop-leave-active {
  transition: opacity 0.22s ease-out;
}

.note-backdrop-enter-from,
.note-backdrop-leave-to {
  opacity: 0;
}

@keyframes popNoteIn {
  0% {
    opacity: 0;
    transform: scale(0.86) translateY(20px) rotate(-3.5deg);
  }
  65% {
    opacity: 1;
    transform: scale(1.02) translateY(-2px) rotate(-0.5deg);
  }
  100% {
    opacity: 1;
    transform: scale(1) translateY(0) rotate(-0.8deg);
  }
}

.animate-pop-note {
  animation: popNoteIn 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

:global(body.app-modal-open) .partner-fab-container {
  opacity: 0 !important;
  pointer-events: none !important;
}
</style>
