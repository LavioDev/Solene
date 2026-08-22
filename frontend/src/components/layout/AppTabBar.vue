<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useTabStore, type TabItem } from '@/stores/tabStore'
import {
  Home,
  Calendar as CalendarIcon,
  StickyNote,
  Users as UsersIcon,
  User as UserIcon,
  Heart,
  X,
  RotateCw,
  MoreVertical,
  XCircle,
  MinusCircle,
  Maximize2,
  Minimize2,
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const tabStore = useTabStore()

const tabsContainerRef = ref<HTMLElement | null>(null)
const isMenuOpen = ref(false)
const menuRef = ref<HTMLElement | null>(null)
const isRefreshing = ref(false)

const routeConfig: Record<string, { title: string; icon: string; name: string }> = {
  '/': { title: 'nav.home', icon: 'Home', name: 'Home' },
  '/calendar': { title: 'nav.calendar', icon: 'Calendar', name: 'Calendar' },
  '/notes': { title: 'nav.notes', icon: 'StickyNote', name: 'Notes' },
  '/users': { title: 'nav.users', icon: 'Users', name: 'Users' },
  '/couples': { title: 'nav.couples', icon: 'Heart', name: 'Couples' },
  '/profile': { title: 'nav.profile', icon: 'User', name: 'Profile' },
}

function getIconComponent(iconName?: string) {
  switch (iconName) {
    case 'Calendar':
      return CalendarIcon
    case 'StickyNote':
      return StickyNote
    case 'Users':
      return UsersIcon
    case 'Heart':
      return Heart
    case 'User':
      return UserIcon
    default:
      return Home
  }
}


// Sync route with tabStore
watch(
  () => route.path,
  (newPath) => {
    const config = routeConfig[newPath]
    if (config) {
      tabStore.addTab({
        title: config.title,
        name: config.name,
        path: newPath,
        closable: newPath !== '/',
        icon: config.icon,
      })
    }
  },
  { immediate: true }
)

function handleTabClick(tab: TabItem) {
  if (route.path !== tab.path) {
    router.push(tab.path)
  }
}

function handleCloseTab(tab: TabItem, e: MouseEvent) {
  e.stopPropagation()
  tabStore.removeTab(tab.path)
}

function handleRefresh() {
  isRefreshing.value = true
  tabStore.refreshTab()
  setTimeout(() => {
    isRefreshing.value = false
  }, 600)
}

function handleCloseOther() {
  isMenuOpen.value = false
  tabStore.closeOtherTabs(route.path)
}

function handleCloseAll() {
  isMenuOpen.value = false
  tabStore.closeAllTabs()
}

function handleToggleFullscreen() {
  isMenuOpen.value = false
  tabStore.toggleContentFullscreen()
}

// Mouse wheel horizontal scrolling
function onWheel(e: WheelEvent) {
  if (!tabsContainerRef.value) return
  if (e.deltaY !== 0) {
    tabsContainerRef.value.scrollLeft += e.deltaY
    e.preventDefault()
  }
}

// Click outside handling for dropdown menu
function handleClickOutside(e: MouseEvent) {
  if (menuRef.value && !menuRef.value.contains(e.target as Node)) {
    isMenuOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<template>
  <div class="h-10 bg-surface-subtle/70 border-b border-border/60 px-3.5 flex items-center justify-between gap-2 select-none z-20 shrink-0">

    <!-- Left: Scrollable Tabs Container -->
    <div
      ref="tabsContainerRef"
      @wheel="onWheel"
      class="flex-1 flex items-center gap-1.5 overflow-x-auto no-scrollbar scroll-smooth py-1"
    >
      <div
        v-for="tab in tabStore.tabs"
        :key="tab.path"
        @click="handleTabClick(tab)"
        class="h-7 px-3 rounded-lg text-xs font-medium transition-all duration-150 flex items-center gap-1.5 cursor-pointer shrink-0 border group relative"
        :class="[
          route.path === tab.path
            ? 'bg-white text-violet-700 font-semibold border-border shadow-2xs'
            : 'text-ink-muted hover:text-ink hover:bg-white/60 border-transparent hover:border-border/40'
        ]"
      >
        <!-- Tab Icon -->
        <component
          :is="getIconComponent(tab.icon)"
          class="w-3.5 h-3.5 transition-colors shrink-0"
          :class="route.path === tab.path ? 'text-violet-600' : 'text-ink-faint group-hover:text-ink-muted'"
        />

        <!-- Tab Title -->
        <span class="truncate max-w-[120px]">{{ t(tab.title) }}</span>

        <!-- Close Button -->
        <button
          v-if="tab.closable"
          type="button"
          @click="(e) => handleCloseTab(tab, e)"
          class="w-3.5 h-3.5 rounded-full flex items-center justify-center text-ink-faint hover:text-ink hover:bg-surface-raised ml-0.5 transition-colors cursor-pointer"
          :class="route.path === tab.path ? 'opacity-80 hover:opacity-100 hover:text-violet-900 hover:bg-violet-100' : 'opacity-0 group-hover:opacity-100'"
        >
          <X class="w-2.5 h-2.5" />
        </button>
      </div>
    </div>

    <!-- Right: Tab Action Controls -->
    <div class="flex items-center gap-1 shrink-0 pl-1 border-l border-border/40">
      <!-- Refresh current tab button -->
      <button
        type="button"
        @click="handleRefresh"
        :title="t('tabs.refresh')"
        class="p-1 rounded-md text-ink-faint hover:text-ink hover:bg-surface-raised transition-colors cursor-pointer"
      >
        <RotateCw
          class="w-3.5 h-3.5"
          :class="isRefreshing ? 'animate-spin text-violet-600' : ''"
        />
      </button>

      <!-- Tab Actions Dropdown Menu -->
      <div ref="menuRef" class="relative">
        <button
          type="button"
          @click.stop="isMenuOpen = !isMenuOpen"
          class="p-1 rounded-md text-ink-faint hover:text-ink hover:bg-surface-raised transition-colors cursor-pointer"
        >
          <MoreVertical class="w-3.5 h-3.5" />
        </button>

        <!-- Dropdown Popup -->
        <transition
          enter-active-class="transition duration-120 ease-out"
          enter-from-class="transform scale-95 opacity-0 -translate-y-1"
          enter-to-class="transform scale-100 opacity-100 translate-y-0"
          leave-active-class="transition duration-100 ease-in"
          leave-from-class="transform scale-100 opacity-100 translate-y-0"
          leave-to-class="transform scale-95 opacity-0 -translate-y-1"
        >
          <div
            v-if="isMenuOpen"
            class="absolute right-0 top-full mt-1.5 w-44 bg-white/95 backdrop-blur-md border border-border rounded-xl shadow-xl p-1 space-y-0.5 z-50 text-xs"
          >
            <button
              type="button"
              @click="handleRefresh"
              class="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-left text-ink hover:bg-surface-raised transition-colors cursor-pointer"
            >
              <RotateCw class="w-3.5 h-3.5 text-ink-muted" />
              <span>{{ t('tabs.refresh') }}</span>
            </button>

            <button
              type="button"
              @click="handleCloseOther"
              class="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-left text-ink hover:bg-surface-raised transition-colors cursor-pointer"
            >
              <XCircle class="w-3.5 h-3.5 text-ink-muted" />
              <span>{{ t('tabs.closeOther') }}</span>
            </button>

            <button
              type="button"
              @click="handleCloseAll"
              class="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-left text-ink hover:bg-surface-raised transition-colors cursor-pointer"
            >
              <MinusCircle class="w-3.5 h-3.5 text-ink-muted" />
              <span>{{ t('tabs.closeAll') }}</span>
            </button>

            <div class="h-px bg-border/60 my-1"></div>

            <button
              type="button"
              @click="handleToggleFullscreen"
              class="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-left text-ink hover:bg-surface-raised transition-colors cursor-pointer"
            >
              <Minimize2 v-if="tabStore.isContentFullscreen" class="w-3.5 h-3.5 text-ink-muted" />
              <Maximize2 v-else class="w-3.5 h-3.5 text-ink-muted" />
              <span>{{ t('tabs.maximizeContent') }}</span>
            </button>
          </div>
        </transition>
      </div>
    </div>

  </div>
</template>

<style scoped>
/* Hide scrollbar for tabs */
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
