<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { apiClient } from '@/services/apiClient'
import {
  Calendar as CalendarIcon,
  CheckSquare,
  ChevronLeft,
  ChevronRight,
  Clock,
  Heart,
  PawPrint,
  Pencil,
  Plus,
  Sparkles,
  Square,
  StickyNote,
  Trash2,
} from 'lucide-vue-next'





import AppButton from '@/components/ui/AppButton.vue'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppModal from '@/components/ui/AppModal.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppTextarea from '@/components/ui/AppTextarea.vue'
import AppSelect from '@/components/ui/AppSelect.vue'
import AppImageUpload from '@/components/ui/AppImageUpload.vue'
import AppConfirmModal from '@/components/ui/AppConfirmModal.vue'
import AutoRuleModal from '../components/AutoRuleModal.vue'
import DayGanttView from '../components/DayGanttView.vue'
import type { EventOccurrence, CalendarDay, TaskItem } from '../types'

const { t, locale } = useI18n()

// Main Sub-Nav mode: 'calendar' | 'gantt'
const mainViewMode = ref<'calendar' | 'gantt'>('calendar')
const ganttViewRef = ref<InstanceType<typeof DayGanttView> | null>(null)

const today = new Date()
const todayStr = today.toISOString().split('T')[0]
const currentYear = ref(today.getFullYear())

const currentMonth = ref(today.getMonth())

// View mode: 'month' | 'week'
const viewMode = ref<'month' | 'week'>('month')
const currentWeekAnchor = ref<Date>(new Date())

const selectedDay = ref<CalendarDay | null>(null)
const selectedEvent = ref<EventOccurrence | null>(null)

// Modals
const showAutoRuleModal = ref(false)
const showNoteModal = ref(false)
const showTaskModal = ref(false)
const showDeleteConfirmModal = ref(false)
const deletingEvent = ref(false)


// Single Day Note Form State (Unified with /notes)
const singleNoteTitle = ref('')
const singleNoteContent = ref('')
const singleNoteImages = ref<string[]>([])
const singleNoteDisplayType = ref<'DATE' | 'RANDOM'>('DATE')
const singleNoteTargetDate = ref(todayStr)
const submittingNote = ref(false)

// Day Tasks State
const dayTasks = ref<TaskItem[]>([])
const loadingDayTasks = ref(false)
const addingTask = ref(false)
const deletingTaskId = ref<string | null>(null)


// New Task Form State (Preset date according to clicked cell, only select start & end time)
const newTaskTitle = ref('')
const newTaskStartTime = ref('09:00')
const newTaskEndTime = ref('10:00')
const newTaskPriority = ref('medium')
const newTaskContent = ref('')

const occurrences = ref<EventOccurrence[]>([])
const loading = ref(false)


const weekDays = computed(() => [
  t('calendar.weekdays.mon'),
  t('calendar.weekdays.tue'),
  t('calendar.weekdays.wed'),
  t('calendar.weekdays.thu'),
  t('calendar.weekdays.fri'),
  t('calendar.weekdays.sat'),
  t('calendar.weekdays.sun'),
])

const headerLabel = computed(() => {
  const loc = locale.value === 'vi' ? 'vi-VN' : locale.value === 'fr' ? 'fr-FR' : locale.value === 'zh' ? 'zh-CN' : 'en-US'
  if (viewMode.value === 'month') {
    const date = new Date(currentYear.value, currentMonth.value, 1)
    return date.toLocaleDateString(loc, { month: 'long', year: 'numeric' })
  } else {
    // Week mode: display range of the week
    if (calendarDays.value.length >= 7) {
      const first = calendarDays.value[0].date
      const last = calendarDays.value[6].date
      const firstStr = first.toLocaleDateString(loc, { month: 'short', day: 'numeric' })
      const lastStr = last.toLocaleDateString(loc, { month: 'short', day: 'numeric', year: 'numeric' })
      return `${firstStr} – ${lastStr}`
    }
    return currentWeekAnchor.value.toLocaleDateString(loc, { month: 'long', year: 'numeric' })
  }
})

function prevStep() {
  if (viewMode.value === 'month') {
    if (currentMonth.value === 0) {
      currentMonth.value = 11
      currentYear.value -= 1
    } else {
      currentMonth.value -= 1
    }
  } else {
    // Step backward 7 days
    const d = new Date(currentWeekAnchor.value)
    d.setDate(d.getDate() - 7)
    currentWeekAnchor.value = d
    currentYear.value = d.getFullYear()
    currentMonth.value = d.getMonth()
  }
}

function nextStep() {
  if (viewMode.value === 'month') {
    if (currentMonth.value === 11) {
      currentMonth.value = 0
      currentYear.value += 1
    } else {
      currentMonth.value += 1
    }
  } else {
    // Step forward 7 days
    const d = new Date(currentWeekAnchor.value)
    d.setDate(d.getDate() + 7)
    currentWeekAnchor.value = d
    currentYear.value = d.getFullYear()
    currentMonth.value = d.getMonth()
  }
}

function goToday() {
  const now = new Date()
  currentYear.value = now.getFullYear()
  currentMonth.value = now.getMonth()
  currentWeekAnchor.value = now
}

function switchToCurrentWeek() {
  currentWeekAnchor.value = new Date()
  viewMode.value = 'week'
}

const calendarDays = computed<CalendarDay[]>(() => {
  if (viewMode.value === 'month') {
    const year = currentYear.value
    const month = currentMonth.value

    const firstDayOfMonth = new Date(year, month, 1)
    const lastDayOfMonth = new Date(year, month + 1, 0)

    let startingDayOfWeek = firstDayOfMonth.getDay() - 1
    if (startingDayOfWeek === -1) startingDayOfWeek = 6

    const daysInMonth = lastDayOfMonth.getDate()
    const days: CalendarDay[] = []

    // Trailing days from previous month
    const prevMonthLastDay = new Date(year, month, 0).getDate()
    for (let i = startingDayOfWeek - 1; i >= 0; i--) {
      const d = new Date(year, month - 1, prevMonthLastDay - i)
      days.push(createDayObj(d, false))
    }

    // Current month days
    for (let i = 1; i <= daysInMonth; i++) {
      const d = new Date(year, month, i)
      days.push(createDayObj(d, true))
    }

    // Leading days from next month
    const remainingCells = (days.length > 35 ? 42 : 35) - days.length
    for (let i = 1; i <= remainingCells; i++) {
      const d = new Date(year, month + 1, i)
      days.push(createDayObj(d, false))
    }

    return days
  } else {
    // Week Mode: 7 days of the active week (Monday to Sunday)
    const anchor = currentWeekAnchor.value
    const dayOfWeek = anchor.getDay()
    const diffToMonday = (dayOfWeek === 0 ? -6 : 1 - dayOfWeek)

    const monday = new Date(anchor)
    monday.setDate(anchor.getDate() + diffToMonday)

    const days: CalendarDay[] = []
    for (let i = 0; i < 7; i++) {
      const d = new Date(monday)
      d.setDate(monday.getDate() + i)
      const isCurrentM = d.getMonth() === currentMonth.value
      days.push(createDayObj(d, isCurrentM))
    }

    return days
  }
})

function createDayObj(d: Date, isCurrentMonth: boolean): CalendarDay {
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const dayStr = String(d.getDate()).padStart(2, '0')
  const dateStr = `${year}-${month}-${dayStr}`

  const isToday =
    d.getDate() === today.getDate() &&
    d.getMonth() === today.getMonth() &&
    d.getFullYear() === today.getFullYear()

  const dayEvents = occurrences.value.filter((o) => o.date === dateStr)

  return {
    date: d,
    dateStr,
    dayNumber: d.getDate(),
    isCurrentMonth,
    isToday,
    events: dayEvents,
  }
}

async function fetchOccurrences() {
  if (calendarDays.value.length === 0) return
  const startDateStr = calendarDays.value[0].dateStr
  const endDateStr = calendarDays.value[calendarDays.value.length - 1].dateStr

  loading.value = true
  try {
    const res = await apiClient.get<EventOccurrence[]>('/events/occurrences', {
      params: { start_date: startDateStr, end_date: endDateStr },
    })
    occurrences.value = res.data
  } catch (err) {
    console.error('Failed to fetch event occurrences:', err)
  } finally {
    loading.value = false
  }
}

watch([currentYear, currentMonth, viewMode, currentWeekAnchor], () => {
  fetchOccurrences()
})

watch(mainViewMode, (newMode) => {
  if (newMode === 'gantt' && ganttViewRef.value) {
    ganttViewRef.value.fetchDayTasks()
  }
})

// Day-Gantt Header Controls & Active Date
const ganttActiveDateStr = ref(todayStr)

const ganttHeaderLabel = computed(() => {
  const loc = locale.value === 'vi' ? 'vi-VN' : locale.value === 'fr' ? 'fr-FR' : locale.value === 'zh' ? 'zh-CN' : 'en-US'
  const parts = ganttActiveDateStr.value.split('-').map(Number)
  if (parts.length !== 3) return ganttActiveDateStr.value
  const d = new Date(parts[0], parts[1] - 1, parts[2])
  if (locale.value === 'vi') {
    return `Ngày ${d.getDate()} Tháng ${d.getMonth() + 1} Năm ${d.getFullYear()}`
  }
  return d.toLocaleDateString(loc, { day: 'numeric', month: 'long', year: 'numeric' })
})

function ganttPrevDay() {
  const parts = ganttActiveDateStr.value.split('-').map(Number)
  const d = new Date(parts[0], parts[1] - 1, parts[2] - 1)
  ganttActiveDateStr.value = getLocalDateStr(d)
}

function ganttNextDay() {
  const parts = ganttActiveDateStr.value.split('-').map(Number)
  const d = new Date(parts[0], parts[1] - 1, parts[2] + 1)
  ganttActiveDateStr.value = getLocalDateStr(d)
}

function ganttGoToday() {
  ganttActiveDateStr.value = getLocalDateStr(new Date())
}

function handleFocusNow() {
  ganttGoToday()
  setTimeout(() => {
    ganttViewRef.value?.scrollToNow()
  }, 100)
}

onMounted(() => {
  fetchOccurrences()
})




function getLocalDateStr(dateInput?: string | Date | null): string {
  if (!dateInput) return ''
  const d = new Date(dateInput)
  if (isNaN(d.getTime())) return ''
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

// Fetch all tasks for a specific date (for modal task list)
async function fetchTasksForDay(dateStr: string) {
  loadingDayTasks.value = true
  try {
    const res = await apiClient.get<TaskItem[]>('/tasks')
    dayTasks.value = res.data.filter((t) => {
      if (t.start_time) {
        return getLocalDateStr(t.start_time) === dateStr
      }
      if (t.created_at) {
        return getLocalDateStr(t.created_at) === dateStr
      }
      return false
    })
  } catch (err) {
    console.error('Failed to fetch tasks for day:', err)
  } finally {
    loadingDayTasks.value = false
  }
}

function formatTaskTime(timeStr?: string | null): string {
  if (!timeStr) return ''
  try {
    const d = new Date(timeStr)
    const hours = String(d.getHours()).padStart(2, '0')
    const minutes = String(d.getMinutes()).padStart(2, '0')
    return `${hours}:${minutes}`
  } catch {
    return ''
  }
}

// Create new task for day (pre-set date according to clicked cell, only set start and end time)
async function handleCreateTaskForDay() {
  if (!newTaskTitle.value.trim()) return

  addingTask.value = true
  try {
    const targetDate = selectedDay.value?.dateStr || singleNoteTargetDate.value || todayStr
    let start_time: string | null = null
    let end_time: string | null = null

    if (newTaskStartTime.value) {
      start_time = new Date(`${targetDate}T${newTaskStartTime.value}:00`).toISOString()
    }
    if (newTaskEndTime.value) {
      end_time = new Date(`${targetDate}T${newTaskEndTime.value}:00`).toISOString()
    }

    const payload = {
      title: newTaskTitle.value.trim(),
      content: newTaskContent.value.trim() || null,
      is_completed: false,
      start_time,
      end_time,
      priority: newTaskPriority.value,
    }

    const res = await apiClient.post<TaskItem>('/tasks', payload)
    dayTasks.value.unshift(res.data)

    // Reset inputs
    newTaskTitle.value = ''
    newTaskContent.value = ''

    // Refresh calendar occurrences and Gantt chart in background
    await fetchOccurrences()
    if (ganttViewRef.value) {
      await ganttViewRef.value.fetchDayTasks()
    }
  } catch (err) {
    console.error('Failed to create task for day:', err)
  } finally {
    addingTask.value = false
  }
}

// Toggle Task Status
async function handleToggleTaskStatus(task: TaskItem) {
  try {
    const res = await apiClient.patch<TaskItem>(`/tasks/${task.id}/toggle`)
    task.is_completed = res.data.is_completed
    await fetchOccurrences()
    if (ganttViewRef.value) {
      await ganttViewRef.value.fetchDayTasks()
    }
  } catch (err) {
    console.error('Failed to toggle task status:', err)
  }
}

// Delete Task
async function handleDeleteTask(task: TaskItem) {
  deletingTaskId.value = task.id
  try {
    await apiClient.delete(`/tasks/${task.id}`)
    dayTasks.value = dayTasks.value.filter((t) => t.id !== task.id)
    await fetchOccurrences()
    if (ganttViewRef.value) {
      await ganttViewRef.value.fetchDayTasks()
    }
  } catch (err) {

    console.error('Failed to delete task:', err)
  } finally {
    deletingTaskId.value = null
  }
}

// Edit Task State & Methods
const showEditTaskModal = ref(false)

const editingTask = ref<TaskItem | null>(null)
const editTaskTitle = ref('')
const editTaskStartTime = ref('09:00')
const editTaskEndTime = ref('10:00')
const editTaskPriority = ref('medium')
const editTaskContent = ref('')
const editTaskIsCompleted = ref(false)
const updatingTask = ref(false)

function openEditTaskModal(task: TaskItem) {
  editingTask.value = task
  editTaskTitle.value = task.title
  editTaskStartTime.value = formatTaskTime(task.start_time) || '09:00'
  editTaskEndTime.value = formatTaskTime(task.end_time) || '10:00'
  editTaskPriority.value = task.priority || 'medium'
  editTaskContent.value = task.content || ''
  editTaskIsCompleted.value = task.is_completed
  showEditTaskModal.value = true
}

async function handleUpdateTask() {
  if (!editingTask.value || !editTaskTitle.value.trim()) return

  updatingTask.value = true
  try {
    const targetDate = selectedDay.value?.dateStr || singleNoteTargetDate.value || todayStr
    let start_time: string | null = null
    let end_time: string | null = null

    if (editTaskStartTime.value) {
      start_time = new Date(`${targetDate}T${editTaskStartTime.value}:00`).toISOString()
    }
    if (editTaskEndTime.value) {
      end_time = new Date(`${targetDate}T${editTaskEndTime.value}:00`).toISOString()
    }

    const payload = {
      title: editTaskTitle.value.trim(),
      content: editTaskContent.value.trim() || null,
      is_completed: editTaskIsCompleted.value,
      start_time,
      end_time,
      priority: editTaskPriority.value,
    }

    const res = await apiClient.put<TaskItem>(`/tasks/${editingTask.value.id}`, payload)
    const idx = dayTasks.value.findIndex((t) => t.id === editingTask.value?.id)
    if (idx !== -1) {
      dayTasks.value[idx] = res.data
    }
    showEditTaskModal.value = false
    editingTask.value = null
    await fetchOccurrences()
    if (ganttViewRef.value) {
      await ganttViewRef.value.fetchDayTasks()
    }
  } catch (err) {
    console.error('Failed to update task:', err)
  } finally {
    updatingTask.value = false
  }
}


// Open Auto-Generate Rule Modal for creation
function openAutoRuleModal() {
  selectedEvent.value = null
  showAutoRuleModal.value = true
}

// Open Single Day Note Modal for creation
function openSingleDayModal(day: CalendarDay) {
  selectedEvent.value = null
  selectedDay.value = day
  singleNoteTitle.value = ''
  singleNoteContent.value = ''
  singleNoteImages.value = []
  singleNoteDisplayType.value = 'DATE'
  singleNoteTargetDate.value = day.dateStr
  showNoteModal.value = true
}

// Open Task Modal directly from Day-Gantt view
function handleGanttAddTask(dateStr: string) {
  selectedEvent.value = null
  selectedDay.value = calendarDays.value.find((d) => d.dateStr === dateStr) || null
  singleNoteTargetDate.value = dateStr
  newTaskTitle.value = ''
  newTaskContent.value = ''
  fetchTasksForDay(dateStr)
  showTaskModal.value = true
}


// Open Edit Modal when clicking on an existing event/note/task
function openEventEditModal(evt: EventOccurrence) {
  selectedEvent.value = evt
  selectedDay.value = calendarDays.value.find((d) => d.dateStr === evt.date) || null

  if (evt.category === 'note') {
    singleNoteTitle.value = evt.title
    singleNoteContent.value = evt.milestone_info || ''
    singleNoteImages.value = evt.image_url ? [evt.image_url] : []
    singleNoteDisplayType.value = 'DATE'
    singleNoteTargetDate.value = evt.date
    showNoteModal.value = true
  } else if (evt.category === 'task') {
    singleNoteTargetDate.value = evt.date
    fetchTasksForDay(evt.date)
    showTaskModal.value = true
  } else {
    showAutoRuleModal.value = true
  }
}

function handleDeleteFromModal(evt: EventOccurrence) {
  selectedEvent.value = evt
  showDeleteConfirmModal.value = true
}

// Save (Create or Update) Single-Day Note
async function handleSaveSingleDayNote() {
  if (!singleNoteContent.value.trim()) return

  submittingNote.value = true
  try {
    const targetDate = singleNoteDisplayType.value === 'DATE' ? singleNoteTargetDate.value : null
    const payload = {
      title: singleNoteTitle.value.trim() || `Note ${singleNoteTargetDate.value}`,
      content: singleNoteContent.value.trim(),
      image_urls: singleNoteImages.value,
      image_url: singleNoteImages.value[0] || null,
      category: 'memory',
      display_type: singleNoteDisplayType.value,
      target_date: targetDate,
    }
    if (selectedEvent.value && selectedEvent.value.category === 'note') {
      await apiClient.put(`/notes/${selectedEvent.value.event_id}`, payload)
    } else {
      await apiClient.post('/notes', payload)
    }
    showNoteModal.value = false
    selectedEvent.value = null
    await fetchOccurrences()
  } catch (err) {
    console.error('Failed to save note for calendar day:', err)
  } finally {
    submittingNote.value = false
  }
}

// Delete Event / Note
async function confirmDeleteEvent() {
  if (!selectedEvent.value) return

  deletingEvent.value = true
  try {
    if (selectedEvent.value.category === 'note') {
      await apiClient.delete(`/notes/${selectedEvent.value.event_id}`)
    } else if (selectedEvent.value.category === 'task') {
      await apiClient.delete(`/tasks/${selectedEvent.value.event_id}`)
    } else {
      await apiClient.delete(`/events/${selectedEvent.value.event_id}`)
    }
    showDeleteConfirmModal.value = false
    showNoteModal.value = false
    showTaskModal.value = false
    showAutoRuleModal.value = false
    selectedEvent.value = null
    await fetchOccurrences()

  } catch (err) {
    console.error('Failed to delete event/note/task:', err)
  } finally {
    deletingEvent.value = false
  }
}

</script>

<template>
  <div class="space-y-3 select-none">

    <!-- Top Sub-Nav Switcher (size: sm) placed above table card -->
    <div class="flex items-center justify-between gap-3">
      <div class="inline-flex items-center gap-1.5 p-1 bg-white border border-border rounded-2xl shadow-card">
        <button
          type="button"
          @click="mainViewMode = 'calendar'"
          class="px-3.5 py-2 text-xs sm:text-sm font-semibold rounded-xl transition-all flex items-center gap-2 cursor-pointer"
          :class="mainViewMode === 'calendar' ? 'bg-violet-50 text-violet-700 font-bold shadow-2xs' : 'text-ink-muted hover:text-ink hover:bg-surface-raised'"
        >
          <CalendarIcon class="w-4 h-4" />
          <span>{{ t('calendar.subnav.calendar') }}</span>
        </button>
        <button
          type="button"
          @click="mainViewMode = 'gantt'"
          class="px-3.5 py-2 text-xs sm:text-sm font-semibold rounded-xl transition-all flex items-center gap-2 cursor-pointer"
          :class="mainViewMode === 'gantt' ? 'bg-violet-50 text-violet-700 font-bold shadow-2xs' : 'text-ink-muted hover:text-ink hover:bg-surface-raised'"
        >
          <Clock class="w-4 h-4" />
          <span>{{ t('calendar.subnav.gantt') }}</span>
        </button>
      </div>
    </div>

    <!-- Main Calendar & Gantt Card Container (Expanded to fill available viewport height) -->
    <div class="w-full flex flex-col bg-white border border-border rounded-2xl shadow-card overflow-hidden min-h-[calc(100vh-210px)] h-[calc(100vh-210px)]">

      <!-- Header Toolbar inside card -->
      <div class="h-14 px-6 border-b border-border/60 flex items-center justify-between bg-white shrink-0">

        <!-- Left: Title / Loading indicator -->
        <div class="flex items-center gap-2.5">
          <h2 class="text-sm sm:text-base font-semibold text-ink capitalize tracking-tight">
            {{ mainViewMode === 'calendar' ? headerLabel : ganttHeaderLabel }}
          </h2>
          <span
            v-if="loading"
            class="text-xs text-ink-faint font-mono animate-pulse"
          >
            {{ t('calendar.loading') }}
          </span>
        </div>

      <!-- Right: Calendar Controls (Only shown in Calendar mode) -->
      <div v-if="mainViewMode === 'calendar'" class="flex items-center gap-1.5">

        <!-- Month / Week tab toggle -->
        <div class="flex items-center gap-0.5 p-0.5 bg-surface-subtle border border-border/60 rounded-xl">
          <AppButton
            variant="ghost"
            size="sm"
            @click="viewMode = 'month'"
            class="px-2.5 py-1 text-xs sm:text-sm font-normal rounded-lg transition-all"
            :class="viewMode === 'month' ? '!bg-white !text-violet-700 font-medium !shadow-2xs' : '!text-ink-muted'"
          >
            {{ t('calendar.monthView') }}
          </AppButton>
          <AppButton
            variant="ghost"
            size="sm"
            @click="switchToCurrentWeek"
            class="px-2.5 py-1 text-xs sm:text-sm font-normal rounded-lg transition-all"
            :class="viewMode === 'week' ? '!bg-white !text-violet-700 font-medium !shadow-2xs' : '!text-ink-muted'"
          >
            {{ t('calendar.weekView') }}
          </AppButton>
        </div>

        <!-- Auto Generate button -->
        <AppButton
          variant="ghost"
          size="sm"
          @click="openAutoRuleModal"
          :title="t('calendar.autoGenerate')"
          class="!px-2.5 !py-1 text-ink-muted hover:!text-violet-600 hover:!bg-violet-50"
        >
          <Sparkles class="w-4 h-4 text-amber-500" />
        </AppButton>

        <!-- Today button -->
        <AppButton
          variant="ghost"
          size="sm"
          @click="goToday"
          class="!px-2.5 !py-1 text-xs sm:text-sm font-normal text-ink-muted hover:!text-ink"
        >
          {{ t('calendar.today') }}
        </AppButton>

        <!-- Prev / Next navigation -->
        <div class="flex items-center gap-0.5">
          <AppButton
            variant="ghost"
            size="sm"
            @click="prevStep"
            class="!p-1.5 text-ink-muted hover:!text-ink"
          >
            <ChevronLeft class="w-4.5 h-4.5" />
          </AppButton>
          <AppButton
            variant="ghost"
            size="sm"
            @click="nextStep"
            class="!p-1.5 text-ink-muted hover:!text-ink"
          >
            <ChevronRight class="w-4.5 h-4.5" />
          </AppButton>
        </div>

      </div>

      <!-- Right: Day-Gantt Controls (Cloned UI 1:1 with Calendar Header style) -->
      <div v-else-if="mainViewMode === 'gantt'" class="flex items-center gap-1.5">
        <!-- Add Task Icon Button -->
        <!-- Focus to Current Time Icon Button -->
        <AppButton
          variant="ghost"
          size="sm"
          @click="handleFocusNow"
          :title="t('calendar.gantt.focusNow')"
          class="!px-2.5 !py-1 text-ink-muted hover:!text-violet-600 hover:!bg-violet-50"
        >
          <PawPrint class="w-4 h-4 text-violet-600" />

        </AppButton>
        <AppButton
          variant="ghost"
          size="sm"
          @click="handleGanttAddTask(ganttActiveDateStr)"
          :title="t('calendar.gantt.addTask')"
          class="!px-2.5 !py-1 text-ink-muted hover:!text-violet-600 hover:!bg-violet-50"
        >
          <Sparkles class="w-4 h-4 text-amber-500" />
        </AppButton>


        <!-- Today button -->
        <AppButton
          variant="ghost"
          size="sm"
          @click="ganttGoToday"
          class="!px-2.5 !py-1 text-xs sm:text-sm font-normal text-ink-muted hover:!text-ink"
        >
          {{ t('calendar.today') }}
        </AppButton>

        <!-- Prev / Next navigation -->
        <div class="flex items-center gap-0.5">
          <AppButton
            variant="ghost"
            size="sm"
            @click="ganttPrevDay"
            class="!p-1.5 text-ink-muted hover:!text-ink"
          >
            <ChevronLeft class="w-4.5 h-4.5" />
          </AppButton>
          <AppButton
            variant="ghost"
            size="sm"
            @click="ganttNextDay"
            class="!p-1.5 text-ink-muted hover:!text-ink"
          >
            <ChevronRight class="w-4.5 h-4.5" />
          </AppButton>
        </div>
      </div>


    </div>

    <!-- SUB-VIEW 1: Scrollable Calendar Grid Area -->
    <div v-if="mainViewMode === 'calendar'" class="flex-1 overflow-x-auto flex flex-col">
      <div class="flex-1 flex flex-col min-w-[800px]">

        <!-- Weekdays Header Row -->
        <div class="grid grid-cols-7 border-b border-border/60 bg-surface-subtle/40 shrink-0">
          <div
            v-for="wd in weekDays"
            :key="wd"
            class="py-2.5 text-center text-xs font-medium uppercase tracking-wider text-ink-muted"
          >
            {{ wd }}
          </div>
        </div>

        <!-- Days Grid -->
        <div class="flex-1 grid grid-cols-7 divide-x divide-y divide-border/40 min-h-0 bg-white">
          <div
            v-for="(day, idx) in calendarDays"
            :key="idx"
            class="p-2.5 flex flex-col gap-1.5 transition-colors cursor-pointer group relative overflow-hidden"
            :class="[
              viewMode === 'week' ? 'min-h-[220px]' : 'min-h-[105px]',
              !day.isCurrentMonth && viewMode === 'month'
                ? 'bg-surface-subtle/40'
                : 'bg-white hover:bg-violet-50/30',
              day.isToday ? 'bg-violet-50/50' : '',
            ]"
          >
            <!-- Day number row -->
            <div class="flex items-center justify-between">
              <span
                class="w-6 h-6 rounded-full flex items-center justify-center text-xs sm:text-[13px] font-normal transition-all"
                :class="[
                  day.isToday
                    ? 'bg-violet-600 text-white font-medium'
                    : !day.isCurrentMonth && viewMode === 'month'
                      ? 'text-ink-faint'
                      : 'text-ink-muted group-hover:text-violet-700',
                ]"
              >
                {{ day.dayNumber }}
              </span>

              <!-- Add note — ghost plus, hidden until hover -->
              <button
                type="button"
                @click.stop="openSingleDayModal(day)"
                class="opacity-0 group-hover:opacity-100 w-5 h-5 flex items-center justify-center rounded-lg text-ink-faint hover:text-violet-600 hover:bg-white transition-all cursor-pointer"
                :title="t('calendar.tabs.note')"
              >
                <Plus class="w-3.5 h-3.5" />
              </button>
            </div>

            <!-- Events — soft pill badges, normal weight text, click to edit (Only Note & Love) -->
            <div class="flex flex-col gap-1 overflow-y-auto min-h-0">
              <div
                v-for="evt in day.events.filter(e => e.category !== 'task')"
                :key="evt.event_id + evt.title"
                @click.stop="openEventEditModal(evt)"
                class="px-2 py-1.5 rounded-md text-xs font-normal truncate flex items-center gap-1.5 cursor-pointer transition-opacity hover:opacity-85"
                :class="[
                  evt.category === 'note'
                    ? 'bg-violet-100/90 text-violet-800'
                    : 'bg-rose-100/90 text-rose-700'
                ]"
              >
                <StickyNote v-if="evt.category === 'note'" class="w-3 h-3 shrink-0" />
                <Heart v-else class="w-3 h-3 fill-current shrink-0" />
                <span class="truncate">{{ evt.title }}</span>
              </div>
            </div>


          </div>
        </div>

      </div>
    </div>

    <!-- SUB-VIEW 2: Day-Gantt Schedule Timeline -->
    <div v-else-if="mainViewMode === 'gantt'" class="flex-1 overflow-hidden flex flex-col">
      <DayGanttView
        ref="ganttViewRef"
        :active-date="ganttActiveDateStr"
        @add-task="handleGanttAddTask"
        @task-updated="fetchOccurrences"
      />
    </div>

    </div>

    <!-- Modal 1: Auto-Generate Rules (Create or Edit) -->
    <AutoRuleModal
      :show="showAutoRuleModal"
      :selected-event="selectedEvent"
      @close="showAutoRuleModal = false"
      @saved="fetchOccurrences"
      @delete="handleDeleteFromModal"
    />

    <!-- Modal 2: Independent Note Modal (Create or Edit Single Day Note) -->
    <AppModal
      :show="showNoteModal"
      :title="selectedEvent && selectedEvent.category === 'note' ? t('common.edit') : t('calendar.modalSingleTitle', { date: selectedDay?.dateStr || singleNoteTargetDate })"
      width="880"
      @close="showNoteModal = false"
    >
      <form @submit.prevent="handleSaveSingleDayNote" class="space-y-4">
        <AppInput
          v-model="singleNoteTitle"
          :label="t('notes.noteTitle')"
          :placeholder="t('notes.noteTitlePlaceholder')"
          required
        />

        <!-- AppSelect for Display Type / Status and Target Date Input -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <AppSelect
            v-model="singleNoteDisplayType"
            :label="t('notes.statusLabel')"
            :options="[
              { label: t('notes.statusOptions.date'), value: 'DATE' },
              { label: t('notes.statusOptions.random'), value: 'RANDOM' },
            ]"
          />

          <div v-if="singleNoteDisplayType === 'DATE'">
            <AppInput
              v-model="singleNoteTargetDate"
              type="date"
              :label="t('notes.targetDateLabel')"
              required
            />
          </div>
        </div>

        <!-- Native UI Image Upload (File Upload & 1-N Media Dropzone) -->
        <AppImageUpload
          v-model="singleNoteImages"
          :multiple="true"
          :max-files="5"
          :label="t('notes.imageUploadLabel')"
        />

        <AppTextarea
          v-model="singleNoteContent"
          :label="t('notes.contentLabel')"
          :placeholder="t('notes.contentPlaceholder')"
          :rows="4"
          required
        />

        <div class="flex items-center justify-between pt-2 border-t border-border">
          <div>
            <AppButton
              v-if="selectedEvent && selectedEvent.category === 'note'"
              variant="outline"
              type="button"
              size="sm"
              class="text-err-text hover:bg-err-bg border-err-border"
              @click="showDeleteConfirmModal = true"
            >
              <Trash2 class="w-3.5 h-3.5 mr-1" />
              {{ t('common.delete') }}
            </AppButton>
          </div>
          <div class="flex gap-2">
            <AppButton variant="outline" type="button" size="sm" @click="showNoteModal = false">
              {{ t('common.cancel') }}
            </AppButton>
            <AppButton type="submit" size="sm" :loading="submittingNote">
              {{ selectedEvent ? t('common.save') : t('common.create') }}
            </AppButton>
          </div>
        </div>
      </form>
    </AppModal>

    <!-- Modal 3: Independent Day Tasks Modal (Add & List Tasks for a Day) -->
    <AppModal
      :show="showTaskModal"
      :title="`${t('calendar.tabs.tasks')} — ${selectedDay?.dateStr || singleNoteTargetDate}`"
      width="880"
      @close="showTaskModal = false"
    >
      <div class="space-y-4">
        <!-- Add Task Form -->
        <div class="p-4 rounded-xl border border-border/80 bg-surface-subtle/30 space-y-3.5">
          <AppInput
            v-model="newTaskTitle"
            :label="t('calendar.tasks.taskTitle')"
            :placeholder="t('calendar.tasks.taskTitlePlaceholder')"
            required
          />

          <!-- Start Time & End Time (Set sẵn theo ngày của cell, chỉ chọn giờ) + Priority -->
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div class="w-full space-y-1.5">
              <label class="block text-xs font-bold text-ink tracking-wider uppercase">
                {{ t('calendar.tasks.startTime') }}
              </label>
              <div class="relative flex items-center">
                <input
                  type="time"
                  v-model="newTaskStartTime"
                  class="w-full px-3.5 py-2.5 text-sm font-medium bg-white border border-border rounded-xl text-ink shadow-2xs hover:border-violet-300 focus:outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-400/20"
                />
              </div>
            </div>

            <div class="w-full space-y-1.5">
              <label class="block text-xs font-bold text-ink tracking-wider uppercase">
                {{ t('calendar.tasks.endTime') }}
              </label>
              <div class="relative flex items-center">
                <input
                  type="time"
                  v-model="newTaskEndTime"
                  class="w-full px-3.5 py-2.5 text-sm font-medium bg-white border border-border rounded-xl text-ink shadow-2xs hover:border-violet-300 focus:outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-400/20"
                />
              </div>
            </div>

            <AppSelect
              v-model="newTaskPriority"
              :label="t('calendar.tasks.priority')"
              :options="[
                { label: t('calendar.tasks.priorityLow'), value: 'low' },
                { label: t('calendar.tasks.priorityMedium'), value: 'medium' },
                { label: t('calendar.tasks.priorityHigh'), value: 'high' },
                { label: t('calendar.tasks.priorityUrgent'), value: 'urgent' },
              ]"
            />
          </div>

          <AppTextarea
            v-model="newTaskContent"
            :label="t('calendar.tasks.content')"
            :placeholder="t('calendar.tasks.contentPlaceholder')"
            :rows="2"
          />

          <div class="flex justify-end pt-1">
            <AppButton
              type="button"
              size="sm"
              :loading="addingTask"
              :disabled="!newTaskTitle.trim()"
              @click="handleCreateTaskForDay"
              class="!bg-violet-600 hover:!bg-violet-700 text-white font-medium cursor-pointer"
            >
              <Plus class="w-3.5 h-3.5 mr-1" />
              {{ t('calendar.tasks.addTask') }}
            </AppButton>
          </div>
        </div>

        <!-- Nested Task List Section (Thêm tự động hiển thị bên dưới) -->
        <div class="space-y-2 pt-2 border-t border-border">
          <h4 class="text-xs font-bold uppercase tracking-wider text-ink-muted">
            {{ t('calendar.tasks.listTitle', { date: selectedDay?.dateStr || singleNoteTargetDate, count: dayTasks.length }) }}
          </h4>

          <div v-if="loadingDayTasks" class="py-6 text-center text-xs text-ink-faint animate-pulse">
            {{ t('calendar.loading') }}
          </div>

          <div
            v-else-if="dayTasks.length === 0"
            class="py-6 px-4 text-center rounded-xl border border-dashed border-border/80 bg-surface-subtle/20 text-xs text-ink-muted"
          >
            {{ t('calendar.tasks.noTasks') }}
          </div>

          <div v-else class="space-y-2 max-h-64 overflow-y-auto pr-1">
            <div
              v-for="task in dayTasks"
              :key="task.id"
              class="p-3 rounded-xl border border-border/70 bg-white hover:border-violet-200 transition-all flex items-start gap-3 group shadow-2xs"
              :class="task.is_completed ? 'bg-surface-subtle/30 opacity-75' : ''"
            >
              <!-- Toggle complete checkbox button -->
              <button
                type="button"
                @click="handleToggleTaskStatus(task)"
                class="mt-0.5 text-ink-faint hover:text-violet-600 transition-colors cursor-pointer shrink-0"
                :title="task.is_completed ? t('calendar.tasks.completed') : t('calendar.tasks.pending')"
              >
                <CheckSquare v-if="task.is_completed" class="w-4 h-4 text-emerald-600" />
                <Square v-else class="w-4 h-4" />
              </button>

              <!-- Task main info -->
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 flex-wrap">
                  <span
                    class="text-sm font-semibold text-ink truncate"
                    :class="task.is_completed ? 'line-through text-ink-muted' : ''"
                  >
                    {{ task.title }}
                  </span>

                  <!-- Priority Badge -->
                  <AppBadge
                    :variant="task.priority === 'urgent' ? 'err' : task.priority === 'high' ? 'warn' : task.priority === 'low' ? 'neutral' : 'info'"
                    size="sm"
                  >
                    {{ task.priority }}
                  </AppBadge>

                  <!-- Time Range Badge -->
                  <span
                    v-if="task.start_time || task.end_time"
                    class="inline-flex items-center gap-1 text-[11px] text-ink-muted font-mono bg-surface-subtle px-1.5 py-0.5 rounded-md border border-border/50"
                  >
                    <Clock class="w-3 h-3 text-violet-500" />
                    {{ formatTaskTime(task.start_time) }}
                    <template v-if="task.end_time"> - {{ formatTaskTime(task.end_time) }}</template>
                  </span>
                </div>

                <p v-if="task.content" class="text-xs text-ink-muted mt-1 whitespace-pre-line leading-relaxed">
                  {{ task.content }}
                </p>
              </div>

              <!-- Action buttons on hover (Edit on left, Delete on right) -->
              <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-all shrink-0">
                <button
                  type="button"
                  @click="openEditTaskModal(task)"
                  class="text-ink-faint hover:text-violet-600 transition-colors p-1 rounded-lg hover:bg-violet-50 cursor-pointer"
                  :title="t('calendar.tasks.editTask')"
                >
                  <Pencil class="w-3.5 h-3.5" />
                </button>
                <button
                  type="button"
                  @click="handleDeleteTask(task)"
                  :disabled="deletingTaskId === task.id"
                  class="text-ink-faint hover:text-rose-600 transition-colors p-1 rounded-lg hover:bg-rose-50 cursor-pointer"
                  :title="t('common.delete')"
                >
                  <Trash2 class="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </AppModal>

    <!-- Modal: Update Task Modal -->
    <AppModal
      :show="showEditTaskModal"
      :title="t('calendar.tasks.editTask')"
      width="880"
      @close="showEditTaskModal = false"
    >
      <form @submit.prevent="handleUpdateTask" class="space-y-4">
        <AppInput
          v-model="editTaskTitle"
          :label="t('calendar.tasks.taskTitle')"
          :placeholder="t('calendar.tasks.taskTitlePlaceholder')"
          required
        />

        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div class="w-full space-y-1.5">
            <label class="block text-xs font-bold text-ink tracking-wider uppercase">
              {{ t('calendar.tasks.startTime') }}
            </label>
            <input
              type="time"
              v-model="editTaskStartTime"
              class="w-full px-3.5 py-2.5 text-sm font-medium bg-white border border-border rounded-xl text-ink shadow-2xs hover:border-violet-300 focus:outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-400/20"
            />
          </div>

          <div class="w-full space-y-1.5">
            <label class="block text-xs font-bold text-ink tracking-wider uppercase">
              {{ t('calendar.tasks.endTime') }}
            </label>
            <input
              type="time"
              v-model="editTaskEndTime"
              class="w-full px-3.5 py-2.5 text-sm font-medium bg-white border border-border rounded-xl text-ink shadow-2xs hover:border-violet-300 focus:outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-400/20"
            />
          </div>

          <AppSelect
            v-model="editTaskPriority"
            :label="t('calendar.tasks.priority')"
            :options="[
              { label: t('calendar.tasks.priorityLow'), value: 'low' },
              { label: t('calendar.tasks.priorityMedium'), value: 'medium' },
              { label: t('calendar.tasks.priorityHigh'), value: 'high' },
              { label: t('calendar.tasks.priorityUrgent'), value: 'urgent' },
            ]"
          />
        </div>

        <AppTextarea
          v-model="editTaskContent"
          :label="t('calendar.tasks.content')"
          :placeholder="t('calendar.tasks.contentPlaceholder')"
          :rows="3"
        />

        <div class="flex items-center justify-between pt-2 border-t border-border">
          <div class="flex items-center gap-2">
            <label class="flex items-center gap-2 text-xs font-medium text-ink cursor-pointer">
              <input
                type="checkbox"
                v-model="editTaskIsCompleted"
                class="rounded text-violet-600 focus:ring-violet-500 w-4 h-4"
              />
              <span>{{ t('calendar.tasks.completed') }}</span>
            </label>
          </div>
          <div class="flex gap-2">
            <AppButton variant="outline" type="button" size="sm" @click="showEditTaskModal = false">
              {{ t('common.cancel') }}
            </AppButton>
            <AppButton type="submit" size="sm" :loading="updatingTask">
              {{ t('common.save') }}
            </AppButton>
          </div>
        </div>
      </form>
    </AppModal>

    <!-- Delete Confirm Modal for Note/Event in Calendar -->

    <AppConfirmModal
      :show="showDeleteConfirmModal"
      :title="t('notes.deleteTitle')"
      :message="t('notes.deleteMessage')"
      :confirmText="t('notes.deleteConfirm')"
      :cancelText="t('common.cancel')"
      variant="danger"
      :loading="deletingEvent"
      @confirm="confirmDeleteEvent"
      @close="showDeleteConfirmModal = false"
    />

  </div>
</template>
