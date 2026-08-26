import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUiStore = defineStore('ui', () => {
  const isSidebarCollapsed = ref(localStorage.getItem('solene_sidebar_collapsed') === 'true')
  const isPageLoading = ref(false)

  let loadingStartTime = 0
  let loadingTimer: ReturnType<typeof setTimeout> | null = null

  function toggleSidebar() {
    isSidebarCollapsed.value = !isSidebarCollapsed.value
    localStorage.setItem('solene_sidebar_collapsed', String(isSidebarCollapsed.value))
  }

  function setSidebarCollapsed(collapsed: boolean) {
    isSidebarCollapsed.value = collapsed
    localStorage.setItem('solene_sidebar_collapsed', String(collapsed))
  }

  function startPageLoading() {
    if (loadingTimer) {
      clearTimeout(loadingTimer)
      loadingTimer = null
    }
    loadingStartTime = Date.now()
    isPageLoading.value = true
  }

  function stopPageLoading(minDurationMs = 500) {
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
    isPageLoading,
    toggleSidebar,
    setSidebarCollapsed,
    startPageLoading,
    stopPageLoading,
  }
})
