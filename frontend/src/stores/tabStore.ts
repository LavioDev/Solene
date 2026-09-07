import { defineStore } from 'pinia'
import { ref } from 'vue'
import { router } from '@/router'
import { useUiStore } from '@/stores/uiStore'

export interface TabItem {
  title: string
  name: string
  path: string
  closable: boolean
  icon?: string
}

export const useTabStore = defineStore('tabs', () => {
  const tabs = ref<TabItem[]>([
    {
      title: 'nav.home',
      name: 'Home',
      path: '/',
      closable: false,
      icon: 'Home',
    },
  ])

  const activeTabPath = ref('/')
  const reloadFlag = ref(true)
  const isContentFullscreen = ref(false)

  function addTab(tab: TabItem) {
    activeTabPath.value = tab.path
    const exists = tabs.value.some((t) => t.path === tab.path)
    if (!exists) {
      tabs.value.push(tab)
    }
  }

  function removeTab(path: string) {
    const index = tabs.value.findIndex((t) => t.path === path)
    if (index === -1) return

    const isCurrentActive = activeTabPath.value === path
    tabs.value.splice(index, 1)

    if (isCurrentActive) {
      const nextTab = tabs.value[index] || tabs.value[index - 1] || tabs.value[0]
      if (nextTab) {
        activeTabPath.value = nextTab.path
        router.push(nextTab.path)
      }
    }
  }

  function closeOtherTabs(currentPath: string) {
    tabs.value = tabs.value.filter((t) => !t.closable || t.path === currentPath)
    activeTabPath.value = currentPath
  }

  function closeAllTabs() {
    tabs.value = tabs.value.filter((t) => !t.closable)
    const first = tabs.value[0]
    if (first) {
      activeTabPath.value = first.path
      router.push(first.path)
    }
  }

  function refreshTab() {
    const uiStore = useUiStore()
    uiStore.startPageLoading()
    reloadFlag.value = false
    setTimeout(() => {
      reloadFlag.value = true
      uiStore.stopPageLoading(500)
    }, 500)
  }

  function toggleContentFullscreen() {
    isContentFullscreen.value = !isContentFullscreen.value
  }

  return {
    tabs,
    activeTabPath,
    reloadFlag,
    isContentFullscreen,
    addTab,
    removeTab,
    closeOtherTabs,
    closeAllTabs,
    refreshTab,
    toggleContentFullscreen,
  }
})
