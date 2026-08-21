import axios, { type AxiosRequestConfig } from 'axios'

export const apiClient = axios.create({
  baseURL: '/api/v1',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Store accessor function to prevent circular imports
let getAccessTokenFn: () => string | null = () => null
let setAccessTokenFn: (token: string | null) => void = () => {}
let onAuthFailedFn: () => void = () => {}

export function configureAuthInterceptors(
  getToken: () => string | null,
  setToken: (token: string | null) => void,
  onFailed: () => void,
) {
  getAccessTokenFn = getToken
  setAccessTokenFn = setToken
  onAuthFailedFn = onFailed
}

// Request Interceptor: Attach in-memory bearer token
apiClient.interceptors.request.use((config) => {
  const token = getAccessTokenFn()
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response Interceptor: Silent refresh on 401
let isRefreshing = false
let failedQueue: Array<{
  resolve: (value?: any) => void
  reject: (reason?: any) => void
  config: AxiosRequestConfig
}> = []

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error)
    } else {
      if (token && prom.config.headers) {
        prom.config.headers.Authorization = `Bearer ${token}`
      }
      apiClient(prom.config).then(prom.resolve).catch(prom.reject)
    }
  })
  failedQueue = []
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (originalRequest.url?.includes('/auth/login') || originalRequest.url?.includes('/auth/refresh')) {
        return Promise.reject(error)
      }

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject, config: originalRequest })
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        const response = await axios.post<{ access_token: string }>(
          '/api/v1/auth/refresh',
          {},
          { withCredentials: true }
        )
        const newToken = response.data.access_token
        setAccessTokenFn(newToken)
        processQueue(null, newToken)
        
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${newToken}`
        }
        return apiClient(originalRequest)
      } catch (refreshErr) {
        processQueue(refreshErr, null)
        setAccessTokenFn(null)
        onAuthFailedFn()
        return Promise.reject(refreshErr)
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(error)
  }
)
