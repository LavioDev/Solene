<script setup lang="ts">
import { watch, onUnmounted } from 'vue'
import { X } from 'lucide-vue-next'

interface Props {
  show: boolean
  title?: string
  width?: 'sm' | 'md' | 'lg' | '880' | '1000' | '1200'
}

const props = withDefaults(defineProps<Props>(), {
  show: false,
  width: 'md',
})

const emit = defineEmits<{ (e: 'close'): void }>()

watch(
  () => props.show,
  (val) => {
    if (typeof document === 'undefined') return
    document.body.style.overflow = val ? 'hidden' : ''
  },
)

onUnmounted(() => {
  if (typeof document !== 'undefined') document.body.style.overflow = ''
})

const maxW: Record<string, string> = {
  sm: 'max-w-sm',
  md: 'max-w-lg',
  lg: 'max-w-2xl',
  '880': 'max-w-[880px]',
  '1000': 'max-w-[1000px]',
  '1200': 'max-w-[1200px]',
}
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="show"
        class="fixed inset-0 z-50 flex items-end sm:items-center justify-center sm:p-4 bg-black/40 backdrop-blur-sm"
        @click.self="emit('close')"
      >
        <div
          class="relative w-full bg-white rounded-t-2xl sm:rounded-2xl border border-border shadow-xl flex flex-col max-h-[90vh] sm:max-h-[88vh]"
          :class="maxW[props.width] ?? 'max-w-lg'"
          @click.stop
        >
          <!-- Header -->
          <div
            v-if="title || $slots.header"
            class="flex items-center justify-between px-5 py-4 border-b border-border shrink-0"
          >
            <slot name="header">
              <h3 class="text-sm font-semibold text-ink">{{ title }}</h3>
            </slot>
            <button
              type="button"
              class="p-1.5 rounded-lg text-ink-faint hover:text-ink hover:bg-surface-subtle transition-colors cursor-pointer"
              @click="emit('close')"
            >
              <X class="w-4 h-4" />
            </button>
          </div>

          <!-- Body -->
          <div class="flex-1 overflow-y-auto px-5 py-4 min-h-0">
            <slot />
          </div>

          <!-- Footer -->
          <div
            v-if="$slots.footer"
            class="px-5 py-4 border-t border-border shrink-0 flex justify-end gap-2"
          >
            <slot name="footer" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.modal-enter-active {
  transition: opacity 0.18s ease;
}
.modal-leave-active {
  transition: opacity 0.14s ease;
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
.modal-enter-active > div,
.modal-leave-active > div {
  transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}
.modal-enter-from > div {
  transform: translateY(16px);
}
.modal-leave-to > div {
  transform: translateY(8px);
}
</style>
