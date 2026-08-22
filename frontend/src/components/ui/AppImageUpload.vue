<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Cropper } from 'vue-advanced-cropper'
import 'vue-advanced-cropper/dist/style.css'
import { apiClient } from '@/services/apiClient'
import {
  UploadCloud,
  X,
  Loader2,
  Crop,
  RotateCcw,
  RotateCw,
  ZoomIn,
  ZoomOut,
  RefreshCw,
  Check,
} from 'lucide-vue-next'
import AppModal from '@/components/ui/AppModal.vue'
import AppButton from '@/components/ui/AppButton.vue'

interface Props {
  modelValue?: string[] | string | null
  label?: string
  multiple?: boolean
  maxFiles?: number
  disabled?: boolean
  required?: boolean
  crop?: boolean
  cropAspectRatio?: number
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: () => [],
  label: '',
  multiple: false,
  maxFiles: 5,
  disabled: false,
  required: false,
  crop: true,
  cropAspectRatio: 1,
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: string[] | string): void
}>()

const { t } = useI18n()
const fileInputRef = ref<HTMLInputElement | null>(null)
const isDragging = ref(false)
const uploading = ref(false)
const uploadError = ref<string | null>(null)

// Cropper Modal state
const showCropModal = ref(false)
const cropImageSrc = ref<string | null>(null)
const cropperRef = ref<any>(null)
const editingIndex = ref<number | null>(null)

// Normalize images array
const images = computed<string[]>(() => {
  if (!props.modelValue) return []
  if (Array.isArray(props.modelValue)) return props.modelValue.filter(Boolean)
  return [props.modelValue]
})

function triggerFileInput() {
  if (props.disabled || uploading.value) return
  if (fileInputRef.value) {
    fileInputRef.value.value = ''
    fileInputRef.value.click()
  }
}

async function uploadFile(file: File | Blob, filename = 'image.jpg') {
  const formData = new FormData()
  formData.append('file', file, filename)

  const res = await apiClient.post<{ url: string; filename: string }>('/media/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return res.data.url
}

async function handleFiles(files: FileList | null) {
  if (!files || files.length === 0) return
  uploadError.value = null

  const filesToUpload = Array.from(files).filter((f) => f.type.startsWith('image/'))
  if (filesToUpload.length === 0) {
    uploadError.value = t('upload.onlyImages') || 'Only image files are accepted.'
    return
  }

  // If crop is enabled and single file uploaded -> open Cropper Modal
  if (props.crop && filesToUpload.length === 1 && !props.multiple) {
    const file = filesToUpload[0]
    const reader = new FileReader()
    reader.onload = (e) => {
      cropImageSrc.value = e.target?.result as string
      editingIndex.value = null
      showCropModal.value = true
    }
    reader.readAsDataURL(file)
    return
  }

  // Otherwise, direct upload
  uploading.value = true
  try {
    const uploadPromises: Promise<string>[] = []
    const currentCount = images.value.length
    const maxCanAdd = props.multiple ? props.maxFiles - currentCount : 1
    const targetFiles = filesToUpload.slice(0, Math.max(0, maxCanAdd))

    for (const file of targetFiles) {
      uploadPromises.push(uploadFile(file, file.name))
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

// Open cropper for existing image
function openCropExisting(url: string, index: number) {
  cropImageSrc.value = url
  editingIndex.value = index
  showCropModal.value = true
}

// Cropper Controls
function handleRotateLeft() {
  cropperRef.value?.rotate(-90)
}

function handleRotateRight() {
  cropperRef.value?.rotate(90)
}

function handleZoomIn() {
  cropperRef.value?.zoom(1.15)
}

function handleZoomOut() {
  cropperRef.value?.zoom(0.85)
}

function handleReset() {
  cropperRef.value?.reset()
}

async function handleCropAndSave() {
  if (!cropperRef.value) return
  const result = cropperRef.value.getResult()
  if (!result || !result.canvas) return

  uploadError.value = null
  uploading.value = true

  try {
    const canvas = result.canvas as HTMLCanvasElement
    const blob = await new Promise<Blob | null>((resolve) => {
      canvas.toBlob((b: Blob | null) => resolve(b), 'image/jpeg', 0.92)
    })

    if (!blob) throw new Error('Could not create image blob.')

    const newUrl = await uploadFile(blob, 'cover.jpg')

    if (props.multiple) {
      if (editingIndex.value !== null && editingIndex.value >= 0) {
        const updated = [...images.value]
        updated[editingIndex.value] = newUrl
        emit('update:modelValue', updated)
      } else {
        const updated = [...images.value, newUrl]
        emit('update:modelValue', updated)
      }
    } else {
      emit('update:modelValue', newUrl)
    }

    closeCropModal()
  } catch (err: any) {
    console.error('Failed to upload cropped cover:', err)
    uploadError.value = err.response?.data?.detail || t('upload.failed')
  } finally {
    uploading.value = false
  }
}

function closeCropModal() {
  showCropModal.value = false
  cropImageSrc.value = null
  editingIndex.value = null
  uploadError.value = null
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

    <!-- Hidden File Input -->
    <input
      ref="fileInputRef"
      type="file"
      accept="image/*"
      :multiple="multiple"
      @change="onFileChange"
      class="hidden"
    />

    <!-- Dropzone Area (When no image or in multiple mode) -->
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
      <div v-if="uploading && !showCropModal" class="flex flex-col items-center gap-2 py-2">
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

    <!-- Uploaded Thumbnails Grid & Square Preview -->
    <div v-if="images.length > 0">
      <!-- 1. Single Image Mode (Square Aspect Ratio) -->
      <div
        v-if="!multiple"
        class="relative w-48 h-48 aspect-square rounded-2xl overflow-hidden border border-border group bg-surface-subtle shadow-card"
      >
        <img
          :src="images[0]"
          alt="Image preview"
          class="w-full h-full object-cover object-center aspect-square"
        />

        <!-- Hover Action Toolbar (Crop & Remove & Re-upload) -->
        <div class="absolute inset-0 bg-black/40 backdrop-blur-2xs opacity-0 group-hover:opacity-100 transition-opacity duration-200 flex items-center justify-center gap-2.5">
          <button
            v-if="crop"
            type="button"
            @click.stop="openCropExisting(images[0], 0)"
            class="px-3 py-1.5 rounded-xl bg-white/90 hover:bg-white text-ink text-xs font-semibold shadow-md transition-all flex items-center gap-1.5 cursor-pointer hover:scale-105"
            :title="t('upload.cropImage')"
          >
            <Crop class="w-3.5 h-3.5 text-violet-600" />
            <span>{{ t('upload.cropImage') }}</span>
          </button>

          <button
            type="button"
            @click.stop="triggerFileInput"
            class="px-3 py-1.5 rounded-xl bg-white/90 hover:bg-white text-ink text-xs font-semibold shadow-md transition-all flex items-center gap-1.5 cursor-pointer hover:scale-105"
            :title="t('upload.changeImage')"
          >
            <UploadCloud class="w-3.5 h-3.5 text-violet-600" />
            <span>{{ t('upload.changeImage') }}</span>
          </button>

          <button
            type="button"
            @click.stop="removeImage(0)"
            class="p-1.5 rounded-xl bg-rose-600/90 hover:bg-rose-600 text-white shadow-md transition-all cursor-pointer hover:scale-105"
            :title="t('common.delete')"
          >
            <X class="w-4 h-4" />
          </button>
        </div>
      </div>

      <!-- 2. Multiple Thumbnails Grid -->
      <div v-else class="grid grid-cols-3 sm:grid-cols-4 gap-2.5 pt-1">
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

          <!-- Action buttons overlay -->
          <div class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-1.5">
            <button
              v-if="crop"
              type="button"
              @click.stop="openCropExisting(imgUrl, index)"
              class="w-7 h-7 rounded-lg bg-white/90 hover:bg-white text-violet-700 flex items-center justify-center transition-colors cursor-pointer shadow-xs"
              :title="t('upload.cropImage')"
            >
              <Crop class="w-3.5 h-3.5" />
            </button>

            <button
              type="button"
              @click.stop="removeImage(index)"
              :title="t('upload.removeImage')"
              class="w-7 h-7 rounded-lg bg-rose-600/90 hover:bg-rose-600 text-white flex items-center justify-center transition-colors cursor-pointer shadow-xs"
            >
              <X class="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Error message -->
    <p v-if="uploadError" class="text-xs text-err-text font-medium">{{ uploadError }}</p>

    <!-- Image Cropper Modal (Solène Native UI Light Theme) -->
    <AppModal
      :show="showCropModal"
      :title="label ? `${t('upload.cropTitle')}: ${label}` : t('upload.cropTitle')"
      width="1000"
      @close="closeCropModal"
    >
      <div class="space-y-4">
        <!-- Error alert -->
        <div v-if="uploadError" class="p-2.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs font-medium">
          {{ uploadError }}
        </div>

        <!-- vue-advanced-cropper Area -->
        <div class="w-full max-h-[60vh] overflow-hidden rounded-2xl bg-surface-subtle border border-border select-none flex items-center justify-center">
          <Cropper
            v-if="cropImageSrc"
            ref="cropperRef"
            :src="cropImageSrc"
            :stencil-props="{
              aspectRatio: cropAspectRatio,
            }"
            class="w-full max-h-[58vh] solene-cover-cropper"
          />
        </div>

        <!-- Cropper Control Buttons -->
        <div class="flex items-center justify-center gap-2 pt-1">
          <button
            type="button"
            @click="handleRotateLeft"
            :title="t('avatar.rotateLeft')"
            class="p-2 rounded-xl bg-surface-subtle hover:bg-surface-raised border border-border text-ink hover:text-violet-700 transition-colors cursor-pointer shadow-2xs"
          >
            <RotateCcw class="w-4 h-4" />
          </button>
          <button
            type="button"
            @click="handleRotateRight"
            :title="t('avatar.rotateRight')"
            class="p-2 rounded-xl bg-surface-subtle hover:bg-surface-raised border border-border text-ink hover:text-violet-700 transition-colors cursor-pointer shadow-2xs"
          >
            <RotateCw class="w-4 h-4" />
          </button>
          <button
            type="button"
            @click="handleZoomIn"
            :title="t('avatar.zoomIn')"
            class="p-2 rounded-xl bg-surface-subtle hover:bg-surface-raised border border-border text-ink hover:text-violet-700 transition-colors cursor-pointer shadow-2xs"
          >
            <ZoomIn class="w-4 h-4" />
          </button>
          <button
            type="button"
            @click="handleZoomOut"
            :title="t('avatar.zoomOut')"
            class="p-2 rounded-xl bg-surface-subtle hover:bg-surface-raised border border-border text-ink hover:text-violet-700 transition-colors cursor-pointer shadow-2xs"
          >
            <ZoomOut class="w-4 h-4" />
          </button>
          <button
            type="button"
            @click="handleReset"
            :title="t('avatar.reset')"
            class="p-2 rounded-xl bg-surface-subtle hover:bg-surface-raised border border-border text-ink hover:text-violet-700 transition-colors cursor-pointer shadow-2xs"
          >
            <RefreshCw class="w-4 h-4" />
          </button>
        </div>

        <!-- Modal Footer Actions -->
        <div class="flex items-center justify-end gap-2 pt-3 border-t border-border">
          <AppButton variant="outline" type="button" size="sm" @click="closeCropModal">
            {{ t('common.cancel') }}
          </AppButton>
          <AppButton type="button" size="sm" :loading="uploading" @click="handleCropAndSave">
            <Check class="w-3.5 h-3.5 mr-1" />
            <span>{{ t('upload.cropAndSave') }}</span>
          </AppButton>
        </div>
      </div>
    </AppModal>
  </div>
</template>

<style>
/* Solène Cover Cropper Styles */
.solene-cover-cropper {
  width: 100%;
  max-height: 58vh;
  background: #fafafa !important;
}

.solene-cover-cropper .vue-advanced-cropper__background,
.solene-cover-cropper .vue-advanced-cropper__foreground {
  background: #fafafa !important;
}

.solene-cover-cropper .vue-simple-handler {
  background: #7c3aed !important;
  border: 2px solid #ffffff !important;
  border-radius: 3px !important;
  width: 12px !important;
  height: 12px !important;
}

.solene-cover-cropper .vue-simple-line {
  border-color: rgba(124, 58, 237, 0.9) !important;
}
</style>
