<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  loading?: boolean
}>()

const progress = ref(0)
const visible = ref(false)
let timer: ReturnType<typeof setTimeout> | null = null
let interval: ReturnType<typeof setInterval> | null = null

watch(
  () => props.loading,
  (isLoading) => {
    if (timer) clearTimeout(timer)
    if (interval) clearInterval(interval)

    if (isLoading) {
      visible.value = true
      progress.value = 15

      // Incremental realistic advance
      interval = setInterval(() => {
        if (progress.value < 85) {
          const step = Math.max(1, (85 - progress.value) * 0.15)
          progress.value = Math.min(85, progress.value + step)
        }
      }, 100)
    } else {
      if (interval) clearInterval(interval)
      progress.value = 100
      timer = setTimeout(() => {
        visible.value = false
        progress.value = 0
      }, 200)
    }
  },
  { immediate: true }
)
</script>

<template>
  <Transition name="nprogress-fade">
    <div
      v-if="visible"
      class="fixed top-0 left-0 right-0 z-[9999] h-[2.5px] pointer-events-none overflow-hidden"
    >
      <div
        class="h-full bg-gradient-to-r from-primary-400 via-primary-500 to-primary-600 shadow-xs shadow-primary-500/40 transition-transform duration-200 ease-out origin-left will-change-transform"
        :style="{ transform: `scaleX(${progress / 100})` }"
      />
    </div>
  </Transition>
</template>

<style scoped>
.nprogress-fade-leave-active {
  transition: opacity 0.25s ease;
  will-change: opacity;
}

.nprogress-fade-leave-to {
  opacity: 0;
}
</style>
