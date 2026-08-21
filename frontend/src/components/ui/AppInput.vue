<script setup lang="ts">
interface Props {
  modelValue?: string | number
  type?: string
  placeholder?: string
  label?: string
  error?: string
  disabled?: boolean
  required?: boolean
}

withDefaults(defineProps<Props>(), {
  modelValue: '',
  type: 'text',
  placeholder: '',
  label: '',
  error: '',
  disabled: false,
  required: false,
})

const emit = defineEmits<{ (e: 'update:modelValue', value: string): void }>()

function onInput(event: Event) {
  emit('update:modelValue', (event.target as HTMLInputElement).value)
}
</script>

<template>
  <div class="w-full space-y-1.5">
    <label v-if="label" class="block text-xs font-bold text-ink tracking-wider uppercase">
      {{ label }}<span v-if="required" class="text-rose-500 ml-0.5">*</span>
    </label>
    <input
      :type="type"
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      :required="required"
      @input="onInput"
      class="w-full px-3.5 py-2.5 text-sm font-medium bg-white border border-border rounded-xl text-ink placeholder-ink-faint
             transition-all duration-150 shadow-2xs hover:border-violet-300 focus:outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-400/20
             disabled:bg-surface-subtle disabled:text-ink-faint disabled:cursor-not-allowed"
      :class="error ? 'border-err-text focus:border-err-text focus:ring-rose-400/20' : ''"
    />
    <p v-if="error" class="text-xs text-err-text font-medium">{{ error }}</p>
  </div>
</template>
