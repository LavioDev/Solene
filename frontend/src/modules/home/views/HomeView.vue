<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { Heart } from 'lucide-vue-next'
import mainPic from '@/img/mainpic.jpg'

const { t } = useI18n()

// Start Date: May 22, 2022 00:00:00 (Month index 4 = May)
const START_DATE = new Date(2022, 4, 22, 0, 0, 0)

const days = ref(0)
const hours = ref(0)
const minutes = ref(0)
const seconds = ref(0)

let timer: number | null = null

function updateLoveCounter() {
  const now = new Date()
  const diffMs = now.getTime() - START_DATE.getTime()

  if (diffMs > 0) {
    const totalSecs = Math.floor(diffMs / 1000)
    days.value = Math.floor(totalSecs / (3600 * 24))
    hours.value = Math.floor((totalSecs % (3600 * 24)) / 3600)
    minutes.value = Math.floor((totalSecs % 3600) / 60)
    seconds.value = totalSecs % 60
  }
}

onMounted(() => {
  updateLoveCounter()
  timer = window.setInterval(updateLoveCounter, 1000)
})

onUnmounted(() => {
  if (timer !== null) {
    clearInterval(timer)
  }
})
</script>

<template>
  <div class="relative w-full h-full min-h-[calc(100vh-4rem)] flex items-center justify-center overflow-hidden select-none">

    <!-- Full-Screen Background Image with Gentle Subtle Blur -->
    <div class="absolute inset-0 -z-10 overflow-hidden">
      <img
        :src="mainPic"
        alt="Solène Love Wallpaper"
        class="w-full h-full object-cover object-center filter blur-[2px] brightness-[0.98]"
      />
      <!-- Gentle transparent overlay -->
      <div class="absolute inset-0 bg-purple-950/10"></div>
    </div>

    <!-- Minimalist, Compact, Delicate Center Love Circle -->
    <div class="relative flex items-center justify-center">

      <!-- Ambient Gentle Ripple Waves -->
      <div class="absolute w-52 h-52 sm:w-60 sm:h-60 rounded-full border border-white/50 animate-gentle-wave-1 pointer-events-none"></div>
      <div class="absolute w-52 h-52 sm:w-60 sm:h-60 rounded-full border border-purple-300/40 animate-gentle-wave-2 pointer-events-none"></div>
      <div class="absolute w-52 h-52 sm:w-60 sm:h-60 rounded-full border border-rose-300/30 animate-gentle-wave-3 pointer-events-none"></div>

      <!-- Main Delicate Frosted Glass Love Circle -->
      <div class="relative w-48 h-48 sm:w-56 sm:h-56 rounded-full bg-white/45 backdrop-blur-md border border-white/70 shadow-xl flex flex-col items-center justify-center p-4 text-center text-slate-800 transition-transform duration-300 hover:scale-105">

        <!-- Beating Heart Icon -->
        <div class="w-7 h-7 rounded-full bg-white/70 shadow-xs flex items-center justify-center mb-1">
          <Heart class="w-3.5 h-3.5 text-rose-500 fill-rose-500 animate-pulse" />
        </div>

        <!-- Label -->
        <p class="text-[10px] uppercase font-mono tracking-[0.24em] text-purple-900/80 font-bold">
          {{ t('home.together') }}
        </p>

        <!-- Big Days Number -->
        <div class="flex items-baseline justify-center gap-1 my-0.5">
          <span
            class="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight"
            style="font-family: 'Plus Jakarta Sans', sans-serif;"
          >
            {{ days }}
          </span>
          <span class="text-[11px] font-bold uppercase tracking-wider text-purple-800 font-mono">
            {{ t('home.days') }}
          </span>
        </div>

        <!-- Real-Time Sub Clock (HH : MM : SS) -->
        <div class="text-[11px] font-mono font-semibold text-slate-700 bg-white/60 px-2.5 py-0.5 rounded-full border border-white/60 shadow-2xs mt-0.5 tracking-wider">
          {{ String(hours).padStart(2, '0') }}:{{ String(minutes).padStart(2, '0') }}:{{ String(seconds).padStart(2, '0') }}
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
@keyframes gentleWave1 {
  0% {
    transform: scale(0.98);
    opacity: 0.7;
  }
  50% {
    transform: scale(1.18);
    opacity: 0.35;
  }
  100% {
    transform: scale(1.38);
    opacity: 0;
  }
}

@keyframes gentleWave2 {
  0% {
    transform: scale(0.98);
    opacity: 0.6;
  }
  50% {
    transform: scale(1.28);
    opacity: 0.25;
  }
  100% {
    transform: scale(1.55);
    opacity: 0;
  }
}

@keyframes gentleWave3 {
  0% {
    transform: scale(0.98);
    opacity: 0.4;
  }
  50% {
    transform: scale(1.38);
    opacity: 0.15;
  }
  100% {
    transform: scale(1.72);
    opacity: 0;
  }
}

.animate-gentle-wave-1 {
  animation: gentleWave1 3.2s cubic-bezier(0, 0, 0.2, 1) infinite;
}

.animate-gentle-wave-2 {
  animation: gentleWave2 3.2s cubic-bezier(0, 0, 0.2, 1) infinite 1s;
}

.animate-gentle-wave-3 {
  animation: gentleWave3 3.2s cubic-bezier(0, 0, 0.2, 1) infinite 2s;
}
</style>
