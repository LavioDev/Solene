<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  modelValue?: boolean
  label?: string
  description?: string
  disabled?: boolean
  size?: 'sm' | 'md'
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: false,
  label: '',
  description: '',
  disabled: false,
  size: 'md',
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
}>()

function toggle() {
  if (props.disabled) return
  emit('update:modelValue', !props.modelValue)
}

const switchTrackClass = computed(() => {
  const base = 'relative inline-flex shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-violet-500/20 shadow-2xs'
  const sizeCls = props.size === 'sm' ? 'h-5 w-9' : 'h-6 w-11'
  const stateCls = props.modelValue ? 'bg-violet-600' : 'bg-surface-raised border-border'
  const disabledCls = props.disabled ? 'opacity-50 cursor-not-allowed' : ''
  return `${base} ${sizeCls} ${stateCls} ${disabledCls}`
})

const switchThumbClass = computed(() => {
  const base = 'pointer-events-none inline-block rounded-full bg-white shadow-2xs transform ring-0 transition duration-200 ease-in-out'
  if (props.size === 'sm') {
    return `${base} h-4 w-4 ${props.modelValue ? 'translate-x-4' : 'translate-x-0'}`
  }
  return `${base} h-5 w-5 ${props.modelValue ? 'translate-x-5' : 'translate-x-0'}`
})
</script>

<template>
  <div
    class="flex items-center justify-between gap-3 select-none cursor-pointer"
    :class="[disabled ? 'opacity-60 cursor-not-allowed' : '']"
    @click="toggle"
  >
    <div v-if="label || description" class="flex flex-col">
      <span v-if="label" class="text-xs sm:text-sm font-semibold text-ink leading-tight">
        {{ label }}
      </span>
      <span v-if="description" class="text-xs text-ink-faint mt-0.5">
        {{ description }}
      </span>
    </div>

    <button
      type="button"
      role="switch"
      :aria-checked="modelValue"
      :disabled="disabled"
      :class="switchTrackClass"
      @click.stop="toggle"
    >
      <span :class="switchThumbClass" />
    </button>
  </div>
</template>
