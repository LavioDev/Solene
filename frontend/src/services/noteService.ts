import { apiClient } from '@/services/apiClient'
import type { NoteItem } from '@/types/note'

export const noteService = {
  async getNotes(): Promise<NoteItem[]> {
    const response = await apiClient.get<NoteItem[]>('/notes')
    return response.data
  },

  async createNote(payload: {
    title: string
    content: string
    image_url?: string | null
    image_urls?: string[]
    category?: string
    display_type?: 'DATE' | 'RANDOM'
    target_date?: string | null
  }): Promise<NoteItem> {
    const response = await apiClient.post<NoteItem>('/notes', payload)
    return response.data
  },

  async updateNote(
    noteId: string,
    payload: {
      title?: string
      content?: string
      image_url?: string | null
      image_urls?: string[]
      category?: string
      display_type?: string
      target_date?: string | null
    },
  ): Promise<NoteItem> {
    const response = await apiClient.put<NoteItem>(`/notes/${noteId}`, payload)
    return response.data
  },

  async deleteNote(noteId: string): Promise<void> {
    await apiClient.delete(`/notes/${noteId}`)
  },
}
