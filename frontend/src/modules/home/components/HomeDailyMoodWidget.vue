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

const myMood = computed(() => moodStore.myTodayMood)
const partnerMood = computed(() => moodStore.partnerTodayMood)

const currentDefinition = computed(() => getMoodByScore(selectedScore.value))

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
  if (!def) return

  isSaving.value = true
  saveSuccess.value = false
  try {
    if (myMood.value) {
      await moodStore.updateTodayMood(myMood.value.id, {
        mood_score: score,
        mood_tag: def.tag,
        note: noteText.value || null,
        is_shared: true,
      })
    } else {
      await moodStore.logTodayMood({
        mood_score: score,
        mood_tag: def.tag,
        note: noteText.value || null,
        is_shared: true,
      })
    }
    saveSuccess.value = true
    setTimeout(() => {
      saveSuccess.value = false
    }, 2000)
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
    width="880"
    :maximizable="false"
    @close="emit('close')"
  >
    <!-- Modal Header -->
    <template #header>
      <div class="flex items-center justify-between gap-3 w-full pr-2">
        <div class="flex items-center gap-2">
          <div>
            <h3 class="text-sm font-bold text-ink leading-tight font-sans">
              {{ t('mood.title') }}
            </h3>
          </div>
        </div>

        <!-- Right: Partner Mood Badge or Link to Heatmap -->
        <div class="flex items-center gap-2">
          <!-- Partner Mood Badge (if available) -->
          <div
            v-if="partnerMood"
            class="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-xl bg-pink-50 text-pink-700 border border-pink-200 text-xs font-semibold"
            :title="partnerMood.note || partnerMood.mood_tag"
          >
            <Heart class="w-3.5 h-3.5 text-pink-500 fill-pink-500" />
            <span>{{ partnerMood.user_full_name ? `${partnerMood.user_full_name}:` : 'Partner:' }}</span>
            <span class="text-sm">{{ getMoodByScore(partnerMood.mood_score)?.emoji }}</span>
            <span>{{ partnerMood.mood_score }}/10</span>
          </div>

          <!-- View Annual Heatmap Button -->
          <!-- <button
            type="button"
            class="inline-flex items-center gap-1 text-xs font-semibold text-violet-700 hover:text-violet-900 bg-violet-50 hover:bg-violet-100 px-3 py-1.5 rounded-xl border border-violet-200 transition-colors cursor-pointer"
            @click="navigateToHeatmap"
          >
            <span>{{ t('mood.viewHeatmap') }}</span>
            <ChevronRight class="w-3.5 h-3.5" />
          </button> -->
        </div>
      </div>
    </template>

    <!-- Modal Body Content -->
    <div class="space-y-4 pt-1 select-none">
      <!-- Partner Mood Mobile Row (visible on small screens) -->
      <div
        v-if="partnerMood"
        class="sm:hidden flex items-center justify-between p-2.5 rounded-xl bg-pink-50/70 border border-pink-100 text-xs text-pink-800"
      >
        <span class="flex items-center gap-1.5 font-medium">
          <Heart class="w-3.5 h-3.5 text-pink-500 fill-pink-500" />
          <span>{{ partnerMood.user_full_name ? `${partnerMood.user_full_name}:` : 'Partner:' }}</span>
        </span>
        <span class="flex items-center gap-1 font-bold">
          <span>{{ getMoodByScore(partnerMood.mood_score)?.emoji }}</span>
          <span>{{ partnerMood.mood_score }}/10 ({{ partnerMood.mood_tag }})</span>
        </span>
      </div>

      <!-- 1-Click Rank 10 Emotion Selector Chips -->
      <div class="space-y-2">
        <div class="grid grid-cols-5 sm:grid-cols-10 gap-1.5 sm:gap-2">
          <button
            v-for="def in MOOD_DEFINITIONS"
            :key="def.score"
            type="button"
            class="relative flex flex-col items-center justify-center p-2 rounded-xl border transition-all cursor-pointer group"
            :class="[
              selectedScore === def.score
                ? 'bg-violet-50/90 border-violet-500 shadow-xs ring-2 ring-violet-400/30 scale-105 z-10'
                : 'bg-surface-subtle/40 border-border/70 hover:border-violet-300 hover:bg-white'
            ]"
            @click="handleSelectScore(def.score)"
          >
            <!-- Emoji -->
            <span class="text-2xl transition-transform group-hover:scale-110">
              {{ def.emoji }}
            </span>

            <!-- Score number -->
            <span
              class="text-[11px] font-bold mt-1"
              :class="selectedScore === def.score ? 'text-violet-700' : 'text-ink-muted'"
            >
              {{ def.score }}
            </span>

            <!-- Active dot indicator -->
            <span
              v-if="selectedScore === def.score"
              class="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-violet-600 ring-2 ring-white"
            />
          </button>
        </div>

        <!-- Selected Emotion Tag Preview -->
        <div class="flex items-center justify-between pt-1 text-xs">
          <div class="flex items-center gap-2">
            <span class="font-bold text-ink">
              {{ currentDefinition?.emoji }} {{ t(currentDefinition?.nameKey || '') }}
            </span>
            
            <span v-if="saveSuccess" class="inline-flex items-center gap-1 text-emerald-600 font-semibold">
              <CheckCircle2 class="w-3.5 h-3.5" />
              <span>Saved!</span>
            </span>
          </div>
        </div>
      </div>

      <!-- Note (Journal / Reflection) Input Area -->
      <div class="space-y-2 pt-2 border-t border-border/60">
        <label class="block text-xs font-semibold text-ink">
          {{ t('mood.noteLabel') }}
        </label>
        <AppTextarea
          v-model="noteText"
          :placeholder="t('mood.notePlaceholder')"
          :rows="3"
        />
      </div>
    </div>

    <!-- Modal Footer Actions -->
    <template #footer>
      <div class="flex items-center justify-between w-full">
        <button
          v-if="myMood"
          type="button"
          class="text-xs text-rose-500 hover:text-rose-700 flex items-center gap-1 cursor-pointer transition-colors"
          @click="handleDelete"
        >
          <Trash2 class="w-3.5 h-3.5" />
          <span>{{ t('mood.deleteMood') }}</span>
        </button>
        <div v-else />

        <div class="flex items-center gap-2">
          <AppButton
            variant="secondary"
            size="sm"
            @click="emit('close')"
          >
            {{ t('common.close') }}
          </AppButton>
          <AppButton
            variant="primary"
            size="sm"
            :disabled="isSaving"
            @click="() => saveMood()"
          >
            <Send class="w-3.5 h-3.5 mr-1" />
            <span>{{ myMood ? t('mood.updateMood') : t('mood.logMood') }}</span>
          </AppButton>
        </div>
      </div>
    </template>
  </AppModal>
</template>
