<script setup lang="ts">
import { computed } from 'vue'
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
} from 'lucide-vue-next'
import AppLangSwitcher from '@/components/ui/AppLangSwitcher.vue'
import faviconImg from '@/img/favicon.png'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const uiStore = useUiStore()
const { t } = useI18n()

const navigation = computed(() => {
  const items = [
    { name: t('nav.home'),     path: '/',         icon: Home },
    { name: t('nav.calendar'), path: '/calendar', icon: CalendarIcon },
    { name: t('nav.schedule'), path: '/schedule', icon: Clock },
    { name: t('nav.notes'),    path: '/notes',    icon: StickyNote },
    { name: t('nav.moods'),    path: '/moods',    icon: Smile },
    { name: t('nav.couples'),  path: '/couples',  icon: Heart },
  ]

  if (authStore.user?.role === 'admin') {
    items.push({ name: t('nav.users'), path: '/users', icon: UsersIcon })
  }

  return items
})

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
    class="bg-white border-r border-border/80 flex flex-col h-screen sticky top-0 shrink-0 select-none z-30 transition-all duration-300 ease-in-out"
    :class="uiStore.isSidebarCollapsed ? 'w-16' : 'w-60'"
  >

    <!-- Wordmark / Brand Header -->
    <div
      class="h-14 flex items-center border-b border-border/60 transition-all"
      :class="uiStore.isSidebarCollapsed ? 'justify-center px-2' : 'px-5'"
    >
      <router-link to="/" class="group flex items-center gap-2">
        <span
          v-if="!uiStore.isSidebarCollapsed"
          class="select-none tracking-tight text-ink font-bold text-lg group-hover:text-violet-700 transition-colors inline-flex items-center gap-1.5"
          style="font-family: 'Plus Jakarta Sans', sans-serif;"
        >
          <span>Solène</span>
          <Sparkles class="w-4 h-4 text-violet-600 animate-pulse" />
        </span>
        <img
          v-else
          :src="faviconImg"
          alt="Solène"
          class="w-8 h-8 rounded-xl object-cover shadow-xs group-hover:opacity-90 transition-opacity"
          title="Solène"
        />
      </router-link>
    </div>

    <!-- Navigation Links -->
    <nav class="flex-1 overflow-y-auto p-2 space-y-1">
      <router-link
        v-for="item in navigation"
        :key="item.path"
        :to="item.path"
        :title="item.name"
        class="flex items-center rounded-xl text-xs sm:text-sm transition-all"
        :class="[
          uiStore.isSidebarCollapsed ? 'justify-center p-2.5' : 'gap-2.5 px-3 py-2',
          isActive(item.path)
            ? 'bg-violet-50 text-violet-700 font-semibold shadow-2xs'
            : 'text-ink-muted hover:bg-surface-raised hover:text-ink font-normal'
        ]"
      >
        <component
          :is="item.icon"
          class="w-4 h-4 shrink-0"
          :class="isActive(item.path) ? 'text-violet-600' : 'text-ink-faint'"
        />
        <span v-if="!uiStore.isSidebarCollapsed" class="truncate">{{ item.name }}</span>
        <!-- Active indicator -->
        <span
          v-if="!uiStore.isSidebarCollapsed && isActive(item.path)"
          class="ml-auto w-1.5 h-1.5 rounded-full bg-violet-500"
        />
      </router-link>
    </nav>

    <!-- Bottom Minimal Section: Language & Account (Expanded vs Collapsed) -->
    <div
      class="p-2 border-t border-border/60 mt-auto bg-surface-subtle/30 space-y-1 transition-all"
      :class="uiStore.isSidebarCollapsed ? 'flex flex-col items-center' : ''"
    >

      <!-- Language Selector -->
      <AppLangSwitcher
        :collapsed="uiStore.isSidebarCollapsed"
        direction="up"
        :align="uiStore.isSidebarCollapsed ? 'left' : 'left'"
      />

      <!-- User Account Row (Expanded) -->
      <div
        v-if="!uiStore.isSidebarCollapsed && authStore.user"
        class="flex items-center justify-between p-1.5 pl-2 rounded-xl hover:bg-surface-raised/80 transition-colors group"
      >
        <router-link to="/profile" class="flex items-center gap-2 min-w-0 flex-1 group/user" :title="t('nav.profile')">
          <div class="w-7 h-7 rounded-full bg-violet-100 group-hover/user:bg-violet-200 text-violet-700 font-semibold text-xs flex items-center justify-center shrink-0 transition-colors overflow-hidden border border-violet-200">
            <img
              v-if="authStore.user.avatar_url"
              :src="authStore.user.avatar_url"
              :alt="authStore.user.full_name"
              class="w-full h-full object-cover"
            />
            <UserIcon v-else class="w-3.5 h-3.5" />
          </div>
          <div class="min-w-0 flex-1">
            <p class="text-xs font-medium text-ink group-hover/user:text-violet-700 truncate leading-tight transition-colors">{{ authStore.user.full_name }}</p>
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
        v-else-if="uiStore.isSidebarCollapsed && authStore.user"
        class="flex flex-col items-center gap-1 pt-1"
      >
        <router-link
          to="/profile"
          :title="`${authStore.user.full_name} (${authStore.user.email})`"
          class="w-8 h-8 rounded-xl bg-violet-100 hover:bg-violet-200 text-violet-700 font-semibold text-xs flex items-center justify-center shrink-0 transition-colors overflow-hidden border border-violet-200"
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
