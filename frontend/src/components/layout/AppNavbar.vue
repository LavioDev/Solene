<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import {
  PanelLeft,
  Search,
  Maximize,
  Minimize,
  LogOut,
  User as UserIcon,
  Home,
  Calendar as CalendarIcon,
  StickyNote,
  Users as UsersIcon,
  Heart,
} from 'lucide-vue-next'
import { useUiStore } from '@/stores/uiStore'
import { useAuthStore } from '@/stores/authStore'
import AppLangSwitcher from '@/components/ui/AppLangSwitcher.vue'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const uiStore = useUiStore()
const authStore = useAuthStore()

// Page Title
const pageTitle = computed(() => {
  switch (route.name) {
    case 'Home':
      return t('nav.home')
    case 'Calendar':
      return t('nav.calendar')
    case 'Notes':
      return t('nav.notes')
    case 'Users':
      return t('nav.users')
    case 'Couples':
      return t('nav.couples')
    case 'Profile':
      return t('nav.profile')
    default:
      return 'Solène'
  }
})

// Navigation Search State
const searchQuery = ref('')
const isSearchOpen = ref(false)
const searchInputRef = ref<HTMLInputElement | null>(null)
const searchContainerRef = ref<HTMLElement | null>(null)

const navItems = computed(() => {
  const items = [
    { name: t('nav.home'),     path: '/',         icon: Home,         desc: t('nav.homeDesc') },
    { name: t('nav.calendar'), path: '/calendar', icon: CalendarIcon, desc: t('nav.calendarDesc') },
    { name: t('nav.notes'),    path: '/notes',    icon: StickyNote,   desc: t('nav.notesDesc') },
    { name: t('nav.couples'),  path: '/couples',  icon: Heart,        desc: t('nav.couplesDesc') },
  ]
  if (authStore.user?.role === 'admin') {
    items.push({ name: t('nav.users'), path: '/users', icon: UsersIcon, desc: t('nav.usersDesc') })
  }
  items.push({ name: t('nav.profile'), path: '/profile', icon: UserIcon, desc: t('nav.profileDesc') })
  return items
})


const filteredNavItems = computed(() => {
  if (!searchQuery.value.trim()) return navItems.value
  const q = searchQuery.value.toLowerCase()
  return navItems.value.filter(item =>
    item.name.toLowerCase().includes(q) || item.path.toLowerCase().includes(q) || item.desc.toLowerCase().includes(q)
  )
})

function navigateTo(path: string) {
  router.push(path)
  searchQuery.value = ''
  isSearchOpen.value = false
}

// Fullscreen State (F11)
const isFullscreen = ref(false)

function toggleFullscreen() {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen().catch(err => {
      console.warn('Cannot enter fullscreen:', err)
    })
  } else {
    document.exitFullscreen().catch(err => {
      console.warn('Cannot exit fullscreen:', err)
    })
  }
}

function handleFullscreenChange() {
  isFullscreen.value = !!document.fullscreenElement
}

// User Menu Popover State
const showUserMenu = ref(false)
const userMenuRef = ref<HTMLElement | null>(null)

async function handleLogout() {
  showUserMenu.value = false
  await authStore.logout()
  router.push('/login')
}

// Click outside handling
function handleClickOutside(e: MouseEvent) {
  const target = e.target as Node
  if (userMenuRef.value && !userMenuRef.value.contains(target)) {
    showUserMenu.value = false
  }
  if (searchContainerRef.value && !searchContainerRef.value.contains(target)) {
    isSearchOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  document.addEventListener('fullscreenchange', handleFullscreenChange)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  document.removeEventListener('fullscreenchange', handleFullscreenChange)
})
</script>

<template>
  <header class="relative h-14 bg-white border-b border-border/60 flex items-center justify-between px-6 shrink-0 z-40 select-none">

    <!-- Left: Sidebar Toggle + Page Title / Breadcrumb -->
    <div class="flex items-center gap-3.5">
      <!-- Sidebar Toggle Icon Button -->
      <button
        type="button"
        @click="uiStore.toggleSidebar"
        :title="uiStore.isSidebarCollapsed ? t('nav.expandSidebar') : t('nav.collapseSidebar')"
        class="p-1.5 rounded-xl text-ink-muted hover:text-ink hover:bg-surface-raised transition-colors cursor-pointer border border-border/40 hover:border-border shadow-2xs"
      >
        <PanelLeft class="w-4 h-4 text-ink-muted hover:text-ink" />
      </button>

      <div class="h-4 w-px bg-border/60"></div>

      <!-- Page Title & Breadcrumb -->
      <div class="flex items-center gap-2">
        <span class="text-sm font-bold text-ink tracking-tight capitalize">
          {{ pageTitle }}
        </span>
        <span class="text-xs text-ink-faint">/</span>
        <span class="text-xs text-ink-muted font-mono">solène</span>
      </div>
    </div>

    <!-- Right: Nav Search Input + Lang Switcher Icon + Fullscreen F11 + User Avatar Icon -->
    <div class="flex items-center gap-2.5">

      <!-- 1. Quick Navigation Search Input -->
      <div ref="searchContainerRef" class="relative">
        <div class="relative flex items-center">
          <Search class="w-3.5 h-3.5 text-ink-faint absolute left-3 pointer-events-none" />
          <input
            ref="searchInputRef"
            v-model="searchQuery"
            type="text"
            :placeholder="t('nav.searchPlaceholder')"
            @focus="isSearchOpen = true"
            @keydown.esc="isSearchOpen = false"
            @keydown.enter="filteredNavItems.length > 0 && navigateTo(filteredNavItems[0].path)"
            class="w-36 focus:w-56 transition-all duration-200 pl-8 pr-3 py-1.5 text-xs bg-surface-subtle/80 hover:bg-surface-raised focus:bg-white border border-border/60 focus:border-violet-400 rounded-xl text-ink placeholder:text-ink-faint focus:outline-none focus:ring-2 focus:ring-violet-400/20"
          />
        </div>

        <!-- Search Results Dropdown -->
        <transition
          enter-active-class="transition duration-150 ease-out"
          enter-from-class="transform scale-95 opacity-0 -translate-y-1"
          enter-to-class="transform scale-100 opacity-100 translate-y-0"
          leave-active-class="transition duration-100 ease-in"
          leave-from-class="transform scale-100 opacity-100 translate-y-0"
          leave-to-class="transform scale-95 opacity-0 -translate-y-1"
        >
          <div
            v-if="isSearchOpen"
            class="absolute right-0 top-full mt-1.5 w-64 bg-white/95 backdrop-blur-md border border-border rounded-xl shadow-xl p-1.5 space-y-1 z-[100]"
          >
            <div class="px-2 py-1 text-[10px] font-bold uppercase tracking-wider text-ink-faint">
              {{ t('nav.navigationPages') }}
            </div>

            <button
              v-for="item in filteredNavItems"
              :key="item.path"
              type="button"
              @click="navigateTo(item.path)"
              class="w-full flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-left text-xs transition-colors hover:bg-violet-50 group cursor-pointer"
            >
              <div class="w-7 h-7 rounded-lg bg-surface-subtle group-hover:bg-violet-100 flex items-center justify-center text-ink-muted group-hover:text-violet-600 shrink-0">
                <component :is="item.icon" class="w-3.5 h-3.5" />
              </div>
              <div class="min-w-0 flex-1">
                <p class="font-semibold text-ink group-hover:text-violet-700 truncate">{{ item.name }}</p>
                <p class="text-[10px] text-ink-faint font-mono truncate">{{ item.desc }}</p>
              </div>
            </button>

            <div v-if="filteredNavItems.length === 0" class="px-3 py-3 text-center text-xs text-ink-faint">
              {{ t('nav.noPagesFound') }}
            </div>
          </div>
        </transition>
      </div>

      <div class="h-4 w-px bg-border/60"></div>

      <!-- 2. Language Switcher (Icon Only) -->
      <div class="flex items-center">
        <AppLangSwitcher :collapsed="true" />
      </div>

      <!-- 3. Fullscreen Toggle (F11 Zoom toàn màn hình) -->
      <button
        type="button"
        @click="toggleFullscreen"
        :title="isFullscreen ? t('nav.exitFullscreen') : t('nav.enterFullscreen')"
        class="p-2 rounded-xl text-ink-muted hover:text-violet-600 hover:bg-surface-raised transition-colors cursor-pointer border border-transparent hover:border-border/60"
      >
        <Minimize v-if="isFullscreen" class="w-4 h-4" />
        <Maximize v-else class="w-4 h-4" />
      </button>

      <div class="h-4 w-px bg-border/60"></div>

      <!-- 4. User Avatar Icon & Dropdown Menu -->
      <div ref="userMenuRef" class="relative">
        <button
          type="button"
          @click.stop="showUserMenu = !showUserMenu"
          :title="authStore.user?.full_name || t('nav.account')"
          class="w-8 h-8 rounded-full bg-violet-100 hover:bg-violet-200 border border-violet-200 flex items-center justify-center text-violet-700 font-bold text-xs transition-colors cursor-pointer overflow-hidden shadow-2xs"
        >
          <img
            v-if="authStore.user?.avatar_url"
            :src="authStore.user.avatar_url"
            :alt="authStore.user.full_name"
            class="w-full h-full object-cover"
          />
          <UserIcon v-else class="w-4 h-4" />
        </button>

        <!-- User Popover Card -->
        <transition
          enter-active-class="transition duration-150 ease-out"
          enter-from-class="transform scale-95 opacity-0 -translate-y-1"
          enter-to-class="transform scale-100 opacity-100 translate-y-0"
          leave-active-class="transition duration-100 ease-in"
          leave-from-class="transform scale-100 opacity-100 translate-y-0"
          leave-to-class="transform scale-95 opacity-0 -translate-y-1"
        >
          <div
            v-if="showUserMenu && authStore.user"
            class="absolute right-0 top-full mt-2 w-56 p-3 bg-white/95 backdrop-blur-md border border-border rounded-2xl shadow-xl space-y-3 z-[100]"
          >
            <!-- User Info Header -->
            <router-link
              to="/profile"
              @click="showUserMenu = false"
              class="flex items-center gap-2.5 pb-2.5 border-b border-border/60 hover:opacity-80 transition-opacity group cursor-pointer"
            >
              <div class="w-8 h-8 rounded-xl bg-violet-100 border border-violet-200 flex items-center justify-center text-violet-700 font-bold text-xs shrink-0 group-hover:bg-violet-200 transition-colors overflow-hidden">
                <img
                  v-if="authStore.user.avatar_url"
                  :src="authStore.user.avatar_url"
                  :alt="authStore.user.full_name"
                  class="w-full h-full object-cover"
                />
                <UserIcon v-else class="w-4 h-4" />
              </div>
              <div class="min-w-0 flex-1">
                <p class="text-xs font-bold text-ink truncate leading-tight group-hover:text-violet-700 transition-colors">{{ authStore.user.full_name }}</p>
                <p class="text-[10px] text-ink-muted font-mono truncate mt-0.5">{{ authStore.user.email }}</p>
              </div>
            </router-link>


            <!-- Profile Page Link Button -->
            <button
              type="button"
              @click="navigateTo('/profile')"
              class="w-full flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-medium text-ink hover:bg-violet-50 hover:text-violet-700 transition-colors cursor-pointer text-left"
            >
              <UserIcon class="w-3.5 h-3.5 text-ink-muted group-hover:text-violet-600" />
              <span>{{ t('nav.profile') }}</span>
            </button>

            <!-- Logout Action -->
            <button
              type="button"
              @click="handleLogout"
              class="w-full flex items-center justify-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold text-err-text bg-err-bg hover:bg-rose-100 border border-err-border transition-colors cursor-pointer"
            >
              <LogOut class="w-3.5 h-3.5" />
              <span>{{ t('nav.logout') }}</span>
            </button>
          </div>
        </transition>

      </div>

    </div>

  </header>
</template>
