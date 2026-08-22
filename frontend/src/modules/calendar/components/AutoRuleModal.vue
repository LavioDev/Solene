<script setup lang="ts">
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Trash2 } from 'lucide-vue-next'
import { apiClient } from '@/services/apiClient'
import AppModal from '@/components/ui/AppModal.vue'
import AppInput from '@/components/ui/AppInput.vue'
import AppSelect from '@/components/ui/AppSelect.vue'
import AppButton from '@/components/ui/AppButton.vue'
import type { EventOccurrence } from '../types'

const props = defineProps<{
  show: boolean
  selectedEvent: EventOccurrence | null
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'saved'): void
  (e: 'delete', event: EventOccurrence): void
}>()

const { t } = useI18n()

const ruleTitle = ref('')
const ruleRecurrenceType = ref<'EVERY_N_DAYS' | 'MONTHLY' | 'YEARLY'>('EVERY_N_DAYS')
const ruleIntervalValue = ref(100)
const ruleAnchorDate = ref('2022-05-22')
const submitting = ref(false)

watch(
  () => [props.show, props.selectedEvent],
  ([show]) => {
    if (show) {
      if (props.selectedEvent) {
        ruleTitle.value = props.selectedEvent.title
        ruleAnchorDate.value = props.selectedEvent.date
        ruleRecurrenceType.value = 'EVERY_N_DAYS'
        ruleIntervalValue.value = 100
      } else {
        ruleTitle.value = ''
        ruleAnchorDate.value = '2022-05-22'
        ruleRecurrenceType.value = 'EVERY_N_DAYS'
        ruleIntervalValue.value = 100
      }
    }
  },
  { immediate: true }
)

async function handleSaveAutoRule() {
  if (!ruleTitle.value.trim() || !ruleAnchorDate.value) return

  submitting.value = true
  try {
    if (props.selectedEvent && props.selectedEvent.category !== 'note') {
      await apiClient.put(`/events/${props.selectedEvent.event_id}`, {
        title: ruleTitle.value.trim(),
        anchor_date: ruleAnchorDate.value,
        recurrence_type: ruleRecurrenceType.value,
        interval_value: ruleIntervalValue.value,
        category: 'love',
      })
    } else {
      await apiClient.post('/events', {
        title: ruleTitle.value.trim(),
        anchor_date: ruleAnchorDate.value,
        recurrence_type: ruleRecurrenceType.value,
        interval_value: ruleIntervalValue.value,
        category: 'love',
      })
    }
    emit('saved')
    emit('close')
  } catch (err) {
    console.error('Failed to save auto rule:', err)
  } finally {
    submitting.value = false
  }
}

function handleDelete() {
  if (props.selectedEvent) {
    emit('delete', props.selectedEvent)
  }
}
</script>

<template>
  <AppModal
    :show="show"
    :title="selectedEvent ? t('common.edit') : t('calendar.modalAutoTitle')"
    width="880"
    @close="emit('close')"
  >
    <form @submit.prevent="handleSaveAutoRule" class="space-y-4">
      <AppInput
        v-model="ruleTitle"
        :label="t('calendar.ruleTitleLabel')"
        :placeholder="t('calendar.ruleTitlePlaceholder')"
        required
      />

      <AppInput
        v-model="ruleAnchorDate"
        type="date"
        :label="t('calendar.anchorDateLabel')"
        required
      />

      <!-- Side-by-Side 2-Column Row for Recurrence Type & Interval using AppSelect and AppInput -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <AppSelect
          v-model="ruleRecurrenceType"
          :label="t('calendar.recurrenceTypeLabel')"
          :options="[
            { label: t('calendar.recurrenceOptions.everyNDays'), value: 'EVERY_N_DAYS' },
            { label: t('calendar.recurrenceOptions.monthly'), value: 'MONTHLY' },
            { label: t('calendar.recurrenceOptions.yearly'), value: 'YEARLY' },
          ]"
        />

        <div v-if="ruleRecurrenceType === 'EVERY_N_DAYS'">
          <AppInput
            v-model.number="ruleIntervalValue"
            type="number"
            :label="t('calendar.intervalLabel')"
            :placeholder="t('calendar.intervalPlaceholder')"
          />
        </div>
      </div>

      <div class="flex items-center justify-between pt-2 border-t border-border">
        <div>
          <AppButton
            v-if="selectedEvent"
            variant="outline"
            type="button"
            size="sm"
            class="text-err-text hover:bg-err-bg border-err-border"
            @click="handleDelete"
          >
            <Trash2 class="w-3.5 h-3.5 mr-1" />
            {{ t('common.delete') }}
          </AppButton>
        </div>
        <div class="flex gap-2">
          <AppButton variant="outline" type="button" size="sm" @click="emit('close')">
            {{ t('common.cancel') }}
          </AppButton>
          <AppButton type="submit" size="sm" :loading="submitting">
            {{ selectedEvent ? t('common.save') : t('calendar.autoGenerate') }}
          </AppButton>
        </div>
      </div>
    </form>
  </AppModal>
</template>
