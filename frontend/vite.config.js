import vue from '@vitejs/plugin-vue'
import frappeui from 'frappe-ui/vite'
import { defineConfig } from 'vite'

// frappe-ui's plugin builds into cb_nairobi_fresh_kitchen_0ea0/public/frontend and copies index.html to
// cb_nairobi_fresh_kitchen_0ea0/www/cb.html so the SPA is served at /cb (ADR-0003).
export default defineConfig({
  plugins: [
    frappeui({
      frontendRoute: '/cb',
      buildConfig: {
        outDir: '../cb_nairobi_fresh_kitchen_0ea0/public/frontend',
        indexHtmlPath: '../cb_nairobi_fresh_kitchen_0ea0/www/cb.html',
        baseUrl: '/assets/cb_nairobi_fresh_kitchen_0ea0/frontend/',
        sourcemap: false,
      },
    }),
    vue(),
  ],
})
