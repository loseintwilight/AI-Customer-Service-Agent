import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/ai': {
        target: 'http://localhost:8089',
        changeOrigin: true,
      },
      '/question': {
        target: 'http://localhost:8089',
        changeOrigin: true,
      },
    },
  },
})