<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  variant?: 'primary' | 'secondary' | 'outline' | 'danger' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  disabled?: boolean
  loading?: boolean
  type?: 'button' | 'submit' | 'reset'
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  disabled: false,
  loading: false,
  type: 'button',
})

const sizeClasses = computed(() => ({
  sm: 'px-3 py-1.5 text-xs font-semibold',
  md: 'px-4 py-2 text-sm font-semibold',
  lg: 'px-5 py-2.5 text-sm font-bold',
}[props.size]))

const variantClasses = computed(() => ({
  primary:   'bg-violet-600 hover:bg-violet-700 text-white shadow-sm',
  secondary: 'bg-violet-50 hover:bg-violet-100 text-violet-700 border border-violet-200',
  outline:   'bg-white hover:bg-surface-subtle text-ink border border-border hover:border-border-strong',
  danger:    'bg-err-bg hover:bg-red-100 text-err-text border border-err-border',
  ghost:     'bg-transparent hover:bg-surface-raised text-ink-muted hover:text-ink',
}[props.variant]))
</script>

<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    class="inline-flex items-center justify-center gap-1.5 rounded-lg transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-violet-400/40 disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
    :class="[sizeClasses, variantClasses]"
  >
    <svg v-if="loading" class="animate-spin h-3.5 w-3.5 shrink-0" viewBox="0 0 24 24" fill="none">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
    </svg>
    <slot />
  </button>
</template>
