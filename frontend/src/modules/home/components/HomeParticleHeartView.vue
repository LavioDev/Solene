<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'

const emit = defineEmits<{
  (e: 'exit'): void
}>()

const containerRef = ref<HTMLDivElement | null>(null)
const canvasRef = ref<HTMLCanvasElement | null>(null)
let animationFrameId: number | null = null
let resizeObserver: ResizeObserver | null = null

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
  const container = containerRef.value
  if (!canvas || !container) return

  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const isMobile = /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(
    (navigator.userAgent || navigator.vendor || (window as unknown as { opera: string }).opera || '').toLowerCase()
  )
  const koef = isMobile ? 0.5 : 1

  let width = (canvas.width = koef * container.clientWidth)
  let height = (canvas.height = koef * container.clientHeight)
  const rand = Math.random

  // Light Mode Background
  ctx.fillStyle = 'rgba(255,255,255,1)'
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
    if (!canvas || !container) return
    width = canvas.width = koef * container.clientWidth
    height = canvas.height = koef * container.clientHeight
    ctx.fillStyle = 'rgba(255,255,255,1)'
    ctx.fillRect(0, 0, width, height)
  }

  resizeObserver = new ResizeObserver(handleResize)
  resizeObserver.observe(container)

  // EXACT ORIGINAL PARAMETERS
  const traceCount = isMobile ? 20 : 50
  const pointsOrigin: [number, number][] = []
  const dr = isMobile ? 0.3 : 0.1

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
      // Vibrant rose-ruby particles visible against white background
      f: 'hsla(' + Math.floor(340 + 20 * rand()) + ',' + Math.floor(80 + 15 * rand()) + '%,' + Math.floor(48 + 10 * rand()) + '%,.45)',
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

    // Light Mode trailing effect
    ctx.fillStyle = 'rgba(255,255,255,.12)'
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
  if (resizeObserver) {
    resizeObserver.disconnect()
    resizeObserver = null
  }
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') {
    emit('exit')
  }
}

onMounted(async () => {
  await nextTick()
  initHeartCanvas()
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  stopAnimation()
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<template>
  <div
    ref="containerRef"
    @click="emit('exit')"
    class="relative w-full h-full min-h-[calc(100vh-4rem)] bg-white flex flex-col items-center justify-center select-none overflow-hidden cursor-pointer"
    title="Click to return to dashboard"
  >
    <!-- Background Animated Canvas (Only the Pure Particle Heart) -->
    <canvas
      ref="canvasRef"
      class="absolute inset-0 w-full h-full pointer-events-none"
    ></canvas>

    <!-- Subtle return hint at bottom -->
    <div class="absolute bottom-4 text-[11px] text-slate-400 font-mono pointer-events-none">
      Click anywhere to return
    </div>
  </div>
</template>
