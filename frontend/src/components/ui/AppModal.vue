<script setup lang="ts">
import { toRef } from 'vue'
import { X } from 'lucide-vue-next'
import { useBottomSheetDrag } from '@/composables/useBottomSheetDrag'
import AppModalDragHandle from './AppModalDragHandle.vue'
import {
  type AppModalProps,
  MODAL_WIDTH_CLASSES,
} from './modalTypes'

const props = withDefaults(defineProps<AppModalProps>(), {
  show: false,
  width: 'md',
  bottomSheetOnMobile: true,
  swipeToClose: true,
  dismissible: true,
  draggable: false,
  maximizable: false,
})

const emit = defineEmits<{ (e: 'close'): void }>()

const {
  panelRef,
  bodyRef,
  isDragging,
  panelStyle,
  backdropStyle,
  onHandlePointerDown,
  onHandlePointerMove,
  onHandlePointerUp,
  onHeaderPointerDown,
  onTouchStart,
  onTouchMove,
  onTouchEnd,
} = useBottomSheetDrag({
  show: toRef(props, 'show'),
  bottomSheetOnMobile: toRef(props, 'bottomSheetOnMobile'),
  swipeToClose: toRef(props, 'swipeToClose'),
  dismissible: toRef(props, 'dismissible'),
  onClose: () => emit('close'),
})

function handleBackdropClick() {
  if (!props.dismissible || isDragging.value) return
  emit('close')
}
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="show"
        class="fixed inset-0 z-50 flex justify-center bg-black/45 backdrop-blur-xs transition-opacity"
        :class="bottomSheetOnMobile ? 'items-end sm:items-center sm:p-4' : 'items-center p-4'"
        :style="backdropStyle"
        @click.self="handleBackdropClick"
      >
        <div
          ref="panelRef"
          class="modal-panel relative w-full bg-white border-border shadow-2xl flex flex-col overflow-hidden"
          :class="[
            bottomSheetOnMobile
              ? 'max-w-full rounded-t-3xl sm:rounded-2xl border-t sm:border max-h-[92vh] sm:max-h-[88vh]'
              : 'rounded-2xl border max-h-[88vh]',
            MODAL_WIDTH_CLASSES[props.width] ?? 'sm:max-w-lg',
          ]"
          :style="panelStyle"
          @click.stop
          @touchstart.passive="onTouchStart"
          @touchmove="onTouchMove"
          @touchend="onTouchEnd"
          @touchcancel="onTouchEnd"
        >
          <!-- Mobile Drag Handle Bar -->
          <AppModalDragHandle
            v-if="bottomSheetOnMobile && swipeToClose"
            @pointerdown="onHandlePointerDown"
            @pointermove="onHandlePointerMove"
            @pointerup="onHandlePointerUp"
            @pointercancel="onHandlePointerUp"
          />

          <!-- Header -->
          <div
            v-if="title || $slots.header"
            class="flex items-center justify-between px-5 py-3 sm:py-4 border-b border-border shrink-0 select-none cursor-grab active:cursor-grabbing sm:cursor-default"
            @pointerdown="onHeaderPointerDown"
            @pointermove="onHandlePointerMove"
            @pointerup="onHandlePointerUp"
            @pointercancel="onHandlePointerUp"
          >
            <slot name="header">
              <h3 class="text-sm font-semibold text-ink">{{ title }}</h3>
            </slot>
            <button
              type="button"
              class="p-1.5 rounded-lg text-ink-faint hover:text-ink hover:bg-surface-subtle transition-colors cursor-pointer shrink-0"
              @click="emit('close')"
            >
              <X class="w-4 h-4" />
            </button>
          </div>

          <!-- Body -->
          <div
            ref="bodyRef"
            class="modal-body flex-1 overflow-y-auto px-5 py-4 min-h-0 overscroll-contain"
          >
            <slot />
          </div>

          <!-- Footer -->
          <div
            v-if="$slots.footer"
            class="px-5 py-3 sm:py-4 border-t border-border shrink-0 flex justify-end gap-2 pb-[max(0.85rem,env(safe-area-inset-bottom))] sm:pb-4"
          >
            <slot name="footer" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
/* Mobile bottom sheet animation */
@media (max-width: 639px) {
  .modal-enter-active,
  .modal-leave-active {
    transition: opacity 0.28s cubic-bezier(0.32, 0.72, 0, 1);
  }
  .modal-enter-from,
  .modal-leave-to {
    opacity: 0;
  }
  .modal-enter-active .modal-panel {
    transition: transform 0.32s cubic-bezier(0.32, 0.72, 0, 1);
    will-change: transform;
  }
  .modal-leave-active .modal-panel {
    transition: transform 0.22s cubic-bezier(0.32, 0.72, 0, 1);
    will-change: transform;
  }
  .modal-enter-from .modal-panel,
  .modal-leave-to .modal-panel {
    transform: translateY(100%);
  }
}

/* Desktop modal animation */
@media (min-width: 640px) {
  .modal-enter-active {
    transition: opacity 0.2s ease-out;
  }
  .modal-leave-active {
    transition: opacity 0.15s ease-in;
  }
  .modal-enter-from,
  .modal-leave-to {
    opacity: 0;
  }
  .modal-enter-active .modal-panel {
    transition: transform 0.24s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.24s ease-out;
  }
  .modal-leave-active .modal-panel {
    transition: transform 0.18s ease-in, opacity 0.18s ease-in;
  }
  .modal-enter-from .modal-panel {
    transform: translateY(14px) scale(0.97);
    opacity: 0;
  }
  .modal-leave-to .modal-panel {
    transform: translateY(8px) scale(0.98);
    opacity: 0;
  }
}

.overscroll-contain {
  overscroll-behavior-y: contain;
  -webkit-overflow-scrolling: touch;
}
</style>
