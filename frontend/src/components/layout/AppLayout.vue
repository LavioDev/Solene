<script setup lang="ts">
import { useTabStore } from '@/stores/tabStore'
import { useUiStore } from '@/stores/uiStore'
import { useThemeStore } from '@/stores/themeStore'
import AppSidebar from '@/components/layout/AppSidebar.vue'
import AppNavbar from '@/components/layout/AppNavbar.vue'
import AppPageLoader from '@/components/ui/AppPageLoader.vue'
import AppNProgress from '@/components/ui/AppNProgress.vue'
import AppPartnerNoteFab from '@/components/layout/AppPartnerNoteFab.vue'

const tabStore = useTabStore()
const uiStore = useUiStore()
const themeStore = useThemeStore()
</script>

<template>
  <div class="fixed inset-0 lg:relative lg:inset-auto flex h-full lg:h-screen w-full bg-surface-subtle overflow-hidden">
    <!-- Sleek Top Navigation Progress Bar (Vben / GitHub Style) -->
    <AppNProgress :loading="uiStore.isRouteLoading" />
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
    <div class="flex flex-col flex-1 min-w-0 h-full overflow-hidden">
      <AppNavbar v-if="!tabStore.isContentFullscreen" class="shrink-0 w-full z-30 relative" />
      <main
        class="flex-1 min-h-0 overflow-y-auto relative z-10 overscroll-y-contain lg:overscroll-y-auto [webkit-overflow-scrolling:touch] transition-colors duration-300"
        :class="`theme-${themeStore.activeThemeId}-content-bg`"
      >
        <!-- Page Transition Loading Overlay (minimum 500ms) -->
        <AppPageLoader :show="uiStore.isPageLoading" />

        <div v-if="tabStore.reloadFlag" class="min-h-full">
          <router-view v-slot="{ Component, route: currentRoute }">
            <transition name="page-fade" mode="out-in">
              <div
                :key="currentRoute.path"
                :class="currentRoute.name === 'Home' ? 'h-full w-full' : 'mx-auto px-4 py-4 sm:px-6 sm:py-6 lg:px-8 lg:py-8'"
              >
                <component :is="Component" />
              </div>
            </transition>
          </router-view>
        </div>
      </main>
    </div>

    <!-- Responsive Draggable Partner Note FAB & Modal (Hiện trên mọi màn khi ở chế độ responsive) -->
    <AppPartnerNoteFab />
  </div>
</template>

<style scoped>
/* Page Transition (Smooth fade + subtle upward slide, vben style) */
.page-fade-enter-active {
  transition: opacity 0.2s cubic-bezier(0.25, 0.46, 0.45, 0.94),
              transform 0.2s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  will-change: opacity, transform;
}

.page-fade-leave-active {
  transition: opacity 0.12s ease-in;
  will-change: opacity;
}

.page-fade-enter-from {
  opacity: 0;
  transform: translateY(6px);
}

.page-fade-leave-to {
  opacity: 0;
}

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
