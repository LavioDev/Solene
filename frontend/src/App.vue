<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/authStore'
import AppPageLoader from '@/components/ui/AppPageLoader.vue'

const authStore = useAuthStore()

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
