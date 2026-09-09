<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useMoodStore } from '@/stores/moodStore'
import { MOOD_DEFINITIONS, getMoodByScore } from '@/constants/moods'
import AppModal from '@/components/ui/AppModal.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppTextarea from '@/components/ui/AppTextarea.vue'
import {
  Heart,
  Send,
  Trash2,
  CheckCircle2,
} from 'lucide-vue-next'

const props = withDefaults(
  defineProps<{
    show: boolean
  }>(),
  {
    show: false,
  }
)

const emit = defineEmits<{
  (e: 'close'): void
}>()

const { t } = useI18n()
const moodStore = useMoodStore()

const selectedScore = ref<number>(7) // Default 7 (Good)
const noteText = ref<string>('')
const isSaving = ref<boolean>(false)
const saveSuccess = ref<boolean>(false)
const successMessage = ref<string>('')

const myMood = computed(() => moodStore.myTodayMood)
const partnerMood = computed(() => moodStore.partnerTodayMood)

// Sync state when myMood changes
watch(
  myMood,
  (val) => {
    if (val) {
      selectedScore.value = val.mood_score
      noteText.value = val.note || ''
    } else {
      selectedScore.value = 7
      noteText.value = ''
    }
  },
  { immediate: true }
)

// When modal opens, refresh and sync
watch(
  () => props.show,
  (isOpen) => {
    if (isOpen) {
      if (myMood.value) {
        selectedScore.value = myMood.value.mood_score
        noteText.value = myMood.value.note || ''
      } else {
        selectedScore.value = 7
        noteText.value = ''
      }
    }
  }
)

function handleSelectScore(score: number) {
  selectedScore.value = score
}

async function saveMood(overrideScore?: number) {
  const score = overrideScore ?? selectedScore.value
  const def = getMoodByScore(score)
  if (!def || isSaving.value) return

  isSaving.value = true
  saveSuccess.value = false
  successMessage.value = ''

  const isUpdating = !!myMood.value

  try {
    const minDelay = new Promise((resolve) => setTimeout(resolve, 500))
    const savePromise = isUpdating
      ? moodStore.updateTodayMood(myMood.value!.id, {
          mood_score: score,
          mood_tag: def.tag,
          note: noteText.value || null,
          is_shared: true,
        })
      : moodStore.logTodayMood({
          mood_score: score,
          mood_tag: def.tag,
          note: noteText.value || null,
          is_shared: true,
        })

    await Promise.all([savePromise, minDelay])

    saveSuccess.value = true
    successMessage.value = isUpdating
      ? t('mood.updateSuccess')
      : t('mood.logSuccess')

    setTimeout(() => {
      saveSuccess.value = false
      successMessage.value = ''
    }, 3000)
  } catch (error) {
    console.error('Failed to save mood:', error)
  } finally {
    isSaving.value = false
  }
}

async function handleDelete() {
  if (!myMood.value) return
  if (confirm(t('mood.confirmDelete'))) {
    await moodStore.deleteTodayMood(myMood.value.id)
    noteText.value = ''
    selectedScore.value = 7
  }
}

onMounted(() => {
  moodStore.fetchTodayMood()
})
</script>

<template>
  <AppModal
    :show="show"
    width="sm"
    :draggable="false"
    :bottom-sheet-on-mobile="false"
    :maximizable="false"
    @close="emit('close')"
  >
    <!-- Modal Header -->
    <template #header>
      <div class="flex items-center justify-between gap-3 w-full pr-2">
        <div class="flex items-center gap-2">
          <h3 class="text-xs sm:text-sm font-bold text-ink leading-tight font-sans">
            {{ t('mood.title') }}
          </h3>
        </div>

        <!-- Right: Partner Mood Badge (Desktop) -->
        <div class="flex items-center gap-2">
          <div
            v-if="partnerMood"
            class="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-xl bg-primary-50 text-primary-700 border border-primary-200 text-xs font-semibold"
            :title="partnerMood.note || (partnerMood.mood_tag ? t(`mood.tags.${partnerMood.mood_tag}`) : '')"
          >
            <Heart class="w-3.5 h-3.5 text-rose-500 fill-rose-500" />
            <span>{{ partnerMood.user_full_name ? `${partnerMood.user_full_name}:` : `${t('mood.partner')}:` }}</span>
            <span class="text-sm">{{ getMoodByScore(partnerMood.mood_score)?.emoji }}</span>
          </div>
        </div>
      </div>
    </template>

    <!-- Modal Body Content -->
    <div class="space-y-3 sm:space-y-4 pt-0 sm:pt-1 select-none">
      <!-- Success Notification Alert -->
      <Transition
        enter-active-class="transition duration-300 ease-out transform"
        enter-from-class="-translate-y-2 opacity-0 scale-95"
        enter-to-class="translate-y-0 opacity-100 scale-100"
        leave-active-class="transition duration-200 ease-in transform"
        leave-from-class="translate-y-0 opacity-100 scale-100"
        leave-to-class="-translate-y-2 opacity-0 scale-95"
      >
        <div
          v-if="saveSuccess"
          class="flex items-center gap-2 p-2.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold shadow-xs"
        >
          <CheckCircle2 class="w-4 h-4 text-emerald-600 shrink-0" />
          <span>{{ successMessage }}</span>
        </div>
      </Transition>

      <!-- Partner Mood Mobile Row (Minimalist pill on small screens) -->
      <div
        v-if="partnerMood"
        class="sm:hidden flex items-center justify-between px-3 py-1.5 rounded-xl bg-primary-50/70 border border-primary-100 text-xs text-primary-800"
      >
        <span class="flex items-center gap-1.5 font-medium truncate">
          <Heart class="w-3 h-3 text-rose-500 fill-rose-500 shrink-0" />
          <span class="truncate">{{ partnerMood.user_full_name || t('mood.partner') }}</span>
        </span>
        <span class="text-sm shrink-0">
          {{ getMoodByScore(partnerMood.mood_score)?.emoji }}
        </span>
      </div>

      <!-- 1-Click Rank 10 Emotion Selector Chips -->
      <div class="space-y-2">
        <div class="grid grid-cols-5 gap-1.5 sm:gap-2">
          <button
            v-for="def in MOOD_DEFINITIONS"
            :key="def.score"
            type="button"
            class="relative flex flex-col items-center justify-center py-2 px-1 rounded-xl border transition-all cursor-pointer group active:scale-95 select-none"
            :class="[
              selectedScore === def.score
                ? 'bg-primary-50 border-primary-500 shadow-xs scale-102 z-10'
                : 'bg-surface-subtle/50 border-border/70 hover:border-primary-200 hover:bg-white'
            ]"
            :title="t(def.nameKey)"
            @click="handleSelectScore(def.score)"
          >
            <!-- Emoji -->
            <span class="text-lg sm:text-xl leading-none transition-transform group-hover:scale-110">
              {{ def.emoji }}
            </span>

            <!-- Score number -->
            <span
              class="text-[11px] font-semibold mt-1 font-mono"
              :class="selectedScore === def.score ? 'text-primary-700' : 'text-ink-muted'"
            >
              {{ def.score }}
            </span>

            <!-- Active dot indicator -->
            <span
              v-if="selectedScore === def.score"
              class="absolute -top-0.5 -right-0.5 w-2 h-2 rounded-full bg-primary-600 ring-2 ring-white"
            />
          </button>
        </div>
      </div>

      <!-- Note (Journal / Reflection) Input Area -->
      <div class="space-y-1.5 pt-1 border-t border-border/50">
        <div class="flex items-center justify-between text-xs">
          <label class="font-semibold text-ink">
            {{ t('mood.noteLabel') }}
          </label>
          <span class="text-[11px] text-ink-muted flex items-center gap-1">
            <Heart class="w-3 h-3 text-rose-400 fill-rose-400" />
            <span>{{ partnerMood?.user_full_name ? t('mood.sendTo', { name: partnerMood.user_full_name }) : t('mood.sendToPartner') }}</span>
          </span>
        </div>
        <AppTextarea
          v-model="noteText"
          :placeholder="t('mood.notePlaceholder')"
          :rows="2"
        />
      </div>
    </div>

    <!-- Modal Footer Actions (Ergonomic Thumb-friendly Bar) -->
    <template #footer>
      <div class="flex items-center w-full gap-2">
        <button
          v-if="myMood"
          type="button"
          class="w-11 h-11 rounded-xl border border-rose-200 text-rose-500 hover:text-rose-700 hover:bg-rose-50 flex items-center justify-center transition-colors cursor-pointer shrink-0 active:scale-95"
          :title="t('mood.deleteMood')"
          @click="handleDelete"
        >
          <Trash2 class="w-4 h-4" />
        </button>

        <AppButton
          variant="secondary"
          size="md"
          class="hidden sm:inline-flex h-11"
          @click="emit('close')"
        >
          {{ t('common.close') }}
        </AppButton>

        <AppButton
          variant="primary"
          size="md"
          :loading="isSaving"
          :disabled="isSaving"
          class="flex-1 h-11 text-sm font-bold shadow-md shadow-primary-500/20 active:scale-98 transition-all"
          :class="{ '!bg-emerald-600 hover:!bg-emerald-700 !border-emerald-600 !shadow-emerald-500/20': saveSuccess }"
          @click="() => saveMood()"
        >
          <Send v-if="!isSaving && !saveSuccess" class="w-4 h-4 mr-1.5" />
          <CheckCircle2 v-else-if="saveSuccess" class="w-4 h-4 mr-1.5 text-white" />
          <span>{{ isSaving ? t('common.saving') : (saveSuccess ? t('common.saved') : (myMood ? t('mood.updateMood') : t('mood.logMood'))) }}</span>
        </AppButton>
      </div>
    </template>
  </AppModal>
</template>
