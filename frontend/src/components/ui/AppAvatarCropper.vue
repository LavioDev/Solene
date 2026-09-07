<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Cropper } from 'vue-advanced-cropper'
import 'vue-advanced-cropper/dist/style.css'
import { apiClient } from '@/services/apiClient'
import {
  Camera,
  RotateCcw,
  RotateCw,
  ZoomIn,
  ZoomOut,
  RefreshCw,
  Check,
} from 'lucide-vue-next'
import AppModal from '@/components/ui/AppModal.vue'
import AppButton from '@/components/ui/AppButton.vue'
import defaultAvatar from '@/img/avatar.jpg'

interface Props {
  modelValue?: string | null
  name?: string
  size?: 'sm' | 'md' | 'lg' | 'xl'
  disabled?: boolean
  editable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: null,
  name: 'User',
  size: 'lg',
  disabled: false,
  editable: true,
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: string | null): void
  (e: 'uploaded', value: string): void
}>()

const { t } = useI18n()

// Cropper Modal state
const showModal = ref(false)
const imageSrc = ref<string | null>(null)
const cropperRef = ref<any>(null)

const fileInputRef = ref<HTMLInputElement | null>(null)
const uploading = ref(false)
const uploadError = ref<string | null>(null)

// Avatar size styles (4x area scaling)
const sizeClasses = computed(() => {
  switch (props.size) {
    case 'sm':
      return 'w-16 h-16 text-base'
    case 'md':
      return 'w-24 h-24 text-xl'
    case 'xl':
      return 'w-48 h-48 text-4xl'
    case 'lg':
    default:
      return 'w-32 h-32 text-3xl'
  }
})

const cameraIconSizeClass = computed(() => {
  switch (props.size) {
    case 'sm':
      return 'w-5 h-5'
    case 'md':
      return 'w-6 h-6'
    case 'xl':
      return 'w-10 h-10'
    case 'lg':
    default:
      return 'w-8 h-8'
  }
})


function triggerFileInput() {
  if (props.disabled || !props.editable) return
  if (fileInputRef.value) {
    fileInputRef.value.value = ''
    fileInputRef.value.click()
  }
}

function onFileSelected(e: Event) {
  const target = e.target as HTMLInputElement
  if (!target.files || target.files.length === 0) return

  const file = target.files[0]
  if (!file.type.startsWith('image/')) return

  const reader = new FileReader()
  reader.onload = (event) => {
    imageSrc.value = event.target?.result as string
    showModal.value = true
  }
  reader.readAsDataURL(file)
}

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
      canvas.toBlob((b: Blob | null) => resolve(b), 'image/jpeg', 0.9)
    })

    if (!blob) throw new Error('Could not create image blob.')

    const formData = new FormData()
    formData.append('file', blob, 'avatar.jpg')

    const response = await apiClient.post<{ url: string }>('/media/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })

    const newUrl = response.data.url
    emit('update:modelValue', newUrl)
    emit('uploaded', newUrl)
    closeModal()
  } catch (err: any) {
    console.error('Failed to upload cropped avatar:', err)
    uploadError.value = err.response?.data?.detail || t('avatar.uploadError')
  } finally {
    uploading.value = false
  }
}

function closeModal() {
  showModal.value = false
  imageSrc.value = null
  uploadError.value = null
}
</script>

<template>
  <div class="inline-flex flex-col items-center">
    <!-- Hidden File Input -->
    <input
      ref="fileInputRef"
      type="file"
      accept="image/jpeg,image/png,image/webp,image/gif"
      class="hidden"
      @change="onFileSelected"
    />

    <!-- Avatar Container (Clickable Frame, Locked Square) -->
    <div
      class="relative group select-none shrink-0 aspect-square"
      :class="[
        sizeClasses,
        editable && !disabled ? 'cursor-pointer' : ''
      ]"
      @click="triggerFileInput"
      :title="editable && !disabled ? t('avatar.change') : ''"
    >
      <div
        class="w-full h-full aspect-square rounded-2xl flex items-center justify-center font-extrabold shadow-sm border overflow-hidden transition-all duration-200 shrink-0"
        :class="[
          modelValue
            ? 'border-primary-200 bg-surface-subtle'
            : 'bg-gradient-to-br from-primary-100 to-primary-200 border-primary-300 text-primary-800',
          editable && !disabled ? 'group-hover:ring-2 group-hover:ring-primary-400/40 group-hover:border-primary-400' : ''
        ]"
      >
        <!-- Actual Avatar Image or Default Avatar -->
        <img
          :src="modelValue || defaultAvatar"
          :alt="name"
          class="w-full h-full object-cover object-center shrink-0 aspect-square"
        />
      </div>

      <!-- Hover Edit Camera Overlay -->
      <div
        v-if="editable && !disabled"
        class="absolute inset-0 rounded-2xl bg-black/35 text-white flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-200 backdrop-blur-2xs shadow-md"
      >
        <Camera :class="[cameraIconSizeClass, 'text-white']" />
      </div>
    </div>

    <!-- Crop & Adjust Modal (Solène Native UI Light Theme) -->
    <AppModal
      :show="showModal"
      :title="t('avatar.cropTitle')"
      width="lg"
      @close="closeModal"
    >
      <div class="space-y-4">
        <!-- Error alert -->
        <div v-if="uploadError" class="p-2.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs font-medium">
          {{ uploadError }}
        </div>

        <!-- vue-advanced-cropper Area (Full width, clean pastel bg, locked 1:1 square) -->
        <div class="w-full max-h-[60vh] overflow-hidden rounded-2xl bg-surface-subtle border border-border select-none">
          <Cropper
            v-if="imageSrc"
            ref="cropperRef"
            :src="imageSrc"
            :stencil-props="{
              aspectRatio: 1,
            }"
            class="w-full max-h-[58vh] solene-cropper"
          />
        </div>

        <!-- Cropper Control Buttons -->
        <div class="flex items-center justify-center gap-2 pt-1">
          <button
            type="button"
            @click="handleRotateLeft"
            :title="t('avatar.rotateLeft')"
            class="p-2 rounded-xl bg-surface-subtle hover:bg-surface-raised border border-border text-ink hover:text-primary-700 transition-colors cursor-pointer shadow-2xs"
          >
            <RotateCcw class="w-4 h-4" />
          </button>
          <button
            type="button"
            @click="handleRotateRight"
            :title="t('avatar.rotateRight')"
            class="p-2 rounded-xl bg-surface-subtle hover:bg-surface-raised border border-border text-ink hover:text-primary-700 transition-colors cursor-pointer shadow-2xs"
          >
            <RotateCw class="w-4 h-4" />
          </button>
          <button
            type="button"
            @click="handleZoomIn"
            :title="t('avatar.zoomIn')"
            class="p-2 rounded-xl bg-surface-subtle hover:bg-surface-raised border border-border text-ink hover:text-primary-700 transition-colors cursor-pointer shadow-2xs"
          >
            <ZoomIn class="w-4 h-4" />
          </button>
          <button
            type="button"
            @click="handleZoomOut"
            :title="t('avatar.zoomOut')"
            class="p-2 rounded-xl bg-surface-subtle hover:bg-surface-raised border border-border text-ink hover:text-primary-700 transition-colors cursor-pointer shadow-2xs"
          >
            <ZoomOut class="w-4 h-4" />
          </button>
          <button
            type="button"
            @click="handleReset"
            :title="t('avatar.reset')"
            class="p-2 rounded-xl bg-surface-subtle hover:bg-surface-raised border border-border text-ink hover:text-primary-700 transition-colors cursor-pointer shadow-2xs"
          >
            <RefreshCw class="w-4 h-4" />
          </button>
        </div>

        <!-- Modal Footer Actions -->
        <div class="flex items-center justify-end gap-2 pt-3 border-t border-border">
          <AppButton variant="outline" type="button" size="sm" @click="closeModal">
            {{ t('common.cancel') }}
          </AppButton>
          <AppButton type="button" size="sm" :loading="uploading" @click="handleCropAndSave">
            <Check class="w-3.5 h-3.5 mr-1" />
            {{ t('avatar.cropAndSave') }}
          </AppButton>
        </div>
      </div>
    </AppModal>
  </div>
</template>

<style>
/* Solène Native UI Vue Advanced Cropper Customization */
.solene-cropper {
  width: 100%;
  max-height: 58vh;
  background: #fafafa !important;
}

.solene-cropper .vue-advanced-cropper__background,
.solene-cropper .vue-advanced-cropper__foreground {
  background: #fafafa !important;
}

.solene-cropper .vue-simple-handler {
  background: #7c3aed !important;
  border: 2px solid #ffffff !important;
  border-radius: 3px !important;
  width: 10px !important;
  height: 10px !important;
}

.solene-cropper .vue-simple-line {
  border-color: rgba(124, 58, 237, 0.9) !important;
}
</style>
