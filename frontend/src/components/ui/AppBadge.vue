<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  variant?: 'primary' | 'violet' | 'rose' | 'ok' | 'warn' | 'err' | 'info' | 'neutral'
  size?: 'sm' | 'md'
}

const props = withDefaults(defineProps<Props>(), { variant: 'neutral', size: 'sm' })

const cls = computed(() => ({
  primary: 'bg-primary-50 text-primary-700 border border-primary-200',
  violet:  'bg-primary-50 text-primary-700 border border-primary-200',
  rose:    'bg-rose-50 text-rose-700 border border-rose-200',
  ok:      'bg-ok-bg text-ok-text border border-ok-border',
  warn:    'bg-warn-bg text-warn-text border border-warn-border',
  err:     'bg-err-bg text-err-text border border-err-border',
  info:    'bg-info-bg text-info-text border border-info-border',
  neutral: 'bg-surface-raised text-ink-muted border border-border',
}[props.variant]))

const sz = computed(() => props.size === 'sm' ? 'px-2 py-0.5 text-[11px]' : 'px-2.5 py-1 text-xs')
</script>

<template>
  <span class="inline-flex items-center gap-1 rounded-md font-semibold leading-none" :class="[cls, sz]">
    <slot />
  </span>
</template>
