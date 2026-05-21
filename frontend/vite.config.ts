import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      // Forward /api/v1/* directly to FastAPI on :8000
      // Backend prefix is /api/v1 (see main.py include_router calls)
      // No path rewriting needed — paths are forwarded verbatim
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})