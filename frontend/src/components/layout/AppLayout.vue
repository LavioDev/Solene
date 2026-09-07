<script setup lang="ts">
import { useRoute } from 'vue-router'
import { useTabStore } from '@/stores/tabStore'
import { useUiStore } from '@/stores/uiStore'
import AppSidebar from '@/components/layout/AppSidebar.vue'
import AppNavbar from '@/components/layout/AppNavbar.vue'
import AppTabBar from '@/components/layout/AppTabBar.vue'
import AppPageLoader from '@/components/ui/AppPageLoader.vue'

const route = useRoute()
const tabStore = useTabStore()
const uiStore = useUiStore()
</script>

<template>
  <div class="flex h-screen bg-surface-subtle overflow-hidden relative">
    <!-- Backdrop overlay for mobile drawer -->
    <transition
      enter-active-class="transition-opacity duration-300 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-opacity duration-200 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="uiStore.isMobileSidebarOpen && !tabStore.isContentFullscreen"
        class="fixed inset-0 bg-black/40 backdrop-blur-xs z-40 lg:hidden"
        @click="uiStore.closeMobileSidebar"
      />
    </transition>

    <AppSidebar v-if="!tabStore.isContentFullscreen" />
    <div class="flex flex-col flex-1 min-w-0 overflow-hidden">
      <AppNavbar v-if="!tabStore.isContentFullscreen" class="relative z-30" />
      <!-- Vben-style Multiple Tabs Bar: hidden on small screens (< 1024px) -->
      <AppTabBar class="hidden lg:flex relative z-20" />
      <main class="flex-1 overflow-y-auto relative z-10">
        <!-- Page Transition Loading Overlay (minimum 500ms) -->
        <AppPageLoader :show="uiStore.isPageLoading" />

        <div v-if="tabStore.reloadFlag">
          <div v-if="route.name === 'Home'" class="h-full w-full">
            <router-view />
          </div>
          <div v-else class="mx-auto px-4 py-4 sm:px-6 sm:py-6 lg:px-8 lg:py-8">
            <router-view />
          </div>
        </div>
      </main>
    </div>
  </div>
</template>
