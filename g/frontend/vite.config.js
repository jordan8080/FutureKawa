import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
// Le front appelle /api/... en same-origin ; en dev, Vite proxifie /api vers
// le backend central (port 8001). En prod, c'est nginx qui s'en charge.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: process.env.VITE_PROXY_TARGET || 'http://localhost:8001',
        changeOrigin: true,
      },
    },
  },
})
