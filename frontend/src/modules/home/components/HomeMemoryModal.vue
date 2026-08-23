<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { MemoryItem } from '@/types/memory'
import { StickyNote } from 'lucide-vue-next'
import AppButton from '@/components/ui/AppButton.vue'
import AppModal from '@/components/ui/AppModal.vue'

interface Props {
  show: boolean
  memory: MemoryItem | null
  authorName?: string
  isShuffling?: boolean
  hasMemories?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  authorName: '',
  isShuffling: false,
  hasMemories: true,
})

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'shuffle'): void
}>()

const { t } = useI18n()

const modalTitle = computed(() => {
  if (props.authorName) {
    return t('home.randomNoteModal.title', { name: props.authorName })
  }
  return t('home.randomNoteModal.defaultTitle')
})

// Thu thập toàn bộ ảnh được lưu (cả memory.images mảng nhiều ảnh và memory.image_url đơn)
const allImages = computed<string[]>(() => {
  if (!props.memory) return []
  const list: string[] = []

  if (props.memory.images && Array.isArray(props.memory.images) && props.memory.images.length > 0) {
    for (const img of props.memory.images) {
      if (img?.file_path && !list.includes(img.file_path)) {
        list.push(img.file_path)
      }
    }
  }

  if (props.memory.image_url && !list.includes(props.memory.image_url)) {
    list.push(props.memory.image_url)
  }

  return list
})
</script>

<template>
  <AppModal
    :show="show"
    :title="modalTitle"
    width="md"
    @close="emit('close')"
  >
    <div v-if="memory" class="space-y-3 py-1">
      <div class="flex items-center justify-between gap-2">
        <h3 class="font-bold text-sm text-ink truncate">{{ memory.title }}</h3>
      </div>

      <p class="text-xs text-slate-700 leading-relaxed whitespace-pre-line">
        {{ memory.content }}
      </p>

      <!-- TOÀN BỘ ẢNH ĐƯỢC LƯU (Tỷ lệ Full, bám theo chiều rộng, không bị cắt) -->
      <div v-if="allImages.length > 0" class="mt-3 space-y-3">
        <div
          v-for="(img, idx) in allImages"
          :key="idx"
          class="rounded-2xl overflow-hidden w-full border border-border/60 shadow-2xs bg-surface-subtle"
        >
          <img
            :src="img"
            :alt="`${memory.title} ${idx + 1}`"
            class="w-full h-auto block"
            loading="lazy"
          />
        </div>
      </div>
    </div>

    <div v-else class="py-8 text-center text-xs text-ink-faint space-y-2">
      <StickyNote class="w-8 h-8 mx-auto text-ink-faint/60" />
      <p>{{ t('home.randomNoteModal.empty') }}</p>
    </div>

    <template #footer>
      <div class="flex items-center justify-end w-full">
        <AppButton
          variant="secondary"
          size="sm"
          @click="emit('close')"
        >
          {{ t('home.randomNoteModal.close') }}
        </AppButton>
      </div>
    </template>
  </AppModal>
</template>
