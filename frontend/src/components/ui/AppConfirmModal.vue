<script setup lang="ts">
import { AlertTriangle } from 'lucide-vue-next'
import AppModal from '@/components/ui/AppModal.vue'
import AppButton from '@/components/ui/AppButton.vue'

interface Props {
  show: boolean
  title?: string
  message?: string
  confirmText?: string
  cancelText?: string
  variant?: 'danger' | 'primary'
  loading?: boolean
}

withDefaults(defineProps<Props>(), {
  show: false,
  title: 'Xác Nhận Thao Tác',
  message: 'Bạn có chắc chắn muốn thực hiện thao tác này?',
  confirmText: 'Xác Nhận',
  cancelText: 'Hủy Bỏ',
  variant: 'danger',
  loading: false,
})

const emit = defineEmits<{
  (e: 'confirm'): void
  (e: 'close'): void
}>()
</script>

<template>
  <AppModal :show="show" width="sm" @close="emit('close')">
    <div class="text-center space-y-4 py-2">
      <!-- Icon -->
      <div
        class="w-12 h-12 rounded-full flex items-center justify-center mx-auto"
        :class="variant === 'danger' ? 'bg-err-bg text-err-text border border-err-border' : 'bg-violet-50 text-violet-600 border border-violet-100'"
      >
        <AlertTriangle class="w-6 h-6" />
      </div>

      <!-- Title & Message -->
      <div class="space-y-1.5">
        <h3 class="text-base font-extrabold text-ink tracking-tight">{{ title }}</h3>
        <p class="text-xs text-ink-muted leading-relaxed px-2">
          {{ message }}
        </p>
      </div>

      <!-- Action Buttons -->
      <div class="flex items-center justify-center gap-2 pt-2 border-t border-border">
        <AppButton variant="outline" size="sm" class="flex-1" @click="emit('close')">
          {{ cancelText }}
        </AppButton>
        <AppButton
          :variant="variant === 'danger' ? 'danger' : 'primary'"
          size="sm"
          class="flex-1"
          :loading="loading"
          @click="emit('confirm')"
        >
          {{ confirmText }}
        </AppButton>
      </div>
    </div>
  </AppModal>
</template>
