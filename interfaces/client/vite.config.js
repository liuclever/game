import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath } from 'node:url'
import path from 'node:path'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  server: {
    host: '0.0.0.0',
    allowedHosts: true,
    proxy: {
      '/api/refine-pot': {
        target: 'http://127.0.0.1:58321',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/refine-pot/, '/refine-pot'),
      },
      '/api': {
        target: 'http://127.0.0.1:58321',
        changeOrigin: true,
      },
    },
  },
})
