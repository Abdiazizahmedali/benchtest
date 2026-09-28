// Serve the built SPA at /cb: copy index.html into the app's www folder (docs/07, ADR-0003).
import { copyFileSync } from 'node:fs'

copyFileSync('../cb_spike/public/frontend/index.html', '../cb_spike/www/cb.html')
