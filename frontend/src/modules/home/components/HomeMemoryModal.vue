<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { NoteItem } from '@/types/note'
import { RotateCw, StickyNote } from 'lucide-vue-next'
import AppButton from '@/components/ui/AppButton.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppModal from '@/components/ui/AppModal.vue'

interface Props {
  show: boolean
  note: NoteItem | null
  authorName?: string
  isShuffling?: boolean
  hasNotes?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  authorName: '',
  isShuffling: false,
  hasNotes: true,
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
</script>

<template>
  <AppModal
    :show="show"
    :title="modalTitle"
    width="sm"
    @close="emit('close')"
  >
    <div v-if="note" class="space-y-3 py-1">
      <div class="flex items-center justify-between gap-2">
        <h3 class="font-bold text-sm text-ink truncate">{{ note.title }}</h3>
        <AppBadge variant="violet" size="sm">
          {{ note.target_date ? note.target_date : t('notes.badgeRandom') }}
        </AppBadge>
      </div>

      <p class="text-xs text-slate-700 leading-relaxed whitespace-pre-line">
        {{ note.content }}
      </p>

      <div
        v-if="note.image_url"
        class="mt-2 rounded-xl overflow-hidden max-h-56 w-full border border-border/60 shadow-2xs"
      >
        <img
          :src="note.image_url"
          :alt="note.title"
          class="w-full h-full object-cover"
        />
      </div>
    </div>

    <div v-else class="py-8 text-center text-xs text-ink-faint space-y-2">
      <StickyNote class="w-8 h-8 mx-auto text-ink-faint/60" />
      <p>{{ t('home.randomNoteModal.empty') }}</p>
    </div>

    <template #footer>
      <div class="flex items-center justify-between w-full">
        <AppButton
          variant="ghost"
          size="sm"
          @click="emit('shuffle')"
          :disabled="!hasNotes"
          class="text-xs font-semibold"
        >
          <RotateCw class="w-3.5 h-3.5 mr-1" :class="{ 'animate-spin': isShuffling }" />
          {{ t('home.randomNoteModal.shuffle') }}
        </AppButton>

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
