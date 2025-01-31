import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    allowedHosts: ['23v1zp1q-tz81e3ay-py9avqk5ju2h.aca2-preview.marscode.dev'],
  },
})
