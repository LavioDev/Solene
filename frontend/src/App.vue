<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/authStore'

const authStore = useAuthStore()

onMounted(async () => {
  if (authStore.isInitializing) {
    await authStore.checkAuth()
  }
})
</script>

<template>
  <div v-if="authStore.isInitializing" class="min-h-screen bg-pastel-bg flex items-center justify-center">
    <div class="flex items-center gap-3 text-xs text-slate-500 font-medium">
      <div class="w-4 h-4 border-2 border-slate-700 border-t-transparent rounded-full animate-spin"></div>
      <span>Initializing Solene Cockpit...</span>
    </div>
  </div>
  <router-view v-else />
</template>
