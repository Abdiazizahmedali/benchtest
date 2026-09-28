import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'

// Built assets live in the app's public folder (served at /assets/cb_spike/frontend/).
export default defineConfig({
  plugins: [vue()],
  build: { outDir: '../cb_spike/public/frontend', emptyOutDir: true },
})
