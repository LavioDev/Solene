import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/authStore'
import { useMoodStore } from '@/stores/moodStore'
import { apiClient } from '@/services/apiClient'
import { coupleService } from '@/services/coupleService'
import { taskService } from '@/services/taskService'
import { noteService } from '@/services/noteService'
import type { Couple, UserPartnerSummary } from '@/types/couple'
import type { PartnerActiveStatus } from '@/types/task'
import type { NoteItem } from '@/types/note'
import type { EventOccurrence } from '@/modules/calendar/types'

export function useHomeDashboard() {
  const { locale } = useI18n()
  const authStore = useAuthStore()
  const moodStore = useMoodStore()

  // State
  const loading = ref(true)
  const isRefreshingPartner = ref(false)
  const couple = ref<Couple | null>(null)
  const partnerStatus = ref<PartnerActiveStatus | null>(null)
  const occurrences = ref<EventOccurrence[]>([])
  const notes = ref<NoteItem[]>([])

  // Random Note Modal State
  const showRandomNoteModal = ref(false)
  const currentRandomNote = ref<NoteItem | null>(null)
  const isShufflingNote = ref(false)

  // Live Love Counter
  const days = ref(0)
  const hours = ref(0)
  const minutes = ref(0)
  const seconds = ref(0)
  let counterInterval: number | null = null
  let partnerPollingInterval: number | null = null

  // Computed Partner Info
  const partner = computed<UserPartnerSummary | null>(() => {
    if (partnerStatus.value?.partner) {
      return partnerStatus.value.partner
    }
    if (!couple.value) return null
    const currentUserId = authStore.user?.id
    if (couple.value.user1_id === currentUserId) {
      return couple.value.user2 || null
    }
    return couple.value.user1 || null
  })

  const coupleNickname = computed(() => {
    if (!couple.value) return ''
    if (couple.value.nickname) return couple.value.nickname
    const u1Name = couple.value.user1?.full_name || 'User 1'
    const u2Name = couple.value.user2?.full_name || 'User 2'
    return `${u1Name} & ${u2Name}`
  })

  // Today's Date String in YYYY-MM-DD format
  const todayDateStr = computed(() => {
    const now = new Date()
    const y = now.getFullYear()
    const m = String(now.getMonth() + 1).padStart(2, '0')
    const d = String(now.getDate()).padStart(2, '0')
    return `${y}-${m}-${d}`
  })

  // Filtered Occurrences
  const todayOccurrences = computed(() => {
    return occurrences.value.filter((o) => o.date === todayDateStr.value)
  })

  const upcomingOccurrences = computed(() => {
    return occurrences.value
      .filter((o) => o.date > todayDateStr.value)
      .sort((a, b) => (a.date > b.date ? 1 : -1))
      .slice(0, 7)
  })

  function updateLoveCounter() {
    if (!couple.value?.start_date) return
    const parts = couple.value.start_date.split('-').map(Number)
    if (parts.length !== 3) return

    const startDate = new Date(parts[0], parts[1] - 1, parts[2], 0, 0, 0)
    const now = new Date()
    const diffMs = now.getTime() - startDate.getTime()

    if (diffMs > 0) {
      const totalSecs = Math.floor(diffMs / 1000)
      days.value = Math.floor(totalSecs / (3600 * 24))
      hours.value = Math.floor((totalSecs % (3600 * 24)) / 3600)
      minutes.value = Math.floor((totalSecs % 3600) / 60)
      seconds.value = totalSecs % 60
    } else {
      days.value = 0
      hours.value = 0
      minutes.value = 0
      seconds.value = 0
    }
  }

  function calculateDaysRemaining(dateStr: string): number {
    const [y, m, d] = dateStr.split('-').map(Number)
    const target = new Date(y, m - 1, d)
    const now = new Date()
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    const diffTime = target.getTime() - today.getTime()
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  }

  function formatDisplayDate(dateStr: string): string {
    const [y, m, d] = dateStr.split('-').map(Number)
    const dateObj = new Date(y, m - 1, d)
    const loc =
      locale.value === 'vi'
        ? 'vi-VN'
        : locale.value === 'fr'
        ? 'fr-FR'
        : locale.value === 'zh'
        ? 'zh-CN'
        : 'en-US'
    return dateObj.toLocaleDateString(loc, { month: 'short', day: 'numeric', year: 'numeric' })
  }

  function formatTaskTime(isoString?: string | null): string {
    if (!isoString) return '--:--'
    try {
      const d = new Date(isoString)
      const hh = String(d.getHours()).padStart(2, '0')
      const mm = String(d.getMinutes()).padStart(2, '0')
      return `${hh}:${mm}`
    } catch {
      return '--:--'
    }
  }

  function getUserInitials(name?: string, email?: string): string {
    if (name && name.trim()) {
      const parts = name.trim().split(' ')
      if (parts.length >= 2) {
        return `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase()
      }
      return name.slice(0, 2).toUpperCase()
    }
    if (email) return email.slice(0, 2).toUpperCase()
    return 'U'
  }

  function pickRandomNote() {
    if (notes.value.length === 0) {
      currentRandomNote.value = null
      return
    }
    isShufflingNote.value = true
    setTimeout(() => {
      const randomPool = notes.value.filter((n) => n.display_type === 'RANDOM')
      const pool = randomPool.length > 0 ? randomPool : notes.value
      const randomIndex = Math.floor(Math.random() * pool.length)
      currentRandomNote.value = pool[randomIndex]
      isShufflingNote.value = false
    }, 180)
  }

  const currentRandomNoteAuthor = computed(() => {
    if (!currentRandomNote.value) return ''
    const noteUserId = currentRandomNote.value.user_id
    if (couple.value) {
      if (noteUserId === couple.value.user1_id && couple.value.user1?.full_name) {
        return couple.value.user1.full_name
      }
      if (noteUserId === couple.value.user2_id && couple.value.user2?.full_name) {
        return couple.value.user2.full_name
      }
    }
    if (authStore.user?.id === noteUserId && authStore.user.full_name) {
      return authStore.user.full_name
    }
    return partner.value?.full_name || authStore.user?.full_name || ''
  })

  function openRandomNoteModal() {
    pickRandomNote()
    showRandomNoteModal.value = true
  }

  function closeRandomNoteModal() {
    showRandomNoteModal.value = false
  }

  async function fetchDashboardData() {
    loading.value = true
    try {
      // 1. Fetch Couple Profile
      try {
        couple.value = await coupleService.getMyCouple()
        updateLoveCounter()
      } catch {
        couple.value = null
      }

      // 2. Fetch Partner Active Status & Today Mood
      try {
        partnerStatus.value = await taskService.getPartnerActiveStatus()
      } catch {
        partnerStatus.value = null
      }

      try {
        await moodStore.fetchTodayMood()
      } catch {
        // ignore background mood fetch error
      }

      // 3. Fetch Occurrences for next 30 days
      try {
        const now = new Date()
        const startStr = todayDateStr.value
        const endDate = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 30)
        const endYear = endDate.getFullYear()
        const endMonth = String(endDate.getMonth() + 1).padStart(2, '0')
        const endDay = String(endDate.getDate()).padStart(2, '0')
        const endStr = `${endYear}-${endMonth}-${endDay}`

        const res = await apiClient.get<EventOccurrence[]>('/events/occurrences', {
          params: { start_date: startStr, end_date: endStr },
        })
        occurrences.value = res.data
      } catch {
        occurrences.value = []
      }

      // 4. Fetch Notes
      try {
        const notesData = await noteService.getNotes({ per_page: 50 })
        notes.value = notesData.items || []
      } catch {
        notes.value = []
      }
    } finally {
      loading.value = false
    }
  }

  async function refreshPartnerStatusOnly() {
    isRefreshingPartner.value = true
    try {
      partnerStatus.value = await taskService.getPartnerActiveStatus()
      await moodStore.fetchTodayMood()
    } catch {
      // catch background polling error
    } finally {
      isRefreshingPartner.value = false
    }
  }

  onMounted(() => {
    fetchDashboardData()
    counterInterval = window.setInterval(updateLoveCounter, 1000)
    partnerPollingInterval = window.setInterval(refreshPartnerStatusOnly, 30000)
  })

  onUnmounted(() => {
    if (counterInterval !== null) {
      clearInterval(counterInterval)
    }
    if (partnerPollingInterval !== null) {
      clearInterval(partnerPollingInterval)
    }
  })

  return {
    loading,
    isRefreshingPartner,
    couple,
    partner,
    partnerStatus,
    occurrences,
    notes,
    days,
    hours,
    minutes,
    seconds,
    coupleNickname,
    todayDateStr,
    todayOccurrences,
    upcomingOccurrences,
    showRandomNoteModal,
    currentRandomNote,
    currentRandomNoteAuthor,
    isShufflingNote,
    formatDisplayDate,
    calculateDaysRemaining,
    formatTaskTime,
    getUserInitials,
    pickRandomNote,
    openRandomNoteModal,
    closeRandomNoteModal,
    fetchDashboardData,
    refreshPartnerStatusOnly,
  }
}
