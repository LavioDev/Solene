<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/authStore'
import { userService } from '@/services/userService'
import {
  User as UserIcon,
  Shield,
  KeyRound,
  CheckCircle2,
  AlertCircle,
  Calendar as CalendarIcon,
  Mail,
  UserCheck,
} from 'lucide-vue-next'
import AppButton from '@/components/ui/AppButton.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppAvatarCropper from '@/components/ui/AppAvatarCropper.vue'


const { t, locale } = useI18n()
const authStore = useAuthStore()

// Profile Form State
const fullName = ref('')
const email = ref('')
const avatarUrl = ref<string | null>(null)
const profileSaving = ref(false)
const profileSuccess = ref<string | null>(null)
const profileError = ref<string | null>(null)

// Password Form State
const newPassword = ref('')
const confirmPassword = ref('')
const passwordSaving = ref(false)
const passwordSuccess = ref<string | null>(null)
const passwordError = ref<string | null>(null)

function initForm() {
  if (authStore.user) {
    fullName.value = authStore.user.full_name || ''
    email.value = authStore.user.email || ''
    avatarUrl.value = authStore.user.avatar_url || null
  }
}

async function handleAvatarUpdated(newAvatarUrl: string | null) {
  if (!authStore.user) return
  avatarUrl.value = newAvatarUrl
  try {
    const updated = await userService.updateUser(authStore.user.id, {
      avatar_url: newAvatarUrl,
    })
    authStore.setUser(updated)
    profileSuccess.value = t('profile.profileUpdated')
    setTimeout(() => {
      profileSuccess.value = null
    }, 4000)
  } catch (err: any) {
    console.error('Failed to update avatar:', err)
    profileError.value = err.response?.data?.detail || 'Failed to update avatar.'
  }
}

async function handleSaveProfile() {
  if (!authStore.user) return
  profileError.value = null
  profileSuccess.value = null

  if (!email.value.trim()) {
    profileError.value = 'Email is required.'
    return
  }

  profileSaving.value = true
  try {
    const updated = await userService.updateUser(authStore.user.id, {
      full_name: fullName.value.trim(),
      email: email.value.trim(),
      avatar_url: avatarUrl.value,
    })
    authStore.setUser(updated)
    profileSuccess.value = t('profile.profileUpdated')
    setTimeout(() => {
      profileSuccess.value = null
    }, 4000)
  } catch (err: any) {
    console.error('Failed to update profile:', err)
    profileError.value = err.response?.data?.detail || 'Failed to update profile.'
  } finally {
    profileSaving.value = false
  }
}


async function handleUpdatePassword() {
  if (!authStore.user) return
  passwordError.value = null
  passwordSuccess.value = null

  if (!newPassword.value) {
    passwordError.value = 'Please enter a new password.'
    return
  }
  if (newPassword.value !== confirmPassword.value) {
    passwordError.value = t('profile.passwordMismatch')
    return
  }

  passwordSaving.value = true
  try {
    await userService.updateUser(authStore.user.id, {
      password: newPassword.value,
    })
    newPassword.value = ''
    confirmPassword.value = ''
    passwordSuccess.value = t('profile.passwordChanged')
    setTimeout(() => {
      passwordSuccess.value = null
    }, 4000)
  } catch (err: any) {
    console.error('Failed to change password:', err)
    passwordError.value = err.response?.data?.detail || 'Failed to change password.'
  } finally {
    passwordSaving.value = false
  }
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
  return d.toLocaleDateString(loc, { year: 'numeric', month: 'long', day: 'numeric' })
}

onMounted(() => {
  initForm()
})

</script>

<template>
  <div class="max-w-4xl mx-auto space-y-6 pb-12 select-none">
    <!-- Account Overview Card -->
    <div v-if="authStore.user" class="bg-white border border-border rounded-2xl p-6 shadow-card flex flex-col sm:flex-row sm:items-center justify-between gap-6">
      <div class="flex items-center gap-5">
        <!-- Avatar with Cropper -->
        <AppAvatarCropper
          :model-value="avatarUrl"
          :name="authStore.user.full_name"
          size="lg"
          @update:model-value="handleAvatarUpdated"
        />

        <div class="space-y-1">
          <div class="flex items-center gap-2 flex-wrap">
            <h2 class="text-base font-bold text-ink">{{ authStore.user.full_name }}</h2>
            <AppBadge v-if="authStore.user.role === 'admin'" variant="violet" size="sm">
              <Shield class="w-3 h-3 mr-0.5" />
              {{ t('users.roleAdmin') }}
            </AppBadge>
            <AppBadge v-else variant="neutral" size="sm">
              <UserIcon class="w-3 h-3 mr-0.5" />
              {{ t('users.roleUser') }}
            </AppBadge>
            <AppBadge v-if="authStore.user.is_active" variant="ok" size="sm">
              <UserCheck class="w-3 h-3 mr-0.5" />
              {{ t('users.statusActive') }}
            </AppBadge>
          </div>
          <p class="text-xs text-ink-muted flex items-center gap-1.5 font-mono">
            <Mail class="w-3.5 h-3.5 text-ink-faint" />
            {{ authStore.user.email }}
          </p>
        </div>
      </div>


      <!-- Registration Date -->
      <div v-if="authStore.user.created_at" class="sm:text-right border-t sm:border-t-0 pt-3 sm:pt-0 border-border/60">
        <p class="text-[10px] font-bold uppercase tracking-wider text-ink-faint">{{ t('users.colCreatedAt') }}</p>
        <p class="text-xs font-semibold text-ink-muted mt-0.5 flex items-center sm:justify-end gap-1 font-mono">
          <CalendarIcon class="w-3.5 h-3.5 text-primary-400" />
          {{ formatDate(authStore.user.created_at) }}
        </p>
      </div>
    </div>

    <!-- 2-Column Settings Layout -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">

      <!-- 1. Personal Information Section -->
      <div class="bg-white border border-border rounded-2xl p-6 shadow-card flex flex-col justify-between space-y-6">
        <div class="space-y-4">
          <div class="flex items-center gap-2 pb-3 border-b border-border/60">
            <UserIcon class="w-4 h-4 text-primary-600 shrink-0" />
            <h3 class="text-sm font-bold text-ink">{{ t('profile.personalInfo') }}</h3>
          </div>

          <!-- Success / Error Alert -->
          <div v-if="profileSuccess" class="flex items-center gap-2 p-2.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-medium">
            <CheckCircle2 class="w-4 h-4 text-emerald-600 shrink-0" />
            <span>{{ profileSuccess }}</span>
          </div>
          <div v-if="profileError" class="flex items-center gap-2 p-2.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs font-medium">
            <AlertCircle class="w-4 h-4 text-rose-600 shrink-0" />
            <span>{{ profileError }}</span>
          </div>

          <form @submit.prevent="handleSaveProfile" id="profile-form" class="space-y-4">
            <AppInput
              v-model="fullName"
              :label="t('auth.fullName')"
              :placeholder="t('users.fullNamePlaceholder')"
              required
            />

            <AppInput
              v-model="email"
              type="email"
              :label="t('auth.email')"
              :placeholder="t('users.emailPlaceholder')"
              required
            />
          </form>
        </div>

        <div class="pt-4 border-t border-border/60 flex justify-end">
          <AppButton
            type="submit"
            form="profile-form"
            size="sm"
            :loading="profileSaving"
            class="w-full sm:w-auto"
          >
            {{ t('profile.saveChanges') }}
          </AppButton>
        </div>
      </div>

      <!-- 2. Security & Password Section -->
      <div class="bg-white border border-border rounded-2xl p-6 shadow-card flex flex-col justify-between space-y-6">
        <div class="space-y-4">
          <div class="flex items-center gap-2 pb-3 border-b border-border/60">
            <KeyRound class="w-4 h-4 text-primary-600 shrink-0" />
            <h3 class="text-sm font-bold text-ink">{{ t('profile.security') }}</h3>
          </div>

          <!-- Success / Error Alert -->
          <div v-if="passwordSuccess" class="flex items-center gap-2 p-2.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-medium">
            <CheckCircle2 class="w-4 h-4 text-emerald-600 shrink-0" />
            <span>{{ passwordSuccess }}</span>
          </div>
          <div v-if="passwordError" class="flex items-center gap-2 p-2.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs font-medium">
            <AlertCircle class="w-4 h-4 text-rose-600 shrink-0" />
            <span>{{ passwordError }}</span>
          </div>

          <form @submit.prevent="handleUpdatePassword" id="password-form" class="space-y-4">
            <AppInput
              v-model="newPassword"
              type="password"
              :label="t('profile.newPassword')"
              :placeholder="t('profile.newPasswordPlaceholder')"
              required
            />

            <AppInput
              v-model="confirmPassword"
              type="password"
              :label="t('profile.confirmPassword')"
              :placeholder="t('profile.confirmPasswordPlaceholder')"
              required
            />
          </form>
        </div>

        <div class="pt-4 border-t border-border/60 flex justify-end">
          <AppButton
            type="submit"
            form="password-form"
            size="sm"
            variant="outline"
            :loading="passwordSaving"
            class="w-full sm:w-auto hover:border-primary-400"
          >
            {{ t('profile.updatePassword') }}
          </AppButton>
        </div>
      </div>

    </div>

  </div>
</template>
