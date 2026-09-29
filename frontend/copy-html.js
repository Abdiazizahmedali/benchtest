// Serve the built SPA at /cb: copy index.html into the app's www folder (ADR-0003).
import { copyFileSync } from 'node:fs'

copyFileSync('../cb_cb_demo/public/frontend/index.html', '../cb_cb_demo/www/cb.html')
