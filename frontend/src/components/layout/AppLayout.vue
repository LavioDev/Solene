<script setup lang="ts">
import { useRoute } from 'vue-router'
import AppSidebar from '@/components/layout/AppSidebar.vue'
import AppNavbar from '@/components/layout/AppNavbar.vue'

const route = useRoute()
</script>

<template>
  <div class="flex h-screen bg-surface-subtle overflow-hidden">
    <AppSidebar />
    <div class="flex flex-col flex-1 min-w-0 overflow-hidden">
      <AppNavbar />
      <main class="flex-1 overflow-y-auto relative">
        <div v-if="route.name === 'Home'" class="h-full w-full">
          <router-view />
        </div>
        <div v-else class="max-w-7xl mx-auto px-8 py-8">
          <router-view />
        </div>
      </main>
    </div>
  </div>
</template>
