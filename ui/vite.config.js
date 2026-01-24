import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/search': 'http://localhost:8080',
      '/verify-password': 'http://localhost:8080',
      '/health': 'http://localhost:8080',
    },
  },
})
