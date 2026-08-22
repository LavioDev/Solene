<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/authStore'
import { userService } from '@/services/userService'
import { coupleService } from '@/services/coupleService'
import type { User } from '@/types/auth'
import type { Couple, CoupleCreatePayload, CoupleUpdatePayload } from '@/types/couple'
import {
  Plus,
  Search,
  Edit2,
  Trash2,
  CheckCircle2,
  AlertCircle,
  Heart,
  Calendar as CalendarIcon,
  Sparkles,
} from 'lucide-vue-next'
import AppButton from '@/components/ui/AppButton.vue'
import AppModal from '@/components/ui/AppModal.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppSelect from '@/components/ui/AppSelect.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppConfirmModal from '@/components/ui/AppConfirmModal.vue'
import AppImageUpload from '@/components/ui/AppImageUpload.vue'
import AppPagination from '@/components/ui/AppPagination.vue'

const { t, locale } = useI18n()
const authStore = useAuthStore()

// State
const users = ref<User[]>([])
const couples = ref<Couple[]>([])
const loading = ref(true)
const errorMessage = ref<string | null>(null)
const successMessage = ref<string | null>(null)

// Pagination State (per-page: 15)
const currentPage = ref(1)
const perPage = ref(15)
const totalCouples = ref(0)
const totalPages = ref(1)

// Filters
const searchQuery = ref('')
const selectedStatus = ref<string>('ALL')

// Couple Create / Edit Modal State
const showCoupleModal = ref(false)
const editingCouple = ref<Couple | null>(null)
const coupleModalSubmitting = ref(false)
const coupleModalError = ref<string | null>(null)

const formCoupleUser1Id = ref('')
const formCoupleUser2Id = ref('')
const formCoupleStartDate = ref('')
const formCoupleNickname = ref('')
const formCoupleStatus = ref('active')
const formCoupleCoverUrl = ref('')

// Couple Delete Modal State
const showDeleteCoupleModal = ref(false)
const deletingCouple = ref<Couple | null>(null)
const deleteCoupleLoading = ref(false)

const statusFilterOptions = computed(() => [
  { label: t('common.all'), value: 'ALL' },
  { label: t('users.couples.statusActive'), value: 'active' },
  { label: t('users.couples.statusPaused'), value: 'paused' },
  { label: t('users.couples.statusEnded'), value: 'ended' },
])

const statusModalOptions = computed(() => [
  { label: t('users.couples.statusActive'), value: 'active' },
  { label: t('users.couples.statusPaused'), value: 'paused' },
  { label: t('users.couples.statusEnded'), value: 'ended' },
])

const user1SelectOptions = computed(() => {
  const list = [...users.value]
  if (authStore.user && !list.some((u) => u.id === authStore.user!.id)) {
    list.unshift(authStore.user)
  }
  if (authStore.user) {
    list.sort((a, b) => (a.id === authStore.user!.id ? -1 : b.id === authStore.user!.id ? 1 : 0))
  }

  return [
    { label: t('users.couples.selectUser1'), value: '' },
    ...list.map((u) => ({
      label: `${u.full_name || 'User'} (${u.email})${authStore.user && u.id === authStore.user.id ? ` - [${t('users.you')}]` : ''}`,
      value: u.id,
    })),
  ]
})

const user2SelectOptions = computed(() => {
  const list = [...users.value]
  if (authStore.user && !list.some((u) => u.id === authStore.user!.id)) {
    list.unshift(authStore.user)
  }

  return [
    { label: t('users.couples.selectUser2'), value: '' },
    ...list.map((u) => ({
      label: `${u.full_name || 'User'} (${u.email})${authStore.user && u.id === authStore.user.id ? ` - [${t('users.you')}]` : ''}`,
      value: u.id,
    })),
  ]
})

// Filtered couples list (rendered directly from server pagination response)
const filteredCouples = computed(() => {
  if (!searchQuery.value.trim()) return couples.value
  const q = searchQuery.value.toLowerCase().trim()
  return couples.value.filter((c) => {
    const matchNickname = c.nickname?.toLowerCase().includes(q)
    const matchUser1 =
      c.user1?.full_name?.toLowerCase().includes(q) || c.user1?.email?.toLowerCase().includes(q)
    const matchUser2 =
      c.user2?.full_name?.toLowerCase().includes(q) || c.user2?.email?.toLowerCase().includes(q)
    return matchNickname || matchUser1 || matchUser2
  })
})

let searchDebounceTimer: ReturnType<typeof setTimeout> | null = null

function handleFilterChange() {
  currentPage.value = 1
  fetchCouples()
}

watch(selectedStatus, () => {
  handleFilterChange()
})

watch(searchQuery, () => {
  if (searchDebounceTimer) clearTimeout(searchDebounceTimer)
  searchDebounceTimer = setTimeout(() => {
    handleFilterChange()
  }, 300)
})

async function fetchCouples() {
  loading.value = true
  errorMessage.value = null
  try {
    const res = await coupleService.getCouples({
      page: currentPage.value,
      per_page: perPage.value,
      status: selectedStatus.value === 'ALL' ? undefined : selectedStatus.value,
      search: searchQuery.value.trim() || undefined,
    })
    couples.value = res.items
    totalCouples.value = res.total
    totalPages.value = res.total_pages
    currentPage.value = res.page
  } catch (err: any) {
    console.error('Failed to load couples:', err)
    errorMessage.value = err.response?.data?.detail || 'Failed to load couples.'
  } finally {
    loading.value = false
  }
}

async function fetchData() {
  try {
    const [_, usersRes] = await Promise.all([
      fetchCouples(),
      userService.getUsers({ per_page: 100 }).catch(() => ({ items: [] })),
    ])
    users.value = usersRes.items || []
  } catch (err: any) {
    console.error('Failed to load initial data:', err)
  }
}

function openCreateCoupleModal() {
  editingCouple.value = null
  formCoupleUser1Id.value = authStore.user?.id || ''
  formCoupleUser2Id.value = ''
  formCoupleStartDate.value = new Date().toISOString().split('T')[0]
  formCoupleNickname.value = ''
  formCoupleStatus.value = 'active'
  formCoupleCoverUrl.value = ''
  coupleModalError.value = null
  showCoupleModal.value = true
}

function openEditCoupleModal(c: Couple) {
  editingCouple.value = c
  formCoupleUser1Id.value = c.user1_id || ''
  formCoupleUser2Id.value = c.user2_id || ''
  formCoupleStartDate.value = c.start_date
  formCoupleNickname.value = c.nickname || ''
  formCoupleStatus.value = c.status || 'active'
  formCoupleCoverUrl.value = c.cover_url || ''
  coupleModalError.value = null
  showCoupleModal.value = true
}

async function handleSaveCouple() {
  coupleModalError.value = null

  if (!formCoupleUser1Id.value || !formCoupleUser2Id.value) {
    coupleModalError.value = t('users.couples.sameUserError')
    return
  }

  if (formCoupleUser1Id.value === formCoupleUser2Id.value) {
    coupleModalError.value = t('users.couples.sameUserError')
    return
  }

  if (!formCoupleStartDate.value) {
    coupleModalError.value = t('users.couples.startDate') + ' is required.'
    return
  }

  coupleModalSubmitting.value = true
  try {
    if (editingCouple.value) {
      const payload: CoupleUpdatePayload = {
        user1_id: formCoupleUser1Id.value,
        user2_id: formCoupleUser2Id.value,
        start_date: formCoupleStartDate.value,
        nickname: formCoupleNickname.value.trim() || null,
        status: formCoupleStatus.value,
        cover_url: formCoupleCoverUrl.value || null,
      }
      await coupleService.updateCouple(editingCouple.value.id, payload)
      showSuccess(t('users.couples.updateSuccess'))
    } else {
      const payload: CoupleCreatePayload = {
        user1_id: formCoupleUser1Id.value,
        user2_id: formCoupleUser2Id.value,
        start_date: formCoupleStartDate.value,
        nickname: formCoupleNickname.value.trim() || null,
        status: formCoupleStatus.value,
        cover_url: formCoupleCoverUrl.value || null,
      }
      await coupleService.createCouple(payload)
      showSuccess(t('users.couples.createSuccess'))
    }

    showCoupleModal.value = false
    await fetchData()
  } catch (err: any) {
    console.error('Failed to save couple:', err)
    coupleModalError.value = err.response?.data?.detail || 'Failed to save couple.'
  } finally {
    coupleModalSubmitting.value = false
  }
}

function promptDeleteCouple(c: Couple) {
  deletingCouple.value = c
  showDeleteCoupleModal.value = true
}

async function confirmDeleteCouple() {
  if (!deletingCouple.value) return
  deleteCoupleLoading.value = true
  try {
    await coupleService.deleteCouple(deletingCouple.value.id)
    showDeleteCoupleModal.value = false
    deletingCouple.value = null
    showSuccess(t('users.couples.deleteSuccess'))
    await fetchData()
  } catch (err: any) {
    console.error('Failed to delete couple:', err)
    errorMessage.value = err.response?.data?.detail || 'Failed to delete couple.'
  } finally {
    deleteCoupleLoading.value = false
  }
}

function showSuccess(msg: string) {
  successMessage.value = msg
  setTimeout(() => {
    if (successMessage.value === msg) {
      successMessage.value = null
    }
  }, 4000)
}

function formatDate(dateStr?: string) {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  const loc =
    locale.value === 'vi'
      ? 'vi-VN'
      : locale.value === 'fr'
      ? 'fr-FR'
      : locale.value === 'zh'
      ? 'zh-CN'
      : 'en-US'
  return d.toLocaleDateString(loc, { year: 'numeric', month: 'short', day: 'numeric' })
}

function getUserInitials(name?: string, email?: string): string {
  if (name && name.trim()) {
    const parts = name.trim().split(' ')
    if (parts.length >= 2) {
      return `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase()
    }
    return name.slice(0, 2).toUpperCase()
  }
  if (email) return email.slice(0, 2).toUpperCase()
  return 'U'
}

onMounted(() => {
  fetchData()
})
</script>

<template>
  <div class="space-y-5 pb-12 select-none">

    <!-- Alert Notifications -->
    <div v-if="successMessage" class="flex items-center gap-2 p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-medium shadow-2xs">
      <CheckCircle2 class="w-4 h-4 text-emerald-600 shrink-0" />
      <span>{{ successMessage }}</span>
    </div>

    <div v-if="errorMessage" class="flex items-center gap-2 p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs font-medium shadow-2xs">
      <AlertCircle class="w-4 h-4 text-rose-600 shrink-0" />
      <span>{{ errorMessage }}</span>
    </div>

    <!-- Action Bar (Search & Filter) -->
    <div class="bg-white border border-border rounded-2xl p-3.5 shadow-card flex flex-col sm:flex-row sm:items-center justify-between gap-3">
      <!-- Couple Search Input -->
      <div class="relative flex-1 max-w-md">
        <Search class="w-4 h-4 text-ink-faint absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
        <input
          v-model="searchQuery"
          type="text"
          :placeholder="t('users.searchPlaceholder')"
          class="w-full h-[42px] pl-9 pr-3.5 py-2.5 text-xs sm:text-sm bg-surface-subtle/80 hover:bg-surface-raised focus:bg-white border border-border rounded-xl text-ink placeholder:text-ink-faint focus:outline-none focus:ring-2 focus:ring-violet-400/20 focus:border-violet-500 transition-all shadow-2xs"
        />
      </div>

      <!-- Filters & Add Couple Button -->
      <div class="flex flex-wrap items-center gap-2.5 shrink-0">
        <div class="w-40 sm:w-48">
          <AppSelect
            v-model="selectedStatus"
            :options="statusFilterOptions"
          />
        </div>
        <AppButton size="md" @click="openCreateCoupleModal" class="h-[42px] py-2.5 px-4 shrink-0 shadow-2xs rounded-xl text-xs sm:text-sm font-semibold inline-flex items-center justify-center">
          <Plus class="w-4 h-4 mr-1" />
          {{ t('users.couples.addCouple') }}
        </AppButton>
      </div>
    </div>

    <!-- Couples Table / List Card -->
    <div class="bg-white border border-border rounded-2xl shadow-card overflow-hidden">
      <!-- Loading State -->
      <div v-if="loading" class="py-20 text-center text-sm text-ink-faint">
        <div class="animate-spin w-6 h-6 border-2 border-violet-600 border-t-transparent rounded-full mx-auto mb-2"></div>
        {{ t('users.couples.loading') }}
      </div>

      <!-- Empty State -->
      <div v-else-if="filteredCouples.length === 0" class="py-16 text-center space-y-3">
        <div class="w-14 h-14 rounded-full bg-violet-50 border border-violet-100 flex items-center justify-center text-violet-600 mx-auto shadow-2xs">
          <Heart class="w-7 h-7 fill-violet-200 text-violet-600" />
        </div>
        <p class="text-sm font-semibold text-ink">{{ t('users.couples.emptyTitle') }}</p>
        <p class="text-xs text-ink-muted max-w-sm mx-auto">{{ t('users.couples.emptySubtitle') }}</p>
        <AppButton size="sm" @click="openCreateCoupleModal" class="mx-auto mt-2">
          <Plus class="w-3.5 h-3.5 mr-1" />
          {{ t('users.couples.addCouple') }}
        </AppButton>
      </div>

      <!-- Table with Clean Shared Model Columns (TR) -->
      <div v-else class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="border-b border-border/80 bg-surface-subtle/40 text-[11px] font-bold text-ink-faint uppercase tracking-wider">
              <th class="py-3.5 px-5">{{ t('users.couples.coupleColumn') }}</th>
              <th class="py-3.5 px-4">{{ t('users.couples.partners') }}</th>
              <th class="py-3.5 px-4">{{ t('users.couples.startDate') }}</th>
              <th class="py-3.5 px-4">{{ t('users.couples.status') }}</th>
              <th class="py-3.5 px-4">{{ t('users.colCreatedAt') }}</th>
              <th class="py-3.5 px-5 text-right">{{ t('users.colActions') }}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border/60 text-xs sm:text-sm">
            <tr
              v-for="c in filteredCouples"
              :key="c.id"
              @click="openEditCoupleModal(c)"
              class="hover:bg-violet-50/40 transition-colors group cursor-pointer"
            >
              <!-- 1. Couple Common Model (Thumbnail / Nickname / Days Together) -->
              <td class="py-3.5 px-5">
                <div class="flex items-center gap-3">
                  <!-- Violet-tone catch cover thumbnail -->
                  <div class="w-10 h-10 rounded-xl bg-violet-600 border border-violet-300/40 text-white font-bold text-xs flex items-center justify-center shrink-0 overflow-hidden shadow-2xs relative">
                    <img
                      v-if="c.cover_url"
                      :src="c.cover_url"
                      :alt="c.nickname || 'Cover'"
                      class="w-full h-full object-cover object-center"
                    />
                    <Heart v-else class="w-5 h-5 fill-white/80 text-white" />
                  </div>

                  <div class="min-w-0">
                    <div class="flex items-center gap-1.5">
                      <p class="font-bold text-ink group-hover:text-violet-700 transition-colors truncate leading-tight">
                        {{ c.nickname || ((c.user1?.full_name || 'User 1') + ' & ' + (c.user2?.full_name || 'User 2')) }}
                      </p>
                      <span
                        v-if="c.days_together !== undefined"
                        class="text-[10px] bg-violet-100 text-violet-700 border border-violet-200/80 font-bold px-1.5 py-0.2 rounded-md font-mono shrink-0 shadow-2xs inline-flex items-center gap-0.5"
                      >
                        <Sparkles class="w-2.5 h-2.5 text-violet-600" />
                        {{ t('users.couples.daysTogetherBadge', { n: c.days_together }) }}
                      </span>
                    </div>
                    <p class="text-[11px] text-ink-faint font-mono truncate mt-0.5">
                      {{ c.days_together !== undefined ? t('users.couples.daysTogether', { n: c.days_together }) : '' }}
                    </p>
                  </div>
                </div>
              </td>

              <!-- 2. Combined Partners Avatar Stack & Names -->
              <td class="py-3.5 px-4">
                <div class="flex items-center gap-2.5 min-w-[180px]">
                  <!-- Overlapping Avatar Stack (with Violet Catch Fallback) -->
                  <div class="flex items-center -space-x-2 shrink-0">
                    <!-- User 1 Avatar -->
                    <div class="w-7 h-7 rounded-full bg-violet-600 text-white border-2 border-white font-bold text-[10px] flex items-center justify-center overflow-hidden shadow-2xs">
                      <img
                        v-if="c.user1?.avatar_url"
                        :src="c.user1.avatar_url"
                        :alt="c.user1.full_name"
                        class="w-full h-full object-cover object-center"
                      />
                      <span v-else>{{ getUserInitials(c.user1?.full_name, c.user1?.email) }}</span>
                    </div>
                    <!-- User 2 Avatar -->
                    <div class="w-7 h-7 rounded-full bg-purple-500 text-white border-2 border-white font-bold text-[10px] flex items-center justify-center overflow-hidden shadow-2xs">
                      <img
                        v-if="c.user2?.avatar_url"
                        :src="c.user2.avatar_url"
                        :alt="c.user2.full_name"
                        class="w-full h-full object-cover object-center"
                      />
                      <span v-else>{{ getUserInitials(c.user2?.full_name, c.user2?.email) }}</span>
                    </div>
                  </div>

                  <div class="min-w-0 text-xs">
                    <p class="font-medium text-ink truncate leading-tight">
                      {{ c.user1?.full_name || 'User 1' }} & {{ c.user2?.full_name || 'User 2' }}
                    </p>
                    <p class="text-[11px] text-ink-faint font-mono truncate">
                      {{ c.user1?.email }}
                    </p>
                  </div>
                </div>
              </td>

              <!-- 3. Relationship Start Date -->
              <td class="py-3.5 px-4 text-ink-muted text-xs font-mono whitespace-nowrap">
                <div class="flex items-center gap-1.5">
                  <CalendarIcon class="w-3.5 h-3.5 text-violet-500 shrink-0" />
                  <span>{{ formatDate(c.start_date) }}</span>
                </div>
              </td>

              <!-- 4. Status Badge -->
              <td class="py-3.5 px-4">
                <AppBadge
                  v-if="c.status === 'active'"
                  variant="ok"
                  size="sm"
                >
                  {{ t('users.couples.statusActive') }}
                </AppBadge>
                <AppBadge
                  v-else-if="c.status === 'paused'"
                  variant="warn"
                  size="sm"
                >
                  {{ t('users.couples.statusPaused') }}
                </AppBadge>
                <AppBadge
                  v-else
                  variant="err"
                  size="sm"
                >
                  {{ t('users.couples.statusEnded') }}
                </AppBadge>
              </td>

              <!-- 5. Created Date -->
              <td class="py-3.5 px-4 text-ink-muted text-xs font-mono whitespace-nowrap">
                {{ formatDate(c.created_at) }}
              </td>

              <!-- 6. Actions -->
              <td class="py-3.5 px-5 text-right" @click.stop>
                <div class="flex items-center justify-end gap-1">
                  <button
                    type="button"
                    @click="openEditCoupleModal(c)"
                    class="p-1.5 rounded-lg text-ink-faint hover:text-violet-600 hover:bg-violet-50 transition-colors cursor-pointer"
                    :title="t('users.couples.editCouple')"
                  >
                    <Edit2 class="w-3.5 h-3.5" />
                  </button>
                  <button
                    type="button"
                    @click="promptDeleteCouple(c)"
                    class="p-1.5 rounded-lg text-ink-faint hover:text-err-text hover:bg-err-bg transition-colors cursor-pointer"
                    :title="t('common.delete')"
                  >
                    <Trash2 class="w-3.5 h-3.5" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Table Pagination (15 items per page) -->
      <div v-if="!loading && totalCouples > 0" class="border-t border-border/60 pt-3 mt-3">
        <AppPagination
          v-model:currentPage="currentPage"
          :totalItems="totalCouples"
          :perPage="perPage"
          :totalPages="totalPages"
          @change="fetchCouples"
        />
      </div>
    </div>

    <!-- ============================================================= -->
    <!-- MODALS: COUPLE CREATE / EDIT (WIDTH 1000px, UNLOCKED SELECTS) -->
    <!-- ============================================================= -->
    <AppModal
      :show="showCoupleModal"
      :title="editingCouple ? t('users.couples.editCouple') : t('users.couples.addCouple')"
      width="1000"
      @close="showCoupleModal = false"
    >
      <form @submit.prevent="handleSaveCouple" class="space-y-4">
        <div v-if="coupleModalError" class="p-2.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs font-medium">
          {{ coupleModalError }}
        </div>

        <!-- 2 Selects for User 1 and User 2 (Unlocked, freely selectable & searchable) -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <AppSelect
            v-model="formCoupleUser1Id"
            :label="t('users.couples.user1')"
            :options="user1SelectOptions"
            searchable
            :search-placeholder="t('users.searchPlaceholder')"
            required
          />

          <AppSelect
            v-model="formCoupleUser2Id"
            :label="t('users.couples.user2')"
            :options="user2SelectOptions"
            searchable
            :search-placeholder="t('users.searchPlaceholder')"
            required
          />
        </div>

        <!-- Relationship Start Date & Status -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <AppInput
            v-model="formCoupleStartDate"
            type="date"
            :label="t('users.couples.startDate')"
            required
          />

          <AppSelect
            v-model="formCoupleStatus"
            :label="t('users.couples.status')"
            :options="statusModalOptions"
          />
        </div>

        <!-- Couple Nickname / Title -->
        <AppInput
          v-model="formCoupleNickname"
          :label="t('users.couples.nickname')"
          :placeholder="t('users.couples.nicknamePlaceholder')"
        />

        <!-- Couple Cover Image -->
        <AppImageUpload
          v-model="formCoupleCoverUrl"
          :label="t('users.couples.coverImage')"
          :multiple="false"
          :crop="true"
          :crop-aspect-ratio="1"
        />

        <div class="flex items-center justify-end gap-2 pt-3 border-t border-border">
          <AppButton variant="outline" type="button" size="sm" @click="showCoupleModal = false">
            {{ t('common.cancel') }}
          </AppButton>
          <AppButton type="submit" size="sm" :loading="coupleModalSubmitting">
            {{ t('common.save') }}
          </AppButton>
        </div>
      </form>
    </AppModal>

    <AppConfirmModal
      :show="showDeleteCoupleModal"
      :title="t('users.couples.deleteTitle')"
      :message="deletingCouple ? t('users.couples.deleteMessage', { name: deletingCouple.nickname || ((deletingCouple.user1?.full_name || 'User 1') + ' & ' + (deletingCouple.user2?.full_name || 'User 2')) }) : ''"
      :confirmText="t('common.delete')"
      :cancelText="t('common.cancel')"
      variant="danger"
      :loading="deleteCoupleLoading"
      @confirm="confirmDeleteCouple"
      @close="showDeleteCoupleModal = false"
    />

  </div>
</template>
