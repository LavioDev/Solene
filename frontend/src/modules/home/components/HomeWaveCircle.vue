<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { Heart } from 'lucide-vue-next'
import type { MoodItem } from '@/types/mood'
import { getMoodByScore } from '@/constants/moods'

interface Props {
  days: number
  hours: number
  minutes: number
  seconds: number
  formattedStartDate: string
  partnerMood?: MoodItem | null
  partnerName?: string
}

withDefaults(defineProps<Props>(), {
  partnerMood: null,
  partnerName: '',
})

const emit = defineEmits<{
  (e: 'open-random-memory'): void
  (e: 'open-particle-heart'): void
}>()

const { t } = useI18n()
</script>

<template>
  <div class="relative py-10 flex items-center justify-center select-none" style="margin-top:0 !important;">
    <!-- Ambient Radiating Ripple Waves (Hiệu ứng sóng tỏa) -->
    <div class="absolute w-52 h-52 sm:w-60 sm:h-60 rounded-full border border-violet-400/35 animate-gentle-wave-1 pointer-events-none"></div>
    <div class="absolute w-52 h-52 sm:w-60 sm:h-60 rounded-full border border-purple-400/25 animate-gentle-wave-2 pointer-events-none"></div>
    <div class="absolute w-52 h-52 sm:w-60 sm:h-60 rounded-full border border-rose-400/20 animate-gentle-wave-3 pointer-events-none"></div>

    <!-- Main Pure White Circular Love Core (Clickable to reveal random memory) -->
    <div
      @click="emit('open-random-memory')"
      class="relative w-52 h-52 sm:w-60 sm:h-60 rounded-full bg-white border border-border/60 shadow-xl shadow-violet-500/10 flex flex-col items-center justify-center p-6 text-center text-ink transition-all duration-300 hover:scale-[1.03] active:scale-[0.98] cursor-pointer group z-10"
      :title="t('home.heartHint')"
    >
      <!-- Beating Heart Button (Click to open Glowing Particle Heart on Black BG) -->
      <button
        type="button"
        @click.stop="emit('open-particle-heart')"
        class="w-7 h-7 rounded-full bg-rose-50 hover:bg-rose-100 flex items-center justify-center transition-transform active:scale-90 cursor-pointer group/heart mb-1"
        :title="t('home.particleHeartHint')"
      >
        <Heart class="w-3.5 h-3.5 text-rose-500 fill-rose-500 animate-heartbeat group-hover/heart:scale-125 transition-transform" />
      </button>

      <!-- Label -->
      <p class="text-[10px] uppercase font-mono tracking-[0.24em] text-violet-700 font-bold">
        {{ t('home.together') }}
      </p>

      <!-- Big Days Number -->
      <div class="flex items-baseline justify-center gap-1.5 my-1">
        <span class="text-4xl sm:text-5xl font-extrabold text-ink tracking-tight font-sans">
          {{ days }}
        </span>
        <span class="text-xs font-bold uppercase tracking-wider text-violet-700 font-mono">
          {{ t('home.days') }}
        </span>
      </div>

      <!-- Real-Time Digital Clock Pill (HH : MM : SS) -->
      <div class="text-xs font-mono font-bold text-ink px-3 py-1 tracking-wider my-0.5">
        {{ String(hours).padStart(2, '0') }}:{{ String(minutes).padStart(2, '0') }}:{{ String(seconds).padStart(2, '0') }}
      </div>

      <!-- Since Date -->
      <p v-if="formattedStartDate" class="text-[10px] text-ink-muted font-mono mt-1">
        {{ t('home.since', { date: formattedStartDate }) }}
      </p>
    </div>

    <!-- TỜ NOTE BÊN PHẢI SÁT MÉP (Biểu diễn ghi chú & cảm xúc trong ngày của đối phương chân thực nhất) -->
    <Transition name="partner-note">
      <div
        v-if="partnerMood"
        class="hidden md:flex flex-col absolute right-0 top-1/2 -translate-y-1/2 w-64 lg:w-72 p-4 pt-4.5 rounded-xl bg-[#fffef5] border border-amber-200/80 shadow-md shadow-amber-900/5 hover:shadow-xl rotate-1 hover:rotate-0 transition-all duration-300 text-left z-20 group"
      >
        <!-- Băng dính Washi Tape dán đầu tờ note -->
        <div class="absolute -top-2.5 left-1/2 -translate-x-1/2 w-16 h-3.5 bg-amber-200/70 border border-amber-300/50 rounded-2xs shadow-2xs rotate-[-1.5deg] pointer-events-none backdrop-blur-xs"></div>

        <!-- Header Note: Tiêu đề ghi chú & Huy hiệu cảm xúc -->
        <div class="flex items-center justify-between gap-2 pb-2 mb-2 border-b border-amber-200/50">
          <div class="flex items-center gap-1.5 min-w-0">
            <Heart class="w-3.5 h-3.5 text-rose-400 fill-rose-400 shrink-0" />
            <span class="text-xs font-bold text-amber-950 truncate font-sans">
              {{ partnerName ? t('mood.partnerMessage', { name: partnerName }) : t('mood.partnerMessage', { name: 'người ấy' }) }}
            </span>
          </div>
        </div>

        <!-- Nội dung Ghi chú hôm nay của đối phương -->
        <div class="relative">
          <p v-if="partnerMood.note" class="text-xs text-amber-950/90 leading-relaxed font-sans whitespace-pre-wrap line-clamp-4 italic">
            “{{ partnerMood.note }}”
          </p>
          <p v-else class="text-xs text-amber-800/60 italic font-sans">
            (Hôm nay cảm thấy {{ partnerMood.mood_tag || 'bình yên' }})
          </p>
        </div>
      </div>
    </Transition>
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

.partner-note-enter-active,
.partner-note-leave-active {
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.partner-note-enter-from,
.partner-note-leave-to {
  opacity: 0;
  transform: translateY(-50%) translateX(12px) scale(0.95);
}
</style>
