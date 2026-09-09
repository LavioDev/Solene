import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUiStore = defineStore('ui', () => {
  const isSidebarCollapsed = ref(localStorage.getItem('solene_sidebar_collapsed') === 'true')
  const isMobileSidebarOpen = ref(false)
  const isPageLoading = ref(false)

  let loadingStartTime = 0
  let loadingTimer: ReturnType<typeof setTimeout> | null = null

  function toggleSidebar() {
    if (typeof window !== 'undefined' && window.innerWidth < 1024) {
      isMobileSidebarOpen.value = !isMobileSidebarOpen.value
    } else {
      isSidebarCollapsed.value = !isSidebarCollapsed.value
      localStorage.setItem('solene_sidebar_collapsed', String(isSidebarCollapsed.value))
    }
  }

  function setSidebarCollapsed(collapsed: boolean) {
    isSidebarCollapsed.value = collapsed
    localStorage.setItem('solene_sidebar_collapsed', String(collapsed))
  }

  function openMobileSidebar() {
    isMobileSidebarOpen.value = true
  }

  function closeMobileSidebar() {
    isMobileSidebarOpen.value = false
  }

  function toggleMobileSidebar() {
    isMobileSidebarOpen.value = !isMobileSidebarOpen.value
  }

  const isRouteLoading = ref(false)
  let routeLoadingTimer: ReturnType<typeof setTimeout> | null = null

  function startRouteLoading() {
    if (routeLoadingTimer) {
      clearTimeout(routeLoadingTimer)
      routeLoadingTimer = null
    }
    isRouteLoading.value = true
  }

  function stopRouteLoading() {
    if (routeLoadingTimer) clearTimeout(routeLoadingTimer)
    routeLoadingTimer = setTimeout(() => {
      isRouteLoading.value = false
      routeLoadingTimer = null
    }, 120)
  }

  function startPageLoading() {
    if (loadingTimer) {
      clearTimeout(loadingTimer)
      loadingTimer = null
    }
    loadingStartTime = Date.now()
    isPageLoading.value = true
  }

  function stopPageLoading(minDurationMs = 150) {
    const elapsed = Date.now() - loadingStartTime
    const remaining = Math.max(0, minDurationMs - elapsed)
    if (loadingTimer) clearTimeout(loadingTimer)
    loadingTimer = setTimeout(() => {
      isPageLoading.value = false
      loadingTimer = null
    }, remaining)
  }

  return {
    isSidebarCollapsed,
    isMobileSidebarOpen,
    isPageLoading,
    isRouteLoading,
    toggleSidebar,
    setSidebarCollapsed,
    openMobileSidebar,
    closeMobileSidebar,
    toggleMobileSidebar,
    startRouteLoading,
    stopRouteLoading,
    startPageLoading,
    stopPageLoading,
  }
})
