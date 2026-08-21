<script setup lang="ts">
interface Props {
  title?: string
  subtitle?: string
}
defineProps<Props>()
</script>

<template>
  <div class="bg-white border border-border rounded-xl shadow-card">
    <div v-if="title || $slots.header" class="flex items-center justify-between px-6 py-4 border-b border-border">
      <slot name="header">
        <div>
          <h3 class="text-sm font-bold text-ink">{{ title }}</h3>
          <p v-if="subtitle" class="text-xs text-ink-muted mt-0.5">{{ subtitle }}</p>
        </div>
      </slot>
      <slot name="action" />
    </div>
    <div class="px-6 py-5">
      <slot />
    </div>
  </div>
</template>
