import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    host: true,
    proxy: {
      '/api': 'http://backend:8000',
      '/previews': 'http://backend:8000',
      '/results': 'http://backend:8000',
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
  }
})
