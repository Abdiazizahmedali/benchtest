import { FrappeUI, frappeRequest, setConfig } from 'frappe-ui'
import { createApp } from 'vue'
import App from './App.vue'
import './index.css'

// Resources call the site's own API with the visitor's session (and CSRF token from boot).
setConfig('resourceFetcher', frappeRequest)

createApp(App).use(FrappeUI).mount('#app')
