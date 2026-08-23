<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { apiClient } from '@/services/apiClient'
import { useAuthStore } from '@/stores/authStore'
import {
  CheckSquare,
  Clock,
  Pencil,
  Square,
  Trash2,
  ZoomIn,
  ZoomOut,
  Heart,
} from 'lucide-vue-next'


import AppButton from '@/components/ui/AppButton.vue'
import AppModal from '@/components/ui/AppModal.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppSelect from '@/components/ui/AppSelect.vue'
import AppTextarea from '@/components/ui/AppTextarea.vue'
import AppSwitch from '@/components/ui/AppSwitch.vue'
import type { TaskItem } from '../types'

interface Props {
  activeDate?: string
  initialDate?: string
  viewMode?: 'my' | 'partner' | 'combined'
}

const props = withDefaults(defineProps<Props>(), {
  activeDate: '',
  initialDate: '',
  viewMode: 'combined',
})

const emit = defineEmits<{
  (e: 'addTask', dateStr: string): void
  (e: 'taskUpdated'): void
}>()

const { t } = useI18n()
const authStore = useAuthStore()
const currentUserId = computed(() => authStore.user?.id)

// Active Day State
const activeDateStr = ref(props.activeDate || props.initialDate || new Date().toISOString().split('T')[0])
const tasks = ref<TaskItem[]>([])

const filteredTasks = computed(() => {
  if (props.viewMode === 'my') {
    return tasks.value.filter((t) => !currentUserId.value || t.user_id === currentUserId.value)
  }
  if (props.viewMode === 'partner') {
    return tasks.value.filter((t) => Boolean(currentUserId.value && t.user_id !== currentUserId.value))
  }
  return tasks.value
})

function isPartnerTask(task: TaskItem): boolean {
  return Boolean(currentUserId.value && task.user_id !== currentUserId.value)
}

const loading = ref(false)
const deletingTaskId = ref<string | null>(null)

// Current time marker state
const currentMinutes = ref(getCurrentMinutes())
let timerInterval: number | null = null

function getCurrentMinutes(): number {
  const now = new Date()
  return now.getHours() * 60 + now.getMinutes()
}

const isToday = computed(() => {
  const todayStr = new Date().toISOString().split('T')[0]
  return activeDateStr.value === todayStr
})

const currentTimePercent = computed(() => {
  return (currentMinutes.value / 1440) * 100
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

// Fetch tasks for the active date
async function fetchDayTasks() {
  loading.value = true
  try {
    const res = await apiClient.get<TaskItem[]>('/tasks')
    tasks.value = res.data
      .filter((t) => {
        if (t.start_time) {
          return getLocalDateStr(t.start_time) === activeDateStr.value
        }
        if (t.created_at) {
          return getLocalDateStr(t.created_at) === activeDateStr.value
        }
        return false
      })
      .sort((a, b) => {
        const timeA = a.start_time ? new Date(a.start_time).getTime() : 0
        const timeB = b.start_time ? new Date(b.start_time).getTime() : 0
        return timeA - timeB
      })
  } catch (err) {
    console.error('Failed to fetch tasks for Gantt:', err)
  } finally {
    loading.value = false
  }
}

watch(
  () => [props.activeDate, props.initialDate],
  ([newActive, newInit]) => {
    const val = newActive || newInit
    if (val) {
      activeDateStr.value = val
    }
  },
)


// Gantt Bar Position calculation
function getGanttBarStyle(task: TaskItem) {
  let startMinutes = 0
  let durationMinutes = 60 // default 1 hour if not specified

  if (task.start_time) {
    const s = new Date(task.start_time)
    startMinutes = s.getHours() * 60 + s.getMinutes()
  }

  if (task.start_time && task.end_time) {
    const s = new Date(task.start_time).getTime()
    const e = new Date(task.end_time).getTime()
    if (e > s) {
      durationMinutes = Math.max(15, Math.round((e - s) / 60000))
    }
  }

  const leftPercent = Math.max(0, Math.min(100, (startMinutes / 1440) * 100))
  const widthPercent = Math.max(2.5, Math.min(100 - leftPercent, (durationMinutes / 1440) * 100))

  return {
    left: `${leftPercent}%`,
    width: `${widthPercent}%`,
  }
}

// Format time string to HH:MM
function formatTimeOnly(timeInput?: string | Date | null): string {
  if (!timeInput) return ''
  try {
    const d = new Date(timeInput)
    if (isNaN(d.getTime())) return ''
    const hours = String(d.getHours()).padStart(2, '0')
    const minutes = String(d.getMinutes()).padStart(2, '0')
    return `${hours}:${minutes}`
  } catch {
    return ''
  }
}

// Toggle Task Status
async function toggleTask(task: TaskItem) {
  try {
    const res = await apiClient.patch<TaskItem>(`/tasks/${task.id}/toggle`)
    task.is_completed = res.data.is_completed
    emit('taskUpdated')
  } catch (err) {
    console.error('Failed to toggle task:', err)
  }
}

// Delete Task
async function deleteTask(task: TaskItem) {
  deletingTaskId.value = task.id
  try {
    await apiClient.delete(`/tasks/${task.id}`)
    tasks.value = tasks.value.filter((t) => t.id !== task.id)
    emit('taskUpdated')
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
const editTaskIsShared = ref(true)
const updatingTask = ref(false)

function openEditTaskModal(task: TaskItem) {
  editingTask.value = task
  editTaskTitle.value = task.title
  editTaskStartTime.value = formatTimeOnly(task.start_time) || '09:00'
  editTaskEndTime.value = formatTimeOnly(task.end_time) || '10:00'
  editTaskPriority.value = task.priority || 'medium'
  editTaskContent.value = task.content || ''
  editTaskIsCompleted.value = task.is_completed
  editTaskIsShared.value = task.is_shared !== undefined ? task.is_shared : true
  showEditTaskModal.value = true
}

async function handleUpdateTask() {
  if (!editingTask.value || !editTaskTitle.value.trim()) return

  updatingTask.value = true
  try {
    let start_time: string | null = null
    let end_time: string | null = null

    if (editTaskStartTime.value) {
      start_time = new Date(`${activeDateStr.value}T${editTaskStartTime.value}:00`).toISOString()
    }
    if (editTaskEndTime.value) {
      end_time = new Date(`${activeDateStr.value}T${editTaskEndTime.value}:00`).toISOString()
    }

    const payload = {
      title: editTaskTitle.value.trim(),
      content: editTaskContent.value.trim() || null,
      is_completed: editTaskIsCompleted.value,
      is_shared: editTaskIsShared.value,
      start_time,
      end_time,
      priority: editTaskPriority.value,
    }

    const res = await apiClient.put<TaskItem>(`/tasks/${editingTask.value.id}`, payload)
    const idx = tasks.value.findIndex((t) => t.id === editingTask.value?.id)
    if (idx !== -1) {
      tasks.value[idx] = res.data
    }
    showEditTaskModal.value = false
    editingTask.value = null
    emit('taskUpdated')
  } catch (err) {
    console.error('Failed to update task:', err)
  } finally {
    updatingTask.value = false
  }
}

// Priority styling helper for timeline bars

function getPriorityBarClass(priority: string, isCompleted: boolean, isPartner: boolean = false): string {
  if (isCompleted) {
    return 'bg-emerald-500/85 text-white border-emerald-600/30'
  }
  if (isPartner) {
    switch (priority) {
      case 'urgent':
        return 'bg-rose-500 text-white shadow-xs'
      case 'high':
        return 'bg-pink-500 text-white shadow-xs'
      case 'low':
        return 'bg-pink-400 text-white shadow-xs'
      default:
        return 'bg-pink-500 text-white shadow-xs'
    }
  }
  switch (priority) {
    case 'urgent':
      return 'bg-rose-500 text-white shadow-xs'
    case 'high':
      return 'bg-amber-500 text-white shadow-xs'
    case 'low':
      return 'bg-slate-500 text-white shadow-xs'
    default:
      return 'bg-violet-600 text-white shadow-xs'
  }
}

// Zoom State (Default 1.5x - 150% as requested, cells are 1.5x wider)
const zoomLevel = ref(1.5)
const hourCellWidth = computed(() => Math.round(60 * (zoomLevel.value / 1.5)))
const timelineTrackWidth = computed(() => `${24 * hourCellWidth.value}px`)

// Time marks 0 to 24 (all 24 hours)
const timeMarks = Array.from({ length: 25 }, (_, i) => i)

function handleWheelZoom(e: WheelEvent) {
  if (e.ctrlKey || e.metaKey || (e.target as HTMLElement)?.closest('.gantt-header-axis')) {
    e.preventDefault()
    const delta = e.deltaY < 0 ? 0.15 : -0.15
    zoomLevel.value = Math.min(3.5, Math.max(0.8, +(zoomLevel.value + delta).toFixed(2)))
  }
}

function zoomIn() {
  zoomLevel.value = Math.min(3.5, +(zoomLevel.value + 0.25).toFixed(2))
}

function zoomOut() {
  zoomLevel.value = Math.max(0.8, +(zoomLevel.value - 0.25).toFixed(2))
}

function resetZoom() {
  zoomLevel.value = 1.5
}

const leftPaneRef = ref<HTMLDivElement | null>(null)
const rightPaneRef = ref<HTMLDivElement | null>(null)
let isSyncingScroll = false

function syncScrollFromLeft() {
  if (isSyncingScroll || !leftPaneRef.value || !rightPaneRef.value) return
  isSyncingScroll = true
  rightPaneRef.value.scrollTop = leftPaneRef.value.scrollTop
  requestAnimationFrame(() => {
    isSyncingScroll = false
  })
}

function syncScrollFromRight() {
  if (isSyncingScroll || !leftPaneRef.value || !rightPaneRef.value) return
  isSyncingScroll = true
  leftPaneRef.value.scrollTop = rightPaneRef.value.scrollTop
  requestAnimationFrame(() => {
    isSyncingScroll = false
  })
}

function scrollToNow() {
  if (!rightPaneRef.value) return
  const container = rightPaneRef.value
  const totalTrackWidth = 24 * hourCellWidth.value
  const currentPixelOffset = (currentTimePercent.value / 100) * totalTrackWidth
  const visibleTimelineWidth = container.clientWidth
  const targetScrollLeft = Math.max(0, currentPixelOffset - visibleTimelineWidth / 2)
  container.scrollTo({
    left: targetScrollLeft,
    behavior: 'smooth',
  })
}

watch(activeDateStr, () => {
  fetchDayTasks()
})

onMounted(() => {
  fetchDayTasks()
  timerInterval = window.setInterval(() => {
    currentMinutes.value = getCurrentMinutes()
  }, 60000)
  if (isToday.value) {
    setTimeout(() => {
      scrollToNow()
    }, 150)
  }
})

onUnmounted(() => {
  if (timerInterval) {
    clearInterval(timerInterval)
  }
})

defineExpose({
  fetchDayTasks,
  activeDateStr,
  zoomLevel,
  scrollToNow,
})
</script>


<template>
  <div class="h-full w-full flex flex-col bg-white overflow-hidden select-none relative">

    <!-- Main 2-Pane Split Layout (Left Fixed Task Pane + Right Timeline Track Pane) -->
    <div class="flex-1 flex overflow-hidden">

      <!-- PANE 1: Left Fixed Task Column -->
      <div class="w-64 sm:w-72 shrink-0 flex flex-col border-r border-border/80 bg-white z-20 shadow-[1px_0_4px_-1px_rgba(0,0,0,0.04)]">
        <!-- Left Header -->
        <div class="h-10 px-4 flex items-center border-b border-border/80 bg-surface-subtle/50 text-[11px] font-bold text-ink-faint uppercase tracking-wider shrink-0">
          {{ t('calendar.gantt.taskColumn') }}
        </div>

        <!-- Left Task Rows -->
        <div
          ref="leftPaneRef"
          class="flex-1 overflow-y-auto overflow-x-hidden divide-y divide-border/40 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden"
          @scroll="syncScrollFromLeft"
        >
          <!-- Empty state -->
          <div
            v-if="filteredTasks.length === 0"
            class="h-56 flex flex-col items-center justify-center gap-2 text-center px-4"
          >
            <div class="w-8 h-8 rounded-xl bg-violet-50 flex items-center justify-center text-violet-500 border border-violet-100/70">
              <Clock class="w-4 h-4" />
            </div>
            <div>
              <p class="text-xs font-semibold text-ink">
                {{ viewMode === 'partner' ? t('calendar.gantt.noPartnerTasks') : viewMode === 'my' ? t('calendar.gantt.noMyTasks') : t('calendar.gantt.noTasks') }}
              </p>
              <p class="text-[10px] text-ink-faint mt-0.5 font-mono">{{ activeDateStr }}</p>
            </div>
          </div>

          <!-- Task Rows (Clean minimalist h-12 height) -->
          <div
            v-for="task in filteredTasks"
            :key="task.id"
            class="h-12 px-3.5 flex items-center gap-2 hover:bg-violet-50/30 transition-colors group"
            :class="task.is_completed ? 'bg-surface-subtle/30' : ''"
          >
            <!-- Toggle Complete Checkbox -->
            <button
              type="button"
              @click="toggleTask(task)"
              class="text-ink-faint hover:text-violet-600 transition-colors cursor-pointer shrink-0"
              :title="task.is_completed ? t('calendar.tasks.completed') : t('calendar.tasks.pending')"
            >
              <CheckSquare v-if="task.is_completed" class="w-4 h-4 text-emerald-600" />
              <Square v-else class="w-4 h-4 text-ink-muted hover:text-violet-600" />
            </button>

            <div class="min-w-0 flex-1">
              <div class="flex items-center gap-1.5 truncate">
                <!-- Partner Badge if in Combined View -->
                <span
                  v-if="viewMode === 'combined' && isPartnerTask(task)"
                  class="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded-md bg-pink-50 text-pink-700 border border-pink-200 text-[9px] font-bold shrink-0 leading-none"
                  :title="t('calendar.gantt.partnerBadge')"
                >
                  <Heart class="w-2.5 h-2.5 text-pink-500 fill-pink-500" />
                  <span>{{ t('calendar.gantt.partnerBadge') }}</span>
                </span>

                <span
                  class="text-sm font-semibold text-ink truncate leading-tight"
                  :class="task.is_completed ? 'line-through text-ink-faint' : ''"
                >
                  {{ task.title }}
                </span>
              </div>
            </div>

            <!-- Action buttons on hover -->
            <div class="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-all shrink-0">
              <button
                type="button"
                @click="openEditTaskModal(task)"
                class="p-1 rounded-md text-ink-faint hover:text-violet-600 hover:bg-violet-50 transition-all cursor-pointer shrink-0"
                :title="t('calendar.tasks.editTask')"
              >
                <Pencil class="w-3 h-3" />
              </button>

              <button
                type="button"
                @click="deleteTask(task)"
                :disabled="deletingTaskId === task.id"
                class="p-1 rounded-md text-ink-faint hover:text-rose-600 hover:bg-rose-50 transition-all cursor-pointer shrink-0"
                :title="t('common.delete')"
              >
                <Trash2 class="w-3 h-3" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- PANE 2: Right Timeline Track (Scrolls horizontally & vertically) -->
      <div
        ref="rightPaneRef"
        class="flex-1 overflow-x-auto overflow-y-auto flex flex-col bg-white"
        @scroll="syncScrollFromRight"
        @wheel="handleWheelZoom"
      >
        <!-- Timeline Header Axis (Sticky top) -->
        <div
          class="h-10 border-b border-border/80 bg-surface-subtle/50 text-[11px] font-mono text-ink-muted sticky top-0 z-10 shrink-0 flex items-center px-4 gantt-header-axis"
          :style="{ width: timelineTrackWidth, minWidth: timelineTrackWidth }"
        >
          <div class="relative w-full h-4 flex items-center">
            <div
              v-for="h in timeMarks"
              :key="h"
              class="absolute -translate-x-1/2 select-none"
              :class="h % 2 === 0 ? 'text-ink/80 font-semibold' : 'text-ink-faint font-normal'"
              :style="{ left: `${(h / 24) * 100}%` }"
            >
              {{ String(h).padStart(2, '0') }}:00
            </div>
          </div>
        </div>

        <!-- Timeline Grid & Rows Area -->
        <div
          class="relative flex-1 divide-y divide-border/40"
          :style="{ width: timelineTrackWidth, minWidth: timelineTrackWidth }"
        >
          <!-- Vertical Background Grid Lines -->
          <div class="absolute inset-0 pointer-events-none flex">
            <div
              v-for="h in timeMarks"
              :key="h"
              class="absolute top-0 bottom-0 border-r"
              :class="h % 2 === 0 ? 'border-border/40' : 'border-border/20 border-dashed'"
              :style="{ left: `${(h / 24) * 100}%` }"
            />
            <!-- Current Time Indicator Vertical Red Line with Dot -->
            <div
              v-if="isToday"
              class="absolute top-0 bottom-0 w-px bg-rose-500 z-10"
              :style="{ left: `${currentTimePercent}%` }"
            >
              <div class="w-2 h-2 rounded-full bg-rose-500 -ml-[3.5px] -mt-0.5 ring-2 ring-white shadow-xs" />
            </div>
          </div>

          <!-- Loading state -->
          <div v-if="loading" class="py-16 text-center text-xs text-ink-faint font-mono animate-pulse">
            {{ t('calendar.loading') }}
          </div>

          <!-- Empty state in Timeline -->
          <div
            v-else-if="filteredTasks.length === 0"
            class="h-56"
          />

          <!-- Task Rows in Timeline (Exact h-12 height matching Left Pane) -->
          <div
            v-for="task in filteredTasks"
            :key="task.id"
            class="h-12 px-4 flex items-center hover:bg-violet-50/30 transition-colors relative"
            :class="task.is_completed ? 'bg-surface-subtle/30' : ''"
          >
            <div class="relative w-full h-6 flex items-center gantt-timeline-track">
              <div
                class="absolute h-5 rounded-md transition-all shadow-2xs hover:shadow-md cursor-pointer select-none flex items-center px-2 overflow-hidden text-[10px] font-medium"
                :class="getPriorityBarClass(task.priority, task.is_completed, isPartnerTask(task))"
                :style="getGanttBarStyle(task)"
                :title="`${task.title} (${formatTimeOnly(task.start_time)} - ${formatTimeOnly(task.end_time)})\n${isPartnerTask(task) ? `[${t('calendar.gantt.partnerBadge')}] ` : ''}${task.content || ''}`"
                @click="openEditTaskModal(task)"
              >
              </div>
            </div>
          </div>
        </div>

      </div>

    </div>

    <!-- Floating Zoom Controls at Bottom Right -->
    <div class="absolute bottom-4 right-6 flex items-center gap-1 bg-white/90 backdrop-blur border border-border/80 rounded-xl p-1 shadow-md z-30">
      <button
        type="button"
        @click="zoomOut"
        :disabled="zoomLevel <= 0.8"
        class="w-7 h-7 flex items-center justify-center rounded-lg text-ink-muted hover:text-ink hover:bg-surface-subtle disabled:opacity-40 cursor-pointer"
        title="Zoom Out (Ctrl + Scroll Down)"
      >
        <ZoomOut class="w-3.5 h-3.5" />
      </button>

      <button
        type="button"
        @click="resetZoom"
        class="px-1.5 py-0.5 text-[11px] font-mono font-medium text-ink-muted hover:text-violet-600 cursor-pointer"
        title="Reset 150% Zoom"
      >
        {{ Math.round(zoomLevel * 100) }}%
      </button>

      <button
        type="button"
        @click="zoomIn"
        :disabled="zoomLevel >= 3.5"
        class="w-7 h-7 flex items-center justify-center rounded-lg text-ink-muted hover:text-ink hover:bg-surface-subtle disabled:opacity-40 cursor-pointer"
        title="Zoom In (Ctrl + Scroll Up)"
      >
        <ZoomIn class="w-3.5 h-3.5" />
      </button>
    </div>



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

        <!-- AppSwitch for Couple Shared Task -->
        <div class="p-3 bg-surface-subtle/40 border border-border/80 rounded-xl">
          <AppSwitch
            v-model="editTaskIsShared"
            :label="t('calendar.tasks.shareWithPartner')"
            :description="t('calendar.tasks.shareWithPartnerDesc')"
          />
        </div>

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

  </div>
</template>

