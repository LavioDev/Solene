<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  show: boolean
  title?: string
  width?: '880' | '1000' | '1200' | 'sm' | 'md' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
  show: false,
  width: 'md',
})

const emit = defineEmits<{
  (e: 'close'): void
}>()

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
</script>

<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div
        v-if="show"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/30 backdrop-blur-xs"
        @click.self="emit('close')"
      >
        <div
          class="bg-white border border-border rounded-2xl w-full p-6 shadow-pop flex flex-col max-h-[88vh] transform transition-all duration-200"
          :class="widthClass"
        >
          <!-- Modal Header -->
          <div v-if="title || $slots.header" class="flex items-center justify-between border-b border-border pb-3 shrink-0">
            <slot name="header">
              <h3 class="text-sm font-bold text-ink">{{ title }}</h3>
            </slot>
            <button
              type="button"
              class="text-ink-faint hover:text-ink rounded-lg p-1 transition-colors cursor-pointer"
              @click="emit('close')"
            >
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- Modal Body (Scrollable if tall) -->
          <div class="flex-1 overflow-y-auto py-3 pr-1 space-y-4">
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
