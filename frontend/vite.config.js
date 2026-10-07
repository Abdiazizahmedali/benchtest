import vue from '@vitejs/plugin-vue'
import frappeui from 'frappe-ui/vite'
import { defineConfig } from 'vite'

// frappe-ui's plugin builds into cb_cb_demo_0255/public/frontend and copies index.html to
// cb_cb_demo_0255/www/cb.html so the SPA is served at /cb (ADR-0003).
export default defineConfig({
  plugins: [
    frappeui({
      frontendRoute: '/cb',
      buildConfig: {
        outDir: '../cb_cb_demo_0255/public/frontend',
        indexHtmlPath: '../cb_cb_demo_0255/www/cb.html',
        baseUrl: '/assets/cb_cb_demo_0255/frontend/',
        sourcemap: false,
      },
    }),
    vue(),
  ],
})
