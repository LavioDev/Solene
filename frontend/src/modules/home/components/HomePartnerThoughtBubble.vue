<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { TaskItem } from '@/types/task'
import { Sparkles, Clock } from 'lucide-vue-next'
import AppBadge from '@/components/ui/AppBadge.vue'
import AppModal from '@/components/ui/AppModal.vue'
import AppButton from '@/components/ui/AppButton.vue'

interface Props {
  partnerName?: string
  task?: TaskItem | null
  isBusy?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  partnerName: 'Người ấy',
  isBusy: false,
})

const { t } = useI18n()

// Trạng thái hover để mở rộng popover mini
const isHovered = ref(false)

// Trạng thái mở Modal chi tiết toàn bộ nội dung khi bấm vào
const showDetailModal = ref(false)

// Định dạng thời gian
function formatTime(isoStr?: string | null): string {
  if (!isoStr) return '--:--'
  try {
    const d = new Date(isoStr)
    const hh = String(d.getHours()).padStart(2, '0')
    const mm = String(d.getMinutes()).padStart(2, '0')
    return `${hh}:${mm}`
  } catch {
    return '--:--'
  }
}

// Badge priority
const priorityVariant = computed<'err' | 'warn' | 'ok' | 'violet'>(() => {
  const p = props.task?.priority?.toLowerCase()
  if (p === 'urgent' || p === 'high') return 'err'
  if (p === 'medium') return 'warn'
  if (p === 'low') return 'ok'
  return 'violet'
})

const priorityLabel = computed(() => {
  const p = props.task?.priority?.toLowerCase()
  if (p === 'urgent') return t('home.partnerStatus.priorityUrgent')
  if (p === 'high') return t('home.partnerStatus.priorityHigh')
  if (p === 'medium') return t('home.partnerStatus.priorityMedium')
  if (p === 'low') return t('home.partnerStatus.priorityLow')
  return props.task?.priority || ''
})

function openModal() {
  showDetailModal.value = true
}
</script>

<template>
  <div
    class="relative inline-flex items-center select-none"
    @mouseenter="isHovered = true"
    @mouseleave="isHovered = false"
  >
    <!-- KHỐI BONG BÓNG SUY NGHĨ (THOUGHT BUBBLE) -->
    <div
      class="relative z-10 transition-all duration-300 ease-out group cursor-pointer"
      :class="[
        isHovered ? 'scale-102 -translate-y-0.5' : '',
      ]"
      @click="openModal"
    >
      <!-- Container chính của Bong bóng -->
      <div
        class="flex items-center gap-2 px-3.5 py-2 rounded-2xl bg-white/95 backdrop-blur-md border border-violet-200/80 shadow-md shadow-violet-500/10 hover:shadow-lg hover:shadow-violet-500/15 hover:border-violet-300 transition-all text-xs"
      >
        <!-- Icon suy nghĩ / Trạng thái -->
        <div class="relative shrink-0 flex items-center justify-center">
          <span class="text-sm">💭</span>
          <span
            v-if="isBusy"
            class="absolute -top-0.5 -right-0.5 w-2 h-2 rounded-full bg-rose-500 border border-white animate-pulse"
          ></span>
        </div>

        <!-- Nội dung suy nghĩ / Task đang làm -->
        <div class="flex items-center gap-1.5 whitespace-nowrap">
          <span v-if="partnerName" class="font-bold text-violet-700 shrink-0 text-xs whitespace-nowrap">
            {{ partnerName }}:
          </span>
          <span class="font-medium text-ink text-xs whitespace-nowrap">
            {{ isBusy && task?.title ? task.title : t('home.partnerStatus.noTasks') }}
          </span>
        </div>

        <!-- Tag thời gian / Priority mini (nếu có task) -->
        <div v-if="isBusy && task?.start_time" class="hidden sm:flex items-center gap-1 shrink-0 pl-1 border-l border-border/60">
          <Clock class="w-3 h-3 text-ink-muted" />
          <span class="text-[10px] font-mono text-ink-muted">
            {{ formatTime(task.start_time) }}-{{ formatTime(task.end_time) }}
          </span>
        </div>

        <!-- Priority badge nhỏ -->
        <AppBadge
          v-if="isBusy && task?.priority"
          :variant="priorityVariant"
          size="sm"
          class="text-[10px] px-1.5 py-0 scale-90 origin-right"
        >
          {{ priorityLabel }}
        </AppBadge>
      </div>

      <!-- ĐUÔI BONG BÓNG SUY NGHĨ (2 HẠT TRÒN MÂY NỐI VÀO AVATAR Ở TRÊN) -->
      <div class="absolute -top-2 left-6 flex flex-col-reverse items-center pointer-events-none">
        <span class="w-2 h-2 rounded-full bg-white border border-violet-200 shadow-2xs -mt-0.5"></span>
        <span class="w-1.5 h-1.5 rounded-full bg-white border border-violet-200 shadow-2xs ml-1 -mt-0.5"></span>
      </div>

    </div>

    <!-- MODAL TOÀN BỘ NỘI DUNG KHI BẤM VÀO (ĐƠN GIẢN & TINH TẾ) -->
    <AppModal
      :show="showDetailModal"
      width="sm"
      :maximizable="false"
      @close="showDetailModal = false"
    >
      <template #header>
        <div class="flex items-center gap-2">
          <span class="text-base">💭</span>
          <h3 class="text-sm font-bold text-ink">
            {{ partnerName }}
          </h3>
          <span
            class="w-2 h-2 rounded-full ml-auto"
            :class="isBusy ? 'bg-rose-500 animate-pulse' : 'bg-emerald-500'"
            :title="isBusy ? t('home.partnerStatus.busy', { name: partnerName }) : t('home.partnerStatus.available', { name: partnerName })"
          ></span>
        </div>
      </template>

      <!-- Nội dung Modal đơn giản -->
      <div class="space-y-3 py-1 text-xs">
        <!-- Tiêu đề task -->
        <div>
          <h4 class="text-sm font-semibold text-ink leading-snug">
            {{ isBusy && task?.title ? task.title : t('home.partnerStatus.available', { name: partnerName }) }}
          </h4>
        </div>

        <!-- Thời gian & Mức độ ưu tiên -->
        <div v-if="isBusy && task?.start_time" class="flex items-center gap-2 text-ink-muted text-[11px] font-mono">
          <Clock class="w-3.5 h-3.5 text-violet-500 shrink-0" />
          <span>{{ formatTime(task.start_time) }} &mdash; {{ formatTime(task.end_time) }}</span>
          <span v-if="task.priority" class="text-ink-faint">·</span>
          <AppBadge v-if="task.priority" :variant="priorityVariant" size="sm">
            {{ priorityLabel }}
          </AppBadge>
        </div>

        <!-- Nội dung ghi chú / suy nghĩ -->
        <p v-if="isBusy && task?.content" class="text-ink-muted leading-relaxed whitespace-pre-wrap pt-1 border-t border-border/40">
          {{ task.content }}
        </p>

        <!-- Trạng thái rảnh -->
        <p v-if="!isBusy" class="text-ink-muted leading-relaxed">
          {{ t('home.partnerStatus.noTasks') }}
        </p>
      </div>

      <template #footer>
        <AppButton variant="secondary" size="sm" class="w-full" @click="showDetailModal = false">
          {{ t('common.close', 'Đóng') }}
        </AppButton>
      </template>
    </AppModal>
  </div>
</template>

<style scoped>
/* Animation nảy nhẹ khi mở popover */
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
