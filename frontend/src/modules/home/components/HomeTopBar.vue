<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/authStore'
import type { Couple, UserPartnerSummary } from '@/types/couple'
import type { PartnerActiveStatus } from '@/types/task'
import type { MoodItem } from '@/types/mood'
import { getMoodByScore } from '@/constants/moods'
import { Heart, RotateCw, Sparkles } from 'lucide-vue-next'
import AppButton from '@/components/ui/AppButton.vue'

interface Props {
  couple: Couple | null
  loading: boolean
  partner: UserPartnerSummary | null
  partnerStatus: PartnerActiveStatus | null
  coupleNickname: string
  formattedStartDate: string
  isRefreshingPartner?: boolean
  isMoodOpen?: boolean
  myMood?: MoodItem | null
  getUserInitials: (name?: string, email?: string) => string
  formatTaskTime?: (isoString?: string | null) => string
}

const props = withDefaults(defineProps<Props>(), {
  isRefreshingPartner: false,
  isMoodOpen: false,
  myMood: null,
})

const emit = defineEmits<{
  (e: 'link-couple'): void
  (e: 'refresh-partner'): void
  (e: 'toggle-mood'): void
}>()

const { t } = useI18n()
const authStore = useAuthStore()

const myUser = computed(() => {
  if (!props.couple) return authStore.user
  if (props.partner && props.couple.user1_id === props.partner.id) {
    return props.couple.user2
  }
  return props.couple.user1
})

const currentMoodDef = computed(() =>
  props.myMood ? getMoodByScore(props.myMood.mood_score) : null
)

const partnerStatusText = computed(() => {
  if (!props.partner) return null
  if (props.partnerStatus?.is_busy && props.partnerStatus.active_task?.title) {
    return props.partnerStatus.active_task.title
  }
  return null
})
</script>

<template>
  <div class="select-none">
    <!-- === SKELETON LOADING === -->
    <div v-if="loading" class="flex items-center justify-between gap-3 pb-3 border-b border-border/60">
      <div class="flex items-center gap-3 flex-1 min-w-0">
        <!-- Avatar skeleton -->
        <div class="flex items-center shrink-0">
          <div class="w-10 h-10 rounded-full bg-surface-raised animate-pulse"></div>
          <div class="w-10 h-10 rounded-full bg-surface-raised animate-pulse -ml-3 border-2 border-white"></div>
        </div>
        <!-- Text skeleton -->
        <div class="space-y-1.5 flex-1 min-w-0">
          <div class="h-3.5 w-32 bg-surface-raised rounded animate-pulse"></div>
          <div class="h-2.5 w-24 bg-surface-raised/70 rounded animate-pulse"></div>
        </div>
      </div>
      <!-- Mood button skeleton -->
      <div class="h-9 w-24 rounded-xl bg-surface-raised animate-pulse shrink-0"></div>
    </div>

    <!-- === NO COUPLE STATE === -->
    <div v-else-if="!couple" class="flex items-center justify-between gap-3 pb-3 border-b border-border/60">
      <div class="flex items-center gap-2 text-xs text-ink-muted min-w-0">
        <Heart class="w-4 h-4 text-primary-400 shrink-0" />
        <span class="truncate">{{ t('home.noCoupleDesc') }}</span>
      </div>
      <AppButton size="sm" class="shrink-0" @click="emit('link-couple')">
        <Sparkles class="w-3.5 h-3.5 mr-1" />
        {{ t('home.linkCoupleBtn') }}
      </AppButton>
    </div>

    <!-- === COUPLE ACTIVE STATE === -->
    <div v-else class="flex items-center justify-between gap-3 sm:gap-4 pb-3.5 sm:pb-4 border-b border-border/60">

      <!-- Left: Avatars + Couple info + Partner status -->
      <div class="flex items-center gap-3 min-w-0 flex-1">
        <!-- Two overlapping avatars -->
        <div class="relative flex items-center shrink-0">
          <!-- My avatar -->
          <div
            class="relative w-10 h-10 rounded-full bg-primary-600 text-white font-bold text-xs flex items-center justify-center border-2 border-white shadow-sm z-10"
            :title="myUser?.full_name"
          >
            <div class="w-full h-full rounded-full overflow-hidden flex items-center justify-center">
              <img
                v-if="myUser?.avatar_url"
                :src="myUser.avatar_url"
                :alt="myUser.full_name || ''"
                class="w-full h-full object-cover"
              />
              <span v-else>{{ getUserInitials(myUser?.full_name, myUser?.email) }}</span>
            </div>

            <!-- My online status badge (Xanh lá nổi bật, không bị cắt mép) -->
            <!-- <span
              class="absolute -bottom-0.5 -left-0.5 w-3 h-3 rounded-full bg-emerald-500 border-2 border-white shadow-sm z-20"
              :title="myUser?.full_name || 'Tôi'"
            >
              <span class="absolute inset-0 rounded-full bg-emerald-400 animate-ping opacity-60"></span>
            </span> -->
          </div>

          <!-- Partner avatar -->
          <div
            class="relative -ml-3.5 w-10 h-10 rounded-full bg-purple-500 text-white font-bold text-xs flex items-center justify-center border-2 border-white shadow-sm z-20"
            :title="partner?.full_name"
          >
            <div class="w-full h-full rounded-full overflow-hidden flex items-center justify-center">
              <img
                v-if="partner?.avatar_url"
                :src="partner.avatar_url"
                :alt="partner?.full_name || ''"
                class="w-full h-full object-cover"
              />
              <span v-else>{{ getUserInitials(partner?.full_name, partner?.email) }}</span>
            </div>

            <!-- Online status dot — Nổi bật, viền trắng sắc nét, không bị overflow cắt xén -->
            <span
              class="absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full border-2 border-white shadow-sm z-30"
              :class="partnerStatus?.is_busy ? 'bg-rose-500' : 'bg-emerald-500'"
              :title="partnerStatus?.is_busy
                ? t('home.partnerStatus.busy', { name: partner?.full_name })
                : t('home.partnerStatus.available', { name: partner?.full_name })"
            >
              <span
                v-if="!partnerStatus?.is_busy"
                class="absolute inset-0 rounded-full bg-emerald-400 animate-ping opacity-60"
              ></span>
            </span>
          </div>
        </div>

        <!-- Couple info text column -->
        <div class="min-w-0 flex-1">
          <!-- Couple name + refresh button -->
          <div class="flex items-center gap-1.5">
            <h1 class="text-sm font-bold text-ink truncate leading-tight">
              {{ coupleNickname }}
            </h1>
            <button
              type="button"
              class="shrink-0 p-0.5 rounded-full text-ink-faint hover:text-primary-600 transition-colors cursor-pointer"
              :class="{ 'animate-spin text-primary-500': isRefreshingPartner }"
              :title="t('home.partnerStatus.title')"
              @click="emit('refresh-partner')"
            >
              <RotateCw class="w-3 h-3" />
            </button>
          </div>
          <!-- Partner active status tag — hiển thị trạng thái xanh nổi bật -->
        </div>
      </div>

      <!-- Right: Messenger Note Style Thought Bubble (Chia sẻ suy nghĩ...) -->
      <div class="shrink-0 flex flex-col items-end">
        <div class="relative inline-flex items-center">
          <button
            type="button"
            class="relative flex items-center justify-center gap-1.5 sm:gap-2 px-3.5 py-2 sm:px-4 sm:py-2.5 rounded-2xl bg-white shadow-[0_2px_10px_rgba(0,0,0,0.08)] border border-neutral-100 hover:shadow-[0_4px_16px_rgba(0,0,0,0.12)] hover:-translate-y-0.5 active:translate-y-0 active:scale-98 transition-all duration-200 cursor-pointer select-none"
            :class="[
              isMoodOpen
                ? 'ring-2 ring-primary-300 border-primary-300'
                : ''
            ]"
            :title="currentMoodDef ? `${currentMoodDef.emoji} ${myMood?.mood_score}/10` : 'Chia sẻ suy nghĩ...'"
            @click="emit('toggle-mood')"
          >
            <!-- State 1: Mood Recorded (Hiển thị như Messenger status note) -->
            <template v-if="currentMoodDef">
              <span class="text-base sm:text-lg leading-none shrink-0">
                {{ currentMoodDef.emoji }}
              </span>
              <span v-if="myMood?.note" class="text-xs sm:text-[13px] text-neutral-700 font-medium truncate max-w-[110px] sm:max-w-[180px]">
                {{ myMood.note }}
              </span>
              <span v-else-if="currentMoodDef.tag" class="hidden sm:inline text-xs sm:text-[13px] text-neutral-700 font-medium">
                {{ t(`mood.tags.${currentMoodDef.tag}`) }}
              </span>
            </template>

            <!-- State 2: Mood Not Recorded Yet (Chia sẻ suy nghĩ... chuẩn Messenger) -->
            <template v-else>
              <span class="text-neutral-500 font-normal text-xs sm:text-[13px] whitespace-nowrap">
                Chia sẻ suy nghĩ...
              </span>
            </template>
          </button>

          <!-- Messenger Note Thought Tail (2 chấm tròn chuẩn kiểu Messenger) -->
          <div class="absolute -bottom-2.5 left-5 flex flex-col items-center pointer-events-none">
            <span class="w-2.5 h-2.5 rounded-full bg-white border border-neutral-200/90 shadow-xs"></span>
            <span class="w-1.5 h-1.5 rounded-full bg-white border border-neutral-200/90 shadow-2xs -mt-0.5"></span>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>
