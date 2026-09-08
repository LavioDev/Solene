<script setup lang="ts">
defineEmits<{
  (e: 'pointerdown', event: PointerEvent): void
  (e: 'pointermove', event: PointerEvent): void
  (e: 'pointerup', event: PointerEvent): void
  (e: 'pointercancel', event: PointerEvent): void
}>()
</script>

<template>
  <div
    class="sm:hidden pt-3 pb-1 flex justify-center cursor-grab active:cursor-grabbing touch-none select-none shrink-0"
    @pointerdown="$emit('pointerdown', $event)"
    @pointermove="$emit('pointermove', $event)"
    @pointerup="$emit('pointerup', $event)"
    @pointercancel="$emit('pointercancel', $event)"
  >
    <div class="w-11 h-1.25 bg-ink-faint/25 rounded-full hover:bg-ink-faint/40 transition-colors" />
  </div>
</template>
