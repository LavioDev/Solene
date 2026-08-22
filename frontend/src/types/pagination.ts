export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  per_page: number
  total_pages: number
  has_more: boolean
}

export interface PaginationParams {
  page?: number
  per_page?: number
  search?: string
  [key: string]: any
}
