<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/authStore'
import type { Couple, UserPartnerSummary } from '@/types/couple'
import type { PartnerActiveStatus } from '@/types/task'
import type { MoodItem } from '@/types/mood'
import { getMoodByScore } from '@/constants/moods'
import { Heart, Smile, FileText, Sparkles } from 'lucide-vue-next'
import AppButton from '@/components/ui/AppButton.vue'
import HomePartnerThoughtBubble from './HomePartnerThoughtBubble.vue'

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
const isMoodHovered = ref(false)
const isPartnerHovered = ref(false)

const myUser = computed(() => {
  if (!props.couple) return authStore.user
  if (props.partner && props.couple.user1_id === props.partner.id) {
    return props.couple.user2
  }
  return props.couple.user1
})
</script>

<template>
  <div class="flex items-center justify-between gap-3 sm:gap-4 pb-3 border-b border-border/60 select-none">
    <!-- Left Group: Couple Avatars (Tôi bên trái, Đối phương bên phải & nằm đè bên trên) + Nickname -->
    <div class="flex items-center gap-2.5 sm:gap-3 min-w-0 flex-1">
      <div v-if="couple" class="flex items-center gap-2.5 sm:gap-3 min-w-0 flex-1">
        <!-- 2 Overlapping Avatars: Tôi bên trái (z-10), Đối phương bên phải & đè lên trên (z-20) -->
        <div class="relative flex items-center shrink-0">
          <!-- 1. My Avatar (Bên trái, z-10) -->
          <div class="relative w-8 h-8 sm:w-9 sm:h-9 rounded-full bg-primary-600 text-white font-bold text-xs flex items-center justify-center border-2 border-white shadow-2xs z-10">
            <div class="w-full h-full rounded-full overflow-hidden flex items-center justify-center">
              <img
                v-if="myUser?.avatar_url"
                :src="myUser.avatar_url"
                :alt="myUser.full_name || 'Tôi'"
                class="w-full h-full object-cover"
              />
              <span v-else>{{ getUserInitials(myUser?.full_name, myUser?.email) }}</span>
            </div>
          </div>

          <!-- 2. Partner Avatar (Bên phải, nằm đè lên trên z-20, hover mọc duy nhất bong bóng suy nghĩ) -->
          <div
            class="relative -ml-3 sm:-ml-3.5 w-8 h-8 sm:w-9 sm:h-9 rounded-full bg-purple-500 text-white font-bold text-xs flex items-center justify-center border-2 border-white shadow-md z-20 cursor-pointer transition-transform hover:scale-110 hover:z-30"
            @mouseenter="isPartnerHovered = true"
            @mouseleave="isPartnerHovered = false"
            @click="isPartnerHovered = !isPartnerHovered"
          >
            <div class="w-full h-full rounded-full overflow-hidden flex items-center justify-center">
              <img
                v-if="partner?.avatar_url"
                :src="partner.avatar_url"
                :alt="partner.full_name"
                class="w-full h-full object-cover"
              />
              <span v-else>{{ getUserInitials(partner?.full_name, partner?.email) }}</span>
            </div>

            <!-- Dot trạng thái của Partner -->
            <span
              class="absolute bottom-0 right-0 w-2.5 h-2.5 rounded-full border-2 border-white shadow-xs z-30"
              :class="partnerStatus?.is_busy ? 'bg-rose-500' : 'bg-emerald-500 animate-pulse'"
            ></span>

            <!-- Bong bóng suy nghĩ mọc ra từ avatar đối phương khi hover -->
            <Transition name="bubble-pop">
              <div
                v-if="isPartnerHovered && partner"
                class="absolute left-0 top-full mt-2.5 z-50 pointer-events-auto"
                @mouseenter="isPartnerHovered = true"
                @mouseleave="isPartnerHovered = false"
              >
                <HomePartnerThoughtBubble
                  :partner-name="partner.full_name"
                  :task="partnerStatus?.active_task"
                  :is-busy="Boolean(partnerStatus?.is_busy)"
                />
              </div>
            </Transition>
          </div>
        </div>

        <!-- Couple Nickname & Since Date -->
        <div class="min-w-0 flex-1">
          <h1 class="text-xs sm:text-sm font-bold text-ink flex items-center gap-1.5 truncate">
            <span class="truncate">{{ coupleNickname }}</span>
          </h1>
          <p class="hidden sm:block text-[10px] sm:text-[11px] text-ink-muted font-mono truncate">
            {{ t('home.since', { date: formattedStartDate }) }}
          </p>
        </div>
      </div>

      <!-- Fallback if No Couple Linked -->
      <div v-if="!loading && !couple" class="flex flex-wrap items-center gap-2 text-xs text-ink-muted">
        <Heart class="w-4 h-4 text-primary-500 shrink-0" />
        <span class="truncate">{{ t('home.noCoupleDesc') }}</span>
        <AppButton size="sm" class="ml-1 sm:ml-2" @click="emit('link-couple')">
          <Sparkles class="w-3.5 h-3.5 mr-1" />
          {{ t('home.linkCoupleBtn') }}
        </AppButton>
      </div>
    </div>

    <!-- Right Controls: Nút Cảm xúc hôm nay (Sát phải - Trên mobile chỉ hiện icon gọn gàng) -->
    <div class="flex items-center gap-2 sm:gap-2.5 ml-auto shrink-0">
      <div
        class="relative inline-flex items-center"
        @mouseenter="isMoodHovered = true"
        @mouseleave="isMoodHovered = false"
      >
        <button
          type="button"
          class="relative flex items-center justify-center gap-1.5 sm:gap-2 p-2 sm:px-3.5 sm:py-2 rounded-xl sm:rounded-2xl border transition-all duration-200 cursor-pointer text-xs select-none shadow-md"
          :class="[
            isMoodOpen
              ? 'bg-primary-600 text-white border-primary-600 shadow-primary-500/20 ring-2 ring-primary-400/30 font-bold scale-102 -translate-y-0.5'
              : myMood
                ? 'bg-white/95 backdrop-blur-md text-ink border-primary-200/80 hover:border-primary-300 shadow-primary-500/10 hover:shadow-lg hover:shadow-primary-500/15 font-semibold hover:scale-102 hover:-translate-y-0.5'
                : 'bg-white/95 backdrop-blur-md text-ink-muted hover:text-ink border-border/80 hover:border-primary-300 shadow-primary-500/5 hover:shadow-md font-medium hover:scale-102 hover:-translate-y-0.5'
          ]"
          :title="myMood ? `${myMood.mood_score}/10` : t('mood.title')"
          @click="emit('toggle-mood')"
        >
          <!-- Icon or Emoji with Note Dot -->
          <div class="relative shrink-0 flex items-center justify-center">
            <span v-if="myMood" class="text-base leading-none">
              {{ getMoodByScore(myMood.mood_score)?.emoji }}
            </span>
            <Smile v-else class="w-4 h-4 text-primary-600" />

            <!-- Dot chỉ thị nếu có ghi chú (Note Dot) -->
            <span
              v-if="myMood?.note"
              class="absolute -top-1 -right-1 w-2 h-2 rounded-full bg-primary-600 border-2 border-white shadow-xs animate-pulse"
              :class="isMoodOpen ? 'bg-amber-300 ring-1 ring-primary-800' : 'bg-primary-600'"
              title="Có ghi chú hôm nay"
            ></span>
          </div>

          <!-- Label: Ẩn trên mobile (< sm), chỉ hiện icon -->
          <span class="hidden sm:inline font-sans whitespace-nowrap">
            {{ myMood ? `${myMood.mood_score}/10` : t('mood.title') }}
          </span>
        </button>

        <!-- Tooltip Hover Popover hiển thị Note khi hover chuột vào nút -->
        <Transition name="bubble-pop">
          <div
            v-if="isMoodHovered && myMood?.note && !isMoodOpen"
            class="absolute right-0 top-full mt-2.5 w-64 sm:w-72 max-w-[calc(100vw-2rem)] p-3 rounded-2xl bg-white/98 backdrop-blur-xl border border-primary-200/90 shadow-xl shadow-primary-900/10 z-30 text-left pointer-events-none"
          >
            <div class="flex items-center justify-between gap-2 pb-1.5 border-b border-border/50 mb-1.5">
              <div class="flex items-center gap-1.5 min-w-0">
                <FileText class="w-3.5 h-3.5 text-primary-600 shrink-0" />
                <span class="text-[11px] font-bold text-primary-700 whitespace-nowrap tracking-tight">
                  Ghi chú hôm nay
                </span>
              </div>
              <span class="text-xs font-bold text-primary-700 shrink-0 whitespace-nowrap">
                {{ getMoodByScore(myMood.mood_score)?.emoji }} {{ myMood.mood_score }}/10
              </span>
            </div>

            <!-- Note Content -->
            <p class="text-xs text-ink leading-relaxed font-sans whitespace-pre-wrap line-clamp-4">
              "{{ myMood.note }}"
            </p>
          </div>
        </Transition>
      </div>
    </div>
  </div>
</template>

<style scoped>
.bubble-pop-enter-active {
  transition: all 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.bubble-pop-leave-active {
  transition: all 0.15s ease-in;
}
.bubble-pop-enter-from {
  opacity: 0;
  transform: translateY(-6px) scale(0.95);
}
.bubble-pop-leave-to {
  opacity: 0;
  transform: translateY(-4px) scale(0.98);
}
</style>
