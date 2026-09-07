<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { apiClient } from '@/services/apiClient'
import {
  ChevronLeft,
  ChevronRight,
  PawPrint,
  Plus,
  Sparkles,
  User,
  Heart,
  Layers,
} from 'lucide-vue-next'
import AppButton from '@/components/ui/AppButton.vue'
import AppModal from '@/components/ui/AppModal.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppSelect from '@/components/ui/AppSelect.vue'
import AppTextarea from '@/components/ui/AppTextarea.vue'
import AppSwitch from '@/components/ui/AppSwitch.vue'
import DayGanttView from '@/modules/calendar/components/DayGanttView.vue'
import type { TaskItem } from '@/modules/calendar/types'

const route = useRoute()
const router = useRouter()
const { t, locale } = useI18n()

const ganttViewRef = ref<InstanceType<typeof DayGanttView> | null>(null)
const viewMode = ref<'my' | 'partner' | 'combined'>('my')

const today = new Date()
const todayStr = today.toISOString().split('T')[0]

// Day-Gantt Active Date
const initialDate = computed(() => (route.query.date as string) || todayStr)
const ganttActiveDateStr = ref(initialDate.value)

// Day-Gantt Header Label (1:1 with old Calendar header)
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

function getLocalDateStr(dateInput?: string | Date | null): string {
  if (!dateInput) return ''
  const d = new Date(dateInput)
  if (isNaN(d.getTime())) return ''
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function ganttPrevDay() {
  const parts = ganttActiveDateStr.value.split('-').map(Number)
  const d = new Date(parts[0], parts[1] - 1, parts[2] - 1)
  ganttActiveDateStr.value = getLocalDateStr(d)
  router.replace({ query: { date: ganttActiveDateStr.value } })
}

function ganttNextDay() {
  const parts = ganttActiveDateStr.value.split('-').map(Number)
  const d = new Date(parts[0], parts[1] - 1, parts[2] + 1)
  ganttActiveDateStr.value = getLocalDateStr(d)
  router.replace({ query: { date: ganttActiveDateStr.value } })
}

function ganttGoToday() {
  ganttActiveDateStr.value = getLocalDateStr(new Date())
  router.replace({ query: { date: ganttActiveDateStr.value } })
  setTimeout(() => {
    ganttViewRef.value?.scrollToNow()
  }, 100)
}

function handleFocusNow() {
  ganttGoToday()
  setTimeout(() => {
    ganttViewRef.value?.scrollToNow()
  }, 100)
}

// Task Modal State
const showTaskModal = ref(false)
const addingTask = ref(false)
const newTaskTitle = ref('')
const newTaskStartTime = ref('09:00')
const newTaskEndTime = ref('10:00')
const newTaskPriority = ref('medium')
const newTaskContent = ref('')
const newTaskIsShared = ref(true)

function handleGanttAddTask(dateStr: string) {
  ganttActiveDateStr.value = dateStr
  newTaskTitle.value = ''
  newTaskContent.value = ''
  newTaskStartTime.value = '09:00'
  newTaskEndTime.value = '10:00'
  newTaskPriority.value = 'medium'
  newTaskIsShared.value = true
  showTaskModal.value = true
}

async function handleCreateTaskForDay() {
  if (!newTaskTitle.value.trim()) return

  addingTask.value = true
  try {
    const targetDate = ganttActiveDateStr.value || todayStr
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
      is_shared: newTaskIsShared.value,
      start_time,
      end_time,
      priority: newTaskPriority.value,
    }

    await apiClient.post<TaskItem>('/tasks', payload)

    // Reset inputs
    newTaskTitle.value = ''
    newTaskContent.value = ''
    newTaskIsShared.value = true
    showTaskModal.value = false

    if (ganttViewRef.value) {
      await ganttViewRef.value.fetchDayTasks()
    }
  } catch (err) {
    console.error('Failed to create task for day:', err)
  } finally {
    addingTask.value = false
  }
}

onMounted(() => {
  if (route.query.date) {
    ganttActiveDateStr.value = String(route.query.date)
  }
})
</script>

<template>
  <div class="space-y-4 px-4 sm:px-6 lg:px-8 pt-1 sm:pt-2 pb-16 w-full select-none">
    <!-- Page Header (Chuẩn 1:1 theo phong cách MoodsView) -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <div class="flex items-center gap-2">
          <h1 class="text-xl sm:text-2xl font-bold text-ink font-sans tracking-tight">
            {{ t('nav.schedule') }}
          </h1>
        </div>
        <p class="text-xs sm:text-sm text-ink-muted mt-0.5">
          {{ t('nav.scheduleDesc') }}
        </p>
      </div>

      <!-- Controls: View Mode Segmented Pill (Responsive scrollable tabs) -->
      <div class="w-full sm:w-auto overflow-x-auto pb-1 max-w-full">
        <!-- View Mode Segmented Pill -->
        <div class="flex bg-surface-raised p-1 rounded-xl border border-border/80 text-xs font-medium shrink-0 w-max">
          <button
            type="button"
            class="px-3.5 py-1.5 rounded-lg transition-all flex items-center gap-1.5 cursor-pointer text-xs font-medium shrink-0 whitespace-nowrap"
            :class="viewMode === 'my' ? 'bg-white text-primary-700 font-semibold shadow-2xs' : 'text-ink-muted hover:text-ink'"
            @click="viewMode = 'my'"
          >
            <User class="w-4 h-4" />
            <span class="text-xs">{{ t('calendar.gantt.mySchedule') }}</span>
          </button>

          <button
            type="button"
            class="px-3.5 py-1.5 rounded-lg transition-all flex items-center gap-1.5 cursor-pointer text-xs font-medium shrink-0 whitespace-nowrap"
            :class="viewMode === 'partner' ? 'bg-white text-pink-600 font-semibold shadow-2xs' : 'text-ink-muted hover:text-ink'"
            @click="viewMode = 'partner'"
          >
            <Heart class="w-4 h-4" />
            <span class="text-xs">{{ t('calendar.gantt.partnerSchedule') }}</span>
          </button>

          <button
            type="button"
            class="px-3.5 py-1.5 rounded-lg transition-all flex items-center gap-1.5 cursor-pointer text-xs font-medium shrink-0 whitespace-nowrap"
            :class="viewMode === 'combined' ? 'bg-white text-emerald-700 font-semibold shadow-2xs' : 'text-ink-muted hover:text-ink'"
            @click="viewMode = 'combined'"
          >
            <Layers class="w-4 h-4" />
            <span class="text-xs">{{ t('calendar.gantt.combinedSchedule') }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Main Card Container (Wrapped in responsive overflow container) -->
    <div class="w-full max-w-full overflow-x-auto pb-2">
      <div class="min-w-[800px] w-full flex flex-col bg-white border border-border rounded-2xl shadow-card overflow-hidden min-h-[600px] h-[calc(100vh-210px)]">

      <!-- Header Toolbar inside card -->
      <div class="h-14 px-6 border-b border-border/60 flex items-center justify-between bg-white shrink-0">

        <!-- Left: Title / Date label -->
        <div class="flex items-center gap-2.5 min-w-0">
          <h2 class="text-sm sm:text-base font-semibold text-ink capitalize tracking-tight truncate">
            {{ ganttHeaderLabel }}
          </h2>
        </div>

        <!-- Right: Day-Gantt Controls -->
        <div class="flex items-center gap-1.5 shrink-0">
          <!-- Focus to Current Time Icon Button -->
          <AppButton
            variant="ghost"
            size="sm"
            @click="handleFocusNow"
            :title="t('calendar.gantt.focusNow')"
            class="!px-2.5 !py-1 text-ink-muted hover:!text-primary-600 hover:!bg-primary-50"
          >
            <PawPrint class="w-4 h-4 text-primary-600" />
          </AppButton>
          <!-- Add Task Icon Button -->
          <AppButton
            variant="ghost"
            size="sm"
            @click="handleGanttAddTask(ganttActiveDateStr)"
            :title="t('calendar.gantt.addTask')"
            class="!px-2.5 !py-1 text-ink-muted hover:!text-primary-600 hover:!bg-primary-50"
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

      <!-- Gantt Timeline Body -->
      <div class="flex-1 overflow-hidden relative">
        <DayGanttView
          ref="ganttViewRef"
          :active-date="ganttActiveDateStr"
          :view-mode="viewMode"
          @add-task="handleGanttAddTask"
        />
      </div>

    </div>
  </div>

    <!-- Modal: Independent Day Tasks Modal -->
    <AppModal
      :show="showTaskModal"
      :title="`${t('calendar.tabs.tasks')} — ${ganttActiveDateStr}`"
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

          <!-- Start Time & End Time + Priority -->
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div class="w-full space-y-1.5">
              <label class="block text-xs font-bold text-ink tracking-wider uppercase">
                {{ t('calendar.tasks.startTime') }}
              </label>
              <div class="relative flex items-center">
                <input
                  type="time"
                  v-model="newTaskStartTime"
                  class="w-full px-3.5 py-2.5 text-sm font-medium bg-white border border-border rounded-xl text-ink shadow-2xs hover:border-primary-300 focus:outline-none focus:border-primary-500 focus:ring-2 focus:ring-primary-400/20"
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
                  class="w-full px-3.5 py-2.5 text-sm font-medium bg-white border border-border rounded-xl text-ink shadow-2xs hover:border-primary-300 focus:outline-none focus:border-primary-500 focus:ring-2 focus:ring-primary-400/20"
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

          <!-- AppSwitch for Couple Shared Task -->
          <div class="p-3 bg-white border border-border/80 rounded-xl">
            <AppSwitch
              v-model="newTaskIsShared"
              :label="t('calendar.tasks.shareWithPartner')"
              :description="t('calendar.tasks.shareWithPartnerDesc')"
            />
          </div>

          <div class="flex justify-end pt-1">
            <AppButton
              type="button"
              size="sm"
              :loading="addingTask"
              :disabled="!newTaskTitle.trim()"
              @click="handleCreateTaskForDay"
              class="!bg-primary-600 hover:!bg-primary-700 text-white font-medium cursor-pointer"
            >
              <Plus class="w-3.5 h-3.5 mr-1" />
              {{ t('calendar.tasks.addTask') }}
            </AppButton>
          </div>
        </div>
      </div>
    </AppModal>

  </div>
</template>
