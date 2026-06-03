import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: true,
    proxy: {
      '/api': {
        target: process.env.VITE_API_TARGET ?? 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      // Proxy external images so the browser loads them same-origin
      '/img-proxy/meals': {
        target: 'https://www.themealdb.com',
        changeOrigin: true,
        rewrite: path => path.replace('/img-proxy/meals', '/images/media/meals'),
      },
      '/img-proxy/food': {
        target: 'https://images.openfoodfacts.org',
        changeOrigin: true,
        rewrite: path => path.replace('/img-proxy/food', ''),
      },
    },
  },
})
