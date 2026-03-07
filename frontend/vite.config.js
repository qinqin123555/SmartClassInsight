import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5174,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        secure: false,
        // 支持长连接
        timeout: 60000, // 60秒超时
        // 禁用缓存
        headers: {
          'Cache-Control': 'no-cache',
          'Connection': 'keep-alive'
        }
      }
    }
  }
})
