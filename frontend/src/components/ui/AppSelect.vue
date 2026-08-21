<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ChevronDown, Check } from 'lucide-vue-next'

export interface OptionItem {
  label: string
  value: string | number
}

interface Props {
  modelValue: string | number
  label?: string
  options: OptionItem[]
  placeholder?: string
  error?: string
  required?: boolean
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  required: false,
  disabled: false,
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: string | number): void
}>()

const isOpen = ref(false)
const selectRef = ref<HTMLElement | null>(null)

const selectedOption = computed(() => {
  return props.options.find(opt => opt.value === props.modelValue)
})

const displayLabel = computed(() => {
  if (selectedOption.value) return selectedOption.value.label
  return props.placeholder || 'Chọn...'
})

function toggleDropdown() {
  if (props.disabled) return
  isOpen.value = !isOpen.value
}

function selectOption(val: string | number) {
  emit('update:modelValue', val)
  isOpen.value = false
}

function handleClickOutside(e: MouseEvent) {
  if (selectRef.value && !selectRef.value.contains(e.target as Node)) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<template>
  <div ref="selectRef" class="space-y-1.5 w-full select-none">
    <!-- Label -->
    <label v-if="label" class="block text-xs font-bold text-ink tracking-wider uppercase">
      {{ label }}
      <span v-if="required" class="text-rose-500">*</span>
    </label>

    <!-- Trigger Button -->
    <div class="relative">
      <button
        type="button"
        :disabled="disabled"
        @click="toggleDropdown"
        class="w-full flex items-center justify-between px-3.5 py-2.5 text-sm font-medium bg-white border rounded-xl text-ink transition-all duration-150 cursor-pointer disabled:bg-surface-subtle disabled:cursor-not-allowed disabled:opacity-60 text-left shadow-2xs"
        :class="[
          error
            ? 'border-err-text focus:border-err-text focus:ring-2 focus:ring-rose-400/20'
            : isOpen
              ? 'border-violet-500 ring-2 ring-violet-400/20'
              : 'border-border hover:border-violet-300',
        ]"
      >
        <span
          class="truncate"
          :class="!selectedOption && placeholder ? 'text-ink-faint' : 'text-ink font-medium'"
        >
          {{ displayLabel }}
        </span>

        <ChevronDown
          class="w-4 h-4 text-ink-muted shrink-0 ml-2 transition-transform duration-200"
          :class="isOpen ? 'rotate-180 text-violet-600' : ''"
        />
      </button>

      <!-- Custom Native UI Popover Dropdown Menu -->
      <transition
        enter-active-class="transition duration-150 ease-out"
        enter-from-class="transform scale-95 opacity-0 -translate-y-1"
        enter-to-class="transform scale-100 opacity-100 translate-y-0"
        leave-active-class="transition duration-100 ease-in"
        leave-from-class="transform scale-100 opacity-100 translate-y-0"
        leave-to-class="transform scale-95 opacity-0 -translate-y-1"
      >
        <div
          v-if="isOpen"
          class="absolute left-0 right-0 top-full mt-1.5 max-h-60 overflow-y-auto bg-white/95 backdrop-blur-md border border-border rounded-xl shadow-xl p-1.5 space-y-0.5 z-50"
        >
          <button
            v-for="opt in options"
            :key="opt.value"
            type="button"
            @click="selectOption(opt.value)"
            class="w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs sm:text-sm font-medium transition-colors cursor-pointer text-left"
            :class="opt.value === modelValue
              ? 'bg-violet-50 text-violet-700 font-semibold shadow-2xs'
              : 'text-ink hover:bg-surface-raised hover:text-violet-700'"
          >
            <span class="truncate">{{ opt.label }}</span>
            <Check
              v-if="opt.value === modelValue"
              class="w-4 h-4 text-violet-600 shrink-0 ml-2"
            />
          </button>
        </div>
      </transition>
    </div>

    <!-- Error message -->
    <p v-if="error" class="text-xs text-err-text font-medium">{{ error }}</p>
  </div>
</template>
