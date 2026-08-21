<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { apiClient } from '@/services/apiClient'
import {
  Plus,
  Trash2,
  Calendar as CalendarIcon,
  Heart,
  Sparkles,
  Edit2,
  Image as ImageIcon,
} from 'lucide-vue-next'
import AppButton from '@/components/ui/AppButton.vue'
import AppModal from '@/components/ui/AppModal.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppSelect from '@/components/ui/AppSelect.vue'
import AppTextarea from '@/components/ui/AppTextarea.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppCard from '@/components/ui/AppCard.vue'
import AppImageUpload from '@/components/ui/AppImageUpload.vue'
import AppConfirmModal from '@/components/ui/AppConfirmModal.vue'

interface NoteImageItem {
  id: string
  file_path: string
  filename?: string
  created_at: string
}

interface UserNote {
  id: string
  title: string
  content: string
  image_url?: string
  images?: NoteImageItem[]
  category: string
  display_type: 'DATE' | 'RANDOM'
  target_date?: string
  created_at: string
}

const { t, locale } = useI18n()
const todayStr = new Date().toISOString().split('T')[0]

const notes = ref<UserNote[]>([])
const loading = ref(true)

// Filter state
const filterType = ref<'ALL' | 'DATE' | 'RANDOM'>('ALL')

const filteredNotes = computed(() => {
  if (filterType.value === 'ALL') return notes.value
  return notes.value.filter(n => n.display_type === filterType.value)
})

// Add / Edit Modal state
const showAddModal = ref(false)
const submitting = ref(false)
const editingNote = ref<UserNote | null>(null)

const formTitle = ref('')
const formContent = ref('')
const formImages = ref<string[]>([])
const formDisplayType = ref<'DATE' | 'RANDOM'>('RANDOM')
const formTargetDate = ref(todayStr)

// Delete Confirm Modal
const showDeleteConfirmModal = ref(false)
const deletingNoteId = ref<string | null>(null)
const deleting = ref(false)

async function fetchNotes() {
  loading.value = true
  try {
    const res = await apiClient.get<UserNote[]>('/notes')
    notes.value = res.data
  } catch (err) {
    console.error('Failed to fetch notes:', err)
  } finally {
    loading.value = false
  }
}

function openAddModal() {
  editingNote.value = null
  formTitle.value = ''
  formContent.value = ''
  formImages.value = []
  formDisplayType.value = 'RANDOM'
  formTargetDate.value = todayStr
  showAddModal.value = true
}

function openEditModal(note: UserNote) {
  editingNote.value = note
  formTitle.value = note.title
  formContent.value = note.content
  if (note.images && note.images.length > 0) {
    formImages.value = note.images.map(img => img.file_path)
  } else if (note.image_url) {
    formImages.value = [note.image_url]
  } else {
    formImages.value = []
  }
  formDisplayType.value = note.display_type
  formTargetDate.value = note.target_date || todayStr
  showAddModal.value = true
}

async function handleSaveNote() {
  if (!formTitle.value.trim() || !formContent.value.trim()) return
  submitting.value = true
  try {
    const payload = {
      title: formTitle.value.trim(),
      content: formContent.value.trim(),
      image_urls: formImages.value,
      image_url: formImages.value[0] || null,
      category: 'memory',
      display_type: formDisplayType.value,
      target_date: formDisplayType.value === 'DATE' ? formTargetDate.value : null,
    }
    if (editingNote.value) {
      await apiClient.put(`/notes/${editingNote.value.id}`, payload)
    } else {
      await apiClient.post('/notes', payload)
    }
    showAddModal.value = false
    await fetchNotes()
  } catch (err) {
    console.error('Failed to save note:', err)
  } finally {
    submitting.value = false
  }
}

function promptDeleteNote(id: string) {
  deletingNoteId.value = id
  showDeleteConfirmModal.value = true
}

async function confirmDeleteNote() {
  if (!deletingNoteId.value) return
  deleting.value = true
  try {
    await apiClient.delete(`/notes/${deletingNoteId.value}`)
    showDeleteConfirmModal.value = false
    deletingNoteId.value = null
    if (editingNote.value?.id === deletingNoteId.value) showAddModal.value = false
    await fetchNotes()
  } catch (err) {
    console.error('Failed to delete note:', err)
  } finally {
    deleting.value = false
  }
}

function formatDate(dateStr: string) {
  const d = new Date(dateStr)
  const loc = locale.value === 'vi' ? 'vi-VN' : locale.value === 'fr' ? 'fr-FR' : locale.value === 'zh' ? 'zh-CN' : 'en-US'
  return d.toLocaleDateString(loc, { year: 'numeric', month: 'short', day: 'numeric' })
}

const counts = computed(() => ({
  all: notes.value.length,
  date: notes.value.filter(n => n.display_type === 'DATE').length,
  random: notes.value.filter(n => n.display_type === 'RANDOM').length,
}))

onMounted(fetchNotes)
</script>

<template>
  <div class="flex gap-6 items-start select-none pb-10">

    <!-- ─── Left Panel (Bọc toàn bộ trong 1 div duy nhất) ─── -->
    <div class="w-60 shrink-0 sticky top-6 bg-white border border-border rounded-2xl p-5 shadow-card space-y-4">
      <!-- Title -->
      <div class="flex items-center gap-2 pb-3 border-b border-border/60">
        <Heart class="w-4 h-4 text-violet-500 shrink-0" />
        <h1 class="text-sm font-bold text-ink">{{ t('notes.title') }}</h1>
      </div>

      <!-- Filter List -->
      <div class="space-y-1">
        <button
          v-for="f in ([
            { key: 'ALL', label: t('common.all'), count: counts.all },
            { key: 'DATE', label: t('notes.statusOptions.date'), count: counts.date },
            { key: 'RANDOM', label: t('notes.statusOptions.random'), count: counts.random },
          ] as const)"
          :key="f.key"
          type="button"
          @click="filterType = f.key"
          class="w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs transition-colors cursor-pointer"
          :class="filterType === f.key
            ? 'bg-violet-50 text-violet-700 font-semibold shadow-2xs'
            : 'text-ink-muted hover:bg-surface-raised hover:text-ink font-medium'"
        >
          <span>{{ f.label }}</span>
          <span
            class="text-[10px] font-mono px-1.5 py-0.5 rounded-md"
            :class="filterType === f.key ? 'bg-violet-100 text-violet-600' : 'bg-surface-raised text-ink-faint'"
          >
            {{ f.count }}
          </span>
        </button>
      </div>

      <!-- Add Button -->
      <div class="pt-3 border-t border-border/60">
        <AppButton class="w-full" size="sm" @click="openAddModal">
          <Plus class="w-3.5 h-3.5 mr-1" />
          {{ t('notes.addNote') }}
        </AppButton>
      </div>
    </div>

    <!-- ─── Main Content Area ─── -->
    <div class="flex-1 min-w-0">

      <!-- Loading -->
      <div v-if="loading" class="py-20 text-center text-sm text-ink-faint">
        {{ t('notes.loading') }}
      </div>

      <!-- Empty State -->
      <AppCard v-else-if="filteredNotes.length === 0">
        <div class="py-12 text-center space-y-3">
          <div class="w-10 h-10 rounded-full bg-violet-50 border border-violet-100 flex items-center justify-center text-violet-400 mx-auto">
            <Heart class="w-5 h-5" />
          </div>
          <p class="text-sm font-medium text-ink">{{ t('notes.emptyTitle') }}</p>
          <p class="text-xs text-ink-muted">{{ t('notes.emptySubtitle') }}</p>
          <AppButton size="sm" @click="openAddModal" class="mx-auto mt-2">
            <Plus class="w-3.5 h-3.5" />
            {{ t('notes.addNote') }}
          </AppButton>
        </div>
      </AppCard>

      <!-- Notes Grid -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
        <div
          v-for="note in filteredNotes"
          :key="note.id"
          class="bg-white border border-border rounded-2xl shadow-card hover:shadow-pop transition-all overflow-hidden flex flex-col group cursor-pointer"
          @click="openEditModal(note)"
        >
          <!-- Image Header -->
          <div
            v-if="(note.images && note.images.length > 0) || note.image_url"
            class="relative h-44 w-full overflow-hidden bg-surface-subtle border-b border-border/60"
          >
            <img
              :src="note.images?.[0]?.file_path || note.image_url"
              :alt="note.title"
              class="w-full h-full object-cover object-center group-hover:scale-105 transition-transform duration-500"
            />
            <!-- Multiple Images Badge -->
            <div
              v-if="note.images && note.images.length > 1"
              class="absolute bottom-2.5 right-2.5 bg-black/60 backdrop-blur-xs text-white text-[10px] font-bold px-2 py-0.5 rounded-full flex items-center gap-1 shadow-xs"
            >
              <ImageIcon class="w-3 h-3" />
              <span>+{{ note.images.length - 1 }}</span>
            </div>
          </div>
          <!-- Placeholder strip if no image -->
          <div v-else class="h-1.5 w-full bg-gradient-to-r from-violet-100 to-violet-50" />

          <!-- Body -->
          <div class="p-5 flex-1 space-y-2.5">
            <div class="flex items-start justify-between gap-2">
              <h3 class="text-sm font-semibold text-ink leading-snug group-hover:text-violet-700 transition-colors line-clamp-2 flex-1">
                {{ note.title }}
              </h3>
              <AppBadge v-if="note.display_type === 'DATE'" variant="violet" size="sm">
                <CalendarIcon class="w-3 h-3" />
              </AppBadge>
              <AppBadge v-else variant="info" size="sm">
                <Sparkles class="w-3 h-3" />
              </AppBadge>
            </div>
            <p class="text-xs text-ink-muted leading-relaxed line-clamp-3">{{ note.content }}</p>
          </div>

          <!-- Footer -->
          <div class="px-5 py-3 border-t border-border/60 bg-surface-subtle/40 flex items-center justify-between">
            <span class="text-[10px] text-ink-faint font-mono flex items-center gap-1">
              <CalendarIcon class="w-3 h-3 text-violet-300" />
              {{ formatDate(note.created_at) }}
            </span>
            <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
              <button
                type="button"
                @click.stop="openEditModal(note)"
                class="p-1 text-ink-faint hover:text-violet-600 hover:bg-violet-50 rounded transition-colors cursor-pointer"
                :title="t('common.edit')"
              >
                <Edit2 class="w-3.5 h-3.5" />
              </button>
              <button
                type="button"
                @click.stop="promptDeleteNote(note.id)"
                class="p-1 text-ink-faint hover:text-err-text hover:bg-err-bg rounded transition-colors cursor-pointer"
                :title="t('common.delete')"
              >
                <Trash2 class="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ─── Add / Edit Modal ─── -->
    <AppModal
      :show="showAddModal"
      :title="editingNote ? t('common.edit') : t('notes.addNote')"
      width="880"
      @close="showAddModal = false"
    >
      <form @submit.prevent="handleSaveNote" class="space-y-4">
        <AppInput
          v-model="formTitle"
          :label="t('notes.noteTitle')"
          :placeholder="t('notes.noteTitlePlaceholder')"
          required
        />

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <AppSelect
            v-model="formDisplayType"
            :label="t('notes.statusLabel')"
            :options="[
              { label: t('notes.statusOptions.random'), value: 'RANDOM' },
              { label: t('notes.statusOptions.date'), value: 'DATE' },
            ]"
          />
          <AppInput
            v-if="formDisplayType === 'DATE'"
            v-model="formTargetDate"
            type="date"
            :label="t('notes.targetDateLabel')"
            required
          />
        </div>

        <!-- Native UI Image Upload (File Upload & 1-N Media Dropzone) -->
        <AppImageUpload
          v-model="formImages"
          :multiple="true"
          :max-files="6"
          :label="t('notes.imageUploadLabel')"
        />

        <AppTextarea
          v-model="formContent"
          :label="t('notes.contentLabel')"
          :placeholder="t('notes.contentPlaceholder')"
          :rows="4"
          required
        />

        <div class="flex items-center justify-between pt-2 border-t border-border">
          <div>
            <AppButton
              v-if="editingNote"
              variant="outline"
              type="button"
              size="sm"
              class="text-err-text hover:bg-err-bg border-err-border"
              @click="promptDeleteNote(editingNote.id)"
            >
              <Trash2 class="w-3.5 h-3.5" />
              {{ t('common.delete') }}
            </AppButton>
          </div>
          <div class="flex gap-2">
            <AppButton variant="outline" type="button" size="sm" @click="showAddModal = false">
              {{ t('common.cancel') }}
            </AppButton>
            <AppButton type="submit" size="sm" :loading="submitting">
              {{ t('common.save') }}
            </AppButton>
          </div>
        </div>
      </form>
    </AppModal>

    <!-- ─── Confirm Delete Modal ─── -->
    <AppConfirmModal
      :show="showDeleteConfirmModal"
      :title="t('notes.deleteTitle')"
      :message="t('notes.deleteMessage')"
      :confirmText="t('notes.deleteConfirm')"
      :cancelText="t('common.cancel')"
      variant="danger"
      :loading="deleting"
      @confirm="confirmDeleteNote"
      @close="showDeleteConfirmModal = false"
    />

  </div>
</template>
