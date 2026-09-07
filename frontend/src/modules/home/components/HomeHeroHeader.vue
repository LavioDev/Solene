<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { Couple } from '@/types/couple'
import { Heart, Plus } from 'lucide-vue-next'
import AppButton from '@/components/ui/AppButton.vue'

interface Props {
  couple: Couple | null
  loading: boolean
  coupleNickname: string
  days: number
  hours: number
  minutes: number
  seconds: number
  formattedStartDate: string
  getUserInitials: (name?: string, email?: string) => string
}

defineProps<Props>()

const emit = defineEmits<{
  (e: 'open-random-memory'): void
  (e: 'link-couple'): void
}>()

const { t } = useI18n()
</script>

<template>
  <div class="relative py-4 flex flex-col items-center justify-center select-none">
    <!-- Active Couple Container -->
    <div v-if="couple" class="relative flex flex-col items-center justify-center w-full">
      <!-- 1. Top Bar Outside Circle: Users Avatars + Couple Nickname + Beating Heart -->
      <div class="flex items-center gap-3 mb-5 bg-white px-4 py-2 rounded-full border border-border/60 shadow-2xs">
        <!-- 2 Avatars overlapping -->
        <div class="flex items-center -space-x-2 shrink-0">
          <div class="w-8 h-8 rounded-full bg-primary-600 text-white font-bold text-xs flex items-center justify-center overflow-hidden border-2 border-white shadow-2xs">
            <img
              v-if="couple.user1?.avatar_url"
              :src="couple.user1.avatar_url"
              :alt="couple.user1.full_name"
              class="w-full h-full object-cover"
            />
            <span v-else>{{ getUserInitials(couple.user1?.full_name, couple.user1?.email) }}</span>
          </div>

          <div class="w-8 h-8 rounded-full bg-purple-500 text-white font-bold text-xs flex items-center justify-center overflow-hidden border-2 border-white shadow-2xs">
            <img
              v-if="couple.user2?.avatar_url"
              :src="couple.user2.avatar_url"
              :alt="couple.user2.full_name"
              class="w-full h-full object-cover"
            />
            <span v-else>{{ getUserInitials(couple.user2?.full_name, couple.user2?.email) }}</span>
          </div>
        </div>

        <!-- Nickname & Heart Button -->
        <div class="flex items-center gap-2">
          <h2 class="text-sm font-bold text-ink">
            {{ coupleNickname }}
          </h2>
          <button
            type="button"
            @click="emit('open-random-memory')"
            class="w-6 h-6 rounded-full bg-rose-50 hover:bg-rose-100 flex items-center justify-center transition-transform active:scale-90 cursor-pointer group"
            :title="t('home.heartHint')"
          >
            <Heart class="w-3.5 h-3.5 text-rose-500 fill-rose-500 animate-heartbeat group-hover:scale-125 transition-transform" />
          </button>
        </div>
      </div>

      <!-- 2. Centered Wave Circle: Clean, Spacious, Focused on Days & Clock -->
      <div class="relative flex items-center justify-center my-3">
        <!-- Ambient Radiating Ripple Waves (Hiệu ứng sóng tỏa) -->
        <div class="absolute w-52 h-52 sm:w-60 sm:h-60 rounded-full border border-primary-400/35 animate-gentle-wave-1 pointer-events-none"></div>
        <div class="absolute w-52 h-52 sm:w-60 sm:h-60 rounded-full border border-primary-300/25 animate-gentle-wave-2 pointer-events-none"></div>
        <div class="absolute w-52 h-52 sm:w-60 sm:h-60 rounded-full border border-rose-400/20 animate-gentle-wave-3 pointer-events-none"></div>

        <!-- Main Circular Core: Crisp White Card with Gentle Shadow -->
        <div class="relative w-52 h-52 sm:w-60 sm:h-60 rounded-full bg-white border border-border/60 shadow-lg shadow-primary-500/10 flex flex-col items-center justify-center p-6 text-center text-ink transition-transform duration-300 hover:scale-[1.02] z-10">
          <!-- Label -->
          <p class="text-[10px] uppercase font-mono tracking-[0.24em] text-primary-700 font-bold mb-0.5">
            {{ t('home.together') }}
          </p>

          <!-- Big Days Number -->
          <div class="flex items-baseline justify-center gap-1.5 my-1">
            <span class="text-4xl sm:text-5xl font-extrabold text-ink tracking-tight font-sans">
              {{ days }}
            </span>
            <span class="text-xs font-bold uppercase tracking-wider text-primary-700 font-mono">
              {{ t('home.days') }}
            </span>
          </div>

          <!-- Real-Time Digital Clock Pill (HH : MM : SS) -->
          <div class="text-xs font-mono font-bold text-ink bg-surface-subtle px-3 py-1 rounded-full border border-border/60 shadow-2xs tracking-wider my-1">
            {{ String(hours).padStart(2, '0') }}:{{ String(minutes).padStart(2, '0') }}:{{ String(seconds).padStart(2, '0') }}
          </div>

          <!-- Since Date -->
          <p class="text-[11px] text-ink-muted font-mono mt-1">
            {{ t('home.since', { date: formattedStartDate }) }}
          </p>
        </div>
      </div>
    </div>

    <!-- Fallback if No Couple Linked -->
    <div
      v-else-if="!loading"
      class="relative flex items-center justify-center"
    >
      <div class="absolute w-52 h-52 rounded-full border border-primary-400/25 animate-gentle-wave-1 pointer-events-none"></div>
      <div class="relative w-52 h-52 rounded-full bg-white border border-border/60 shadow-lg shadow-primary-500/10 flex flex-col items-center justify-center p-5 text-center text-ink z-10 space-y-2.5">
        <div class="w-10 h-10 rounded-full bg-primary-50 flex items-center justify-center text-primary-600">
          <Heart class="w-5 h-5" />
        </div>
        <p class="text-xs text-ink-muted max-w-[150px] leading-relaxed">
          {{ t('home.noCoupleDesc') }}
        </p>
        <AppButton size="sm" @click="emit('link-couple')">
          <Plus class="w-3.5 h-3.5 mr-1" />
          {{ t('home.linkCoupleBtn') }}
        </AppButton>
      </div>
    </div>
  </div>
</template>

<style scoped>
@keyframes gentleWave1 {
  0% {
    transform: scale(0.96);
    opacity: 0.75;
  }
  50% {
    transform: scale(1.22);
    opacity: 0.35;
  }
  100% {
    transform: scale(1.48);
    opacity: 0;
  }
}

@keyframes gentleWave2 {
  0% {
    transform: scale(0.96);
    opacity: 0.6;
  }
  50% {
    transform: scale(1.36);
    opacity: 0.25;
  }
  100% {
    transform: scale(1.75);
    opacity: 0;
  }
}

@keyframes gentleWave3 {
  0% {
    transform: scale(0.96);
    opacity: 0.45;
  }
  50% {
    transform: scale(1.48);
    opacity: 0.15;
  }
  100% {
    transform: scale(2.02);
    opacity: 0;
  }
}

.animate-gentle-wave-1 {
  animation: gentleWave1 3.2s cubic-bezier(0, 0, 0.2, 1) infinite;
}

.animate-gentle-wave-2 {
  animation: gentleWave2 3.2s cubic-bezier(0, 0, 0.2, 1) infinite 1.05s;
}

.animate-gentle-wave-3 {
  animation: gentleWave3 3.2s cubic-bezier(0, 0, 0.2, 1) infinite 2.1s;
}

@keyframes heartbeat {
  0% {
    transform: scale(1);
  }
  14% {
    transform: scale(1.24);
  }
  28% {
    transform: scale(1);
  }
  42% {
    transform: scale(1.18);
  }
  70% {
    transform: scale(1);
  }
}

.animate-heartbeat {
  animation: heartbeat 1.8s ease-in-out infinite;
}
</style>
