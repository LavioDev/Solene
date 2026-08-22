<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { Couple, UserPartnerSummary } from '@/types/couple'
import type { PartnerActiveStatus } from '@/types/task'
import { Heart, Plus } from 'lucide-vue-next'
import AppButton from '@/components/ui/AppButton.vue'

interface Props {
  couple: Couple | null
  loading: boolean
  partner: UserPartnerSummary | null
  partnerStatus: PartnerActiveStatus | null
  coupleNickname: string
  formattedStartDate: string
  isRefreshingPartner?: boolean
  getUserInitials: (name?: string, email?: string) => string
  formatTaskTime?: (isoString?: string | null) => string
}

withDefaults(defineProps<Props>(), {
  isRefreshingPartner: false,
})

const emit = defineEmits<{
  (e: 'link-couple'): void
  (e: 'refresh-partner'): void
}>()

const { t } = useI18n()
</script>

<template>
  <div class="flex items-center justify-between gap-4 pb-3 border-b border-border/60 select-none">
    <!-- Left: Couple Avatars & Nickname & Status Dot -->
    <div v-if="couple" class="flex items-center gap-3">
      <!-- 2 Overlapping Avatars -->
      <div class="flex items-center -space-x-2 shrink-0">
        <!-- User 1 Avatar -->
        <div class="relative w-9 h-9 rounded-full bg-violet-600 text-white font-bold text-xs flex items-center justify-center border-2 border-white shadow-2xs">
          <div class="w-full h-full rounded-full overflow-hidden flex items-center justify-center">
            <img
              v-if="couple.user1?.avatar_url"
              :src="couple.user1.avatar_url"
              :alt="couple.user1.full_name"
              class="w-full h-full object-cover"
            />
            <span v-else>{{ getUserInitials(couple.user1?.full_name, couple.user1?.email) }}</span>
          </div>

          <!-- Dot on User 1 if User 1 is the Partner -->
          <span
            v-if="partner && partner.id === couple.user1_id"
            class="absolute bottom-0 right-0 w-2.5 h-2.5 rounded-full border-2 border-white shadow-xs z-10"
            :class="partnerStatus?.is_busy ? 'bg-rose-500' : 'bg-emerald-500'"
            :title="partnerStatus?.is_busy ? t('home.partnerStatus.busy', { name: partner.full_name }) : t('home.partnerStatus.available', { name: partner.full_name })"
          ></span>
        </div>

        <!-- User 2 Avatar -->
        <div class="relative w-9 h-9 rounded-full bg-purple-500 text-white font-bold text-xs flex items-center justify-center border-2 border-white shadow-2xs z-10">
          <div class="w-full h-full rounded-full overflow-hidden flex items-center justify-center">
            <img
              v-if="couple.user2?.avatar_url"
              :src="couple.user2.avatar_url"
              :alt="couple.user2.full_name"
              class="w-full h-full object-cover"
            />
            <span v-else>{{ getUserInitials(couple.user2?.full_name, couple.user2?.email) }}</span>
          </div>

          <!-- Dot on User 2 if User 2 is the Partner -->
          <span
            v-if="partner && (partner.id === couple.user2_id || !couple.user1_id)"
            class="absolute bottom-0 right-0 w-2.5 h-2.5 rounded-full border-2 border-white shadow-xs z-20"
            :class="partnerStatus?.is_busy ? 'bg-rose-500' : 'bg-emerald-500'"
            :title="partnerStatus?.is_busy ? t('home.partnerStatus.busy', { name: partner.full_name }) : t('home.partnerStatus.available', { name: partner.full_name })"
          ></span>
        </div>
      </div>

      <!-- Couple Nickname & Since Date -->
      <div>
        <h1 class="text-sm font-bold text-ink flex items-center gap-1.5">
          <span>{{ coupleNickname }}</span>
        </h1>
        <p class="text-[11px] text-ink-muted font-mono">
          {{ t('home.since', { date: formattedStartDate }) }}
        </p>
      </div>
    </div>

    <!-- Fallback if No Couple Linked -->
    <div v-else-if="!loading" class="flex items-center gap-2 text-xs text-ink-muted">
      <Heart class="w-4 h-4 text-violet-500" />
      <span>{{ t('home.noCoupleDesc') }}</span>
      <AppButton size="sm" class="ml-2" @click="emit('link-couple')">
        <Plus class="w-3.5 h-3.5 mr-1" />
        {{ t('home.linkCoupleBtn') }}
      </AppButton>
    </div>
  </div>
</template>
