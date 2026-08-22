<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from 'lucide-vue-next'

interface Props {
  currentPage: number
  totalItems: number
  perPage?: number
  totalPages?: number
}

const props = withDefaults(defineProps<Props>(), {
  perPage: 15,
  totalPages: undefined,
})

const emit = defineEmits<{
  (e: 'update:currentPage', page: number): void
  (e: 'change', page: number): void
}>()

const { t } = useI18n()

const calculatedTotalPages = computed(() => {
  if (typeof props.totalPages === 'number' && props.totalPages > 0) {
    return props.totalPages
  }
  return Math.ceil(props.totalItems / props.perPage) || 1
})

const startItem = computed(() => {
  if (props.totalItems === 0) return 0
  return (props.currentPage - 1) * props.perPage + 1
})

const endItem = computed(() => {
  return Math.min(props.currentPage * props.perPage, props.totalItems)
})

function setPage(page: number) {
  if (page < 1 || page > calculatedTotalPages.value || page === props.currentPage) return
  emit('update:currentPage', page)
  emit('change', page)
}

// Generate smart visible page range with ellipsis
const visiblePages = computed(() => {
  const current = props.currentPage
  const total = calculatedTotalPages.value
  const delta = 1 // adjacent pages

  if (total <= 7) {
    return Array.from({ length: total }, (_, i) => i + 1)
  }

  const range: (number | string)[] = []
  const left = Math.max(2, current - delta)
  const right = Math.min(total - 1, current + delta)

  range.push(1)

  if (left > 2) {
    range.push('...')
  }

  for (let i = left; i <= right; i++) {
    range.push(i)
  }

  if (right < total - 1) {
    range.push('...')
  }

  range.push(total)

  return range
})
</script>

<template>
  <div class="flex flex-col sm:flex-row items-center justify-between gap-3 p-4 select-none">
    <!-- Showing entries count -->
    <div class="text-xs text-ink-muted font-medium">
      <span v-if="totalItems > 0">
        {{ t('common.pagination.showing', { start: startItem, end: endItem, total: totalItems }) }}
      </span>
      <span v-else>
        {{ t('common.noResults') }}
      </span>
    </div>

    <!-- Pagination controls -->
    <div v-if="calculatedTotalPages > 1" class="flex items-center gap-1">
      <!-- First Page -->
      <button
        type="button"
        @click="setPage(1)"
        :disabled="currentPage <= 1"
        class="p-1.5 rounded-lg text-ink-muted hover:text-ink hover:bg-surface-raised disabled:opacity-30 disabled:pointer-events-none transition-all cursor-pointer"
        :title="t('common.pagination.first')"
      >
        <ChevronsLeft class="w-4 h-4" />
      </button>

      <!-- Previous -->
      <button
        type="button"
        @click="setPage(currentPage - 1)"
        :disabled="currentPage <= 1"
        class="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-xl text-xs font-medium text-ink-muted hover:text-ink hover:bg-surface-raised disabled:opacity-30 disabled:pointer-events-none transition-all cursor-pointer"
      >
        <ChevronLeft class="w-3.5 h-3.5" />
        <span class="hidden sm:inline">{{ t('common.pagination.prev') }}</span>
      </button>

      <!-- Numbered Page Pills -->
      <div class="flex items-center gap-1 mx-1">
        <template v-for="(p, idx) in visiblePages" :key="idx">
          <span
            v-if="p === '...'"
            class="px-2 py-1 text-xs text-ink-faint font-semibold select-none"
          >
            ...
          </span>
          <button
            v-else
            type="button"
            @click="setPage(Number(p))"
            class="min-w-[32px] h-8 px-2 flex items-center justify-center rounded-xl text-xs font-semibold transition-all cursor-pointer"
            :class="p === currentPage
              ? 'bg-violet-600 text-white shadow-2xs shadow-violet-200'
              : 'text-ink-muted hover:text-ink hover:bg-surface-raised font-medium'"
          >
            {{ p }}
          </button>
        </template>
      </div>

      <!-- Next -->
      <button
        type="button"
        @click="setPage(currentPage + 1)"
        :disabled="currentPage >= calculatedTotalPages"
        class="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-xl text-xs font-medium text-ink-muted hover:text-ink hover:bg-surface-raised disabled:opacity-30 disabled:pointer-events-none transition-all cursor-pointer"
      >
        <span class="hidden sm:inline">{{ t('common.pagination.next') }}</span>
        <ChevronRight class="w-3.5 h-3.5" />
      </button>

      <!-- Last Page -->
      <button
        type="button"
        @click="setPage(calculatedTotalPages)"
        :disabled="currentPage >= calculatedTotalPages"
        class="p-1.5 rounded-lg text-ink-muted hover:text-ink hover:bg-surface-raised disabled:opacity-30 disabled:pointer-events-none transition-all cursor-pointer"
        :title="t('common.pagination.last')"
      >
        <ChevronsRight class="w-4 h-4" />
      </button>
    </div>
  </div>
</template>
