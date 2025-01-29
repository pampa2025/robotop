import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    allowedHosts: ['h3vpzaeq-y3swm9ke-iwmtm82sj1s7.aca2-preview.marscode.dev'],
  },
})
