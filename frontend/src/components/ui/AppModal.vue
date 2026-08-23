<script setup lang="ts">
import { ref, computed, watch, onUnmounted } from 'vue'
import { Maximize2, Minimize2, X } from 'lucide-vue-next'

interface Props {
  show: boolean
  title?: string
  width?: '880' | '1000' | '1200' | 'sm' | 'md' | 'lg'
  draggable?: boolean
  maximizable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  show: false,
  width: 'md',
  draggable: true,
  maximizable: true,
})

const emit = defineEmits<{
  (e: 'close'): void
}>()

// Maximize / Zoom State
const isMaximized = ref(false)

function toggleMaximize() {
  isMaximized.value = !isMaximized.value
  if (isMaximized.value) {
    position.value = { x: 0, y: 0 }
  }
}

// Drag & Move State
const isDragging = ref(false)
const position = ref({ x: 0, y: 0 })
const dragStart = { x: 0, y: 0 }
const initialPos = { x: 0, y: 0 }

function startDrag(e: MouseEvent | TouchEvent) {
  if (!props.draggable || isMaximized.value) return

  const target = e.target as HTMLElement
  if (target && target.closest('button, input, select, textarea, a, .no-drag')) {
    return
  }

  isDragging.value = true
  const clientX = 'touches' in e ? e.touches[0].clientX : e.clientX
  const clientY = 'touches' in e ? e.touches[0].clientY : e.clientY
  dragStart.x = clientX
  dragStart.y = clientY
  initialPos.x = position.value.x
  initialPos.y = position.value.y

  window.addEventListener('mousemove', onDrag)
  window.addEventListener('mouseup', stopDrag)
  window.addEventListener('touchmove', onDrag)
  window.addEventListener('touchend', stopDrag)
}

function onDrag(e: MouseEvent | TouchEvent) {
  if (!isDragging.value) return
  const clientX = 'touches' in e ? e.touches[0].clientX : e.clientX
  const clientY = 'touches' in e ? e.touches[0].clientY : e.clientY

  const deltaX = clientX - dragStart.x
  const deltaY = clientY - dragStart.y

  position.value = {
    x: initialPos.x + deltaX,
    y: initialPos.y + deltaY,
  }
}

function stopDrag() {
  if (!isDragging.value) return
  isDragging.value = false
  window.removeEventListener('mousemove', onDrag)
  window.removeEventListener('mouseup', stopDrag)
  window.removeEventListener('touchmove', onDrag)
  window.removeEventListener('touchend', stopDrag)
}

watch(
  () => props.show,
  (newVal) => {
    if (newVal) {
      position.value = { x: 0, y: 0 }
      isMaximized.value = false
    }
  },
)

onUnmounted(() => {
  stopDrag()
})

const widthClass = computed(() => {
  switch (props.width) {
    case '880':
      return 'max-w-[880px]'
    case '1000':
      return 'max-w-[1000px]'
    case '1200':
      return 'max-w-[1200px]'
    case 'sm':
      return 'max-w-sm'
    case 'lg':
      return 'max-w-2xl'
    default:
      return 'max-w-lg'
  }
})

const modalTransformStyle = computed(() => {
  if (isMaximized.value || (position.value.x === 0 && position.value.y === 0)) {
    return {}
  }
  return {
    transform: `translate3d(${position.value.x}px, ${position.value.y}px, 0)`,
  }
})
</script>

<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div
        v-if="show"
        class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/30 backdrop-blur-xs"
        :class="isMaximized ? 'p-0' : 'p-4'"
        @click.self="emit('close')"
      >
        <div
          ref="modalRef"
          class="bg-white flex flex-col transform transition-all duration-200"
          :class="[
            isMaximized
              ? 'w-screen h-screen max-w-none max-h-none rounded-none border-none shadow-none p-6'
              : `${widthClass} border border-border rounded-2xl w-full p-6 shadow-pop max-h-[88vh]`,
            isDragging && !isMaximized ? 'transition-none shadow-2xl select-none ring-2 ring-violet-400/20' : ''
          ]"
          :style="modalTransformStyle"
        >
          <!-- Modal Header -->
          <div
            v-if="title || $slots.header"
            @mousedown="startDrag"
            @touchstart.passive="startDrag"
            class="flex items-center justify-between border-b border-border pb-3 shrink-0 gap-3"
            :class="draggable && !isMaximized ? 'cursor-grab active:cursor-grabbing select-none' : ''"
          >
            <div class="flex-1 min-w-0">
              <slot name="header">
                <h3 class="text-sm font-bold text-ink truncate">{{ title }}</h3>
              </slot>
            </div>

            <!-- Action buttons: Zoom (Maximize) and Close -->
            <div class="flex items-center gap-1 shrink-0">
              <!-- Zoom / Maximize Button (Left of Close 'X') -->
              <button
                v-if="maximizable"
                type="button"
                class="text-ink-faint hover:text-violet-600 hover:bg-violet-50 rounded-lg p-1.5 transition-colors cursor-pointer"
                :title="isMaximized ? 'Thu nhỏ' : 'Phóng to toàn màn hình'"
                @click.stop="toggleMaximize"
              >
                <Minimize2 v-if="isMaximized" class="w-4 h-4" />
                <Maximize2 v-else class="w-4 h-4" />
              </button>

              <!-- Close 'X' Button -->
              <button
                type="button"
                class="text-ink-faint hover:text-ink hover:bg-surface-subtle rounded-lg p-1.5 transition-colors cursor-pointer"
                @click.stop="emit('close')"
                title="Đóng"
              >
                <X class="w-4 h-4" />
              </button>
            </div>
          </div>

          <!-- Modal Body (Scrollable if tall) -->
            <div class="flex-1 overflow-y-auto py-3 pr-1 space-y-4 min-h-0">
            <slot />
          </div>

          <!-- Modal Footer -->
          <div v-if="$slots.footer" class="pt-3 border-t border-border flex justify-end gap-2 shrink-0">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-from .shadow-pop,
.modal-fade-leave-to .shadow-pop {
  transform: scale(0.96);
}
</style>
