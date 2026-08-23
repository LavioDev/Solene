export interface MemoryImage {
  id: string
  memory_id: string
  file_path: string
  filename?: string | null
  created_at: string
}

export interface MemoryItem {
  id: string
  user_id: string
  title: string
  content: string
  image_url?: string | null
  images: MemoryImage[]
  category: string
  display_type: 'DATE' | 'RANDOM'
  target_date?: string | null
  is_shared?: boolean
  created_at: string
  updated_at: string
}
