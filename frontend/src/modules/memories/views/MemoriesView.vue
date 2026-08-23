<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { memoryService } from '@/services/memoryService'
import {
  Trash2,
  Calendar as CalendarIcon,
  Heart,
  Sparkles,
  Edit2,
  Image as ImageIcon,
  Loader2,
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
import AppSwitch from '@/components/ui/AppSwitch.vue'
import type { MemoryItem } from '@/types/memory'

const { t, locale } = useI18n()
const todayStr = new Date().toISOString().split('T')[0]

// Data & Lazy load state (per-page: 15)
const memories = ref<MemoryItem[]>([])
const loading = ref(true)
const loadingMore = ref(false)
const page = ref(1)
const perPage = ref(15)
const hasMore = ref(true)
const totalCount = ref(0)

// Sentinel ref for IntersectionObserver
const sentinelRef = ref<HTMLElement | null>(null)
let observer: IntersectionObserver | null = null

// Filter state
const filterType = ref<'ALL' | 'DATE' | 'RANDOM'>('ALL')

const filteredMemories = computed(() => memories.value)

// Add / Edit Modal state
const showAddModal = ref(false)
const submitting = ref(false)
const editingMemory = ref<MemoryItem | null>(null)

const formTitle = ref('')
const formContent = ref('')
const formImages = ref<string[]>([])
const formDisplayType = ref<'DATE' | 'RANDOM'>('RANDOM')
const formTargetDate = ref(todayStr)
const formIsShared = ref(true)

// Delete Confirm Modal
const showDeleteConfirmModal = ref(false)
const deletingMemoryId = ref<string | null>(null)
const deleting = ref(false)

async function fetchMemories(reset = false) {
  if (reset) {
    page.value = 1
    hasMore.value = true
    loading.value = true
  } else {
    loadingMore.value = true
  }

  try {
    const res = await memoryService.getMemories({
      page: page.value,
      per_page: perPage.value,
      display_type: filterType.value === 'ALL' ? undefined : filterType.value,
    })

    if (reset) {
      memories.value = res.items
    } else {
      const existingIds = new Set(memories.value.map(n => n.id))
      const newItems = res.items.filter(n => !existingIds.has(n.id))
      memories.value = [...memories.value, ...newItems]
    }

    totalCount.value = res.total
    hasMore.value = res.has_more
  } catch (err) {
    console.error('Failed to fetch memories:', err)
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

function loadMore() {
  if (loading.value || loadingMore.value || !hasMore.value) return
  page.value += 1
  fetchMemories(false)
}

function setupObserver() {
  if (observer) {
    observer.disconnect()
  }

  if (typeof IntersectionObserver === 'undefined') return

  observer = new IntersectionObserver(
    (entries) => {
      const entry = entries[0]
      if (entry && entry.isIntersecting) {
        loadMore()
      }
    },
    {
      root: null,
      rootMargin: '250px',
      threshold: 0.1,
    }
  )

  if (sentinelRef.value) {
    observer.observe(sentinelRef.value)
  }
}

watch(filterType, () => {
  fetchMemories(true)
})

watch(sentinelRef, (newEl) => {
  if (newEl && observer) {
    observer.observe(newEl)
  }
})

function openAddModal() {
  editingMemory.value = null
  formTitle.value = ''
  formContent.value = ''
  formImages.value = []
  formDisplayType.value = 'RANDOM'
  formTargetDate.value = todayStr
  formIsShared.value = true
  showAddModal.value = true
}

function openEditModal(memory: MemoryItem) {
  editingMemory.value = memory
  formTitle.value = memory.title
  formContent.value = memory.content
  if (memory.images && memory.images.length > 0) {
    formImages.value = memory.images.map(img => img.file_path)
  } else if (memory.image_url) {
    formImages.value = [memory.image_url]
  } else {
    formImages.value = []
  }
  formDisplayType.value = memory.display_type
  formTargetDate.value = memory.target_date || todayStr
  formIsShared.value = memory.is_shared !== undefined ? memory.is_shared : true
  showAddModal.value = true
}

async function handleSaveMemory() {
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
      is_shared: formIsShared.value,
    }
    if (editingMemory.value) {
      const updated = await memoryService.updateMemory(editingMemory.value.id, payload)
      // Update in-place
      const idx = memories.value.findIndex(n => n.id === editingMemory.value!.id)
      if (idx !== -1) {
        memories.value[idx] = { ...memories.value[idx], ...updated }
      }
    } else {
      await memoryService.createMemory(payload)
      await fetchMemories(true)
    }
    showAddModal.value = false
  } catch (err) {
    console.error('Failed to save memory:', err)
  } finally {
    submitting.value = false
  }
}

function promptDeleteMemory(id: string) {
  deletingMemoryId.value = id
  showDeleteConfirmModal.value = true
}

async function confirmDeleteMemory() {
  if (!deletingMemoryId.value) return
  deleting.value = true
  try {
    await memoryService.deleteMemory(deletingMemoryId.value)
    showDeleteConfirmModal.value = false
    const deletedId = deletingMemoryId.value
    deletingMemoryId.value = null
    if (editingMemory.value?.id === deletedId) showAddModal.value = false
    memories.value = memories.value.filter(n => n.id !== deletedId)
    totalCount.value = Math.max(0, totalCount.value - 1)
  } catch (err) {
    console.error('Failed to delete memory:', err)
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
  all: totalCount.value || memories.value.length,
  date: memories.value.filter(n => n.display_type === 'DATE').length,
  random: memories.value.filter(n => n.display_type === 'RANDOM').length,
}))

onMounted(() => {
  fetchMemories(true).then(() => {
    setupObserver()
  })
})

onUnmounted(() => {
  if (observer) {
    observer.disconnect()
    observer = null
  }
})
</script>

<template>
  <div class="flex gap-6 items-start select-none pb-10">

    <!-- ─── Left Panel ─── -->
    <div class="w-60 shrink-0 sticky top-6 bg-white border border-border rounded-2xl p-5 shadow-card space-y-4">
      <!-- Title -->
      <div class="flex items-center gap-2 pb-3 border-b border-border/60">
        <Heart class="w-4 h-4 text-violet-500 shrink-0" />
        <h1 class="text-sm font-bold text-ink">{{ t('memories.title') }}</h1>
      </div>

      <!-- Filter List -->
      <div class="space-y-1">
        <button
          v-for="f in ([
            { key: 'ALL', label: t('common.all'), count: counts.all },
            { key: 'DATE', label: t('memories.statusOptions.date'), count: counts.date },
            { key: 'RANDOM', label: t('memories.statusOptions.random'), count: counts.random },
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
          <Sparkles class="w-3.5 h-3.5 mr-1 text-white" />
          {{ t('memories.addMemory') }}
        </AppButton>
      </div>
    </div>

    <!-- ─── Main Content Area ─── -->
    <div class="flex-1 min-w-0">

      <!-- Loading Placeholder -->
      <div v-if="loading" class="py-20 text-center text-sm text-ink-faint">
        {{ t('memories.loading') }}
      </div>

      <!-- Empty State -->
      <AppCard v-else-if="filteredMemories.length === 0">
        <div class="py-12 text-center space-y-3">
          <div class="w-10 h-10 rounded-full bg-violet-50 border border-violet-100 flex items-center justify-center text-violet-400 mx-auto">
            <Heart class="w-5 h-5" />
          </div>
          <p class="text-sm font-medium text-ink">{{ t('memories.emptyTitle') }}</p>
          <p class="text-xs text-ink-muted">{{ t('memories.emptySubtitle') }}</p>
        </div>
      </AppCard>

      <!-- Memories Grid -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
        <div
          v-for="memory in filteredMemories"
          :key="memory.id"
          class="bg-white border border-border rounded-2xl shadow-card hover:shadow-pop transition-all overflow-hidden flex flex-col group cursor-pointer"
          @click="openEditModal(memory)"
        >
          <!-- Image Header -->
          <div
            v-if="(memory.images && memory.images.length > 0) || memory.image_url"
            class="relative h-44 w-full overflow-hidden bg-surface-subtle border-b border-border/60"
          >
            <img
              :src="memory.images?.[0]?.file_path || memory.image_url || ''"
              :alt="memory.title"
              class="w-full h-full object-cover object-center group-hover:scale-105 transition-transform duration-500"
            />
            <!-- Multiple Images Badge -->
            <div
              v-if="memory.images && memory.images.length > 1"
              class="absolute bottom-2.5 right-2.5 bg-black/60 backdrop-blur-xs text-white text-[10px] font-bold px-2 py-0.5 rounded-full flex items-center gap-1 shadow-xs"
            >
              <ImageIcon class="w-3 h-3" />
              <span>+{{ memory.images.length - 1 }}</span>
            </div>
          </div>
          <!-- Placeholder strip if no image -->
          <div v-else class="h-1.5 w-full bg-gradient-to-r from-violet-100 to-violet-50" />

          <!-- Body -->
          <div class="p-5 flex-1 space-y-2.5">
            <div class="flex items-start justify-between gap-2">
              <h3 class="text-sm font-semibold text-ink leading-snug group-hover:text-violet-700 transition-colors line-clamp-2 flex-1">
                {{ memory.title }}
              </h3>
              <div class="flex items-center gap-1 shrink-0">
                <AppBadge v-if="memory.is_shared" variant="violet" size="sm" :title="t('common.shared')">
                  <Heart class="w-3 h-3 fill-current text-violet-500" />
                </AppBadge>
                <AppBadge v-if="memory.display_type === 'DATE'" variant="violet" size="sm">
                  <CalendarIcon class="w-3 h-3" />
                </AppBadge>
                <AppBadge v-else variant="info" size="sm">
                  <Sparkles class="w-3 h-3" />
                </AppBadge>
              </div>
            </div>
            <p class="text-xs text-ink-muted leading-relaxed line-clamp-3">{{ memory.content }}</p>
          </div>

          <!-- Footer -->
          <div class="px-5 py-3 border-t border-border/60 bg-surface-subtle/40 flex items-center justify-between">
            <span class="text-[10px] text-ink-faint font-mono flex items-center gap-1">
              <CalendarIcon class="w-3 h-3 text-violet-300" />
              {{ formatDate(memory.created_at) }}
            </span>
            <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
              <button
                type="button"
                @click.stop="openEditModal(memory)"
                class="p-1 text-ink-faint hover:text-violet-600 hover:bg-violet-50 rounded transition-colors cursor-pointer"
                :title="t('common.edit')"
              >
                <Edit2 class="w-3.5 h-3.5" />
              </button>
              <button
                type="button"
                @click.stop="promptDeleteMemory(memory.id)"
                class="p-1 text-ink-faint hover:text-err-text hover:bg-err-bg rounded transition-colors cursor-pointer"
                :title="t('common.delete')"
              >
                <Trash2 class="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Infinite Scroll Sentinel & Loading Indicators -->
      <div ref="sentinelRef" class="w-full py-4 flex flex-col items-center justify-center">
        <!-- Loading More Spinner -->
        <div
          v-if="loadingMore"
          class="flex items-center gap-2 py-3 px-4 rounded-xl bg-violet-50/80 border border-violet-100 text-violet-700 text-xs font-medium shadow-2xs animate-pulse"
        >
          <Loader2 class="w-4 h-4 animate-spin text-violet-600" />
          <span>{{ t('memories.loadingMore') }}</span>
        </div>

        <!-- End of Memories indicator -->
        <div
          v-else-if="!hasMore && memories.length > 0"
          class="py-4 text-center text-xs text-ink-faint flex items-center justify-center gap-1.5"
        >
          <Heart class="w-3.5 h-3.5 text-violet-300 fill-violet-50" />
          <span>{{ t('memories.allLoaded') }}</span>
        </div>
      </div>
    </div>

    <!-- ─── Add / Edit Modal ─── -->
    <AppModal
      :show="showAddModal"
      :title="editingMemory ? t('common.edit') : t('memories.addMemory')"
      width="880"
      @close="showAddModal = false"
    >
      <form @submit.prevent="handleSaveMemory" class="space-y-4">
        <AppInput
          v-model="formTitle"
          :label="t('memories.memoryTitle')"
          :placeholder="t('memories.memoryTitlePlaceholder')"
          required
        />

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <AppSelect
            v-model="formDisplayType"
            :label="t('memories.statusLabel')"
            :options="[
              { label: t('memories.statusOptions.random'), value: 'RANDOM' },
              { label: t('memories.statusOptions.date'), value: 'DATE' },
            ]"
          />
          <AppInput
            v-if="formDisplayType === 'DATE'"
            v-model="formTargetDate"
            type="date"
            :label="t('memories.targetDateLabel')"
            required
          />
        </div>

        <!-- Native UI Image Upload (File Upload & 1-N Media Dropzone) -->
        <AppImageUpload
          v-model="formImages"
          :multiple="true"
          :max-files="6"
          :label="t('memories.imageUploadLabel')"
        />

        <AppTextarea
          v-model="formContent"
          :label="t('memories.contentLabel')"
          :placeholder="t('memories.contentPlaceholder')"
          :rows="4"
          required
        />

        <!-- AppSwitch for Couple Shared Memory -->
        <div class="p-3 bg-surface-subtle/40 border border-border/80 rounded-xl">
          <AppSwitch
            v-model="formIsShared"
            :label="t('memories.shareWithPartner')"
            :description="t('memories.shareWithPartnerDesc')"
          />
        </div>

        <div class="flex items-center justify-between pt-2 border-t border-border">
          <div>
            <AppButton
              v-if="editingMemory"
              variant="outline"
              type="button"
              size="sm"
              class="text-err-text hover:bg-err-bg border-err-border"
              @click="promptDeleteMemory(editingMemory.id)"
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
      :title="t('memories.deleteTitle')"
      :message="t('memories.deleteMessage')"
      :confirmText="t('memories.deleteConfirm')"
      :cancelText="t('common.cancel')"
      variant="danger"
      :loading="deleting"
      @confirm="confirmDeleteMemory"
      @close="showDeleteConfirmModal = false"
    />

  </div>
</template>
