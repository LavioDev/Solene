<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useHomeDashboard } from '../composables/useHomeDashboard'
import HomeTopBar from '../components/HomeTopBar.vue'
import HomeWaveCircle from '../components/HomeWaveCircle.vue'
import HomeTodayEvents from '../components/HomeTodayEvents.vue'
import HomeUpcomingEvents from '../components/HomeUpcomingEvents.vue'
import HomeQuickActions from '../components/HomeQuickActions.vue'
import HomeMemoryModal from '../components/HomeMemoryModal.vue'
import HomeParticleHeartView from '../components/HomeParticleHeartView.vue'

const router = useRouter()
const showParticleHeart = ref(false)

const {
  loading,
  isRefreshingPartner,
  couple,
  partner,
  partnerStatus,
  notes,
  days,
  hours,
  minutes,
  seconds,
  coupleNickname,
  todayDateStr,
  todayOccurrences,
  upcomingOccurrences,
  showRandomNoteModal,
  currentRandomNote,
  currentRandomNoteAuthor,
  isShufflingNote,
  formatDisplayDate,
  calculateDaysRemaining,
  formatTaskTime,
  getUserInitials,
  pickRandomNote,
  openRandomNoteModal,
  closeRandomNoteModal,
  refreshPartnerStatusOnly,
} = useHomeDashboard()

function navigateTo(path: string) {
  router.push(path)
}
</script>

<template>
  <div class="h-full w-full select-none">
    <Transition name="fade" mode="out-in">
      <!-- 1. Pure Particle Heart View (Chỉ mở khi bấm vào trái tim ở Dashboard) -->
      <div v-if="showParticleHeart" class="w-full h-full">
        <HomeParticleHeartView @exit="showParticleHeart = false" />
      </div>

      <!-- 2. Main Dashboard (Màn hình chính mặc định) -->
      <div v-else class="space-y-6 px-6 py-6 pb-12 min-w-[800px] max-w-5xl mx-auto">
        <!-- Top Bar: Couple Profile (Left) & Partner Active Status (Right) -->
        <HomeTopBar
          :couple="couple"
          :loading="loading"
          :partner="partner"
          :partner-status="partnerStatus"
          :couple-nickname="coupleNickname"
          :formatted-start-date="couple?.start_date ? formatDisplayDate(couple.start_date) : ''"
          :is-refreshing-partner="isRefreshingPartner"
          :get-user-initials="getUserInitials"
          :format-task-time="formatTaskTime"
          @link-couple="navigateTo('/couples')"
          @refresh-partner="refreshPartnerStatusOnly"
        />

        <!-- Centered Love Wave Circle (Bấm trái tim -> mở màn hình hạt sáng, Bấm khối tròn -> mở ghi chú kỷ niệm) -->
        <HomeWaveCircle
          :days="days"
          :hours="hours"
          :minutes="minutes"
          :seconds="seconds"
          :formatted-start-date="couple?.start_date ? formatDisplayDate(couple.start_date) : ''"
          @open-random-memory="openRandomNoteModal"
          @open-particle-heart="showParticleHeart = true"
        />

        <!-- White Cards: Today & Upcoming Events -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Column 1: Today's Events & Date Notes -->
          <HomeTodayEvents
            :occurrences="todayOccurrences"
            :today-date-str="todayDateStr"
            :format-display-date="formatDisplayDate"
          />

          <!-- Column 2: Upcoming Events & Notes -->
          <HomeUpcomingEvents
            :occurrences="upcomingOccurrences"
            :format-display-date="formatDisplayDate"
            :calculate-days-remaining="calculateDaysRemaining"
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
      :show="showRandomNoteModal"
      :note="currentRandomNote"
      :author-name="currentRandomNoteAuthor"
      :is-shuffling="isShufflingNote"
      :has-notes="notes.length > 0"
      @close="closeRandomNoteModal"
      @shuffle="pickRandomNote"
    />
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
