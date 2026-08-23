<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/authStore'
import { userService } from '@/services/userService'
import type { User, UserCreatePayload, UserUpdatePayload } from '@/types/auth'
import {
  Search,
  Edit2,
  Trash2,
  ShieldCheck,
  UserX,
  User as UserIcon,
  CheckCircle2,
  AlertCircle,
  Sparkles,
} from 'lucide-vue-next'
import AppButton from '@/components/ui/AppButton.vue'
import AppModal from '@/components/ui/AppModal.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppSelect from '@/components/ui/AppSelect.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppConfirmModal from '@/components/ui/AppConfirmModal.vue'
import AppAvatarCropper from '@/components/ui/AppAvatarCropper.vue'
import AppPagination from '@/components/ui/AppPagination.vue'

const { t, locale } = useI18n()
const authStore = useAuthStore()

// State
const users = ref<User[]>([])
const loading = ref(true)
const errorMessage = ref<string | null>(null)
const successMessage = ref<string | null>(null)

// Pagination State (per-page: 15)
const currentPage = ref(1)
const perPage = ref(15)
const totalUsers = ref(0)
const totalPages = ref(1)

// Users Filters
const searchQuery = ref('')
const selectedRole = ref<string>('ALL')
const selectedStatus = ref<string>('ALL')

// User Add / Edit Modal State
const showUserModal = ref(false)
const editingUser = ref<User | null>(null)
const modalSubmitting = ref(false)
const modalError = ref<string | null>(null)

const formFullName = ref('')
const formEmail = ref('')
const formPassword = ref('')
const formRole = ref('user')
const formAvatarUrl = ref<string | null>(null)
const formIsActive = ref('true')

// User Delete Modal State
const showDeleteModal = ref(false)
const deletingUser = ref<User | null>(null)
const deleteLoading = ref(false)

// Select options
const roleFilterOptions = computed(() => [
  { label: t('users.roleAll'), value: 'ALL' },
  { label: t('users.roleAdmin'), value: 'admin' },
  { label: t('users.roleUser'), value: 'user' },
])

const statusFilterOptions = computed(() => [
  { label: t('users.statusAll'), value: 'ALL' },
  { label: t('users.statusActive'), value: 'true' },
  { label: t('users.statusInactive'), value: 'false' },
])

const modalRoleOptions = computed(() => [
  { label: t('users.roleAdmin'), value: 'admin' },
  { label: t('users.roleUser'), value: 'user' },
])

const modalStatusOptions = computed(() => [
  { label: t('users.statusActive'), value: 'true' },
  { label: t('users.statusInactive'), value: 'false' },
])

// Filtered users list (rendered directly from server pagination response)
const filteredUsers = computed(() => users.value)

let searchDebounceTimer: ReturnType<typeof setTimeout> | null = null

function handleFilterChange() {
  currentPage.value = 1
  fetchUsers()
}

watch([selectedRole, selectedStatus], () => {
  handleFilterChange()
})

watch(searchQuery, () => {
  if (searchDebounceTimer) clearTimeout(searchDebounceTimer)
  searchDebounceTimer = setTimeout(() => {
    handleFilterChange()
  }, 300)
})

async function fetchUsers() {
  loading.value = true
  errorMessage.value = null
  try {
    const res = await userService.getUsers({
      page: currentPage.value,
      per_page: perPage.value,
      role: selectedRole.value === 'ALL' ? undefined : selectedRole.value,
      is_active: selectedStatus.value === 'ALL' ? undefined : (selectedStatus.value === 'true'),
      search: searchQuery.value.trim() || undefined,
    })
    users.value = res.items
    totalUsers.value = res.total
    totalPages.value = res.total_pages
    currentPage.value = res.page
  } catch (err: any) {
    console.error('Failed to load users:', err)
    errorMessage.value = err.response?.data?.detail || 'Failed to load users.'
  } finally {
    loading.value = false
  }
}

function openCreateModal() {
  editingUser.value = null
  formFullName.value = ''
  formEmail.value = ''
  formPassword.value = ''
  formRole.value = 'user'
  formAvatarUrl.value = null
  formIsActive.value = 'true'
  modalError.value = null
  showUserModal.value = true
}

function openEditModal(user: User) {
  editingUser.value = user
  formFullName.value = user.full_name || ''
  formEmail.value = user.email || ''
  formPassword.value = ''
  formRole.value = user.role || 'user'
  formAvatarUrl.value = user.avatar_url || null
  formIsActive.value = user.is_active ? 'true' : 'false'
  modalError.value = null
  showUserModal.value = true
}

async function handleSaveUser() {
  modalError.value = null
  if (!formEmail.value.trim()) {
    modalError.value = 'Email is required.'
    return
  }
  if (!editingUser.value && !formPassword.value.trim()) {
    modalError.value = 'Password is required for new users.'
    return
  }

  modalSubmitting.value = true
  try {
    if (editingUser.value) {
      const payload: UserUpdatePayload = {
        full_name: formFullName.value.trim(),
        email: formEmail.value.trim(),
        role: formRole.value,
        avatar_url: formAvatarUrl.value,
        is_active: formIsActive.value === 'true',
      }
      if (formPassword.value.trim()) {
        payload.password = formPassword.value.trim()
      }
      await userService.updateUser(editingUser.value.id, payload)
      showSuccess(t('users.updateSuccess'))
    } else {
      const payload: UserCreatePayload = {
        full_name: formFullName.value.trim(),
        email: formEmail.value.trim(),
        password: formPassword.value.trim(),
        role: formRole.value,
        avatar_url: formAvatarUrl.value,
        is_active: formIsActive.value === 'true',
      }
      await userService.createUser(payload)
      showSuccess(t('users.createSuccess'))
    }

    showUserModal.value = false
    await fetchUsers()
  } catch (err: any) {
    console.error('Failed to save user:', err)
    modalError.value = err.response?.data?.detail || 'Failed to save user.'
  } finally {
    modalSubmitting.value = false
  }
}

function promptDeleteUser(user: User) {
  if (authStore.user && user.id === authStore.user.id) {
    errorMessage.value = t('users.cannotDeleteSelf')
    return
  }
  deletingUser.value = user
  showDeleteModal.value = true
}

async function confirmDeleteUser() {
  if (!deletingUser.value) return
  deleteLoading.value = true
  try {
    await userService.deleteUser(deletingUser.value.id)
    showDeleteModal.value = false
    deletingUser.value = null
    showSuccess(t('users.deleteSuccess'))
    await fetchUsers()
  } catch (err: any) {
    console.error('Failed to delete user:', err)
    errorMessage.value = err.response?.data?.detail || 'Failed to delete user.'
  } finally {
    deleteLoading.value = false
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
  fetchUsers()
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

    <!-- Action Bar (Search, Filters, Actions) -->
    <div class="bg-white border border-border rounded-2xl p-3.5 shadow-card flex flex-col sm:flex-row sm:items-center justify-between gap-3">
      <!-- Search Input -->
      <div class="relative flex-1 max-w-md">
        <Search class="w-3.5 h-3.5 text-ink-faint absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
        <input
          v-model="searchQuery"
          type="text"
          :placeholder="t('users.searchPlaceholder')"
          class="w-full h-[42px] pl-9 pr-3.5 py-2.5 text-xs bg-surface-subtle/80 hover:bg-surface-raised focus:bg-white border border-border rounded-xl text-ink placeholder:text-ink-faint focus:outline-none focus:ring-2 focus:ring-violet-400/20 focus:border-violet-500 transition-all shadow-2xs"
        />
      </div>

      <!-- Dropdown Filters & Actions -->
      <div class="flex flex-wrap items-center gap-2.5 shrink-0">
        <div class="w-36 sm:w-40">
          <AppSelect
            v-model="selectedRole"
            :options="roleFilterOptions"
            size="sm"
          />
        </div>
        <div class="w-36 sm:w-40">
          <AppSelect
            v-model="selectedStatus"
            :options="statusFilterOptions"
            size="sm"
          />
        </div>
        <AppButton size="md" @click="openCreateModal" class="h-[42px] py-2.5 px-4 shrink-0 shadow-2xs rounded-xl text-xs font-semibold inline-flex items-center justify-center">
          <Sparkles class="w-3.5 h-3.5 mr-1 text-white" />
          {{ t('users.addUser') }}
        </AppButton>
      </div>
    </div>

    <!-- Users Table / List Card -->
    <div class="bg-white border border-border rounded-2xl shadow-card overflow-hidden">
      <!-- Loading State -->
      <div v-if="loading" class="py-20 text-center text-sm text-ink-faint">
        <div class="animate-spin w-6 h-6 border-2 border-violet-600 border-t-transparent rounded-full mx-auto mb-2"></div>
        {{ t('users.loading') }}
      </div>

      <!-- Empty State -->
      <div v-else-if="filteredUsers.length === 0" class="py-16 text-center space-y-3">
        <div class="w-12 h-12 rounded-full bg-violet-50 border border-violet-100 flex items-center justify-center text-violet-400 mx-auto">
          <UserX class="w-6 h-6" />
        </div>
        <p class="text-sm font-semibold text-ink">{{ t('users.emptyTitle') }}</p>
        <p class="text-xs text-ink-muted">{{ t('users.emptySubtitle') }}</p>
        <AppButton size="sm" @click="openCreateModal" class="mx-auto mt-2">
          <Sparkles class="w-3.5 h-3.5 mr-1 text-white" />
          {{ t('users.addUser') }}
        </AppButton>
      </div>

      <!-- Table -->
      <div v-else class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="border-b border-border/80 bg-surface-subtle/40 text-[11px] font-bold text-ink-faint uppercase tracking-wider">
              <th class="py-3.5 px-5">{{ t('users.colUser') }}</th>
              <th class="py-3.5 px-4">{{ t('users.colRole') }}</th>
              <th class="py-3.5 px-4">{{ t('users.colStatus') }}</th>
              <th class="py-3.5 px-4">{{ t('users.colCreatedAt') }}</th>
              <th class="py-3.5 px-5 text-right">{{ t('users.colActions') }}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border/60 text-xs sm:text-sm">
            <tr
              v-for="u in filteredUsers"
              :key="u.id"
              class="hover:bg-surface-raised/60 transition-colors group"
            >
              <!-- User Info (Avatar + Name + Email) -->
              <td class="py-3.5 px-5">
                <div class="flex items-center gap-3">
                  <div
                    class="w-9 h-9 rounded-xl flex items-center justify-center font-bold text-xs shrink-0 shadow-2xs border overflow-hidden"
                    :class="u.role === 'admin'
                      ? 'bg-violet-100 text-violet-700 border-violet-200'
                      : 'bg-violet-50 text-violet-600 border-violet-200/70'"
                  >
                    <img
                      v-if="u.avatar_url"
                      :src="u.avatar_url"
                      :alt="u.full_name"
                      class="w-full h-full object-cover object-center"
                    />
                    <span v-else>{{ getUserInitials(u.full_name, u.email) }}</span>
                  </div>
                  <div class="min-w-0">
                    <div class="flex items-center gap-1.5">
                      <p class="font-semibold text-ink truncate leading-tight">{{ u.full_name || 'User' }}</p>
                      <span
                        v-if="authStore.user && u.id === authStore.user.id"
                        class="text-[10px] bg-violet-100 text-violet-700 font-bold px-1.5 py-0.2 rounded-md font-mono"
                      >
                        {{ t('users.you') }}
                      </span>
                    </div>
                    <p class="text-xs text-ink-faint font-mono truncate mt-0.5">{{ u.email }}</p>
                  </div>
                </div>
              </td>

              <!-- Role Badge -->
              <td class="py-3.5 px-4">
                <AppBadge v-if="u.role === 'admin'" variant="violet" size="sm">
                  <ShieldCheck class="w-3 h-3 mr-0.5" />
                  {{ t('users.roleAdmin') }}
                </AppBadge>
                <AppBadge v-else variant="neutral" size="sm">
                  <UserIcon class="w-3 h-3 mr-0.5" />
                  {{ t('users.roleUser') }}
                </AppBadge>
              </td>

              <!-- Status Badge -->
              <td class="py-3.5 px-4">
                <AppBadge v-if="u.is_active" variant="ok" size="sm">
                  {{ t('users.statusActive') }}
                </AppBadge>
                <AppBadge v-else variant="err" size="sm">
                  {{ t('users.statusInactive') }}
                </AppBadge>
              </td>

              <!-- Joined Date -->
              <td class="py-3.5 px-4 text-ink-muted text-xs font-mono">
                {{ formatDate(u.created_at) }}
              </td>

              <!-- Actions -->
              <td class="py-3.5 px-5 text-right">
                <div class="flex items-center justify-end gap-1">
                  <button
                    type="button"
                    @click="openEditModal(u)"
                    class="p-1.5 rounded-lg text-ink-faint hover:text-violet-600 hover:bg-violet-50 transition-colors cursor-pointer"
                    :title="t('users.editUser')"
                  >
                    <Edit2 class="w-3.5 h-3.5" />
                  </button>
                  <button
                    type="button"
                    @click="promptDeleteUser(u)"
                    :disabled="Boolean(authStore.user && u.id === authStore.user.id)"
                    class="p-1.5 rounded-lg text-ink-faint hover:text-err-text hover:bg-err-bg transition-colors cursor-pointer disabled:opacity-30 disabled:cursor-not-allowed"
                    :title="authStore.user && u.id === authStore.user.id ? t('users.cannotDeleteSelf') : t('common.delete')"
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
      <div v-if="!loading && totalUsers > 0" class="border-t border-border/60 pt-3 mt-3">
        <AppPagination
          v-model:currentPage="currentPage"
          :totalItems="totalUsers"
          :perPage="perPage"
          :totalPages="totalPages"
          @change="fetchUsers"
        />
      </div>
    </div>

    <!-- ============================================================= -->
    <!-- MODALS: USER CREATE / EDIT & DELETE                           -->
    <!-- ============================================================= -->
    <AppModal
      :show="showUserModal"
      :title="editingUser ? t('users.editUser') : t('users.addUser')"
      width="md"
      @close="showUserModal = false"
    >
      <form @submit.prevent="handleSaveUser" class="space-y-4">
        <div v-if="modalError" class="p-2.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs font-medium">
          {{ modalError }}
        </div>

        <div class="flex justify-center pb-2">
          <AppAvatarCropper
            v-model="formAvatarUrl"
            :name="formFullName || 'User'"
            size="lg"
          />
        </div>

        <AppInput
          v-model="formFullName"
          :label="t('auth.fullName')"
          :placeholder="t('users.fullNamePlaceholder')"
          required
        />

        <AppInput
          v-model="formEmail"
          type="email"
          :label="t('auth.email')"
          :placeholder="t('users.emailPlaceholder')"
          required
        />

        <AppInput
          v-model="formPassword"
          type="password"
          :label="t('auth.password')"
          :placeholder="editingUser ? t('users.passwordHint') : t('users.passwordPlaceholder')"
          :required="!editingUser"
        />

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <AppSelect
            v-model="formRole"
            :label="t('users.colRole')"
            :options="modalRoleOptions"
          />

          <AppSelect
            v-model="formIsActive"
            :label="t('users.colStatus')"
            :options="modalStatusOptions"
          />
        </div>

        <div class="flex items-center justify-end gap-2 pt-3 border-t border-border">
          <AppButton variant="outline" type="button" size="sm" @click="showUserModal = false">
            {{ t('common.cancel') }}
          </AppButton>
          <AppButton type="submit" size="sm" :loading="modalSubmitting">
            {{ t('common.save') }}
          </AppButton>
        </div>
      </form>
    </AppModal>

    <AppConfirmModal
      :show="showDeleteModal"
      :title="t('users.deleteTitle')"
      :message="deletingUser ? t('users.deleteMessage', { name: deletingUser.full_name, email: deletingUser.email }) : ''"
      :confirmText="t('common.delete')"
      :cancelText="t('common.cancel')"
      variant="danger"
      :loading="deleteLoading"
      @confirm="confirmDeleteUser"
      @close="showDeleteModal = false"
    />

  </div>
</template>
