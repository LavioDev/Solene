import type { MoodDefinition } from '@/types/mood'

export const MOOD_DEFINITIONS: MoodDefinition[] = [
  {
    score: 1,
    emoji: '😭',
    tag: 'terrible',
    nameKey: 'mood.scores.terrible',
    color: '#ef4444', // Red-500
    badgeColor: 'bg-red-50 text-red-700 border-red-200',
    heatmapClass: 'bg-red-500/80',
  },
  {
    score: 2,
    emoji: '😣',
    tag: 'very_bad',
    nameKey: 'mood.scores.very_bad',
    color: '#f43f5e', // Rose-500
    badgeColor: 'bg-rose-50 text-rose-700 border-rose-200',
    heatmapClass: 'bg-rose-400/80',
  },
  {
    score: 3,
    emoji: '😞',
    tag: 'sad',
    nameKey: 'mood.scores.sad',
    color: '#f97316', // Orange-500
    badgeColor: 'bg-orange-50 text-orange-700 border-orange-200',
    heatmapClass: 'bg-orange-400/80',
  },
  {
    score: 4,
    emoji: '🥱',
    tag: 'tired',
    nameKey: 'mood.scores.tired',
    color: '#eab308', // Yellow-500
    badgeColor: 'bg-amber-50 text-amber-700 border-amber-200',
    heatmapClass: 'bg-amber-400/80',
  },
  {
    score: 5,
    emoji: '😐',
    tag: 'neutral',
    nameKey: 'mood.scores.neutral',
    color: '#64748b', // Slate-500
    badgeColor: 'bg-slate-50 text-slate-700 border-slate-200',
    heatmapClass: 'bg-slate-400/80',
  },
  {
    score: 6,
    emoji: '🙂',
    tag: 'okay',
    nameKey: 'mood.scores.okay',
    color: '#14b8a6', // Teal-500
    badgeColor: 'bg-teal-50 text-teal-700 border-teal-200',
    heatmapClass: 'bg-teal-500/80',
  },
  {
    score: 7,
    emoji: '😊',
    tag: 'good',
    nameKey: 'mood.scores.good',
    color: '#10b981', // Emerald-500
    badgeColor: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    heatmapClass: 'bg-emerald-500/80',
  },
  {
    score: 8,
    emoji: '😃',
    tag: 'excited',
    nameKey: 'mood.scores.excited',
    color: '#06b6d4', // Cyan-500
    badgeColor: 'bg-cyan-50 text-cyan-700 border-cyan-200',
    heatmapClass: 'bg-cyan-500/80',
  },
  {
    score: 9,
    emoji: '🥰',
    tag: 'loving',
    nameKey: 'mood.scores.loving',
    color: '#ec4899', // Pink-500
    badgeColor: 'bg-pink-50 text-pink-700 border-pink-200',
    heatmapClass: 'bg-pink-500/80',
  },
  {
    score: 10,
    emoji: '🤩',
    tag: 'awesome',
    nameKey: 'mood.scores.awesome',
    color: '#7c3aed', // Violet-600 (Solène signature)
    badgeColor: 'bg-primary-50 text-primary-700 border-primary-200',
    heatmapClass: 'bg-primary-600',
  },
]

export function getMoodByScore(score?: number | null): MoodDefinition | null {
  if (!score || score < 1 || score > 10) return null
  return MOOD_DEFINITIONS[score - 1] || null
}

export function getMoodByTag(tag?: string | null): MoodDefinition | null {
  if (!tag) return null
  return MOOD_DEFINITIONS.find((m) => m.tag === tag) || null
}

// GitHub Matrix Color scale mapping for 1-10 scores
export function getHeatmapCellColor(score?: number | null, isDark: boolean = false): string {
  if (!score || score < 1) {
    return isDark ? 'bg-zinc-800/80 hover:border-zinc-500' : 'bg-surface-raised/90 border-border/70 hover:border-primary-300'
  }
  
  // High contrast heatmap colors
  if (score <= 2) return 'bg-rose-400 text-white'
  if (score <= 4) return 'bg-amber-400 text-white'
  if (score <= 5) return 'bg-slate-400 text-white'
  if (score <= 6) return 'bg-teal-400 text-white'
  if (score <= 8) return 'bg-emerald-500 text-white'
  return 'bg-primary-600 text-white shadow-xs ring-1 ring-primary-400/40'
}
