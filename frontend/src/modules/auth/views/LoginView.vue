<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/authStore'
import { useThemeStore } from '@/stores/themeStore'
import { ArrowRight, Sparkles } from 'lucide-vue-next'
import AppButton from '@/components/ui/AppButton.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppLangSwitcher from '@/components/ui/AppLangSwitcher.vue'
import AppThemeSwitcher from '@/components/ui/AppThemeSwitcher.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const themeStore = useThemeStore()
const { t } = useI18n()

const email = ref('')
const password = ref('')
const loading = ref(false)
const errorMessage = ref('')

async function handleSubmit() {
  errorMessage.value = ''
  loading.value = true
  try {
    await authStore.login({ email: email.value, password: password.value })
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
  <div
    class="min-h-screen w-full flex flex-col items-center justify-center p-4 sm:p-6 relative overflow-hidden select-none transition-colors duration-300"
    :class="`theme-${themeStore.activeThemeId}-content-bg`"
  >
    <!-- Ambient glowing pastel orbs for glass reflection -->
    <div class="absolute -top-32 -left-32 w-80 sm:w-96 h-80 sm:h-96 bg-primary-400/25 rounded-full blur-3xl pointer-events-none transform-gpu animate-pulse duration-1000" />
    <div class="absolute -bottom-32 -right-32 w-80 sm:w-96 h-80 sm:h-96 bg-primary-300/20 rounded-full blur-3xl pointer-events-none transform-gpu" />
    <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-white/40 rounded-full blur-2xl pointer-events-none" />

    <!-- Top Right Controls (Theme & Language Switchers in Glass Pill) -->
    <div class="absolute top-5 right-5 sm:top-6 sm:right-6 z-20 flex items-center gap-1.5 p-1.5 rounded-2xl bg-white/70 backdrop-blur-md border border-white/80 shadow-xs">
      <AppThemeSwitcher />
      <div class="w-px h-4 bg-border/60 mx-0.5" />
      <AppLangSwitcher />
    </div>

    <!-- Login Glassmorphic Container -->
    <div class="w-full max-w-[400px] relative z-10 space-y-6 sm:space-y-7">
      <!-- Brand Header -->
      <div class="text-center space-y-2">
        <div class="inline-flex items-center justify-center gap-2">
          <h1
            class="tracking-tight select-none inline-flex items-center justify-center gap-1.5"
            style="
              font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
              font-size: 2.25rem;
              font-weight: 800;
              letter-spacing: -0.04em;
              color: #111111;
            "
          >
            <span>Solène</span>
            <Sparkles class="w-6 h-6 text-primary-600 animate-pulse" />
          </h1>
        </div>
      </div>

      <!-- Glassmorphism Form Card -->
      <div class="bg-white/75 backdrop-blur-xl border border-white/90 shadow-2xl shadow-primary-500/10 rounded-3xl p-6 sm:p-8 transition-all duration-300">
        <form @submit.prevent="handleSubmit" class="space-y-4">
          <!-- Error Alert -->
          <div
            v-if="errorMessage"
            class="px-3.5 py-2.5 bg-err-bg/90 backdrop-blur-xs border border-err-border rounded-xl text-xs font-semibold text-err-text animate-fade-in"
          >
            {{ errorMessage }}
          </div>

          <AppInput
            v-model="email"
            type="email"
            :label="t('auth.email')"
            :placeholder="t('auth.email') + '...'"
            required
          />
          <AppInput
            v-model="password"
            type="password"
            :label="t('auth.password')"
            :placeholder="t('auth.password') + '...'"
            required
          />

          <!-- Submit Button -->
          <AppButton
            type="submit"
            :loading="loading"
            variant="primary"
            size="lg"
            class="w-full h-11 text-sm font-bold shadow-md shadow-primary-500/25 active:scale-98 transition-all mt-2"
          >
            <span>{{ t('auth.signIn') }}</span>
            <ArrowRight class="w-4 h-4 ml-1" />
          </AppButton>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Base Mobile Backgrounds */
.theme-yellow-content-bg  { background-color: #fffff7; background-image: url('@/img/bg/bg_yellow.jpg'); }
.theme-rose-content-bg    { background-color: #fff6f8; background-image: url('@/img/bg/bg_rose.jpg'); }
.theme-violet-content-bg  { background-color: #faf7ff; background-image: url('@/img/bg/bg_violet.jpg'); }
.theme-blue-content-bg    { background-color: #f4f8ff; background-image: url('@/img/bg/bg_blue.jpg'); }
.theme-emerald-content-bg { background-color: #f4fdf8; background-image: url('@/img/bg/bg_emerald.jpg'); }
.theme-cyan-content-bg    { background-color: #f2fdff; background-image: url('@/img/bg/bg_cyan.jpg'); }
.theme-pink-content-bg    { background-color: #fff5fb; background-image: url('@/img/bg/bg_pink.jpg'); }
.theme-amber-content-bg   { background-color: #fffbf2; background-image: url('@/img/bg/bg_amber.jpg'); }
.theme-indigo-content-bg  { background-color: #f7f8ff; background-image: url('@/img/bg/bg_indigo.jpg'); }

[class*="theme-"][class*="-content-bg"] {
  background-size: cover;
  background-position: center top;
  background-repeat: no-repeat;
}

/* Desktop Tiled Backgrounds */
@media (min-width: 1024px) {
  .theme-yellow-content-bg  { background-image: url('@/img/bg/bg_yellow-desktop.jpg'); }
  .theme-rose-content-bg    { background-image: url('@/img/bg/bg_rose-desktop.jpg'); }
  .theme-violet-content-bg  { background-image: url('@/img/bg/bg_violet-desktop.jpg'); }
  .theme-blue-content-bg    { background-image: url('@/img/bg/bg_blue-desktop.jpg'); }
  .theme-emerald-content-bg { background-image: url('@/img/bg/bg_emerald-desktop.jpg'); }
  .theme-cyan-content-bg    { background-image: url('@/img/bg/bg_cyan-desktop.jpg'); }
  .theme-pink-content-bg    { background-image: url('@/img/bg/bg_pink-desktop.jpg'); }
  .theme-amber-content-bg   { background-image: url('@/img/bg/bg_amber-desktop.jpg'); }
  .theme-indigo-content-bg  { background-image: url('@/img/bg/bg_indigo-desktop.jpg'); }

  [class*="theme-"][class*="-content-bg"] {
    background-size: 1920px auto;
    background-repeat: repeat;
    background-position: center top;
  }
}
</style>
