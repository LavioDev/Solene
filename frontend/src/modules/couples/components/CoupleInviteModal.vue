<script setup lang="ts">
import { ref, computed, watch, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { coupleService } from '@/services/coupleService'
import type { CoupleInvitation } from '@/types/couple'
import {
  Heart,
  Copy,
  Check,
  Share2,
  Sparkles,
  RefreshCw,
  Clock,
  Trash2,
  AlertCircle,
  Link as LinkIcon,
} from 'lucide-vue-next'
import AppModal from '@/components/ui/AppModal.vue'
import AppButton from '@/components/ui/AppButton.vue'


interface Props {
  show: boolean
}

const props = withDefaults(defineProps<Props>(), {
  show: false,
})

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'paired'): void
}>()

const { t } = useI18n()

// State
const loading = ref(false)
const actionLoading = ref(false)
const errorMessage = ref<string | null>(null)
const invitation = ref<CoupleInvitation | null>(null)
const copiedCode = ref(false)
const copiedLink = ref(false)
const countdownText = ref('')
let timerInterval: ReturnType<typeof setInterval> | null = null

const fullInviteUrl = computed(() => {
  if (!invitation.value?.code) return ''
  const origin = window.location.origin
  return `${origin}/pair?code=${invitation.value.code}`
})

const canShare = computed(() => {
  return typeof navigator !== 'undefined' && !!navigator.share
})

async function fetchOrCreateInvitation() {
  loading.value = true
  errorMessage.value = null
  try {
    const current = await coupleService.getCurrentInvitation()
    if (current && current.status === 'pending') {
      invitation.value = current
    } else {
      invitation.value = await coupleService.createInvitation()
    }
    startCountdown()
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || t('couples.invite.createError')
  } finally {
    loading.value = false
  }
}

async function handleRegenerate() {
  actionLoading.value = true
  errorMessage.value = null
  try {
    invitation.value = await coupleService.createInvitation()
    startCountdown()
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || t('couples.invite.createError')
  } finally {
    actionLoading.value = false
  }
}

async function handleRevoke() {
  actionLoading.value = true
  errorMessage.value = null
  try {
    await coupleService.revokeCurrentInvitation()
    invitation.value = null
    stopCountdown()
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || t('couples.invite.revokeError')
  } finally {
    actionLoading.value = false
  }
}

async function copyToClipboard(text: string, type: 'code' | 'link') {
  try {
    await navigator.clipboard.writeText(text)
    if (type === 'code') {
      copiedCode.value = true
      setTimeout(() => (copiedCode.value = false), 2000)
    } else {
      copiedLink.value = true
      setTimeout(() => (copiedLink.value = false), 2000)
    }
  } catch (err) {
    console.error('Failed to copy', err)
  }
}

async function shareInvite() {
  if (!fullInviteUrl.value || !canShare.value) return
  try {
    await navigator.share({
      title: t('couples.invite.shareTitle'),
      text: t('couples.invite.shareMessage', { code: invitation.value?.code }),
      url: fullInviteUrl.value,
    })
  } catch (err: any) {
    if (err.name !== 'AbortError') {
      console.error('Error sharing:', err)
    }
  }
}

function startCountdown() {
  stopCountdown()
  updateCountdown()
  timerInterval = setInterval(updateCountdown, 1000)
}

function stopCountdown() {
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
}

function updateCountdown() {
  if (!invitation.value?.expires_at) {
    countdownText.value = ''
    return
  }
  const expiryTime = new Date(invitation.value.expires_at).getTime()
  const now = new Date().getTime()
  const diff = expiryTime - now

  if (diff <= 0) {
    countdownText.value = t('couples.invite.expired')
    stopCountdown()
    return
  }

  const hours = Math.floor(diff / (1000 * 60 * 60))
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
  const seconds = Math.floor((diff % (1000 * 60)) / 1000)

  countdownText.value = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
}

watch(
  () => props.show,
  (isShown) => {
    if (isShown) {
      fetchOrCreateInvitation()
    } else {
      stopCountdown()
    }
  },
  { immediate: true },
)

onUnmounted(() => {
  stopCountdown()
})
</script>

<template>
  <AppModal
    :show="show"
    :title="t('couples.invite.modalTitle')"
    width="md"
    @close="emit('close')"
  >
    <div class="p-6 space-y-6 select-none">
      <!-- Header with Cute Icon -->
      <div class="text-center space-y-2">
        <div class="w-14 h-14 mx-auto rounded-2xl bg-violet-100 text-violet-600 flex items-center justify-center shadow-xs">
          <Heart class="w-7 h-7 fill-violet-500 text-violet-600 animate-pulse" />
        </div>
        <h3 class="text-lg font-bold text-ink">
          {{ t('couples.invite.connectTitle') }}
        </h3>
        <p class="text-xs text-ink-muted max-w-sm mx-auto">
          {{ t('couples.invite.connectSubtitle') }}
        </p>
      </div>

      <!-- Error Alert -->
      <div
        v-if="errorMessage"
        class="flex items-center gap-2 p-3 rounded-xl bg-red-50 text-err-text text-xs border border-red-100"
      >
        <AlertCircle class="w-4 h-4 shrink-0" />
        <span>{{ errorMessage }}</span>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="py-10 flex flex-col items-center justify-center gap-3">
        <div class="w-8 h-8 rounded-full border-2 border-violet-600 border-t-transparent animate-spin"></div>
        <p class="text-xs text-ink-muted">{{ t('couples.invite.generating') }}</p>
      </div>

      <!-- Active Invitation Content -->
      <div v-else-if="invitation" class="space-y-4">
        <!-- 1. Highlighted Big Pairing Code Box -->
        <div class="p-4 rounded-2xl bg-surface-subtle/80 border border-violet-100 flex flex-col items-center justify-center gap-2 text-center relative overflow-hidden group">
          <span class="text-[11px] font-semibold text-ink-muted uppercase tracking-wider">
            {{ t('couples.invite.codeLabel') }}
          </span>
          <div class="text-2xl font-black text-violet-700 tracking-widest font-mono">
            {{ invitation.code }}
          </div>

          <div class="flex items-center gap-2 mt-1">
            <AppButton
              size="sm"
              variant="secondary"
              @click="copyToClipboard(invitation.code, 'code')"
            >
              <Check v-if="copiedCode" class="w-3.5 h-3.5 text-emerald-600 mr-1" />
              <Copy v-else class="w-3.5 h-3.5 mr-1" />
              <span>{{ copiedCode ? t('common.copied') : t('couples.invite.copyCode') }}</span>
            </AppButton>

            <AppButton
              v-if="canShare"
              size="sm"
              variant="primary"
              @click="shareInvite"
            >
              <Share2 class="w-3.5 h-3.5 mr-1" />
              <span>{{ t('couples.invite.shareLink') }}</span>
            </AppButton>
          </div>
        </div>

        <!-- 2. Direct Invite URL Box -->
        <div class="space-y-1.5">
          <label class="text-xs font-semibold text-ink-muted flex items-center justify-between">
            <span class="flex items-center gap-1">
              <LinkIcon class="w-3.5 h-3.5 text-violet-500" />
              {{ t('couples.invite.directUrlLabel') }}
            </span>
            <span v-if="countdownText" class="text-[11px] font-mono text-violet-600 flex items-center gap-1">
              <Clock class="w-3 h-3" />
              {{ countdownText }}
            </span>
          </label>

          <div class="flex items-center gap-2">
            <div class="flex-1 px-3 py-2 text-xs font-mono bg-surface rounded-xl border border-border text-ink-muted truncate">
              {{ fullInviteUrl }}
            </div>
            <AppButton
              size="sm"
              variant="outline"
              @click="copyToClipboard(fullInviteUrl, 'link')"
            >
              <Check v-if="copiedLink" class="w-3.5 h-3.5 text-emerald-600 mr-1" />
              <Copy v-else class="w-3.5 h-3.5 mr-1" />
              <span>{{ copiedLink ? t('common.copied') : t('common.copy') }}</span>
            </AppButton>
          </div>
        </div>

        <!-- 3. Helper Instructions -->
        <div class="p-3.5 rounded-xl bg-violet-50/50 border border-violet-100/60 text-xs text-ink-muted space-y-1.5">
          <div class="font-semibold text-ink flex items-center gap-1.5">
            <Sparkles class="w-3.5 h-3.5 text-violet-600" />
            <span>{{ t('couples.invite.guideTitle') }}</span>
          </div>
          <ol class="list-decimal list-inside space-y-0.5 text-[11px] leading-relaxed text-ink-muted pl-1">
            <li>{{ t('couples.invite.step1') }}</li>
            <li>{{ t('couples.invite.step2') }}</li>
            <li>{{ t('couples.invite.step3') }}</li>
          </ol>
        </div>

        <!-- 4. Action Controls (Regenerate / Revoke) -->
        <div class="pt-2 flex items-center justify-between border-t border-border/60">
          <button
            type="button"
            class="text-xs text-ink-muted hover:text-err-text flex items-center gap-1 transition-colors cursor-pointer"
            :disabled="actionLoading"
            @click="handleRevoke"
          >
            <Trash2 class="w-3.5 h-3.5" />
            <span>{{ t('couples.invite.revokeBtn') }}</span>
          </button>

          <button
            type="button"
            class="text-xs text-violet-600 hover:text-violet-700 font-semibold flex items-center gap-1 transition-colors cursor-pointer"
            :disabled="actionLoading"
            @click="handleRegenerate"
          >
            <RefreshCw class="w-3.5 h-3.5" :class="{ 'animate-spin': actionLoading }" />
            <span>{{ t('couples.invite.regenerateBtn') }}</span>
          </button>
        </div>
      </div>

      <!-- Empty State (if revoked) -->
      <div v-else class="text-center py-6 space-y-4">
        <p class="text-xs text-ink-muted">{{ t('couples.invite.noActiveCode') }}</p>
        <AppButton variant="primary" :loading="actionLoading" @click="handleRegenerate">
          <Sparkles class="w-4 h-4 mr-1.5" />
          {{ t('couples.invite.createBtn') }}
        </AppButton>
      </div>
    </div>
  </AppModal>
</template>
