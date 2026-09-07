<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/authStore'
import { useThemeStore } from '@/stores/themeStore'
import AppPageLoader from '@/components/ui/AppPageLoader.vue'

const authStore = useAuthStore()
const themeStore = useThemeStore()

// Initialize theme immediately to prevent FOUC
themeStore.initTheme()

onMounted(async () => {
  if (authStore.isInitializing) {
    await authStore.checkAuth()
  }
})
</script>

<template>
  <AppPageLoader v-if="authStore.isInitializing" :show="true" :fullScreen="true" />
  <router-view v-else />
</template>
