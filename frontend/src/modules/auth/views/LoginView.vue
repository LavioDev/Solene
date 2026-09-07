<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/authStore'
import { ArrowRight, Sparkles } from 'lucide-vue-next'
import AppButton from '@/components/ui/AppButton.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppCard from '@/components/ui/AppCard.vue'
import AppLangSwitcher from '@/components/ui/AppLangSwitcher.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const { t } = useI18n()

const isRegister = ref(false)
const email = ref('')
const password = ref('')
const fullName = ref('')
const loading = ref(false)
const errorMessage = ref('')

async function handleSubmit() {
  errorMessage.value = ''
  loading.value = true
  try {
    if (isRegister.value) {
      await authStore.register({ email: email.value, password: password.value, full_name: fullName.value || 'User' })
    } else {
      await authStore.login({ email: email.value, password: password.value })
    }
    const redirectPath = typeof route.query.redirect === 'string' ? route.query.redirect : '/'
    router.push(redirectPath)
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || t('auth.authFailed')
  } finally {
    loading.value = false
  }
}

</script>

<template>
  <div class="min-h-screen bg-surface-subtle flex flex-col items-center justify-center p-6 relative">

    <!-- Top Right Language Switcher on Login Page -->
    <div class="absolute top-6 right-6">
      <AppLangSwitcher />
    </div>

    <div class="w-full max-w-sm space-y-8">

      <!-- Wordmark -->
      <div class="text-center">
        <h1
          class="tracking-tight select-none inline-flex items-center justify-center gap-1.5"
          style="
            font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
            font-size: 2rem;
            font-weight: 800;
            letter-spacing: -0.04em;
            color: #111111;
          "
        >
          <span>Solène</span>

          <Sparkles class="w-6 h-6 text-primary-600 animate-pulse ml-1" />
        </h1>
      </div>

      <!-- Card -->
      <AppCard>
        <form @submit.prevent="handleSubmit" class="space-y-4">
          <div v-if="errorMessage" class="px-3.5 py-2.5 bg-err-bg border border-err-border rounded-lg text-xs font-medium text-err-text">
            {{ errorMessage }}
          </div>

          <AppInput v-if="isRegister" v-model="fullName" :label="t('auth.fullName')" :placeholder="t('auth.fullName') + '...'" />
          <AppInput v-model="email" type="email" :label="t('auth.email')" :placeholder="t('auth.email') + '...'" required />
          <AppInput v-model="password" type="password" :label="t('auth.password')" :placeholder="t('auth.password') + '...'" required />

          <AppButton type="submit" :loading="loading" size="lg" class="w-full">
            {{ isRegister ? t('auth.register') : t('auth.signIn') }}
            <ArrowRight class="w-4 h-4" />
          </AppButton>
        </form>

        <div class="mt-5 pt-4 border-t border-border text-center">
          <button
            type="button"
            class="text-xs font-medium text-ink-muted hover:text-primary-700 transition-colors"
            @click="isRegister = !isRegister; errorMessage = ''"
          >
            {{ isRegister ? t('auth.alreadyHaveAccount') : t('auth.dontHaveAccount') }}
          </button>
        </div>
      </AppCard>
    </div>
  </div>
</template>
