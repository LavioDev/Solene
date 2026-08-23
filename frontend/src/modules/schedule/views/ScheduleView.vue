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
  <div class="space-y-3 select-none">

    <!-- Main Card Container (Exact original style & height) -->
    <div class="w-full flex flex-col bg-white border border-border rounded-2xl shadow-card overflow-hidden min-h-[calc(100vh-210px)] h-[calc(100vh-210px)]">

      <!-- Header Toolbar inside card (Exact original 1:1 style) -->
      <div class="h-14 px-6 border-b border-border/60 flex items-center justify-between bg-white shrink-0">

        <!-- Left: Title / Loading indicator -->
        <div class="flex items-center gap-2.5">
          <h2 class="text-sm sm:text-base font-semibold text-ink capitalize tracking-tight">
            {{ ganttHeaderLabel }}
          </h2>
        </div>

        <!-- Right: Day-Gantt Controls (Original exact 1:1 Calendar Header style) -->
        <div class="flex items-center gap-1.5">
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
          <!-- Add Task Icon Button -->
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

      <!-- Gantt Timeline Body -->
      <div class="flex-1 overflow-hidden relative">
        <DayGanttView
          ref="ganttViewRef"
          :active-date="ganttActiveDateStr"
          @add-task="handleGanttAddTask"
        />
      </div>

    </div>

    <!-- Modal: Independent Day Tasks Modal (Exact 1:1 original modal) -->
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
              class="!bg-violet-600 hover:!bg-violet-700 text-white font-medium cursor-pointer"
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
