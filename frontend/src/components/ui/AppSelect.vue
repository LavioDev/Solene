<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { ChevronDown, Check, Search } from 'lucide-vue-next'

export interface OptionItem {
  label: string
  value: string | number
}

interface Props {
  modelValue: string | number
  label?: string
  options: OptionItem[]
  placeholder?: string
  searchable?: boolean
  searchPlaceholder?: string
  error?: string
  required?: boolean
  disabled?: boolean
  size?: 'sm' | 'md'
}

const props = withDefaults(defineProps<Props>(), {
  required: false,
  disabled: false,
  searchable: false,
  size: 'md',
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: string | number): void
}>()

const { t } = useI18n()
const isOpen = ref(false)
const searchQuery = ref('')
const selectRef = ref<HTMLElement | null>(null)
const searchInputRef = ref<HTMLInputElement | null>(null)

const selectedOption = computed(() => {
  return props.options.find((opt) => opt.value === props.modelValue)
})

const displayLabel = computed(() => {
  if (selectedOption.value && selectedOption.value.value !== '') {
    return selectedOption.value.label
  }
  return props.placeholder || t('common.all') || 'Select...'
})

const filteredOptions = computed(() => {
  if (!props.searchable || !searchQuery.value.trim()) {
    return props.options
  }
  const q = searchQuery.value.toLowerCase().trim()
  return props.options.filter(
    (opt) =>
      opt.label.toLowerCase().includes(q) ||
      String(opt.value).toLowerCase().includes(q),
  )
})

function toggleDropdown() {
  if (props.disabled) return
  isOpen.value = !isOpen.value
}

watch(isOpen, (newVal) => {
  if (newVal) {
    searchQuery.value = ''
    if (props.searchable) {
      nextTick(() => {
        searchInputRef.value?.focus()
      })
    }
  }
})

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
        class="w-full flex items-center justify-between px-3.5 py-2.5 font-medium bg-white border rounded-xl text-ink transition-all duration-150 cursor-pointer disabled:bg-surface-subtle disabled:cursor-not-allowed disabled:opacity-60 text-left shadow-2xs"
        :class="[
          size === 'sm' ? 'text-xs' : 'text-xs sm:text-sm',
          error
            ? 'border-err-text focus:border-err-text focus:ring-2 focus:ring-rose-400/20'
            : isOpen
              ? 'border-primary-500 ring-2 ring-primary-400/20'
              : 'border-border hover:border-primary-300',
        ]"
      >
        <span
          class="truncate"
          :class="[
            size === 'sm' ? 'text-xs' : 'text-xs sm:text-sm',
            (!selectedOption || selectedOption.value === '') ? 'text-ink-faint' : 'text-ink font-medium'
          ]"
        >
          {{ displayLabel }}
        </span>

        <ChevronDown
          class="text-ink-muted shrink-0 ml-2 transition-transform duration-200"
          :class="[
            size === 'sm' ? 'w-3.5 h-3.5' : 'w-4 h-4',
            isOpen ? 'rotate-180 text-primary-600' : ''
          ]"
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
          class="absolute left-0 right-0 top-full mt-1.5 max-h-64 overflow-y-auto bg-white/95 backdrop-blur-md border border-border rounded-xl shadow-xl p-1.5 space-y-0.5 z-50"
        >
          <!-- Search Input for Searchable Select -->
          <div
            v-if="searchable"
            class="p-1 pb-1.5 sticky top-0 bg-white/95 backdrop-blur-md z-10 border-b border-border/60 mb-1"
            @click.stop
          >
            <div class="relative">
              <Search class="w-3.5 h-3.5 text-ink-faint absolute left-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
              <input
                ref="searchInputRef"
                v-model="searchQuery"
                type="text"
                :placeholder="searchPlaceholder || t('users.searchPlaceholder') || 'Search...'"
                class="w-full pl-8 pr-2.5 py-1.5 text-xs bg-surface-subtle focus:bg-white border border-border rounded-lg text-ink placeholder:text-ink-faint focus:outline-none focus:ring-1 focus:ring-primary-400 focus:border-primary-500 transition-all"
                @click.stop
                @keydown.stop
              />
            </div>
          </div>

          <!-- Options List -->
          <div v-if="filteredOptions.length > 0" class="space-y-0.5">
            <button
              v-for="opt in filteredOptions"
              :key="opt.value"
              type="button"
              @click="selectOption(opt.value)"
              class="w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium transition-colors cursor-pointer text-left"
              :class="opt.value === modelValue
                ? 'bg-primary-50 text-primary-700 font-semibold shadow-2xs'
                : 'text-ink hover:bg-surface-raised hover:text-primary-700'"
            >
              <span class="truncate">{{ opt.label }}</span>
              <Check
                v-if="opt.value === modelValue"
                class="w-3.5 h-3.5 text-primary-600 shrink-0 ml-2"
              />
            </button>
          </div>

          <!-- Empty search results -->
          <div v-else class="py-4 text-center text-xs text-ink-faint font-medium">
            {{ t('common.noResults') }}
          </div>
        </div>
      </transition>
    </div>

    <!-- Error message -->
    <p v-if="error" class="text-xs text-err-text font-medium">{{ error }}</p>
  </div>
</template>
