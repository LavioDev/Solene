import { ref, onUnmounted } from 'vue'

export function useWebSocket<T = any>(path: string) {
  const isConnected = ref(false)
  const lastMessage = ref<T | null>(null)
  const error = ref<Event | null>(null)
  let socket: WebSocket | null = null
  let reconnectTimeout: number | null = null

  function connect() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    const wsUrl = `${protocol}//${host}${path}`

    socket = new WebSocket(wsUrl)

    socket.onopen = () => {
      isConnected.value = true
      error.value = null
    }

    socket.onmessage = (event) => {
      try {
        if (typeof event.data === 'string') {
          lastMessage.value = JSON.parse(event.data)
        } else {
          lastMessage.value = event.data as T
        }
      } catch {
        lastMessage.value = event.data as T
      }
    }

    socket.onerror = (err) => {
      error.value = err
    }

    socket.onclose = () => {
      isConnected.value = false
      // Attempt auto-reconnect every 3 seconds
      reconnectTimeout = window.setTimeout(() => {
        connect()
      }, 3000)
    }
  }

  function send(data: string | ArrayBufferLike | Blob | ArrayBufferView) {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(data)
    }
  }

  function disconnect() {
    if (reconnectTimeout) {
      clearTimeout(reconnectTimeout)
    }
    if (socket) {
      socket.close()
    }
  }

  onUnmounted(() => {
    disconnect()
  })

  return {
    isConnected,
    lastMessage,
    error,
    connect,
    send,
    disconnect,
  }
}
