<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { apiClient } from '@/services/apiClient'
import {
  ChevronLeft,
  ChevronRight,
  Heart,
  Plus,
  Sparkles,
  StickyNote,
  Trash2,
} from 'lucide-vue-next'
import AppButton from '@/components/ui/AppButton.vue'
import AppModal from '@/components/ui/AppModal.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppTextarea from '@/components/ui/AppTextarea.vue'
import AppSelect from '@/components/ui/AppSelect.vue'
import AppImageUpload from '@/components/ui/AppImageUpload.vue'
import AppConfirmModal from '@/components/ui/AppConfirmModal.vue'
import AutoRuleModal from '../components/AutoRuleModal.vue'
import type { EventOccurrence, CalendarDay } from '../types'

const { t, locale } = useI18n()

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
const showSingleDayModal = ref(false)
const showDeleteConfirmModal = ref(false)
const deletingEvent = ref(false)

// Single Day Note Form State (Unified with /notes)
const singleNoteTitle = ref('')
const singleNoteContent = ref('')
const singleNoteImages = ref<string[]>([])
const singleNoteDisplayType = ref<'DATE' | 'RANDOM'>('DATE')
const singleNoteTargetDate = ref(todayStr)
const submittingNote = ref(false)

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

onMounted(() => {
  fetchOccurrences()
})

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
  showSingleDayModal.value = true
}

// Open Edit Modal when clicking on an existing event/note
function openEventEditModal(evt: EventOccurrence) {
  selectedEvent.value = evt
  selectedDay.value = calendarDays.value.find((d) => d.dateStr === evt.date) || null

  if (evt.category === 'note') {
    singleNoteTitle.value = evt.title
    singleNoteContent.value = evt.milestone_info || ''
    singleNoteImages.value = evt.image_url ? [evt.image_url] : []
    singleNoteDisplayType.value = 'DATE'
    singleNoteTargetDate.value = evt.date
    showSingleDayModal.value = true
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
    showSingleDayModal.value = false
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
    } else {
      await apiClient.delete(`/events/${selectedEvent.value.event_id}`)
    }
    showDeleteConfirmModal.value = false
    showSingleDayModal.value = false
    showAutoRuleModal.value = false
    selectedEvent.value = null
    await fetchOccurrences()
  } catch (err) {
    console.error('Failed to delete event/note:', err)
  } finally {
    deletingEvent.value = false
  }
}
</script>

<template>
  <div class="h-full w-full flex flex-col bg-white border border-border rounded-2xl shadow-card overflow-hidden select-none">

    <!-- Header Toolbar — slim, quiet -->
    <div class="h-14 px-6 border-b border-border/60 flex items-center justify-between bg-white shrink-0">

      <!-- Left: Title + loading indicator -->
      <div class="flex items-center gap-2.5">
        <h2 class="text-sm sm:text-base font-semibold text-ink capitalize tracking-tight">
          {{ headerLabel }}
        </h2>
        <span
          v-if="loading"
          class="text-xs text-ink-faint font-mono animate-pulse"
        >
          {{ t('calendar.loading') }}
        </span>
      </div>

      <!-- Right: Controls group with Native UI AppButton components -->
      <div class="flex items-center gap-1.5">

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
    </div>

    <!-- Scrollable Calendar Area -->
    <div class="flex-1 overflow-x-auto flex flex-col">
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
                :title="t('common.create')"
              >
                <Plus class="w-3.5 h-3.5" />
              </button>
            </div>

            <!-- Events — soft pill badges, normal weight text, click to edit -->
            <div class="flex flex-col gap-1 overflow-y-auto min-h-0">
              <div
                v-for="evt in day.events"
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

    <!-- Modal 1: Auto-Generate Rules (Create or Edit) -->
    <AutoRuleModal
      :show="showAutoRuleModal"
      :selected-event="selectedEvent"
      @close="showAutoRuleModal = false"
      @saved="fetchOccurrences"
      @delete="handleDeleteFromModal"
    />

    <!-- Modal 2: Note Modal (Native UI AppInput, AppSelect, AppTextarea, AppButton) -->
    <AppModal
      :show="showSingleDayModal"
      :title="selectedEvent ? t('common.edit') : t('calendar.modalSingleTitle', { date: selectedDay?.dateStr || singleNoteTargetDate })"
      width="880"
      @close="showSingleDayModal = false"
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
              v-if="selectedEvent"
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
            <AppButton variant="outline" type="button" size="sm" @click="showSingleDayModal = false">
              {{ t('common.cancel') }}
            </AppButton>
            <AppButton type="submit" size="sm" :loading="submittingNote">
              {{ selectedEvent ? t('common.save') : t('common.create') }}
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
