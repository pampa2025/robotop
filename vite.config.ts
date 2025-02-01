import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    allowedHosts: ['dkeegcl3-g4g1xzlm-mf7k3imdzjyf.aca2-preview.marscode.dev'],
  },
})
