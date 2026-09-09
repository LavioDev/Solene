<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useHomeDashboard } from '../composables/useHomeDashboard'
import { useMoodStore } from '@/stores/moodStore'
import { useStickerBoard } from '../composables/useStickerBoard'
import HomeTopBar from '../components/HomeTopBar.vue'
import HomeDailyMoodWidget from '../components/HomeDailyMoodWidget.vue'
import HomeWaveCircle from '../components/HomeWaveCircle.vue'
import HomeTodayEvents from '../components/HomeTodayEvents.vue'
import HomeUpcomingEvents from '../components/HomeUpcomingEvents.vue'
import HomeQuickActions from '../components/HomeQuickActions.vue'
import HomeMemoryModal from '../components/HomeMemoryModal.vue'
import HomeParticleHeartView from '../components/HomeParticleHeartView.vue'
import HomeStickerCanvas from '../components/HomeStickerCanvas.vue'
import HomeStickerPickerDrawer from '../components/HomeStickerPickerDrawer.vue'
import CoupleInviteModal from '@/modules/couples/components/CoupleInviteModal.vue'

const router = useRouter()
const { t } = useI18n()
const moodStore = useMoodStore()
const showParticleHeart = ref(false)
const showDailyMoodWidget = ref(false)
const showInviteModal = ref(false)

const {
  pinnedStickers,
  isPickerOpen,
  packManifest,
  pinSticker,
  updateStickerLocal,
  bringToFront,
  removeSticker,
  toggleLock,
  clearAll,
} = useStickerBoard()


const {
  loading,
  isRefreshingPartner,
  couple,
  partner,
  partnerStatus,
  memories,
  days,
  hours,
  minutes,
  seconds,
  coupleNickname,
  todayDateStr,
  todayOccurrences,
  upcomingOccurrences,
  showRandomMemoryModal,
  currentRandomMemory,
  currentRandomMemoryAuthor,
  isShufflingMemory,
  formatDisplayDate,
  calculateDaysRemaining,
  formatTaskTime,
  getUserInitials,
  pickRandomMemory,
  openRandomMemoryModal,
  closeRandomMemoryModal,
  refreshPartnerStatusOnly,
} = useHomeDashboard()

function navigateTo(path: string) {
  router.push(path)
}
</script>

<template>
  <div class="relative min-h-full w-full select-none">
    <!-- Chiikawa Desktop Sticker Canvas Overlay (Chỉ hiển thị cho 2 người trong quan hệ kết đôi) -->
    <HomeStickerCanvas
      v-if="!showParticleHeart && Boolean(couple)"
      :stickers="pinnedStickers"
      @update-sticker="updateStickerLocal"
      @remove-sticker="removeSticker"
      @bring-to-front="bringToFront"
      @toggle-lock="toggleLock"
    />

    <Transition name="fade" mode="out-in">
      <!-- 1. Pure Particle Heart View (Chỉ mở khi bấm vào trái tim ở Dashboard) -->
      <div v-if="showParticleHeart" class="w-full h-full">
        <HomeParticleHeartView @exit="showParticleHeart = false" />
      </div>

      <!-- 2. Main Dashboard (Màn hình chính mặc định) -->
      <div v-else class="w-full max-w-5xl mx-auto px-4 py-4 sm:px-6 sm:py-6 pb-12 space-y-5 sm:space-y-6">

        <!-- Top Bar: Couple Profile (Left) & Mood Button / Partner Active Status (Right) -->
        <HomeTopBar
          :couple="couple"
          :loading="loading"
          :partner="partner"
          :partner-status="partnerStatus"
          :couple-nickname="coupleNickname"
          :formatted-start-date="couple?.start_date ? formatDisplayDate(couple.start_date) : ''"
          :is-refreshing-partner="isRefreshingPartner"
          :is-mood-open="showDailyMoodWidget"
          :my-mood="moodStore.myTodayMood"
          :get-user-initials="getUserInitials"
          :format-task-time="formatTaskTime"
          @link-couple="showInviteModal = true"
          @refresh-partner="refreshPartnerStatusOnly"
          @toggle-mood="showDailyMoodWidget = !showDailyMoodWidget"
        />

        <!-- Daily Mood Tracker Modal (Mở khi bấm vào nút Cảm xúc ở TopBar) -->
        <HomeDailyMoodWidget
          :show="showDailyMoodWidget"
          @close="showDailyMoodWidget = false"
        />

        <!-- Centered Love Wave Circle (Bấm trái tim -> mở màn hình hạt sáng, Bấm khối tròn -> mở ghi chú kỷ niệm) -->
        <HomeWaveCircle
          :days="days"
          :hours="hours"
          :minutes="minutes"
          :seconds="seconds"
          :formatted-start-date="couple?.start_date ? formatDisplayDate(couple.start_date) : ''"
          :partner-mood="moodStore.partnerTodayMood"
          :partner-name="partner?.full_name"
          @open-random-memory="openRandomMemoryModal"
          @open-particle-heart="showParticleHeart = true"
        />

        <!-- White Cards: Today & Upcoming Events -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
          <!-- Column 1: Today's Events & Date Memories -->
          <HomeTodayEvents
            :occurrences="todayOccurrences"
            :today-date-str="todayDateStr"
            :format-display-date="formatDisplayDate"
            :loading="loading"
          />

          <!-- Column 2: Upcoming Events & Memories -->
          <HomeUpcomingEvents
            :occurrences="upcomingOccurrences"
            :format-display-date="formatDisplayDate"
            :calculate-days-remaining="calculateDaysRemaining"
            :loading="loading"
            @view-calendar="navigateTo('/calendar')"
          />
        </div>

        <!-- Quick Action Navigation Pills -->
        <HomeQuickActions
          @navigate="navigateTo"
        />
      </div>
    </Transition>

    <!-- Sweet Memory Modal -->
    <HomeMemoryModal
      :show="showRandomMemoryModal"
      :memory="currentRandomMemory"
      :author-name="currentRandomMemoryAuthor"
      :is-shuffling="isShufflingMemory"
      :has-memories="memories.length > 0"
      @close="closeRandomMemoryModal"
      @shuffle="pickRandomMemory"
    />

    <!-- Couple Invite & Link Modal -->
    <CoupleInviteModal
      :show="showInviteModal"
      @close="showInviteModal = false"
    />

    <!-- Chiikawa Sticker Picker Drawer (Chỉ mở khi có relation kết đôi) -->
    <HomeStickerPickerDrawer
      v-if="Boolean(couple)"
      :show="isPickerOpen && Boolean(couple)"
      :manifest="packManifest"
      :pinned-count="pinnedStickers.length"
      @close="isPickerOpen = false"
      @select-sticker="pinSticker"
      @clear-all="clearAll"
    />

    <!-- Desktop Floating Action Button (FAB) to open Sticker Board (Chỉ hiện khi có relation) -->
    <div
      v-if="Boolean(couple)"
      class="fixed bottom-6 right-6 hidden lg:flex flex-col items-end gap-2 z-40 select-none"
    >
      <button
        type="button"
        class="group relative flex items-center gap-2 pl-2 pr-3.5 py-1.5 rounded-2xl bg-white/95 hover:bg-white border border-primary-200/90 hover:border-primary-300 shadow-lg shadow-primary-500/15 hover:shadow-xl hover:shadow-primary-500/25 hover:-translate-y-0.5 active:translate-y-0 active:scale-95 transition-all duration-200 cursor-pointer backdrop-blur-md"
        :title="t('stickers.openPicker')"
        @click="isPickerOpen = true"
      >
        <div class="w-8 h-8 rounded-xl bg-primary-50 border border-primary-100 flex items-center justify-center p-0.5 shrink-0 group-hover:scale-110 transition-transform overflow-hidden">
          <img
            src="/stickers/chiikawa/gifs/chiikawa_anim_01.gif"
            alt="Chiikawa"
            class="w-full h-full object-contain"
          />
        </div>
        <span class="text-xs font-bold text-primary-950 font-sans tracking-wide">
          {{ t('stickers.buttonLabel') }}
        </span>
      </button>
    </div>
  </div>
</template>


<style scoped>
.fade-enter-active {
  transition: opacity 0.18s ease-out;
  will-change: opacity;
}

.fade-leave-active {
  transition: opacity 0.12s ease-in;
  will-change: opacity;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
