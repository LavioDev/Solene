<script setup lang="ts">
import { Sparkles, Heart } from 'lucide-vue-next'

defineProps<{
  show?: boolean
  fullScreen?: boolean
}>()
</script>

<template>
  <Transition name="loader-fade">
    <div
      v-if="show"
      :class="[
        fullScreen
          ? 'fixed inset-0 z-50'
          : 'absolute inset-0 z-40',
        'flex flex-col items-center justify-center bg-surface-subtle/85 backdrop-blur-xs select-none'
      ]"
    >
      <div class="flex flex-col items-center gap-4">
        <!-- Logo / Icon with Pulse & Spinner Ring -->
        <div class="relative flex items-center justify-center">
          <!-- Outer Spinning Track Ring -->
          <div class="w-14 h-14 rounded-full border-2 border-violet-100 border-t-violet-600 animate-spin"></div>
          <!-- Inner Floating Heart Core -->
          <div class="absolute inset-0 flex items-center justify-center">
            <div class="w-8 h-8 rounded-full bg-violet-50 flex items-center justify-center shadow-2xs">
              <Heart class="w-4 h-4 text-violet-600 fill-violet-400 animate-pulse" />
            </div>
          </div>
        </div>

        <!-- Text & Animated Bar -->
        <div class="flex flex-col items-center gap-2 text-center">
          <span class="text-xs font-semibold text-ink tracking-tight flex items-center gap-1.5 font-sans">
            <span>Solène</span>
            <Sparkles class="w-3.5 h-3.5 text-violet-600 animate-pulse" />
          </span>
          <!-- Indeterminate Progress Pill Bar -->
          <div class="w-28 h-1 bg-violet-100 rounded-full overflow-hidden relative">
            <div class="absolute inset-y-0 w-1/2 bg-violet-600 rounded-full animate-loader-bar"></div>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.loader-fade-enter-active,
.loader-fade-leave-active {
  transition: opacity 0.25s ease;
}

.loader-fade-enter-from,
.loader-fade-leave-to {
  opacity: 0;
}

@keyframes loaderBar {
  0% {
    left: -50%;
  }
  100% {
    left: 100%;
  }
}

.animate-loader-bar {
  animation: loaderBar 1.2s ease-in-out infinite;
}
</style>
