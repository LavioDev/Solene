<script setup lang="ts">
import { useRoute } from 'vue-router'
import { useTabStore } from '@/stores/tabStore'
import AppSidebar from '@/components/layout/AppSidebar.vue'
import AppNavbar from '@/components/layout/AppNavbar.vue'
import AppTabBar from '@/components/layout/AppTabBar.vue'

const route = useRoute()
const tabStore = useTabStore()
</script>

<template>
  <div class="flex h-screen bg-surface-subtle overflow-hidden">
    <AppSidebar v-if="!tabStore.isContentFullscreen" />
    <div class="flex flex-col flex-1 min-w-0 overflow-hidden">
      <AppNavbar v-if="!tabStore.isContentFullscreen" />
      <!-- Vben-style Multiple Tabs Bar -->
      <AppTabBar />
      <main class="flex-1 overflow-y-auto relative">
        <div v-if="tabStore.reloadFlag">
          <div v-if="route.name === 'Home'" class="h-full w-full">
            <router-view />
          </div>
          <div v-else class="max-w-7xl mx-auto px-6 py-6 lg:px-8 lg:py-8">
            <router-view />
          </div>
        </div>
      </main>
    </div>
  </div>
</template>
