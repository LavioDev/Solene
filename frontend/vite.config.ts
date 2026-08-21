import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import VueDevTools from 'vite-plugin-vue-devtools'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [
    vue(),
    VueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8200',
        changeOrigin: true
      },
      '/uploads': {
        target: 'http://127.0.0.1:8200',
        changeOrigin: true
      },
      '/ws': {
        target: 'ws://127.0.0.1:8200',
        ws: true
      }
    }
  }
})
