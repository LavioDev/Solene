import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useUiStore } from '@/stores/uiStore'
import AppLayout from '@/components/layout/AppLayout.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/modules/auth/views/LoginView.vue'),
    meta: { requiresGuest: true },
  },
  {
    path: '/',
    component: AppLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Home',
        component: () => import('@/modules/home/views/HomeView.vue'),
      },
      {
        path: 'calendar',
        name: 'Calendar',
        component: () => import('@/modules/calendar/views/CalendarView.vue'),
      },
      {
        path: 'schedule',
        name: 'Schedule',
        component: () => import('@/modules/schedule/views/ScheduleView.vue'),
      },
      {
        path: 'memories',
        name: 'Memories',
        component: () => import('@/modules/memories/views/MemoriesView.vue'),
      },
      {
        path: 'moods',
        name: 'Moods',
        component: () => import('@/modules/moods/views/MoodsView.vue'),
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/modules/users/views/UsersView.vue'),
      },
      {
        path: 'couples',
        name: 'Couples',
        component: () => import('@/modules/couples/views/CouplesView.vue'),
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/modules/profile/views/ProfileView.vue'),
      },
    ],
  },

  {
    path: '/:pathMatch(.*)*',
    redirect: '/',
  },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  const uiStore = useUiStore()

  if (to.path !== from.path) {
    uiStore.startPageLoading()
  }

  if (authStore.isInitializing) {
    await authStore.checkAuth()
  }

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.meta.requiresGuest && authStore.isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

router.afterEach((to, from) => {
  const uiStore = useUiStore()
  if (to.path !== from.path) {
    uiStore.stopPageLoading(500)
  }
})

router.onError(() => {
  const uiStore = useUiStore()
  uiStore.stopPageLoading(500)
})
