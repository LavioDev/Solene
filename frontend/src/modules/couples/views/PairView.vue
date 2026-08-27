<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/authStore'
import { coupleService } from '@/services/coupleService'
import type { CoupleInvitationInfo } from '@/types/couple'
import {
  Heart,
  Sparkles,
  ArrowRight,
  AlertCircle,
  CheckCircle2,
  Smile,
  Copy,
  Check,
  LogIn,
  KeyRound,
} from 'lucide-vue-next'

import AppButton from '@/components/ui/AppButton.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppLangSwitcher from '@/components/ui/AppLangSwitcher.vue'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const authStore = useAuthStore()

// State
const inputCode = ref('')
const loadingInfo = ref(false)
const invitationInfo = ref<CoupleInvitationInfo | null>(null)
const errorReason = ref<string | null>(null)

// Accept form state
const formStartDate = ref(new Date().toISOString().split('T')[0])
const formNickname = ref('')
const submitting = ref(false)
const acceptError = ref<string | null>(null)
const pairSuccess = ref(false)
const copied = ref(false)

const queryCode = computed(() => {
  const codeParam = route.query.code
  return typeof codeParam === 'string' ? codeParam.trim().toUpperCase() : ''
})

const isSelfInvitation = computed(() => {
  if (!authStore.isAuthenticated || !authStore.user || !invitationInfo.value?.inviter) {
    return false
  }
  return authStore.user.id === invitationInfo.value.inviter.id
})

async function checkCode(codeToCheck: string) {
  if (!codeToCheck) {
    invitationInfo.value = null
    return
  }
  loadingInfo.value = true
  errorReason.value = null
  acceptError.value = null
  try {
    const res = await coupleService.getInvitationInfo(codeToCheck)
    invitationInfo.value = res
    if (!res.is_valid) {
      errorReason.value = res.error_reason || t('couples.pair.invalidCode')
    }
  } catch (err: any) {
    invitationInfo.value = null
    errorReason.value = err.response?.data?.detail || t('couples.pair.checkError')
  } finally {
    loadingInfo.value = false
  }
}

async function handleManualSubmit() {
  if (!inputCode.value.trim()) return
  const cleanCode = inputCode.value.trim().toUpperCase()
  router.replace({ query: { code: cleanCode } })
  await checkCode(cleanCode)
}

async function handleAcceptPairing() {
  if (!invitationInfo.value?.code) return
  submitting.value = true
  acceptError.value = null
  try {
    await coupleService.acceptInvitation({
      code: invitationInfo.value.code,
      start_date: formStartDate.value || new Date().toISOString().split('T')[0],
      nickname: formNickname.value.trim() || undefined,
    })
    pairSuccess.value = true
    setTimeout(() => {
      router.push('/')
    }, 2000)
  } catch (err: any) {
    acceptError.value = err.response?.data?.detail || t('couples.pair.acceptError')
  } finally {
    submitting.value = false
  }
}

function handleLoginRedirect() {
  const redirectUrl = route.fullPath
  router.push({
    path: '/login',
    query: { redirect: redirectUrl },
  })
}

async function copyCurrentLink() {
  try {
    const url = typeof window !== 'undefined' ? window.location.href : ''
    if (url) {
      await navigator.clipboard.writeText(url)
      copied.value = true
      setTimeout(() => (copied.value = false), 2000)
    }
  } catch (e) {
    console.error(e)
  }
}


function getUserInitials(name?: string, email?: string): string {
  if (name) {
    const parts = name.trim().split(/\s+/)
    if (parts.length >= 2) {
      return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
    }
    return name.slice(0, 2).toUpperCase()
  }
  return email ? email.slice(0, 2).toUpperCase() : 'U'
}

watch(
  queryCode,
  (newCode) => {
    if (newCode) {
      inputCode.value = newCode
      checkCode(newCode)
    }
  },
  { immediate: true },
)

onMounted(() => {
  if (queryCode.value) {
    inputCode.value = queryCode.value
    checkCode(queryCode.value)
  }
})
</script>

<template>
  <div class="min-h-screen bg-[#fafafa] flex flex-col justify-between p-4 sm:p-8 select-none">
    <!-- Top Header -->
    <header class="w-full max-w-4xl mx-auto flex items-center justify-between py-2">
      <div
        class="flex items-center gap-2 cursor-pointer transition-opacity hover:opacity-80"
        @click="router.push('/')"
      >
        <div class="w-8 h-8 rounded-xl bg-violet-600 flex items-center justify-center text-white shadow-sm shadow-violet-500/30">
          <Heart class="w-4 h-4 fill-white" />
        </div>
        <span class="text-base font-bold text-ink tracking-tight font-serif">Solène</span>
      </div>

      <div class="flex items-center gap-3">
        <AppLangSwitcher />
      </div>
    </header>

    <!-- Main Container -->
    <main class="w-full max-w-lg mx-auto my-auto py-8">
      <div class="bg-white rounded-3xl border border-violet-100/80 shadow-card p-6 sm:p-8 space-y-6 relative overflow-hidden">
        <!-- Background Ambient Glow -->
        <div class="absolute -top-24 -right-24 w-48 h-48 rounded-full bg-violet-200/30 blur-3xl pointer-events-none"></div>
        <div class="absolute -bottom-24 -left-24 w-48 h-48 rounded-full bg-pink-200/30 blur-3xl pointer-events-none"></div>

        <!-- 1. State: Success Animation -->
        <div v-if="pairSuccess" class="py-8 text-center space-y-4">
          <div class="w-16 h-16 mx-auto rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center animate-bounce shadow-sm">
            <CheckCircle2 class="w-9 h-9" />
          </div>
          <div class="space-y-1">
            <h2 class="text-xl font-bold text-ink">
              {{ t('couples.pair.successTitle') }}
            </h2>
            <p class="text-xs text-ink-muted">
              {{ t('couples.pair.successDesc') }}
            </p>
          </div>
        </div>

        <!-- 2. State: Loading Code Info -->
        <div v-else-if="loadingInfo" class="py-12 flex flex-col items-center justify-center gap-3">
          <div class="w-9 h-9 rounded-full border-3 border-violet-600 border-t-transparent animate-spin"></div>
          <p class="text-xs font-semibold text-ink-muted">
            {{ t('couples.pair.verifying') }}
          </p>
        </div>

        <!-- 3. State: Code Valid -> Prompt to Accept (or Login) -->
        <div v-else-if="invitationInfo && invitationInfo.is_valid" class="space-y-6">
          <!-- Inviter Avatar & Match Preview -->
          <div class="text-center space-y-3">
            <div class="relative inline-flex items-center justify-center">
              <!-- Inviter Avatar (Left) -->
              <div class="relative w-16 h-16 rounded-full bg-violet-600 text-white font-bold text-base flex items-center justify-center border-4 border-white shadow-md z-10">
                <img
                  v-if="invitationInfo.inviter?.avatar_url"
                  :src="invitationInfo.inviter.avatar_url"
                  :alt="invitationInfo.inviter.full_name"
                  class="w-full h-full rounded-full object-cover"
                />
                <span v-else>{{ getUserInitials(invitationInfo.inviter?.full_name, invitationInfo.inviter?.email) }}</span>
              </div>

              <!-- Intersecting Heart Badge (Center) -->
              <div class="w-8 h-8 rounded-full bg-white text-rose-500 flex items-center justify-center shadow-md z-20 -mx-3 border border-rose-100">
                <Heart class="w-4 h-4 fill-rose-500 text-rose-500 animate-pulse" />
              </div>

              <!-- Current User / Guest Avatar (Right) -->
              <div class="relative w-16 h-16 rounded-full bg-pink-500 text-white font-bold text-base flex items-center justify-center border-4 border-white shadow-md z-10">
                <img
                  v-if="authStore.user?.avatar_url"
                  :src="authStore.user.avatar_url"
                  :alt="authStore.user.full_name"
                  class="w-full h-full rounded-full object-cover"
                />
                <span v-else-if="authStore.isAuthenticated">
                  {{ getUserInitials(authStore.user?.full_name, authStore.user?.email) }}
                </span>
                <Smile v-else class="w-7 h-7 text-white" />
              </div>
            </div>

            <div class="space-y-1">
              <span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-violet-100 text-violet-700">
                <Sparkles class="w-3 h-3" />
                {{ t('couples.pair.inviteBadge') }}
              </span>
              <h2 class="text-lg font-bold text-ink">
                {{ invitationInfo.inviter?.full_name }}
              </h2>
              <p class="text-xs text-ink-muted max-w-xs mx-auto">
                {{ t('couples.pair.inviteText', { name: invitationInfo.inviter?.full_name }) }}
              </p>
            </div>
          </div>

          <!-- Error Alert if any during submit -->
          <div
            v-if="acceptError"
            class="flex items-center gap-2 p-3 rounded-xl bg-red-50 text-err-text text-xs border border-red-100"
          >
            <AlertCircle class="w-4 h-4 shrink-0" />
            <span>{{ acceptError }}</span>
          </div>

          <!-- Case A: Self Invitation -->
          <div v-if="isSelfInvitation" class="p-4 rounded-2xl bg-surface-subtle border border-border text-center space-y-3">
            <p class="text-xs text-ink-muted">
              {{ t('couples.pair.selfInviteNotice') }}
            </p>
            <div class="flex items-center justify-center gap-2">
              <span class="text-sm font-mono font-bold text-violet-700 bg-white px-3 py-1.5 rounded-lg border border-border">
                {{ invitationInfo.code }}
              </span>
              <AppButton size="sm" variant="outline" @click="copyCurrentLink">
                <Check v-if="copied" class="w-3.5 h-3.5 text-emerald-600 mr-1" />
                <Copy v-else class="w-3.5 h-3.5 mr-1" />
                <span>{{ copied ? t('common.copied') : t('couples.invite.copyLink') }}</span>
              </AppButton>

            </div>
            <AppButton variant="secondary" class="w-full mt-2" @click="router.push('/')">
              {{ t('couples.pair.backToHome') }}
            </AppButton>
          </div>

          <!-- Case B: Guest User (Needs Login / Register) -->
          <div v-else-if="!authStore.isAuthenticated" class="space-y-4">
            <div class="p-4 rounded-2xl bg-violet-50/60 border border-violet-100 text-xs text-ink-muted leading-relaxed">
              {{ t('couples.pair.loginPrompt') }}
            </div>
            <AppButton
              variant="primary"
              size="lg"
              class="w-full"
              @click="handleLoginRedirect"
            >
              <LogIn class="w-4 h-4 mr-2" />
              {{ t('couples.pair.loginToPairBtn') }}
            </AppButton>
          </div>

          <!-- Case C: Authenticated Recipient -> Form to Pair -->
          <form v-else class="space-y-4" @submit.prevent="handleAcceptPairing">
            <AppInput
              v-model="formStartDate"
              type="date"
              :label="t('couples.pair.startDateLabel')"
              required
            />

            <AppInput
              v-model="formNickname"
              type="text"
              :label="t('couples.pair.nicknameLabel')"
              :placeholder="t('couples.pair.nicknamePlaceholder')"
            />

            <div class="pt-2">
              <AppButton
                type="submit"
                variant="primary"
                size="lg"
                class="w-full"
                :loading="submitting"
              >
                <Heart class="w-4 h-4 mr-1.5 fill-current" />
                {{ t('couples.pair.acceptPairBtn') }}
              </AppButton>
            </div>
          </form>
        </div>

        <!-- 4. State: Invalid Code / Error State -->
        <div v-else-if="errorReason || (invitationInfo && !invitationInfo.is_valid)" class="space-y-6">
          <div class="text-center space-y-2">
            <div class="w-12 h-12 mx-auto rounded-2xl bg-amber-100 text-amber-600 flex items-center justify-center">
              <AlertCircle class="w-6 h-6" />
            </div>
            <h3 class="text-base font-bold text-ink">
              {{ t('couples.pair.invalidTitle') }}
            </h3>
            <p class="text-xs text-ink-muted max-w-sm mx-auto">
              {{ errorReason || t('couples.pair.invalidDesc') }}
            </p>
          </div>

          <!-- Manual Code Form -->
          <form class="space-y-3 pt-2" @submit.prevent="handleManualSubmit">
            <AppInput
              v-model="inputCode"
              :label="t('couples.pair.enterAnotherCode')"
              placeholder="SL-XXXXXX"
              required
            />
            <div class="flex items-center gap-2">
              <AppButton
                type="button"
                variant="outline"
                class="w-1/2"
                @click="router.push('/')"
              >
                {{ t('couples.pair.backToHome') }}
              </AppButton>
              <AppButton
                type="submit"
                variant="primary"
                class="w-1/2"
                :loading="loadingInfo"
              >
                <ArrowRight class="w-4 h-4 mr-1" />
                {{ t('couples.pair.verifyCodeBtn') }}
              </AppButton>
            </div>
          </form>
        </div>

        <!-- 5. State: No Code in URL -> Prompt to enter code -->
        <div v-else class="space-y-6">
          <div class="text-center space-y-2">
            <div class="w-12 h-12 mx-auto rounded-2xl bg-violet-100 text-violet-600 flex items-center justify-center">
              <KeyRound class="w-6 h-6" />
            </div>
            <h3 class="text-base font-bold text-ink">
              {{ t('couples.pair.enterCodeTitle') }}
            </h3>
            <p class="text-xs text-ink-muted max-w-sm mx-auto">
              {{ t('couples.pair.enterCodeSubtitle') }}
            </p>
          </div>

          <form class="space-y-4" @submit.prevent="handleManualSubmit">
            <AppInput
              v-model="inputCode"
              :label="t('couples.pair.codeLabel')"
              placeholder="SL-XXXXXX"
              required
            />
            <AppButton
              type="submit"
              variant="primary"
              size="lg"
              class="w-full"
              :loading="loadingInfo"
            >
              <Sparkles class="w-4 h-4 mr-1.5" />
              {{ t('couples.pair.checkCodeBtn') }}
            </AppButton>
          </form>
        </div>
      </div>
    </main>

    <!-- Footer -->
    <footer class="w-full max-w-4xl mx-auto text-center py-4 text-[11px] text-ink-faint">
      &copy; {{ new Date().getFullYear() }} Solène. All rights reserved.
    </footer>
  </div>
</template>
