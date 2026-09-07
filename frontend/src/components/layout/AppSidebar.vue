<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/authStore'
import { useUiStore } from '@/stores/uiStore'
import {
  Home,
  Calendar as CalendarIcon,
  Clock,
  StickyNote,
  Smile,
  Users as UsersIcon,
  Heart,
  LogOut,
  User as UserIcon,
  Sparkles,
  ShieldCheck,
  ChevronDown,
  X,
} from 'lucide-vue-next'
import AppLangSwitcher from '@/components/ui/AppLangSwitcher.vue'
import faviconImg from '@/img/favicon.png'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const uiStore = useUiStore()
const { t } = useI18n()

const isManagementOpen = ref(true)
const isMobile = ref(false)

function updateMobileState() {
  if (typeof window !== 'undefined') {
    isMobile.value = window.innerWidth < 1024
    if (!isMobile.value && uiStore.isMobileSidebarOpen) {
      uiStore.closeMobileSidebar()
    }
  }
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape' && uiStore.isMobileSidebarOpen) {
    uiStore.closeMobileSidebar()
  }
}

onMounted(() => {
  updateMobileState()
  window.addEventListener('resize', updateMobileState)
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('resize', updateMobileState)
  window.removeEventListener('keydown', handleKeydown)
})

const isEffectivelyCollapsed = computed(() => {
  if (isMobile.value) return false
  return uiStore.isSidebarCollapsed
})

const primaryNavigation = computed(() => [
  { name: t('nav.home'),     path: '/',         icon: Home },
  { name: t('nav.calendar'), path: '/calendar', icon: CalendarIcon },
  { name: t('nav.schedule'), path: '/schedule', icon: Clock },
  { name: t('nav.memories'), path: '/memories', icon: StickyNote },
  { name: t('nav.moods'),    path: '/moods',    icon: Smile },
])

const managementChildren = computed(() => {
  const children = []
  if (authStore.isAdmin || authStore.hasPermission('couples:read')) {
    children.push({ name: t('nav.couples'), path: '/couples', icon: Heart })
  }
  if (authStore.isAdmin || authStore.hasPermission('users:read')) {
    children.push({ name: t('nav.users'), path: '/users', icon: UsersIcon })
  }
  return children
})

const isManagementActive = computed(() => {
  return route.path.startsWith('/couples') || route.path.startsWith('/users')
})

watch(
  () => route.path,
  (path) => {
    if (path.startsWith('/couples') || path.startsWith('/users')) {
      isManagementOpen.value = true
    }
    if (uiStore.isMobileSidebarOpen) {
      uiStore.closeMobileSidebar()
    }
  },
  { immediate: true }
)

function isActive(path: string) {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}

async function handleLogout() {
  await authStore.logout()
  router.push('/login')
}
</script>

<template>
  <aside
    class="bg-white border-r border-border/80 flex flex-col h-screen select-none transition-all duration-300 ease-in-out fixed inset-y-0 left-0 z-50 lg:static lg:top-0 lg:shrink-0 lg:z-30"
    :class="[
      uiStore.isMobileSidebarOpen
        ? 'translate-x-0 shadow-2xl pointer-events-auto'
        : '-translate-x-full lg:translate-x-0 pointer-events-none lg:pointer-events-auto',
      isEffectivelyCollapsed ? 'w-16' : 'w-64 lg:w-60'
    ]"
  >

    <!-- Wordmark / Brand Header -->
    <div
      class="h-14 flex items-center border-b border-border/60 transition-all"
      :class="isEffectivelyCollapsed ? 'justify-center px-2' : 'px-5 justify-between'"
    >
      <router-link to="/" class="group flex items-center gap-2">
        <span
          v-if="!isEffectivelyCollapsed"
          class="select-none tracking-tight text-ink font-bold text-lg group-hover:text-primary-700 transition-colors inline-flex items-center gap-1.5"
          style="font-family: 'Plus Jakarta Sans', sans-serif;"
        >
          <span>Solène</span>
          <Sparkles class="w-4 h-4 text-primary-600 animate-pulse" />
        </span>
        <img
          v-else
          :src="faviconImg"
          alt="Solène"
          class="w-8 h-8 rounded-xl object-cover shadow-xs group-hover:opacity-90 transition-opacity"
          title="Solène"
        />
      </router-link>

      <!-- Close button on mobile drawer -->
      <button
        v-if="isMobile"
        type="button"
        @click="uiStore.closeMobileSidebar"
        class="p-1.5 rounded-xl text-ink-muted hover:text-ink hover:bg-surface-raised transition-colors cursor-pointer"
        :title="t('nav.collapseSidebar')"
      >
        <X class="w-4 h-4" />
      </button>
    </div>

    <!-- Navigation Links -->
    <nav class="flex-1 overflow-y-auto p-2 space-y-1">
      <!-- Primary Links -->
      <router-link
        v-for="item in primaryNavigation"
        :key="item.path"
        :to="item.path"
        :title="item.name"
        class="flex items-center rounded-xl text-xs sm:text-sm transition-all"
        :class="[
          isEffectivelyCollapsed ? 'justify-center p-2.5' : 'gap-2.5 px-3 py-2',
          isActive(item.path)
            ? 'bg-primary-50 text-primary-700 font-semibold shadow-2xs'
            : 'text-ink-muted hover:bg-surface-raised hover:text-ink font-normal'
        ]"
      >
        <component
          :is="item.icon"
          class="w-4 h-4 shrink-0"
          :class="isActive(item.path) ? 'text-primary-600' : 'text-ink-faint'"
        />
        <span v-if="!isEffectivelyCollapsed" class="truncate">{{ item.name }}</span>
        <!-- Active indicator -->
        <span
          v-if="!isEffectivelyCollapsed && isActive(item.path)"
          class="ml-auto w-1.5 h-1.5 rounded-full bg-primary-500"
        />
      </router-link>

      <!-- Grouped Management Navigation (Couples & Users) -->
      <!-- Case A: Expanded Sidebar -->
      <div v-if="!isEffectivelyCollapsed && managementChildren.length > 0" class="pt-1.5">
        <!-- Parent Collapsible Button -->
        <button
          type="button"
          @click="isManagementOpen = !isManagementOpen"
          class="w-full flex items-center justify-between gap-2.5 px-3 py-2 rounded-xl text-xs sm:text-sm transition-all cursor-pointer select-none"
          :class="[
            isManagementActive
              ? 'text-primary-800 font-semibold bg-primary-50/60'
              : 'text-ink-muted hover:bg-surface-raised hover:text-ink font-medium'
          ]"
          :title="t('nav.management')"
        >
          <div class="flex items-center gap-2.5 min-w-0">
            <ShieldCheck
              class="w-4 h-4 shrink-0"
              :class="isManagementActive ? 'text-primary-600' : 'text-ink-faint'"
            />
            <span class="truncate">{{ t('nav.management') }}</span>
          </div>
          <ChevronDown
            class="w-3.5 h-3.5 shrink-0 text-ink-faint transition-transform duration-200"
            :class="{ 'rotate-180': isManagementOpen }"
          />
        </button>

        <!-- Submenu Children -->
        <div
          v-show="isManagementOpen"
          class="mt-1 ml-3.5 pl-3 space-y-1 border-l border-primary-100 transition-all"
        >
          <router-link
            v-for="sub in managementChildren"
            :key="sub.path"
            :to="sub.path"
            :title="sub.name"
            class="flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-xs transition-all"
            :class="[
              isActive(sub.path)
                ? 'bg-primary-50 text-primary-700 font-semibold shadow-2xs'
                : 'text-ink-muted hover:bg-surface-raised hover:text-ink font-normal'
            ]"
          >
            <component
              :is="sub.icon"
              class="w-3.5 h-3.5 shrink-0"
              :class="isActive(sub.path) ? 'text-primary-600' : 'text-ink-faint'"
            />
            <span class="truncate">{{ sub.name }}</span>
            <span
              v-if="isActive(sub.path)"
              class="ml-auto w-1.5 h-1.5 rounded-full bg-primary-500"
            />
          </router-link>
        </div>
      </div>

      <!-- Case B: Collapsed Sidebar (Flyout popover on hover) -->
      <div v-else-if="isEffectivelyCollapsed && managementChildren.length > 0" class="pt-1 relative group/popover">
        <button
          type="button"
          class="w-full flex items-center justify-center p-2.5 rounded-xl text-xs transition-all cursor-pointer"
          :class="[
            isManagementActive
              ? 'bg-primary-50 text-primary-700 font-semibold shadow-2xs'
              : 'text-ink-muted hover:bg-surface-raised hover:text-ink font-normal'
          ]"
          :title="t('nav.management')"
        >
          <ShieldCheck
            class="w-4 h-4 shrink-0"
            :class="isManagementActive ? 'text-primary-600' : 'text-ink-faint'"
          />
        </button>

        <!-- Hover Flyout Menu -->
        <div
          class="absolute left-full top-0 ml-2 hidden group-hover/popover:flex flex-col bg-white border border-border/80 rounded-xl shadow-xl shadow-primary-500/10 p-1.5 min-w-40 z-50 pointer-events-auto"
        >
          <div class="px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider text-ink-faint border-b border-border/50 mb-1">
            {{ t('nav.management') }}
          </div>
          <router-link
            v-for="sub in managementChildren"
            :key="sub.path"
            :to="sub.path"
            class="flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-xs transition-all"
            :class="[
              isActive(sub.path)
                ? 'bg-primary-50 text-primary-700 font-semibold'
                : 'text-ink-muted hover:bg-surface-raised hover:text-ink'
            ]"
          >
            <component
              :is="sub.icon"
              class="w-3.5 h-3.5 shrink-0"
              :class="isActive(sub.path) ? 'text-primary-600' : 'text-ink-faint'"
            />
            <span class="truncate">{{ sub.name }}</span>
          </router-link>
        </div>
      </div>
    </nav>

    <!-- Bottom Minimal Section: Language & Account (Expanded vs Collapsed) -->
    <div
      class="p-2 border-t border-border/60 mt-auto bg-surface-subtle/30 space-y-1 transition-all"
      :class="isEffectivelyCollapsed ? 'flex flex-col items-center' : ''"
    >

      <!-- Language Selector -->
      <AppLangSwitcher
        :collapsed="isEffectivelyCollapsed"
        direction="up"
        :align="isEffectivelyCollapsed ? 'left' : 'left'"
      />

      <!-- User Account Row (Expanded) -->
      <div
        v-if="!isEffectivelyCollapsed && authStore.user"
        class="flex items-center justify-between p-1.5 pl-2 rounded-xl hover:bg-surface-raised/80 transition-colors group"
      >
        <router-link to="/profile" class="flex items-center gap-2 min-w-0 flex-1 group/user" :title="t('nav.profile')">
          <div class="w-7 h-7 rounded-full bg-primary-100 group-hover/user:bg-primary-200 text-primary-700 font-semibold text-xs flex items-center justify-center shrink-0 transition-colors overflow-hidden border border-primary-200">
            <img
              v-if="authStore.user.avatar_url"
              :src="authStore.user.avatar_url"
              :alt="authStore.user.full_name"
              class="w-full h-full object-cover"
            />
            <UserIcon v-else class="w-3.5 h-3.5" />
          </div>
          <div class="min-w-0 flex-1">
            <p class="text-xs font-medium text-ink group-hover/user:text-primary-700 truncate leading-tight transition-colors">{{ authStore.user.full_name }}</p>
            <p class="text-[10px] text-ink-faint truncate">{{ authStore.user.email }}</p>
          </div>
        </router-link>

        <!-- Ghost Logout Button -->
        <button
          type="button"
          @click="handleLogout"
          :title="t('nav.logout')"
          class="w-7 h-7 flex items-center justify-center rounded-lg text-ink-faint hover:text-err-text hover:bg-err-bg transition-colors cursor-pointer shrink-0 ml-1"
        >
          <LogOut class="w-3.5 h-3.5" />
        </button>
      </div>

      <!-- User Account Row (Collapsed) -->
      <div
        v-else-if="isEffectivelyCollapsed && authStore.user"
        class="flex flex-col items-center gap-1 pt-1"
      >
        <router-link
          to="/profile"
          :title="`${authStore.user.full_name} (${authStore.user.email})`"
          class="w-8 h-8 rounded-xl bg-primary-100 hover:bg-primary-200 text-primary-700 font-semibold text-xs flex items-center justify-center shrink-0 transition-colors overflow-hidden border border-primary-200"
        >
          <img
            v-if="authStore.user.avatar_url"
            :src="authStore.user.avatar_url"
            :alt="authStore.user.full_name"
            class="w-full h-full object-cover"
          />
          <UserIcon v-else class="w-3.5 h-3.5" />
        </router-link>


        <button
          type="button"
          @click="handleLogout"
          :title="t('nav.logout')"
          class="w-8 h-8 flex items-center justify-center rounded-xl text-ink-faint hover:text-err-text hover:bg-err-bg transition-colors cursor-pointer"
        >
          <LogOut class="w-3.5 h-3.5" />
        </button>
      </div>

    </div>


  </aside>
</template>
