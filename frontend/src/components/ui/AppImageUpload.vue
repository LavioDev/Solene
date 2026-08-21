<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { apiClient } from '@/services/apiClient'
import { UploadCloud, X, Loader2 } from 'lucide-vue-next'

interface Props {
  modelValue?: string[] | string | null
  label?: string
  multiple?: boolean
  maxFiles?: number
  disabled?: boolean
  required?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: () => [],
  label: '',
  multiple: false,
  maxFiles: 5,
  disabled: false,
  required: false,
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: string[] | string): void
}>()

const { t } = useI18n()
const fileInputRef = ref<HTMLInputElement | null>(null)
const isDragging = ref(false)
const uploading = ref(false)
const uploadError = ref<string | null>(null)

// Normalize images array
const images = computed<string[]>(() => {
  if (!props.modelValue) return []
  if (Array.isArray(props.modelValue)) return props.modelValue
  return [props.modelValue]
})

function triggerFileInput() {
  if (props.disabled || uploading.value) return
  fileInputRef.value?.click()
}

async function uploadFile(file: File) {
  const formData = new FormData()
  formData.append('file', file)

  const res = await apiClient.post<{ url: string; filename: string }>('/media/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return res.data.url
}

async function handleFiles(files: FileList | null) {
  if (!files || files.length === 0) return
  uploadError.value = null
  uploading.value = true

  try {
    const uploadPromises: Promise<string>[] = []
    const filesToUpload = Array.from(files).filter(f => f.type.startsWith('image/'))

    if (filesToUpload.length === 0) {
      uploadError.value = t('upload.onlyImages')
      return
    }

    const currentCount = images.value.length
    const maxCanAdd = props.multiple ? props.maxFiles - currentCount : 1
    const targetFiles = filesToUpload.slice(0, Math.max(0, maxCanAdd))

    for (const file of targetFiles) {
      uploadPromises.push(uploadFile(file))
    }

    const newUrls = await Promise.all(uploadPromises)

    if (props.multiple) {
      const updated = [...images.value, ...newUrls]
      emit('update:modelValue', updated)
    } else {
      emit('update:modelValue', newUrls[0] || '')
    }
  } catch (err: any) {
    console.error('Failed to upload image:', err)
    uploadError.value = err.response?.data?.detail || t('upload.failed')
  } finally {
    uploading.value = false
    if (fileInputRef.value) fileInputRef.value.value = ''
  }
}

function onFileChange(e: Event) {
  const input = e.target as HTMLInputElement
  handleFiles(input.files)
}

function onDrop(e: DragEvent) {
  isDragging.value = false
  if (props.disabled) return
  handleFiles(e.dataTransfer?.files || null)
}

function removeImage(index: number) {
  if (props.multiple) {
    const updated = [...images.value]
    updated.splice(index, 1)
    emit('update:modelValue', updated)
  } else {
    emit('update:modelValue', '')
  }
}
</script>

<template>
  <div class="space-y-2 w-full select-none">
    <!-- Label -->
    <div v-if="label" class="flex items-center justify-between">
      <label class="block text-xs font-bold text-ink tracking-wider uppercase">
        {{ label }}
        <span v-if="required" class="text-rose-500">*</span>
      </label>
      <span v-if="multiple" class="text-[11px] text-ink-faint font-mono">
        {{ images.length }}/{{ maxFiles }}
      </span>
    </div>

    <!-- Dropzone Area -->
    <div
      v-if="!images.length || multiple"
      @click="triggerFileInput"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="onDrop"
      class="border-2 border-dashed rounded-2xl p-4 transition-all duration-150 cursor-pointer flex flex-col items-center justify-center text-center group"
      :class="[
        isDragging
          ? 'border-violet-500 bg-violet-50/60'
          : 'border-border/80 hover:border-violet-400 bg-surface-subtle/50 hover:bg-surface-raised',
        disabled ? 'opacity-50 cursor-not-allowed' : ''
      ]"
    >
      <input
        ref="fileInputRef"
        type="file"
        accept="image/*"
        :multiple="multiple"
        @change="onFileChange"
        class="hidden"
      />

      <div v-if="uploading" class="flex flex-col items-center gap-2 py-2">
        <Loader2 class="w-6 h-6 text-violet-600 animate-spin" />
        <span class="text-xs font-medium text-ink-muted">{{ t('upload.uploading') }}</span>
      </div>

      <div v-else class="flex flex-col items-center gap-1.5 py-1">
        <div class="w-9 h-9 rounded-xl bg-violet-50 border border-violet-100 flex items-center justify-center text-violet-600 group-hover:scale-110 transition-transform">
          <UploadCloud class="w-5 h-5" />
        </div>
        <div class="text-xs font-semibold text-ink mt-0.5">
          {{ t('upload.dragOrClick') }}
        </div>
        <p class="text-[11px] text-ink-faint">
          {{ t('upload.supportedFormats') }}
        </p>
      </div>
    </div>

    <!-- Uploaded Thumbnails Grid -->
    <div v-if="images.length > 0" class="grid grid-cols-3 sm:grid-cols-4 gap-2.5 pt-1">
      <div
        v-for="(imgUrl, index) in images"
        :key="imgUrl + index"
        class="relative aspect-square rounded-xl overflow-hidden border border-border group bg-surface-subtle shadow-2xs"
      >
        <img
          :src="imgUrl"
          alt="Uploaded preview"
          class="w-full h-full object-cover object-center"
        />

        <!-- Remove Button -->
        <button
          type="button"
          @click.stop="removeImage(index)"
          :title="t('upload.removeImage')"
          class="absolute top-1.5 right-1.5 w-6 h-6 rounded-full bg-black/60 hover:bg-rose-600 text-white flex items-center justify-center transition-colors cursor-pointer opacity-90 group-hover:opacity-100 shadow-xs"
        >
          <X class="w-3.5 h-3.5" />
        </button>
      </div>
    </div>

    <!-- Error message -->
    <p v-if="uploadError" class="text-xs text-err-text font-medium">{{ uploadError }}</p>
  </div>
</template>
