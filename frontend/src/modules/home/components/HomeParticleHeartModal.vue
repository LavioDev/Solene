<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import type { Couple } from '@/types/couple'
import { X, Sparkles } from 'lucide-vue-next'

interface Props {
  show: boolean
  couple: Couple | null
  days: number
  hours: number
  minutes: number
  seconds: number
  formattedStartDate: string
  coupleNickname: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

const { t } = useI18n()

const canvasRef = ref<HTMLCanvasElement | null>(null)
let animationFrameId: number | null = null

interface Particle {
  vx: number
  vy: number
  R: number
  speed: number
  q: number
  D: number
  force: number
  f: string
  trace: { x: number; y: number }[]
}

function initHeartCanvas() {
  const canvas = canvasRef.value
  if (!canvas) return

  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const isMobile = /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(
    (navigator.userAgent || navigator.vendor || (window as unknown as { opera: string }).opera || '').toLowerCase()
  )
  const koef = isMobile ? 0.75 : 1

  let width = (canvas.width = koef * window.innerWidth)
  let height = (canvas.height = koef * window.innerHeight)
  const rand = Math.random

  ctx.fillStyle = 'rgba(0,0,0,1)'
  ctx.fillRect(0, 0, width, height)

  const heartPosition = (rad: number): [number, number] => {
    return [
      Math.pow(Math.sin(rad), 3),
      -(
        15 * Math.cos(rad) -
        5 * Math.cos(2 * rad) -
        2 * Math.cos(3 * rad) -
        Math.cos(4 * rad)
      ),
    ]
  }

  const scaleAndTranslate = (
    pos: [number, number],
    sx: number,
    sy: number,
    dx: number,
    dy: number
  ): [number, number] => {
    return [dx + pos[0] * sx, dy + pos[1] * sy]
  }

  const handleResize = () => {
    if (!canvas) return
    width = canvas.width = koef * window.innerWidth
    height = canvas.height = koef * window.innerHeight
    ctx.fillStyle = 'rgba(0,0,0,1)'
    ctx.fillRect(0, 0, width, height)
  }

  window.addEventListener('resize', handleResize)

  const traceCount = isMobile ? 24 : 50
  const pointsOrigin: [number, number][] = []
  const dr = isMobile ? 0.18 : 0.1

  for (let i = 0; i < Math.PI * 2; i += dr) {
    pointsOrigin.push(scaleAndTranslate(heartPosition(i), 210, 13, 0, 0))
  }
  for (let i = 0; i < Math.PI * 2; i += dr) {
    pointsOrigin.push(scaleAndTranslate(heartPosition(i), 150, 9, 0, 0))
  }
  for (let i = 0; i < Math.PI * 2; i += dr) {
    pointsOrigin.push(scaleAndTranslate(heartPosition(i), 90, 5, 0, 0))
  }
  const heartPointsCount = pointsOrigin.length

  const targetPoints: [number, number][] = []
  const pulse = (kx: number, ky: number) => {
    for (let i = 0; i < pointsOrigin.length; i++) {
      targetPoints[i] = [
        kx * pointsOrigin[i][0] + width / 2,
        ky * pointsOrigin[i][1] + height / 2,
      ]
    }
  }

  const particles: Particle[] = []
  for (let i = 0; i < heartPointsCount; i++) {
    const x = rand() * width
    const y = rand() * height
    const trace: { x: number; y: number }[] = []
    for (let k = 0; k < traceCount; k++) {
      trace[k] = { x, y }
    }

    particles[i] = {
      vx: 0,
      vy: 0,
      R: 2,
      speed: rand() + 5,
      q: Math.floor(rand() * heartPointsCount),
      D: 2 * (i % 2) - 1,
      force: 0.2 * rand() + 0.7,
      f: `hsla(${Math.floor(rand() * 40 + 330)}, ${Math.floor(40 * rand() + 60)}%, ${Math.floor(60 * rand() + 20)}%, 0.4)`,
      trace,
    }
  }

  const config = {
    traceK: 0.4,
    timeDelta: 0.01,
  }

  let time = 0
  const loop = () => {
    const n = -Math.cos(time)
    pulse((1 + n) * 0.5, (1 + n) * 0.5)
    time += (Math.sin(time) < 0 ? 9 : n > 0.8 ? 0.2 : 1) * config.timeDelta

    ctx.fillStyle = 'rgba(0,0,0,0.1)'
    ctx.fillRect(0, 0, width, height)

    for (let i = particles.length; i--; ) {
      const u = particles[i]
      const q = targetPoints[u.q]
      if (!q) continue

      const dx = u.trace[0].x - q[0]
      const dy = u.trace[0].y - q[1]
      const length = Math.sqrt(dx * dx + dy * dy)

      if (length < 10) {
        if (rand() > 0.95) {
          u.q = Math.floor(rand() * heartPointsCount)
        } else {
          if (rand() > 0.99) {
            u.D *= -1
          }
          u.q += u.D
          u.q %= heartPointsCount
          if (u.q < 0) {
            u.q += heartPointsCount
          }
        }
      }

      u.vx += (-dx / length) * u.speed
      u.vy += (-dy / length) * u.speed
      u.trace[0].x += u.vx
      u.trace[0].y += u.vy
      u.vx *= u.force
      u.vy *= u.force

      for (let k = 0; k < u.trace.length - 1; ) {
        const T = u.trace[k]
        const N = u.trace[++k]
        N.x -= config.traceK * (N.x - T.x)
        N.y -= config.traceK * (N.y - T.y)
      }

      ctx.fillStyle = u.f
      for (let k = 0; k < u.trace.length; k++) {
        ctx.fillRect(u.trace[k].x, u.trace[k].y, 1.2, 1.2)
      }
    }

    animationFrameId = window.requestAnimationFrame(loop)
  }

  loop()
}

function stopAnimation() {
  if (animationFrameId !== null) {
    cancelAnimationFrame(animationFrameId)
    animationFrameId = null
  }
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape' && props.show) {
    emit('close')
  }
}

watch(
  () => props.show,
  async (isShown) => {
    if (isShown) {
      await nextTick()
      initHeartCanvas()
      window.addEventListener('keydown', handleKeydown)
    } else {
      stopAnimation()
      window.removeEventListener('keydown', handleKeydown)
    }
  }
)

onMounted(() => {
  if (props.show) {
    initHeartCanvas()
    window.addEventListener('keydown', handleKeydown)
  }
})

onUnmounted(() => {
  stopAnimation()
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<template>
  <Transition name="fade">
    <div
      v-if="show"
      class="fixed inset-0 z-50 bg-black select-none flex flex-col items-center justify-center overflow-hidden"
    >
      <!-- Glowing Particle Canvas -->
      <canvas
        ref="canvasRef"
        class="absolute inset-0 w-full h-full cursor-pointer"
        @click="emit('close')"
      ></canvas>

      <!-- Top-Right Close Button -->
      <button
        type="button"
        @click="emit('close')"
        class="absolute top-5 right-5 z-20 flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white/10 hover:bg-white/20 text-white/80 hover:text-white backdrop-blur-md border border-white/15 transition-all text-xs cursor-pointer shadow-lg active:scale-95"
      >
        <span>{{ t('home.randomNoteModal.close') }}</span>
        <X class="w-4 h-4" />
      </button>

      <!-- Center Romantic Floating Content (Centered over the Beating Particle Heart) -->
      <div class="relative z-10 flex flex-col items-center text-center pointer-events-none px-4 max-w-lg">
        <!-- Couple Nickname with subtle glowing gradient -->
        <h1
          v-if="coupleNickname"
          class="text-xl sm:text-2xl md:text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-rose-200 via-pink-100 to-rose-300 drop-shadow-[0_0_25px_rgba(244,63,94,0.6)] mb-2 tracking-wide"
        >
          {{ coupleNickname }}
        </h1>

        <!-- Together Tag -->
        <div class="inline-flex items-center gap-1.5 px-3 py-0.5 rounded-full bg-rose-500/20 border border-rose-500/30 text-[10px] sm:text-xs font-mono font-bold tracking-[0.2em] text-rose-300 uppercase mb-2 backdrop-blur-xs">
          <Sparkles class="w-3 h-3 text-rose-400 animate-pulse" />
          <span>{{ t('home.together') }}</span>
        </div>

        <!-- Big Days Number with Glowing Halo -->
        <div class="flex items-baseline justify-center gap-2 my-1">
          <span
            class="text-5xl sm:text-7xl font-extrabold text-white tracking-tight drop-shadow-[0_0_35px_rgba(251,113,133,0.8)] font-sans"
          >
            {{ days }}
          </span>
          <span class="text-sm sm:text-base font-bold uppercase tracking-widest text-rose-400 font-mono drop-shadow-[0_0_12px_rgba(244,63,94,0.8)]">
            {{ t('home.days') }}
          </span>
        </div>

        <!-- Real-Time Digital Sub Clock -->
        <div class="mt-2 text-sm sm:text-base font-mono font-bold text-rose-100/90 bg-black/40 px-4 py-1 rounded-full border border-rose-500/30 backdrop-blur-md tracking-widest shadow-[0_0_20px_rgba(244,63,94,0.3)]">
          {{ String(hours).padStart(2, '0') }} : {{ String(minutes).padStart(2, '0') }} : {{ String(seconds).padStart(2, '0') }}
        </div>

        <!-- Since Date -->
        <p v-if="formattedStartDate" class="text-xs sm:text-sm text-rose-200/60 font-mono mt-3">
          {{ t('home.since', { date: formattedStartDate }) }}
        </p>
      </div>

      <!-- Bottom Hint to dismiss -->
      <div class="absolute bottom-6 z-10 text-[11px] text-white/40 font-mono pointer-events-none">
        Click anywhere or press Esc to return
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
