import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Use VPS backend IP from environment or default to localhost for dev
const API_URL = process.env.VITE_API_URL || 'http://114.29.239.50:8000'

export default defineConfig({
  plugins: [react()],
  define: {
    'import.meta.env.VITE_API_URL': JSON.stringify(API_URL)
  }
})